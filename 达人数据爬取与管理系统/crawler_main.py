# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 主爬虫脚本
支持按类型分类保存、断点续爬、多账号管理、任务调度
创建时间: 2025-01-23
"""

import os
import json
import time
import csv
import argparse
import logging
import random
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

# 加载环境变量
load_dotenv()

class DarenCrawler:
    def __init__(self):
        self.base_url = "https://agent.oceanengine.com/star/mirror/gw/api/gsearch/search_for_author_square"
        self.setup_logging()
        self.setup_directories()
        self.db_config = self.get_db_config()
        self.current_account = None
        self.task_id = None
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"crawler_{date.today().strftime('%Y%m%d')}.log"
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
        
    def setup_directories(self):
        """创建必要的目录结构"""
        directories = [
            "logs",
            "data_by_type", 
            "exports",
            "temp",
            "backups"
        ]
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
            
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
            
    def load_account_config(self, account_id: int = None):
        """加载账号配置"""
        conn = self.get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                if account_id:
                    cursor.execute(
                        "SELECT * FROM daoren_account WHERE id = %s AND status = 'active'",
                        (account_id,)
                    )
                else:
                    # 选择最少使用的活跃账号
                    cursor.execute("""
                        SELECT * FROM daoren_account 
                        WHERE status = 'active' 
                        AND (cooldown_until IS NULL OR cooldown_until < NOW())
                        ORDER BY last_used_at ASC, success_count ASC 
                        LIMIT 1
                    """)
                
                account = cursor.fetchone()
                if account:
                    self.current_account = account
                    # 更新最后使用时间
                    cursor.execute(
                        "UPDATE daoren_account SET last_used_at = NOW() WHERE id = %s",
                        (account['id'],)
                    )
                    conn.commit()
                    self.logger.info(f"使用账号: {account['account_name']}")
                    return account
                else:
                    self.logger.warning("没有可用的活跃账号")
                    return None
                    
        except Exception as e:
            self.logger.error(f"加载账号配置失败: {e}")
            return None
        finally:
            conn.close()
            
    def get_headers(self):
        """获取请求头"""
        if self.current_account and self.current_account.get('headers'):
            try:
                custom_headers = json.loads(self.current_account['headers'])
                return custom_headers
            except:
                pass
                
        # 默认请求头
        return {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'agw-js-conv': 'str',
            'content-type': 'application/json',
            'origin': 'https://agent.oceanengine.com',
            'priority': 'u=1, i',
            'referer': 'https://agent.oceanengine.com/admin/star-agent/vue2/market',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-login-source': '1',
            'x-tt-possess-scene': '2',
            'x-tt-possess-star-id': '1843934177451019',
            'cookie': self.current_account.get('cookies', '') if self.current_account else ''
        }
        
    def create_task(self, task_name: str, start_page: int, end_page: int, domain_filter: str = None):
        """创建爬取任务"""
        conn = self.get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO daoren_task_log 
                    (task_name, domain_filter, start_page, end_page, status, start_time)
                    VALUES (%s, %s, %s, %s, 'running', NOW())
                """, (task_name, domain_filter, start_page, end_page))
                
                task_id = cursor.lastrowid
                conn.commit()
                self.task_id = task_id
                self.logger.info(f"创建任务 ID: {task_id}, 名称: {task_name}")
                return task_id
                
        except Exception as e:
            self.logger.error(f"创建任务失败: {e}")
            return None
        finally:
            conn.close()
            
    def update_task_progress(self, current_page: int, total_authors: int = None, 
                           success_authors: int = None, failed_authors: int = None):
        """更新任务进度"""
        if not self.task_id:
            return
            
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                update_fields = ["current_page = %s"]
                params = [current_page]
                
                if total_authors is not None:
                    update_fields.append("total_authors = %s")
                    params.append(total_authors)
                    
                if success_authors is not None:
                    update_fields.append("success_authors = %s")
                    params.append(success_authors)
                    
                if failed_authors is not None:
                    update_fields.append("failed_authors = %s")
                    params.append(failed_authors)
                    
                params.append(self.task_id)
                
                cursor.execute(f"""
                    UPDATE daoren_task_log 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """, params)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"更新任务进度失败: {e}")
        finally:
            conn.close()
            
    def complete_task(self, status: str = 'completed', error_message: str = None):
        """完成任务"""
        if not self.task_id:
            return
            
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE daoren_task_log 
                    SET status = %s, end_time = NOW(), error_message = %s
                    WHERE id = %s
                """, (status, error_message, self.task_id))
                
                conn.commit()
                self.logger.info(f"任务 {self.task_id} 状态更新为: {status}")
                
        except Exception as e:
            self.logger.error(f"完成任务失败: {e}")
        finally:
            conn.close()
            
    def fetch_daren_data_by_page(self, page_num: int) -> Dict[str, Any]:
        """获取指定页码的达人数据"""
        headers = self.get_headers()
        
        payload = {
            "scene_param": {
                "platform_source": 1,
                "search_scene": 1,
                "display_scene": 1,
                "marketing_target": 1,
                "task_category": 1,
                "first_industry_id": 0,
                "task_status": 3
            },
            "search_param": {
                "seach_type": 2
            },
            "sort_param": {
                "sort_type": 2,
                "sort_field": {
                    "field_name": "score"
                }
            },
            "page_param": {
                "page": page_num,
                "limit": 20
            },
            "attribute_filter": [
                {
                    "field": {
                        "field_name": "tag_level_two"
                    },
                    "field_value": "[2]"
                },
                {
                    "field": {
                        "field_name": "price_by_video_type__ge",
                        "rel_id": "2"
                    },
                    "field_value": "0"
                }
            ]
        }
        
        try:
            self.logger.info(f"正在请求第 {page_num} 页数据...")
            
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload, 
                timeout=int(os.getenv('API_TIMEOUT', 30))
            )
            response.raise_for_status()
            
            # 更新账号成功计数
            if self.current_account:
                self.update_account_stats(self.current_account['id'], success=True)
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求第 {page_num} 页失败: {e}")
            
            # 更新账号失败计数
            if self.current_account:
                self.update_account_stats(self.current_account['id'], success=False)
                
            return {}
            
    def update_account_stats(self, account_id: int, success: bool):
        """更新账号统计信息"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                if success:
                    cursor.execute(
                        "UPDATE daoren_account SET success_count = success_count + 1 WHERE id = %s",
                        (account_id,)
                    )
                else:
                    cursor.execute(
                        "UPDATE daoren_account SET failed_count = failed_count + 1 WHERE id = %s",
                        (account_id,)
                    )
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"更新账号统计失败: {e}")
        finally:
            conn.close()
            
    def parse_author_data(self, author: Dict[str, Any], page_num: int) -> Dict[str, Any]:
        """解析单个达人的数据"""
        attr_data = author.get('attribute_datas', {})
        
        # 安全获取task_info，避免list index out of range错误
        task_infos = author.get('task_infos', [])
        task_info = task_infos[0] if task_infos else {}
        
        # 安全获取price_info，避免list index out of range错误
        price_infos = task_info.get('price_infos', [])
        price_info = price_infos[0] if price_infos else {}
        
        # 安全获取数值，避免None和NaN
        def safe_get_number(data, key, default=0):
            value = data.get(key, default)
            if value is None or str(value).lower() == 'nan':
                return default
            try:
                return int(value) if isinstance(value, (int, float)) and value == int(value) else float(value)
            except (ValueError, TypeError):
                return default
                
        def safe_get_string(data, key, default=''):
            value = data.get(key, default)
            if value is None or str(value).lower() == 'nan':
                return default
            return str(value).strip()
        
        # 提取核心字段
        parsed_data = {
            "达人ID (star_id)": safe_get_string(author, 'star_id'),
            "昵称 (nick_name)": safe_get_string(attr_data, 'nick_name'),
            "粉丝数 (follower)": safe_get_number(attr_data, 'follower', 0),
            "所在地 (city)": safe_get_string(attr_data, 'city'),
            "近30天平均播放量 (vv_median_30d)": safe_get_number(attr_data, 'vv_median_30d', 0),
            "近30天互动率 (interact_rate_within_30d)": safe_get_number(attr_data, 'interact_rate_within_30d', 0.0),
            "报价 (price)": safe_get_number(price_info, 'price', 0),
            "星图指数 (star_index)": safe_get_number(attr_data, 'star_index', 0),
            "电商等级 (author_ecom_level)": safe_get_string(attr_data, 'author_ecom_level'),
            "内容主题标签 (content_theme_labels_180d)": safe_get_string(attr_data, 'content_theme_labels_180d'),
            "页码": page_num,
            "爬取日期": date.today().strftime('%Y-%m-%d')
        }
        
        # 提取达人类型
        tags_relation_str = attr_data.get('tags_relation', '{}')
        try:
            # 安全处理tags_relation字段
            if tags_relation_str is None or str(tags_relation_str).lower() == 'nan':
                tags_relation_str = '{}'
            elif not isinstance(tags_relation_str, str):
                tags_relation_str = str(tags_relation_str)
                
            tags_relation_dict = json.loads(tags_relation_str)
            达人类型列表 = [tag for tag in tags_relation_dict.keys() if tag and str(tag).strip()]
        except (json.JSONDecodeError, TypeError, AttributeError):
            达人类型列表 = []
            
        parsed_data["达人类型 (tags)"] = 达人类型列表
        
        return parsed_data
        
    def ensure_directory(self, path: str):
        """确保目录存在"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
    def save_author_to_type_folder(self, author_data: Dict[str, Any], page_num: int, crawl_date: str):
        """根据达人类型，保存到对应文件夹下的独立CSV"""
        tags = author_data.get("达人类型 (tags)", [])
        nick_name = author_data.get("昵称 (nick_name)", "未知昵称")
        
        # 确保nick_name不是NaN或None
        if not nick_name or str(nick_name).lower() == 'nan':
            nick_name = "未知昵称"
        
        # 清理文件名中的特殊字符
        safe_nick_name = "".join(c for c in str(nick_name) if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_nick_name:
            safe_nick_name = f"达人_{author_data.get('达人ID (star_id)', 'unknown')}"
            
        # 如果没有类型，默认存入 "未分类"
        if not tags or not isinstance(tags, list):
            tags = ["未分类"]
            
        for tag in tags:
            # 确保tag是有效字符串
            if not tag or str(tag).lower() == 'nan':
                tag = "未分类"
            tag = str(tag).strip()
            
            folder_path = f"data_by_type/{tag}"
            self.ensure_directory(folder_path)
            
            filename = f"{tag}-{safe_nick_name}-第{page_num}页-{crawl_date}.csv"
            filepath = os.path.join(folder_path, filename)
            
            # 清理数据中的NaN值
            clean_data = {}
            for key, value in author_data.items():
                if value is None or str(value).lower() == 'nan':
                    if key in ['粉丝数 (follower)', '近30天平均播放量 (vv_median_30d)', '报价 (price)', '星图指数 (star_index)', '页码']:
                        clean_data[key] = 0
                    elif key == '近30天互动率 (interact_rate_within_30d)':
                        clean_data[key] = 0.0
                    else:
                        clean_data[key] = ''
                else:
                    clean_data[key] = value
            
            # 写入单条记录
            try:
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=clean_data.keys())
                    writer.writeheader()
                    writer.writerow(clean_data)
                    
                self.logger.debug(f"保存达人数据: {filepath}")
                
            except Exception as e:
                self.logger.error(f"保存文件失败 {filepath}: {e}")
                
    def crawl_pages(self, start_page: int, end_page: int, task_name: str = None, 
                   domain_filter: str = None, resume_from: int = None):
        """爬取指定页面范围的数据"""
        
        # 创建任务
        if not task_name:
            task_name = f"爬取_{start_page}到{end_page}页_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        self.create_task(task_name, start_page, end_page, domain_filter)
        
        crawl_date = date.today().strftime("%Y%m%d")
        total_authors = 0
        success_authors = 0
        failed_authors = 0
        
        # 确定起始页码（支持断点续爬）
        actual_start_page = resume_from if resume_from else start_page
        
        self.logger.info(f"开始爬取任务: {task_name}")
        self.logger.info(f"页面范围: {actual_start_page} - {end_page}")
        
        try:
            for page in range(actual_start_page, end_page + 1):
                # 加载账号配置
                if not self.current_account:
                    account = self.load_account_config()
                    if not account:
                        self.logger.error("无可用账号，停止爬取")
                        break
                        
                self.logger.info(f"📄 正在处理第 {page} 页...")
                
                # 获取数据
                raw_data = self.fetch_daren_data_by_page(page)
                
                if not raw_data or raw_data.get('base_resp', {}).get('status_code') != 0:
                    self.logger.warning(f"第 {page} 页请求失败")
                    failed_authors += 1
                    continue
                    
                # 解析数据
                authors = raw_data.get('authors', [])
                page_success = 0
                
                for author in authors:
                    try:
                        parsed = self.parse_author_data(author, page)
                        
                        # 如果设置了类型筛选，检查是否匹配
                        if domain_filter:
                            author_tags = parsed.get("达人类型 (tags)", [])
                            filter_tags = [tag.strip() for tag in domain_filter.split(',')]
                            if not any(tag in author_tags for tag in filter_tags):
                                continue
                                
                        self.save_author_to_type_folder(parsed, page, crawl_date)
                        page_success += 1
                        success_authors += 1
                        
                    except Exception as e:
                        self.logger.error(f"处理达人数据失败: {e}")
                        failed_authors += 1
                        
                total_authors += len(authors)
                
                # 更新任务进度
                self.update_task_progress(page, total_authors, success_authors, failed_authors)
                
                self.logger.info(f"✅ 第 {page} 页处理完成，成功: {page_success}, 总计: {len(authors)}")
                
                # 检查是否还有更多数据
                has_more = raw_data.get('pagination', {}).get('has_more', False)
                if not has_more:
                    self.logger.info("已到达最后一页，停止爬取")
                    break
                    
                # 随机延迟防反爬
                delay = random.uniform(
                    float(os.getenv('CRAWL_DELAY_MIN', 1.0)),
                    float(os.getenv('CRAWL_DELAY_MAX', 3.0))
                )
                time.sleep(delay)
                
            # 完成任务
            self.complete_task('completed')
            self.logger.info(f"🎉 爬取任务完成！总计处理 {total_authors} 位达人，成功 {success_authors}，失败 {failed_authors}")
            
        except KeyboardInterrupt:
            self.logger.info("用户中断爬取")
            self.complete_task('paused', '用户中断')
        except Exception as e:
            self.logger.error(f"爬取过程中发生错误: {e}")
            self.complete_task('failed', str(e))
            
    def resume_task(self, task_id: int):
        """恢复未完成的任务"""
        conn = self.get_db_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM daoren_task_log WHERE id = %s",
                    (task_id,)
                )
                task = cursor.fetchone()
                
                if not task:
                    self.logger.error(f"任务 {task_id} 不存在")
                    return
                    
                if task['status'] not in ['paused', 'failed']:
                    self.logger.error(f"任务 {task_id} 状态为 {task['status']}，无法恢复")
                    return
                    
                self.logger.info(f"恢复任务: {task['task_name']}")
                
                # 从当前页码+1开始继续
                resume_page = task['current_page'] + 1 if task['current_page'] > 0 else task['start_page']
                
                self.task_id = task_id
                self.crawl_pages(
                    task['start_page'], 
                    task['end_page'],
                    task['task_name'],
                    task['domain_filter'],
                    resume_page
                )
                
        except Exception as e:
            self.logger.error(f"恢复任务失败: {e}")
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description='达人数据爬取与管理系统')
    parser.add_argument('--start', type=int, default=1, help='起始页码')
    parser.add_argument('--end', type=int, default=5, help='结束页码')
    parser.add_argument('--task-name', type=str, help='任务名称')
    parser.add_argument('--domain-filter', type=str, help='类型筛选，多个用逗号分隔，如: 美妆,时尚')
    parser.add_argument('--resume-task', type=int, help='恢复指定ID的任务')
    parser.add_argument('--account-id', type=int, help='指定使用的账号ID')
    
    args = parser.parse_args()
    
    crawler = DarenCrawler()
    
    if args.resume_task:
        crawler.resume_task(args.resume_task)
    else:
        # 加载指定账号或自动选择
        crawler.load_account_config(args.account_id)
        
        crawler.crawl_pages(
            args.start, 
            args.end, 
            args.task_name,
            args.domain_filter
        )


if __name__ == "__main__":
    main()