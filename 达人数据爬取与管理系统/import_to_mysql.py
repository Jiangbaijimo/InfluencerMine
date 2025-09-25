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
        
        # 完整字段映射 - 支持新的数据库结构
        field_mapping = {
            # 基础身份信息
            '达人ID (star_id)': 'star_id',
            '昵称 (nick_name)': 'nick_name',
            '核心用户ID (core_user_id)': 'core_user_id',
            '头像链接 (avatar_uri)': 'avatar_uri',
            '性别 (gender)': 'gender',
            '所在地 (city)': 'city',
            '省份 (province)': 'province',
            '达人类型 (author_type)': 'author_type',
            '账号状态 (author_status)': 'author_status',
            '达人等级 (grade)': 'grade',
            
            # 粉丝与影响力数据
            '粉丝数 (follower)': 'follower',
            '15天粉丝增长数 (fans_increment_within_15d)': 'fans_increment_within_15d',
            '30天粉丝增长数 (fans_increment_within_30d)': 'fans_increment_within_30d',
            '15天粉丝增长率 (fans_increment_rate_within_15d)': 'fans_increment_rate_within_15d',
            '近30天互动率 (interact_rate_within_30d)': 'interact_rate_within_30d',
            '30天互动中位数 (interaction_median_30d)': 'interaction_median_30d',
            '30天播放完成率 (play_over_rate_within_30d)': 'play_over_rate_within_30d',
            '近30天平均播放量 (vv_median_30d)': 'vv_median_30d',
            
            # 内容创作数据
            '30天星图视频数量 (star_item_count_within_30d)': 'star_item_count_within_30d',
            '90天星图视频总数 (star_video_cnt_90d)': 'star_video_cnt_90d',
            '90天星图视频互动率 (star_video_interact_rate_90d)': 'star_video_interact_rate_90d',
            '90天星图视频完播率 (star_video_finish_vv_rate_90d)': 'star_video_finish_vv_rate_90d',
            '90天星图视频播放中位数 (star_video_median_vv_90d)': 'star_video_median_vv_90d',
            
            # 商业价值数据
            '1-20秒视频报价 (price_1_20)': 'price_1_20',
            '20-60秒视频报价 (price_20_60)': 'price_20_60',
            '60秒以上视频报价 (price_60)': 'price_60',
            '指派任务价格区间 (assign_task_price_list)': 'assign_task_price_list',
            '预期播放量 (expected_play_num)': 'expected_play_num',
            '预期自然播放量 (expected_natural_play_num)': 'expected_natural_play_num',
            '星图指数 (star_index)': 'star_index',
            
            # CPM成本数据
            '1-20秒预期CPM (prospective_1_20_cpm)': 'prospective_1_20_cpm',
            '20-60秒预期CPM (prospective_20_60_cpm)': 'prospective_20_60_cpm',
            '60秒以上预期CPM (prospective_60_cpm)': 'prospective_60_cpm',
            '推广1-20秒预期CPM (promotion_prospective_1_20_cpm)': 'promotion_prospective_1_20_cpm',
            '推广20-60秒预期CPM (promotion_prospective_20_60_cpm)': 'promotion_prospective_20_60_cpm',
            '推广60秒以上预期CPM (promotion_prospective_60_cpm)': 'promotion_prospective_60_cpm',
            '推广预期播放量 (promotion_prospective_vv)': 'promotion_prospective_vv',
            
            # 电商数据
            '电商功能开通 (e_commerce_enable)': 'e_commerce_enable',
            '电商等级 (author_ecom_level)': 'author_ecom_level',
            '30天GMV范围 (ecom_gmv_30d_range)': 'ecom_gmv_30d_range',
            '30天平均订单价值 (ecom_avg_order_value_30d_range)': 'ecom_avg_order_value_30d_range',
            '30天毛利率范围 (ecom_gpm_30d_range)': 'ecom_gpm_30d_range',
            '30天带货视频数 (ecom_video_product_num_30d)': 'ecom_video_product_num_30d',
            '30天星图带货视频数 (star_ecom_video_num_30d)': 'star_ecom_video_num_30d',
            
            # 性能指标
            '链接转化指数 (link_convert_index)': 'link_convert_index',
            '行业链接转化指数 (link_convert_index_by_industry)': 'link_convert_index_by_industry',
            '购物指数 (link_shopping_index)': 'link_shopping_index',
            '传播指数 (link_spread_index)': 'link_spread_index',
            '行业传播指数 (link_spread_index_by_industry)': 'link_spread_index_by_industry',
            '链接星图指数 (link_star_index)': 'link_star_index',
            '行业链接星图指数 (link_star_index_by_industry)': 'link_star_index_by_industry',
            '行业推荐指数 (link_recommend_index_by_industry)': 'link_recommend_index_by_industry',
            '搜索后观看指数 (search_after_view_index_by_industry)': 'search_after_view_index_by_industry',
            
            # 认证与等级
            '优质达人 (is_excellenct_author)': 'is_excellenct_author',
            '星图优质达人 (star_excellent_author)': 'star_excellent_author',
            '头像框等级 (author_avatar_frame_icon)': 'author_avatar_frame_icon',
            '黑马达人 (is_black_horse_author)': 'is_black_horse_author',
            '共创达人 (is_cocreate_author)': 'is_cocreate_author',
            'CPM项目达人 (is_cpm_project_author)': 'is_cpm_project_author',
            '短剧达人 (is_short_drama)': 'is_short_drama',
            '星图私信达人 (star_whispers_author)': 'star_whispers_author',
            '本地低门槛达人 (local_lower_threshold_author)': 'local_lower_threshold_author',
            
            # 其他数据
            '爆文率 (burst_text_rate)': 'burst_text_rate',
            '品牌提升播放量 (brand_boost_vv)': 'brand_boost_vv',
            '视频品牌提升 (video_brand_boost)': 'video_brand_boost',
            '视频品牌提升播放量 (video_brand_boost_vv)': 'video_brand_boost_vv',
            '预期CPA3等级 (expected_cpa3_level)': 'expected_cpa3_level',
            '游戏类型 (game_type)': 'game_type',
            
            # 组件数据
            '90天组件安装完成数 (star_component_install_finish_cnt_90d)': 'star_component_install_finish_cnt_90d',
            '90天组件链接点击数 (star_component_link_click_cnt_90d)': 'star_component_link_click_cnt_90d',
            '90天视频安装>=1次数 (star_video_install_ge_1_cnt_90d)': 'star_video_install_ge_1_cnt_90d',
            
            # 系统字段
            '页码': 'page_num',
            '爬取日期': 'crawled_at',
            '来源URL (source_url)': 'source_url'
        }
        
        # 数值字段定义
        integer_fields = [
            'follower', 'fans_increment_within_15d', 'fans_increment_within_30d', 'interaction_median_30d',
            'vv_median_30d', 'star_item_count_within_30d', 'star_video_cnt_90d', 'star_video_median_vv_90d',
            'expected_play_num', 'expected_natural_play_num', 'promotion_prospective_vv',
            'ecom_video_product_num_30d', 'star_ecom_video_num_30d', 'star_component_install_finish_cnt_90d',
            'star_component_link_click_cnt_90d', 'star_video_install_ge_1_cnt_90d', 'brand_boost_vv',
            'video_brand_boost_vv', 'page_num', 'gender', 'author_type', 'author_status', 'grade',
            'e_commerce_enable', 'is_excellenct_author', 'star_excellent_author', 'is_black_horse_author',
            'is_cocreate_author', 'is_cpm_project_author', 'is_short_drama', 'star_whispers_author',
            'local_lower_threshold_author', 'video_brand_boost', 'expected_cpa3_level'
        ]
        
        decimal_fields = [
            'fans_increment_rate_within_15d', 'interact_rate_within_30d', 'play_over_rate_within_30d',
            'star_video_interact_rate_90d', 'star_video_finish_vv_rate_90d', 'price_1_20', 'price_20_60',
            'price_60', 'star_index', 'prospective_1_20_cpm', 'prospective_20_60_cpm', 'prospective_60_cpm',
            'promotion_prospective_1_20_cpm', 'promotion_prospective_20_60_cpm', 'promotion_prospective_60_cpm',
            'link_convert_index', 'link_convert_index_by_industry', 'link_shopping_index', 'link_spread_index',
            'link_spread_index_by_industry', 'link_star_index', 'link_star_index_by_industry',
            'link_recommend_index_by_industry', 'search_after_view_index_by_industry', 'burst_text_rate'
        ]
        
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
                # 整数字段类型转换
                if db_field in integer_fields:
                    try:
                        processed[db_field] = int(float(str(value))) if value else 0
                    except (ValueError, TypeError):
                        processed[db_field] = 0
                # 小数字段类型转换
                elif db_field in decimal_fields:
                    try:
                        processed[db_field] = float(str(value)) if value else 0.0
                    except (ValueError, TypeError):
                        processed[db_field] = 0.0
                else:
                    processed[db_field] = str(value) if value else None
            else:
                # 设置默认值
                if db_field in integer_fields:
                    processed[db_field] = 0
                elif db_field in decimal_fields:
                    processed[db_field] = 0.0
                else:
                    processed[db_field] = None
                    
        # 处理JSON字段 - 直接处理已经是JSON格式的字段
        def safe_json_field(field_value):
            """安全处理JSON字段，确保返回有效的JSON字符串"""
            if pd.isna(field_value) or field_value is None or str(field_value).lower() == 'nan':
                return '[]'  # 返回空数组而不是空对象
            
            field_str = str(field_value).strip()
            if not field_str:
                return '[]'
                
            # 如果已经是有效的JSON字符串，直接返回
            try:
                # 验证JSON格式并重新序列化以确保格式正确
                parsed_data = json.loads(field_str)
                return json.dumps(parsed_data, ensure_ascii=False, separators=(',', ':'))
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效JSON，尝试解析为列表格式
                try:
                    parsed = self.parse_json_field(field_value)
                    return json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
                except Exception as e:
                    self.logger.warning(f"JSON字段解析失败: {field_value[:100]}..., 错误: {e}")
                    return '[]'
        
        # 处理各种JSON字段
        processed['content_theme_labels_180d'] = safe_json_field(record.get('内容主题标签 (content_theme_labels_180d)', ''))
        processed['tags_relation'] = safe_json_field(record.get('达人标签关系 (tags_relation)', ''))
        processed['last_10_items'] = safe_json_field(record.get('最近10个视频数据 (last_10_items)', ''))
        processed['items'] = safe_json_field(record.get('热门视频列表 (items)', ''))
        processed['task_infos'] = safe_json_field(record.get('任务信息 (task_infos)', ''))
        
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
                # 先尝试插入，如果存在则更新
                insert_sql = """
                    INSERT INTO daoren_author 
                    (star_id, nick_name, core_user_id, avatar_uri, gender, city, province, author_type, 
                     author_status, grade, follower, fans_increment_within_15d, fans_increment_within_30d,
                     fans_increment_rate_within_15d, interact_rate_within_30d, interaction_median_30d,
                     play_over_rate_within_30d, vv_median_30d, star_item_count_within_30d, star_video_cnt_90d,
                     star_video_interact_rate_90d, star_video_finish_vv_rate_90d, star_video_median_vv_90d,
                     price_1_20, price_20_60, price_60, assign_task_price_list, expected_play_num,
                     expected_natural_play_num, star_index, prospective_1_20_cpm, prospective_20_60_cpm,
                     prospective_60_cpm, promotion_prospective_1_20_cpm, promotion_prospective_20_60_cpm,
                     promotion_prospective_60_cpm, promotion_prospective_vv, e_commerce_enable, author_ecom_level,
                     ecom_gmv_30d_range, ecom_avg_order_value_30d_range, ecom_gpm_30d_range,
                     ecom_video_product_num_30d, star_ecom_video_num_30d, link_convert_index,
                     link_convert_index_by_industry, link_shopping_index, link_spread_index,
                     link_spread_index_by_industry, link_star_index, link_star_index_by_industry,
                     link_recommend_index_by_industry, search_after_view_index_by_industry,
                     is_excellenct_author, star_excellent_author, author_avatar_frame_icon,
                     is_black_horse_author, is_cocreate_author, is_cpm_project_author, is_short_drama,
                     star_whispers_author, local_lower_threshold_author, burst_text_rate, brand_boost_vv,
                     video_brand_boost, video_brand_boost_vv, expected_cpa3_level, game_type,
                     star_component_install_finish_cnt_90d, star_component_link_click_cnt_90d,
                     star_video_install_ge_1_cnt_90d, content_theme_labels_180d, tags_relation,
                     last_10_items, items, task_infos, crawled_at, page_num, source_url)
                    VALUES 
                    (%(star_id)s, %(nick_name)s, %(core_user_id)s, %(avatar_uri)s, %(gender)s, %(city)s,
                     %(province)s, %(author_type)s, %(author_status)s, %(grade)s, %(follower)s,
                     %(fans_increment_within_15d)s, %(fans_increment_within_30d)s, %(fans_increment_rate_within_15d)s,
                     %(interact_rate_within_30d)s, %(interaction_median_30d)s, %(play_over_rate_within_30d)s,
                     %(vv_median_30d)s, %(star_item_count_within_30d)s, %(star_video_cnt_90d)s,
                     %(star_video_interact_rate_90d)s, %(star_video_finish_vv_rate_90d)s, %(star_video_median_vv_90d)s,
                     %(price_1_20)s, %(price_20_60)s, %(price_60)s, %(assign_task_price_list)s,
                     %(expected_play_num)s, %(expected_natural_play_num)s, %(star_index)s,
                     %(prospective_1_20_cpm)s, %(prospective_20_60_cpm)s, %(prospective_60_cpm)s,
                     %(promotion_prospective_1_20_cpm)s, %(promotion_prospective_20_60_cpm)s,
                     %(promotion_prospective_60_cpm)s, %(promotion_prospective_vv)s, %(e_commerce_enable)s,
                     %(author_ecom_level)s, %(ecom_gmv_30d_range)s, %(ecom_avg_order_value_30d_range)s,
                     %(ecom_gpm_30d_range)s, %(ecom_video_product_num_30d)s, %(star_ecom_video_num_30d)s,
                     %(link_convert_index)s, %(link_convert_index_by_industry)s, %(link_shopping_index)s,
                     %(link_spread_index)s, %(link_spread_index_by_industry)s, %(link_star_index)s,
                     %(link_star_index_by_industry)s, %(link_recommend_index_by_industry)s,
                     %(search_after_view_index_by_industry)s, %(is_excellenct_author)s, %(star_excellent_author)s,
                     %(author_avatar_frame_icon)s, %(is_black_horse_author)s, %(is_cocreate_author)s,
                     %(is_cpm_project_author)s, %(is_short_drama)s, %(star_whispers_author)s,
                     %(local_lower_threshold_author)s, %(burst_text_rate)s, %(brand_boost_vv)s,
                     %(video_brand_boost)s, %(video_brand_boost_vv)s, %(expected_cpa3_level)s, %(game_type)s,
                     %(star_component_install_finish_cnt_90d)s, %(star_component_link_click_cnt_90d)s,
                     %(star_video_install_ge_1_cnt_90d)s, %(content_theme_labels_180d)s, %(tags_relation)s,
                     %(last_10_items)s, %(items)s, %(task_infos)s, %(crawled_at)s, %(page_num)s, %(source_url)s)
                """
                
                try:
                    cursor.execute(insert_sql, record)
                    self.stats['success_records'] += 1
                    return True
                except pymysql.IntegrityError as ie:
                    # 如果是重复键错误，则执行更新操作
                    if ie.args[0] == 1062:  # Duplicate entry error
                        update_sql = """
                            UPDATE daoren_author SET
                                nick_name = %(nick_name)s,
                                core_user_id = %(core_user_id)s,
                                avatar_uri = %(avatar_uri)s,
                                gender = %(gender)s,
                                city = %(city)s,
                                province = %(province)s,
                                author_type = %(author_type)s,
                                author_status = %(author_status)s,
                                grade = %(grade)s,
                                follower = %(follower)s,
                                fans_increment_within_15d = %(fans_increment_within_15d)s,
                                fans_increment_within_30d = %(fans_increment_within_30d)s,
                                fans_increment_rate_within_15d = %(fans_increment_rate_within_15d)s,
                                interact_rate_within_30d = %(interact_rate_within_30d)s,
                                interaction_median_30d = %(interaction_median_30d)s,
                                play_over_rate_within_30d = %(play_over_rate_within_30d)s,
                                vv_median_30d = %(vv_median_30d)s,
                                star_item_count_within_30d = %(star_item_count_within_30d)s,
                                star_video_cnt_90d = %(star_video_cnt_90d)s,
                                star_video_interact_rate_90d = %(star_video_interact_rate_90d)s,
                                star_video_finish_vv_rate_90d = %(star_video_finish_vv_rate_90d)s,
                                star_video_median_vv_90d = %(star_video_median_vv_90d)s,
                                price_1_20 = %(price_1_20)s,
                                price_20_60 = %(price_20_60)s,
                                price_60 = %(price_60)s,
                                assign_task_price_list = %(assign_task_price_list)s,
                                expected_play_num = %(expected_play_num)s,
                                expected_natural_play_num = %(expected_natural_play_num)s,
                                star_index = %(star_index)s,
                                prospective_1_20_cpm = %(prospective_1_20_cpm)s,
                                prospective_20_60_cpm = %(prospective_20_60_cpm)s,
                                prospective_60_cpm = %(prospective_60_cpm)s,
                                promotion_prospective_1_20_cpm = %(promotion_prospective_1_20_cpm)s,
                                promotion_prospective_20_60_cpm = %(promotion_prospective_20_60_cpm)s,
                                promotion_prospective_60_cpm = %(promotion_prospective_60_cpm)s,
                                promotion_prospective_vv = %(promotion_prospective_vv)s,
                                e_commerce_enable = %(e_commerce_enable)s,
                                author_ecom_level = %(author_ecom_level)s,
                                ecom_gmv_30d_range = %(ecom_gmv_30d_range)s,
                                ecom_avg_order_value_30d_range = %(ecom_avg_order_value_30d_range)s,
                                ecom_gpm_30d_range = %(ecom_gpm_30d_range)s,
                                ecom_video_product_num_30d = %(ecom_video_product_num_30d)s,
                                star_ecom_video_num_30d = %(star_ecom_video_num_30d)s,
                                link_convert_index = %(link_convert_index)s,
                                link_convert_index_by_industry = %(link_convert_index_by_industry)s,
                                link_shopping_index = %(link_shopping_index)s,
                                link_spread_index = %(link_spread_index)s,
                                link_spread_index_by_industry = %(link_spread_index_by_industry)s,
                                link_star_index = %(link_star_index)s,
                                link_star_index_by_industry = %(link_star_index_by_industry)s,
                                link_recommend_index_by_industry = %(link_recommend_index_by_industry)s,
                                search_after_view_index_by_industry = %(search_after_view_index_by_industry)s,
                                is_excellenct_author = %(is_excellenct_author)s,
                                star_excellent_author = %(star_excellent_author)s,
                                author_avatar_frame_icon = %(author_avatar_frame_icon)s,
                                is_black_horse_author = %(is_black_horse_author)s,
                                is_cocreate_author = %(is_cocreate_author)s,
                                is_cpm_project_author = %(is_cpm_project_author)s,
                                is_short_drama = %(is_short_drama)s,
                                star_whispers_author = %(star_whispers_author)s,
                                local_lower_threshold_author = %(local_lower_threshold_author)s,
                                burst_text_rate = %(burst_text_rate)s,
                                brand_boost_vv = %(brand_boost_vv)s,
                                video_brand_boost = %(video_brand_boost)s,
                                video_brand_boost_vv = %(video_brand_boost_vv)s,
                                expected_cpa3_level = %(expected_cpa3_level)s,
                                game_type = %(game_type)s,
                                star_component_install_finish_cnt_90d = %(star_component_install_finish_cnt_90d)s,
                                star_component_link_click_cnt_90d = %(star_component_link_click_cnt_90d)s,
                                star_video_install_ge_1_cnt_90d = %(star_video_install_ge_1_cnt_90d)s,
                                content_theme_labels_180d = %(content_theme_labels_180d)s,
                                tags_relation = %(tags_relation)s,
                                last_10_items = %(last_10_items)s,
                                items = %(items)s,
                                task_infos = %(task_infos)s,
                                crawled_at = %(crawled_at)s,
                                page_num = %(page_num)s,
                                source_url = %(source_url)s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE star_id = %(star_id)s
                        """
                        cursor.execute(update_sql, record)
                        self.stats['updated_records'] += 1
                        return True
                    else:
                        raise ie
                
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
        importer.create_export_log('csv', args.domain_filter)
        
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