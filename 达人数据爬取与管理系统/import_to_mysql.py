# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 数据入库脚本
将CSV数据导入MySQL数据库，支持去重、批量处理、数据验证
创建时间: 2025-01-23
"""

import os
import json
import csv
import logging
import argparse
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DataImporter:
    def __init__(self):
        self.setup_logging()
        self.db_config = self.get_db_config()
        self.batch_size = int(os.getenv('BATCH_SIZE', 50))
        self.stats = {
            'total_files': 0,
            'total_records': 0,
            'success_records': 0,
            'failed_records': 0,
            'duplicate_records': 0,
            'updated_records': 0
        }
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"import_{date.today().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_db_config(self):
        """获取数据库配置"""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'influencer_crawler'),
            'charset': 'utf8mb4'
        }
        
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            return pymysql.connect(**self.db_config, cursorclass=DictCursor)
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            return None
            
    def validate_record(self, record: Dict[str, Any]) -> bool:
        """验证记录数据的有效性"""
        required_fields = ['达人ID (star_id)', '昵称 (nick_name)']
        
        for field in required_fields:
            value = record.get(field)
            # 处理NaN值和空值
            if pd.isna(value) or value is None or str(value).lower() == 'nan':
                self.logger.warning(f"记录缺少必要字段 {field}: {record}")
                return False
            
            # 对于昵称字段，特别处理数字0的情况
            if field == '昵称 (nick_name)':
                str_value = str(value).strip()
                if not str_value or str_value == '0':
                    self.logger.warning(f"记录缺少必要字段 {field}: {record}")
                    return False
            # 对于其他字段，检查是否为空字符串
            elif isinstance(value, str) and not value.strip():
                self.logger.warning(f"记录缺少必要字段 {field}: {record}")
                return False
                
        # 验证数值字段
        numeric_fields = [
            '粉丝数 (follower)',
            '近30天平均播放量 (vv_median_30d)',
            '近30天互动率 (interact_rate_within_30d)',
            '报价 (price)',
            '星图指数 (star_index)'
        ]
        
        for field in numeric_fields:
            value = record.get(field)
            # 处理NaN、None和空值
            if pd.isna(value) or value is None or str(value).lower() == 'nan':
                record[field] = 0
                continue
                
            # 处理字符串类型的数值
            if isinstance(value, str):
                value = value.strip()
                if not value or not value.replace('.', '').replace('-', '').isdigit():
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        self.logger.warning(f"字段 {field} 数值格式错误: {value}")
                        record[field] = 0
            # 处理float类型
            elif isinstance(value, (int, float)):
                if pd.isna(value):
                    record[field] = 0
                    
        return True
        
    def parse_json_field(self, value: str) -> List[str]:
        """解析JSON字符串字段"""
        # 处理NaN值、None值和空值
        if pd.isna(value) or value is None or str(value).lower() == 'nan':
            return []
            
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
                
        try:
            # 处理不同格式的JSON字符串
            if isinstance(value, str):
                # 处理单引号格式
                if value.startswith("['") and value.endswith("']"):
                    value = value.replace("'", '"')
                # 处理Python列表格式
                elif value.startswith('[') and value.endswith(']'):
                    value = value.replace("'", '"')
                    
                return json.loads(value)
            elif isinstance(value, list):
                return value
            elif isinstance(value, (int, float)):
                # 处理数值类型，转为字符串列表
                return [str(value)] if not pd.isna(value) else []
            else:
                return []
                
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.warning(f"解析JSON字段失败: {value}, 错误: {e}")
            return []
            
    def process_csv_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """处理单条CSV记录，转换为数据库格式"""
        processed = {}
        
        # 基础字段映射
        field_mapping = {
            '达人ID (star_id)': 'star_id',
            '昵称 (nick_name)': 'nick_name',
            '粉丝数 (follower)': 'follower',
            '所在地 (city)': 'city',
            '近30天平均播放量 (vv_median_30d)': 'vv_median_30d',
            '近30天互动率 (interact_rate_within_30d)': 'interact_rate_within_30d',
            '报价 (price)': 'price',
            '星图指数 (star_index)': 'star_index',
            '电商等级 (author_ecom_level)': 'author_ecom_level',
            '页码': 'page_num',
            '爬取日期': 'crawled_at'
        }
        
        for csv_field, db_field in field_mapping.items():
            value = record.get(csv_field)
            
            # 统一处理NaN值、None值和空值
            if pd.isna(value) or value is None or str(value).lower() == 'nan':
                value = None
            elif isinstance(value, str):
                value = value.strip()
                if not value:
                    value = None
            
            # 根据字段类型设置值或默认值
            if value is not None and value != '':
                # 数值字段类型转换
                if db_field in ['follower', 'vv_median_30d', 'price', 'star_index', 'page_num']:
                    try:
                        processed[db_field] = int(float(str(value))) if value else 0
                    except (ValueError, TypeError):
                        processed[db_field] = 0
                elif db_field == 'interact_rate_within_30d':
                    try:
                        processed[db_field] = float(str(value)) if value else 0.0
                    except (ValueError, TypeError):
                        processed[db_field] = 0.0
                else:
                    processed[db_field] = str(value) if value else None
            else:
                # 设置默认值
                if db_field in ['follower', 'vv_median_30d', 'price', 'star_index', 'page_num']:
                    processed[db_field] = 0
                elif db_field == 'interact_rate_within_30d':
                    processed[db_field] = 0.0
                else:
                    processed[db_field] = None
                    
        # 处理JSON字段
        content_labels = self.parse_json_field(record.get('内容主题标签 (content_theme_labels_180d)', ''))
        tags = self.parse_json_field(record.get('达人类型 (tags)', ''))
        
        processed['content_theme_labels'] = json.dumps(content_labels, ensure_ascii=False)
        processed['tags'] = json.dumps(tags, ensure_ascii=False)
        
        # 处理日期字段
        crawled_date = record.get('爬取日期')
        if crawled_date:
            try:
                if isinstance(crawled_date, str):
                    if len(crawled_date) == 8:  # YYYYMMDD格式
                        processed['crawled_at'] = datetime.strptime(crawled_date, '%Y%m%d').date()
                    else:  # YYYY-MM-DD格式
                        processed['crawled_at'] = datetime.strptime(crawled_date, '%Y-%m-%d').date()
                else:
                    processed['crawled_at'] = crawled_date
            except ValueError:
                processed['crawled_at'] = date.today()
        else:
            processed['crawled_at'] = date.today()
            
        return processed
        
    def insert_record(self, conn, record: Dict[str, Any]) -> bool:
        """插入单条记录到数据库"""
        try:
            with conn.cursor() as cursor:
                # 使用 INSERT ... ON DUPLICATE KEY UPDATE 语句
                sql = """
                    INSERT INTO daoren_author 
                    (star_id, nick_name, follower, city, vv_median_30d, interact_rate_within_30d,
                     price, star_index, author_ecom_level, content_theme_labels, tags, 
                     crawled_at, page_num)
                    VALUES 
                    (%(star_id)s, %(nick_name)s, %(follower)s, %(city)s, %(vv_median_30d)s, 
                     %(interact_rate_within_30d)s, %(price)s, %(star_index)s, %(author_ecom_level)s,
                     %(content_theme_labels)s, %(tags)s, %(crawled_at)s, %(page_num)s)
                    ON DUPLICATE KEY UPDATE
                        nick_name = VALUES(nick_name),
                        follower = VALUES(follower),
                        city = VALUES(city),
                        vv_median_30d = VALUES(vv_median_30d),
                        interact_rate_within_30d = VALUES(interact_rate_within_30d),
                        price = VALUES(price),
                        star_index = VALUES(star_index),
                        author_ecom_level = VALUES(author_ecom_level),
                        content_theme_labels = VALUES(content_theme_labels),
                        tags = VALUES(tags),
                        crawled_at = VALUES(crawled_at),
                        page_num = VALUES(page_num),
                        updated_at = CURRENT_TIMESTAMP
                """
                
                cursor.execute(sql, record)
                
                # 检查是否是更新操作
                if cursor.rowcount == 1:
                    self.stats['success_records'] += 1
                elif cursor.rowcount == 2:
                    self.stats['updated_records'] += 1
                else:
                    self.stats['duplicate_records'] += 1
                    
                return True
                
        except Exception as e:
            self.logger.error(f"插入记录失败: {record.get('nick_name', 'unknown')}, 错误: {e}")
            self.stats['failed_records'] += 1
            return False
            
    def process_csv_file(self, filepath: str) -> bool:
        """处理单个CSV文件"""
        self.logger.info(f"开始处理文件: {filepath}")
        
        try:
            # 读取CSV文件
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            
            if df.empty:
                self.logger.warning(f"文件为空: {filepath}")
                return False
                
            conn = self.get_db_connection()
            if not conn:
                return False
                
            try:
                records_processed = 0
                
                for index, row in df.iterrows():
                    record_dict = row.to_dict()
                    
                    # 验证记录
                    if not self.validate_record(record_dict):
                        self.stats['failed_records'] += 1
                        continue
                        
                    # 处理记录
                    processed_record = self.process_csv_record(record_dict)
                    
                    # 插入数据库
                    if self.insert_record(conn, processed_record):
                        records_processed += 1
                        
                    # 批量提交
                    if records_processed % self.batch_size == 0:
                        conn.commit()
                        self.logger.debug(f"已处理 {records_processed} 条记录")
                        
                # 最终提交
                conn.commit()
                self.logger.info(f"文件处理完成: {filepath}, 处理记录数: {records_processed}")
                return True
                
            finally:
                conn.close()
                
        except Exception as e:
            self.logger.error(f"处理文件失败: {filepath}, 错误: {e}")
            return False
            
    def import_from_directory(self, directory: str, domain_filter: str = None) -> bool:
        """从目录导入所有CSV文件"""
        data_dir = Path(directory)
        
        if not data_dir.exists():
            self.logger.error(f"目录不存在: {directory}")
            return False
            
        csv_files = []
        
        # 如果指定了类型筛选，只处理对应文件夹
        if domain_filter:
            filter_domains = [d.strip() for d in domain_filter.split(',')]
            for domain in filter_domains:
                domain_dir = data_dir / domain
                if domain_dir.exists():
                    csv_files.extend(domain_dir.glob('*.csv'))
        else:
            # 处理所有子文件夹中的CSV文件
            csv_files = list(data_dir.rglob('*.csv'))
            
        if not csv_files:
            self.logger.warning(f"在目录 {directory} 中未找到CSV文件")
            return False
            
        self.logger.info(f"找到 {len(csv_files)} 个CSV文件")
        self.stats['total_files'] = len(csv_files)
        
        success_count = 0
        
        for csv_file in csv_files:
            if self.process_csv_file(str(csv_file)):
                success_count += 1
                
        self.logger.info(f"导入完成，成功处理 {success_count}/{len(csv_files)} 个文件")
        return success_count > 0
        
    def import_single_file(self, filepath: str) -> bool:
        """导入单个CSV文件"""
        if not Path(filepath).exists():
            self.logger.error(f"文件不存在: {filepath}")
            return False
            
        self.stats['total_files'] = 1
        return self.process_csv_file(filepath)
        
    def update_domain_table(self):
        """更新达人类型表"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                # 获取所有唯一的达人类型
                cursor.execute("""
                    SELECT DISTINCT tag_value
                    FROM daoren_author da
                    CROSS JOIN JSON_TABLE(da.tags, '$[*]' COLUMNS (tag_value VARCHAR(50) PATH '$')) AS jt
                    WHERE tag_value IS NOT NULL AND tag_value != ''
                """)
                
                tags = cursor.fetchall()
                
                # 插入新的类型到domain表
                for tag in tags:
                    tag_name = tag['tag_value']
                    cursor.execute("""
                        INSERT IGNORE INTO daoren_domain (name, description)
                        VALUES (%s, %s)
                    """, (tag_name, f'{tag_name}类型达人'))
                    
                conn.commit()
                self.logger.info(f"更新了 {len(tags)} 个达人类型")
                
        except Exception as e:
            self.logger.error(f"更新达人类型表失败: {e}")
        finally:
            conn.close()
            
    def create_export_log(self, export_type: str = 'csv', domain_filter: str = None):
        """创建导出日志记录"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO daoren_export_log 
                    (export_type, file_path, domain_filter, total_records, status)
                    VALUES (%s, %s, %s, %s, 'completed')
                """, (
                    export_type,
                    f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    domain_filter,
                    self.stats['success_records'] + self.stats['updated_records']
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"创建导出日志失败: {e}")
        finally:
            conn.close()
            
    def print_stats(self):
        """打印统计信息"""
        self.logger.info("=" * 50)
        self.logger.info("数据导入统计:")
        self.logger.info(f"处理文件数: {self.stats['total_files']}")
        self.logger.info(f"总记录数: {self.stats['total_records']}")
        self.logger.info(f"成功插入: {self.stats['success_records']}")
        self.logger.info(f"更新记录: {self.stats['updated_records']}")
        self.logger.info(f"重复记录: {self.stats['duplicate_records']}")
        self.logger.info(f"失败记录: {self.stats['failed_records']}")
        self.logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='达人数据入库脚本')
    parser.add_argument('--directory', type=str, default='data_by_type', 
                       help='CSV文件目录路径')
    parser.add_argument('--file', type=str, help='单个CSV文件路径')
    parser.add_argument('--domain-filter', type=str, 
                       help='类型筛选，多个用逗号分隔，如: 美妆,时尚')
    parser.add_argument('--update-domains', action='store_true',
                       help='更新达人类型表')
    
    args = parser.parse_args()
    
    importer = DataImporter()
    
    try:
        if args.file:
            # 导入单个文件
            success = importer.import_single_file(args.file)
        else:
            # 导入目录
            success = importer.import_from_directory(args.directory, args.domain_filter)
            
        if success and args.update_domains:
            importer.update_domain_table()
            
        # 创建导出日志
        importer.create_export_log('import', args.domain_filter)
        
        # 打印统计信息
        importer.print_stats()
        
        if success:
            importer.logger.info("✅ 数据导入完成！")
        else:
            importer.logger.error("❌ 数据导入失败！")
            
    except KeyboardInterrupt:
        importer.logger.info("用户中断导入")
    except Exception as e:
        importer.logger.error(f"导入过程中发生错误: {e}")


if __name__ == "__main__":
    main()