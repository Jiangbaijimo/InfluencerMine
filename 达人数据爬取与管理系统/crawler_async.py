# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 多线程异步爬虫脚本
支持并发爬取、线程池管理、异步数据处理
创建时间: 2025-01-23
"""

import os
import json
import time
import csv
import argparse
import logging
import random
import threading
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
import requests
from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor
from monitor import get_monitor, start_monitoring, stop_monitoring, record_request

# 加载环境变量
load_dotenv()

class AsyncDarenCrawler:
    def __init__(self, max_workers: int = 5):
        self.base_url = "https://agent.oceanengine.com/star/mirror/gw/api/gsearch/search_for_author_square"
        self.max_workers = max_workers
        self.setup_logging()
        self.setup_directories()
        self.db_config = self.get_db_config()
        self.current_accounts = []
        self.task_id = None
        
        # 线程安全锁
        self.db_lock = threading.Lock()
        self.file_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        # 统计信息
        self.total_authors = 0
        self.success_authors = 0
        self.failed_authors = 0
        
        # 性能监控
        self.monitor = get_monitor()
        
        # 错误处理配置
        self.max_consecutive_errors = int(os.getenv('MAX_CONSECUTIVE_ERRORS', 5))
        self.error_cooldown = int(os.getenv('ERROR_COOLDOWN_SECONDS', 60))
        self.consecutive_errors = 0
        self.last_error_time = None
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"async_crawler_{date.today().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s'),
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
        """获取数据库连接（线程安全）"""
        try:
            return pymysql.connect(**self.db_config, cursorclass=DictCursor)
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            return None
            
    def load_all_accounts(self, account_id: int = None):
        """加载所有可用账号或指定账号"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                if account_id:
                    # 加载指定账号
                    cursor.execute("""
                        SELECT * FROM daoren_account 
                        WHERE id = %s AND status = 'active' 
                        AND (cooldown_until IS NULL OR cooldown_until < NOW())
                    """, (account_id,))
                    self.logger.info(f"尝试加载指定账号 ID: {account_id}")
                else:
                    # 加载所有可用账号
                    cursor.execute("""
                        SELECT * FROM daoren_account 
                        WHERE status = 'active' 
                        AND (cooldown_until IS NULL OR cooldown_until < NOW())
                        ORDER BY last_used_at ASC, success_count ASC
                    """)
                
                accounts = cursor.fetchall()
                self.current_accounts = accounts
                
                if account_id and not accounts:
                    self.logger.error(f"指定的账号 ID {account_id} 不存在或不可用")
                    return []
                    
                self.logger.info(f"加载了 {len(accounts)} 个可用账号")
                return accounts
                
        except Exception as e:
            self.logger.error(f"加载账号配置失败: {e}")
            return []
        finally:
            conn.close()
            
    def get_account_for_thread(self, thread_id: int):
        """为线程分配账号"""
        if not self.current_accounts:
            return None
        # 轮询分配账号
        account_index = thread_id % len(self.current_accounts)
        return self.current_accounts[account_index]
        
    def get_headers(self, account: Dict[str, Any]):
        """获取请求头"""
        if account and account.get('headers'):
            try:
                custom_headers = json.loads(account['headers'])
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
            'cookie': account.get('cookies', '') if account else ''
        }
        
    def create_task(self, task_name: str, start_page: int, end_page: int, domain_filter: str = None):
        """创建爬取任务"""
        with self.db_lock:
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
                
    def update_task_progress(self, current_page: int):
        """更新任务进度（线程安全）"""
        if not self.task_id:
            return
            
        with self.db_lock:
            conn = self.get_db_connection()
            if not conn:
                return
                
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE daoren_task_log 
                        SET current_page = %s, total_authors = %s, success_authors = %s, failed_authors = %s
                        WHERE id = %s
                    """, (current_page, self.total_authors, self.success_authors, self.failed_authors, self.task_id))
                    
                    conn.commit()
                    
            except Exception as e:
                self.logger.error(f"更新任务进度失败: {e}")
            finally:
                conn.close()
                
    def complete_task(self, status: str = 'completed', error_message: str = None):
        """完成任务"""
        if not self.task_id:
            return
            
        with self.db_lock:
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
                
    def fetch_page_data(self, page_num: int, thread_id: int) -> Dict[str, Any]:
        """获取单页数据（线程安全）"""
        account = self.get_account_for_thread(thread_id)
        if not account:
            self.logger.error(f"线程 {thread_id} 无可用账号")
            record_request(False, 0, 'no_account')
            return {}
            
        headers = self.get_headers(account)
        
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
                        "field_name": "price_by_video_type__ge",
                        "rel_id": "2"
                    },
                    "field_value": "0"
                }
            ]
        }
        
        start_time = time.time()
        
        try:
            self.logger.info(f"[线程{thread_id}] 正在请求第 {page_num} 页数据...")
            
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload, 
                timeout=int(os.getenv('API_TIMEOUT', 30))
            )
            response.raise_for_status()
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 记录成功请求
            record_request(True, response_time)
            
            # 更新账号成功计数
            self.update_account_stats(account['id'], success=True)
            
            # 重置连续错误计数
            self.consecutive_errors = 0
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            error_type = self._classify_error(e)
            
            self.logger.error(f"[线程{thread_id}] 请求第 {page_num} 页失败: {e}")
            
            # 记录失败请求
            record_request(False, response_time, error_type)
            
            # 更新账号失败计数
            self.update_account_stats(account['id'], success=False)
            
            # 处理连续错误
            self._handle_consecutive_error()
            
            return {}
            
    def _classify_error(self, error: Exception) -> str:
        """分类错误类型"""
        error_str = str(error).lower()
        if 'timeout' in error_str:
            return 'timeout'
        elif 'connection' in error_str:
            return 'connection_error'
        elif '401' in error_str or '403' in error_str:
            return 'auth_error'
        elif '429' in error_str:
            return 'rate_limit'
        elif '500' in error_str or '502' in error_str or '503' in error_str:
            return 'server_error'
        else:
            return 'unknown_error'
            
    def _handle_consecutive_error(self):
        """处理连续错误"""
        self.consecutive_errors += 1
        self.last_error_time = time.time()
        
        if self.consecutive_errors >= self.max_consecutive_errors:
            self.logger.warning(f"连续 {self.consecutive_errors} 次错误，暂停 {self.error_cooldown} 秒")
            time.sleep(self.error_cooldown)
            self.consecutive_errors = 0
            
    def update_account_stats(self, account_id: int, success: bool):
        """更新账号统计信息（线程安全）"""
        with self.db_lock:
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
        """解析单个达人的数据 - 完整版本，包含所有有价值字段"""
        
        # 添加调试输出
        print(f"\n=== 调试信息 - 第{page_num}页达人数据 ===")
        print(f"原始author数据结构: {json.dumps(author, ensure_ascii=False, indent=2)[:1000]}...")
        
        attr_data = author.get('attribute_datas', {})
        print(f"attribute_datas存在: {bool(attr_data)}")
        if attr_data:
            print(f"nick_name字段: {attr_data.get('nick_name', '不存在')}")
            print(f"follower字段: {attr_data.get('follower', '不存在')}")
            print(f"tags_relation字段: {attr_data.get('tags_relation', '不存在')}")
        print("=" * 50)
        
        # 安全获取task_info，避免list index out of range错误
        task_infos = author.get('task_infos', [])
        task_info = task_infos[0] if task_infos else {}
        
        # 安全获取price_info，避免list index out of range错误
        price_infos = task_info.get('price_infos', [])
        
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
            # 转换为字符串并去除空白，如果结果为空则返回默认值
            str_value = str(value).strip()
            if not str_value or str_value == '0':
                return default if default else '未知'
            return str_value
            
        def safe_get_json_string(data, key, default=''):
            """安全获取JSON字符串并格式化"""
            value = data.get(key, default)
            if value is None or str(value).lower() == 'nan':
                return default
            try:
                if isinstance(value, str):
                    # 尝试解析JSON并重新格式化
                    parsed = json.loads(value)
                    return json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
                elif isinstance(value, (list, dict)):
                    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
                else:
                    return str(value)
            except:
                return str(value) if value else default
        
        # 提取达人类型
        tags_relation_str = attr_data.get('tags_relation', '{}')
        达人类型列表 = []
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
        
        # 获取所有价格信息
        price_1_20 = safe_get_number(attr_data, 'price_1_20', 0)
        price_20_60 = safe_get_number(attr_data, 'price_20_60', 0)
        price_60 = safe_get_number(attr_data, 'price_60', 0)
        
        # 从price_infos中获取更多价格信息
        all_prices = []
        video_types = []
        for price_info in price_infos:
            price = safe_get_number(price_info, 'price', 0)
            video_type = safe_get_number(price_info, 'video_type', 0)
            if price > 0:
                all_prices.append(price)
                video_types.append(video_type)
        
        # 计算价格统计
        min_price = min(all_prices) if all_prices else 0
        max_price = max(all_prices) if all_prices else 0
        avg_price = sum(all_prices) / len(all_prices) if all_prices else 0
        
        # 构建完整的数据字典
        parsed_data = {
            # === 基础身份信息 ===
            "达人ID (star_id)": safe_get_string(author, 'star_id'),
            "昵称 (nick_name)": safe_get_string(attr_data, 'nick_name'),
            "核心用户ID (core_user_id)": safe_get_string(attr_data, 'core_user_id'),
            "头像链接 (avatar_uri)": safe_get_string(attr_data, 'avatar_uri'),
            "性别 (gender)": safe_get_number(attr_data, 'gender'),
            "所在地 (city)": safe_get_string(attr_data, 'city'),
            "省份 (province)": safe_get_string(attr_data, 'province'),
            "达人类型 (author_type)": safe_get_number(attr_data, 'author_type'),
            "账号状态 (author_status)": safe_get_number(attr_data, 'author_status'),
            "达人等级 (grade)": safe_get_number(attr_data, 'grade'),
            
            # === 粉丝与影响力数据 ===
            "粉丝数 (follower)": safe_get_number(attr_data, 'follower'),
            "15天粉丝增长数 (fans_increment_within_15d)": safe_get_number(attr_data, 'fans_increment_within_15d'),
            "30天粉丝增长数 (fans_increment_within_30d)": safe_get_number(attr_data, 'fans_increment_within_30d'),
            "15天粉丝增长率 (fans_increment_rate_within_15d)": safe_get_number(attr_data, 'fans_increment_rate_within_15d'),
            "近30天互动率 (interact_rate_within_30d)": safe_get_number(attr_data, 'interact_rate_within_30d'),
            "30天互动中位数 (interaction_median_30d)": safe_get_number(attr_data, 'interaction_median_30d'),
            "30天播放完成率 (play_over_rate_within_30d)": safe_get_number(attr_data, 'play_over_rate_within_30d'),
            "近30天平均播放量 (vv_median_30d)": safe_get_number(attr_data, 'vv_median_30d'),
            
            # === 内容创作数据 ===
            "30天星图视频数量 (star_item_count_within_30d)": safe_get_number(attr_data, 'star_item_count_within_30d'),
            "90天星图视频总数 (star_video_cnt_90d)": safe_get_number(attr_data, 'star_video_cnt_90d'),
            "90天星图视频互动率 (star_video_interact_rate_90d)": safe_get_number(attr_data, 'star_video_interact_rate_90d'),
            "90天星图视频完播率 (star_video_finish_vv_rate_90d)": safe_get_number(attr_data, 'star_video_finish_vv_rate_90d'),
            "90天星图视频播放中位数 (star_video_median_vv_90d)": safe_get_number(attr_data, 'star_video_median_vv_90d'),
            "内容主题标签 (content_theme_labels_180d)": safe_get_json_string(attr_data, 'content_theme_labels_180d'),
            "达人标签关系 (tags_relation)": safe_get_json_string(attr_data, 'tags_relation'),
            "达人类型 (tags)": 达人类型列表,
            
            # === 商业价值数据 ===
            "1-20秒视频报价 (price_1_20)": price_1_20,
            "20-60秒视频报价 (price_20_60)": price_20_60,
            "60秒以上视频报价 (price_60)": price_60,
            "指派任务价格区间 (assign_task_price_list)": safe_get_string(attr_data, 'assign_task_price_list'),
            "预期播放量 (expected_play_num)": safe_get_number(attr_data, 'expected_play_num'),
            "预期自然播放量 (expected_natural_play_num)": safe_get_number(attr_data, 'expected_natural_play_num'),
            "星图指数 (star_index)": safe_get_number(attr_data, 'star_index'),
            
            # === CPM成本数据 ===
            "1-20秒预期CPM (prospective_1_20_cpm)": safe_get_number(attr_data, 'prospective_1_20_cpm'),
            "20-60秒预期CPM (prospective_20_60_cpm)": safe_get_number(attr_data, 'prospective_20_60_cpm'),
            "60秒以上预期CPM (prospective_60_cpm)": safe_get_number(attr_data, 'prospective_60_cpm'),
            "推广1-20秒预期CPM (promotion_prospective_1_20_cpm)": safe_get_number(attr_data, 'promotion_prospective_1_20_cpm'),
            "推广20-60秒预期CPM (promotion_prospective_20_60_cpm)": safe_get_number(attr_data, 'promotion_prospective_20_60_cpm'),
            "推广60秒以上预期CPM (promotion_prospective_60_cpm)": safe_get_number(attr_data, 'promotion_prospective_60_cpm'),
            "推广预期播放量 (promotion_prospective_vv)": safe_get_number(attr_data, 'promotion_prospective_vv'),
            
            # === 电商数据 ===
            "电商功能开通 (e_commerce_enable)": safe_get_number(attr_data, 'e_commerce_enable'),
            "电商等级 (author_ecom_level)": safe_get_string(attr_data, 'author_ecom_level'),
            "30天GMV范围 (ecom_gmv_30d_range)": safe_get_string(attr_data, 'ecom_gmv_30d_range'),
            "30天平均订单价值 (ecom_avg_order_value_30d_range)": safe_get_string(attr_data, 'ecom_avg_order_value_30d_range'),
            "30天毛利率范围 (ecom_gpm_30d_range)": safe_get_string(attr_data, 'ecom_gpm_30d_range'),
            "30天带货视频数 (ecom_video_product_num_30d)": safe_get_number(attr_data, 'ecom_video_product_num_30d'),
            "30天星图带货视频数 (star_ecom_video_num_30d)": safe_get_number(attr_data, 'star_ecom_video_num_30d'),
            
            # === 性能指标 ===
            "链接转化指数 (link_convert_index)": safe_get_number(attr_data, 'link_convert_index'),
            "行业链接转化指数 (link_convert_index_by_industry)": safe_get_number(attr_data, 'link_convert_index_by_industry'),
            "购物指数 (link_shopping_index)": safe_get_number(attr_data, 'link_shopping_index'),
            "传播指数 (link_spread_index)": safe_get_number(attr_data, 'link_spread_index'),
            "行业传播指数 (link_spread_index_by_industry)": safe_get_number(attr_data, 'link_spread_index_by_industry'),
            "链接星图指数 (link_star_index)": safe_get_number(attr_data, 'link_star_index'),
            "行业链接星图指数 (link_star_index_by_industry)": safe_get_number(attr_data, 'link_star_index_by_industry'),
            "行业推荐指数 (link_recommend_index_by_industry)": safe_get_number(attr_data, 'link_recommend_index_by_industry'),
            "搜索后观看指数 (search_after_view_index_by_industry)": safe_get_number(attr_data, 'search_after_view_index_by_industry'),
            
            # === 认证与等级 ===
            "优质达人 (is_excellenct_author)": safe_get_number(attr_data, 'is_excellenct_author'),
            "星图优质达人 (star_excellent_author)": safe_get_number(attr_data, 'star_excellent_author'),
            "头像框等级 (author_avatar_frame_icon)": safe_get_string(attr_data, 'author_avatar_frame_icon'),
            "黑马达人 (is_black_horse_author)": safe_get_number(attr_data, 'is_black_horse_author'),
            "共创达人 (is_cocreate_author)": safe_get_number(attr_data, 'is_cocreate_author'),
            "CPM项目达人 (is_cpm_project_author)": safe_get_number(attr_data, 'is_cpm_project_author'),
            "短剧达人 (is_short_drama)": safe_get_number(attr_data, 'is_short_drama'),
            "星图私信达人 (star_whispers_author)": safe_get_number(attr_data, 'star_whispers_author'),
            "本地低门槛达人 (local_lower_threshold_author)": safe_get_number(attr_data, 'local_lower_threshold_author'),
            
            # === 其他数据 ===
            "爆文率 (burst_text_rate)": safe_get_number(attr_data, 'burst_text_rate'),
            "品牌提升播放量 (brand_boost_vv)": safe_get_number(attr_data, 'brand_boost_vv'),
            "视频品牌提升 (video_brand_boost)": safe_get_number(attr_data, 'video_brand_boost'),
            "视频品牌提升播放量 (video_brand_boost_vv)": safe_get_number(attr_data, 'video_brand_boost_vv'),
            "预期CPA3等级 (expected_cpa3_level)": safe_get_number(attr_data, 'expected_cpa3_level'),
            "游戏类型 (game_type)": safe_get_string(attr_data, 'game_type'),
            
            # === 组件数据 ===
            "90天组件安装完成数 (star_component_install_finish_cnt_90d)": safe_get_number(attr_data, 'star_component_install_finish_cnt_90d'),
            "90天组件链接点击数 (star_component_link_click_cnt_90d)": safe_get_number(attr_data, 'star_component_link_click_cnt_90d'),
            "90天视频安装>=1次数 (star_video_install_ge_1_cnt_90d)": safe_get_number(attr_data, 'star_video_install_ge_1_cnt_90d'),
            
            # === 热门视频数据 ===
            "热门视频数量": len(author.get('items', [])),
            "热门视频总播放量": sum([safe_get_number(item, 'vv', 0) for item in author.get('items', [])]),
            "热门视频平均播放量": round(sum([safe_get_number(item, 'vv', 0) for item in author.get('items', [])]) / len(author.get('items', [])), 0) if author.get('items') else 0,
            
            # === 达人类型标签 ===
            "达人类型 (tags)": 达人类型列表,
            
            # === 系统字段 ===
            "页码": page_num,
            "爬取日期": date.today().strftime('%Y-%m-%d'),
            "爬取时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "来源URL (source_url)": "",
            
            # === 原始数据（用于调试和完整性） ===
            "最近10个视频数据 (last_10_items)": safe_get_json_string(attr_data, 'last_10_items'),
            "热门视频列表 (items)": json.dumps(author.get('items', []), ensure_ascii=False, separators=(',', ':')),
            "任务信息 (task_infos)": json.dumps(task_infos, ensure_ascii=False, separators=(',', ':'))
        }
        
        return parsed_data
        
    def ensure_directory(self, path: str):
        """确保目录存在"""
        Path(path).mkdir(parents=True, exist_ok=True)
        
    def save_author_to_type_folder(self, author_data: Dict[str, Any], page_num: int, crawl_date: str):
        """根据达人类型，保存到对应文件夹下的独立CSV（线程安全）"""
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
            
            # 定义完整的字段顺序，确保CSV输出的可读性和一致性
            field_order = [
                # === 基础身份信息 ===
                "达人ID (star_id)",
                "昵称 (nick_name)",
                "核心用户ID (core_user_id)",
                "头像链接 (avatar_uri)",
                "性别 (gender)",
                "所在地 (city)",
                "省份 (province)",
                "达人类型 (author_type)",
                "账号状态 (author_status)",
                "达人等级 (grade)",
                
                # === 粉丝与影响力数据 ===
                "粉丝数 (follower)",
                "15天粉丝增长数 (fans_increment_within_15d)",
                "30天粉丝增长数 (fans_increment_within_30d)",
                "15天粉丝增长率 (fans_increment_rate_within_15d)",
                "近30天互动率 (interact_rate_within_30d)",
                "30天互动中位数 (interaction_median_30d)",
                "30天播放完成率 (play_over_rate_within_30d)",
                "近30天平均播放量 (vv_median_30d)",
                
                # === 内容创作数据 ===
                "30天星图视频数量 (star_item_count_within_30d)",
                "90天星图视频总数 (star_video_cnt_90d)",
                "90天星图视频互动率 (star_video_interact_rate_90d)",
                "90天星图视频完播率 (star_video_finish_vv_rate_90d)",
                "90天星图视频播放中位数 (star_video_median_vv_90d)",
                "内容主题标签 (content_theme_labels_180d)",
                "达人标签关系 (tags_relation)",
                
                # === 商业价值数据 ===
                "1-20秒视频报价 (price_1_20)",
                "20-60秒视频报价 (price_20_60)",
                "60秒以上视频报价 (price_60)",
                "指派任务价格区间 (assign_task_price_list)",
                "预期播放量 (expected_play_num)",
                "预期自然播放量 (expected_natural_play_num)",
                "星图指数 (star_index)",
                
                # === CPM成本数据 ===
                "1-20秒预期CPM (prospective_1_20_cpm)",
                "20-60秒预期CPM (prospective_20_60_cpm)",
                "60秒以上预期CPM (prospective_60_cpm)",
                "推广1-20秒预期CPM (promotion_prospective_1_20_cpm)",
                "推广20-60秒预期CPM (promotion_prospective_20_60_cpm)",
                "推广60秒以上预期CPM (promotion_prospective_60_cpm)",
                "推广预期播放量 (promotion_prospective_vv)",
                
                # === 电商数据 ===
                "电商功能开通 (e_commerce_enable)",
                "电商等级 (author_ecom_level)",
                "30天GMV范围 (ecom_gmv_30d_range)",
                "30天平均订单价值 (ecom_avg_order_value_30d_range)",
                "30天毛利率范围 (ecom_gpm_30d_range)",
                "30天带货视频数 (ecom_video_product_num_30d)",
                "30天星图带货视频数 (star_ecom_video_num_30d)",
                
                # === 性能指标 ===
                "链接转化指数 (link_convert_index)",
                "行业链接转化指数 (link_convert_index_by_industry)",
                "购物指数 (link_shopping_index)",
                "传播指数 (link_spread_index)",
                "行业传播指数 (link_spread_index_by_industry)",
                "链接星图指数 (link_star_index)",
                "行业链接星图指数 (link_star_index_by_industry)",
                "行业推荐指数 (link_recommend_index_by_industry)",
                "搜索后观看指数 (search_after_view_index_by_industry)",
                
                # === 认证与等级 ===
                "优质达人 (is_excellenct_author)",
                "星图优质达人 (star_excellent_author)",
                "头像框等级 (author_avatar_frame_icon)",
                "黑马达人 (is_black_horse_author)",
                "共创达人 (is_cocreate_author)",
                "CPM项目达人 (is_cpm_project_author)",
                "短剧达人 (is_short_drama)",
                "星图私信达人 (star_whispers_author)",
                "本地低门槛达人 (local_lower_threshold_author)",
                
                # === 其他数据 ===
                "爆文率 (burst_text_rate)",
                "品牌提升播放量 (brand_boost_vv)",
                "视频品牌提升 (video_brand_boost)",
                "视频品牌提升播放量 (video_brand_boost_vv)",
                "预期CPA3等级 (expected_cpa3_level)",
                "游戏类型 (game_type)",
                
                # === 组件数据 ===
                "90天组件安装完成数 (star_component_install_finish_cnt_90d)",
                "90天组件链接点击数 (star_component_link_click_cnt_90d)",
                "90天视频安装>=1次数 (star_video_install_ge_1_cnt_90d)",
                
                # === 热门视频数据 ===
                "热门视频数量",
                "热门视频总播放量",
                "热门视频平均播放量",
                
                # === 达人类型标签 ===
                "达人类型 (tags)",
                
                # === 系统字段 ===
                "页码",
                "爬取日期",
                "爬取时间",
                "来源URL (source_url)",
                
                # === 原始数据（用于调试和完整性） ===
                "最近10个视频数据 (last_10_items)",
                "热门视频列表 (items)",
                "任务信息 (task_infos)"
            ]
            
            # 清理数据中的NaN值并按字段顺序组织数据
            clean_data = {}
            
            # 数值字段定义（用于NaN值处理）
            numeric_fields = {
                '粉丝数 (follower)', '15天粉丝增长数 (fans_increment_within_15d)', 
                '30天粉丝增长数 (fans_increment_within_30d)', '30天互动中位数 (interaction_median_30d)',
                '近30天平均播放量 (vv_median_30d)', '30天星图视频数量 (star_item_count_within_30d)',
                '90天星图视频总数 (star_video_cnt_90d)', '90天星图视频播放中位数 (star_video_median_vv_90d)',
                '1-20秒视频报价 (price_1_20)', '20-60秒视频报价 (price_20_60)', 
                '60秒以上视频报价 (price_60)', '预期播放量 (expected_play_num)',
                '预期自然播放量 (expected_natural_play_num)', '推广预期播放量 (promotion_prospective_vv)',
                '30天带货视频数 (ecom_video_product_num_30d)', '30天星图带货视频数 (star_ecom_video_num_30d)',
                '90天组件安装完成数 (star_component_install_finish_cnt_90d)', 
                '90天组件链接点击数 (star_component_link_click_cnt_90d)',
                '90天视频安装>=1次数 (star_video_install_ge_1_cnt_90d)', '品牌提升播放量 (brand_boost_vv)',
                '视频品牌提升播放量 (video_brand_boost_vv)', '页码', '性别 (gender)',
                '达人类型 (author_type)', '账号状态 (author_status)', '达人等级 (grade)',
                '电商功能开通 (e_commerce_enable)', '优质达人 (is_excellenct_author)',
                '星图优质达人 (star_excellent_author)', '黑马达人 (is_black_horse_author)',
                '共创达人 (is_cocreate_author)', 'CPM项目达人 (is_cmp_project_author)',
                '短剧达人 (is_short_drama)', '星图私信达人 (star_whispers_author)',
                '本地低门槛达人 (local_lower_threshold_author)', '视频品牌提升 (video_brand_boost)',
                '预期CPA3等级 (expected_cpa3_level)', '热门视频数量', '热门视频总播放量', '热门视频平均播放量'
            }
            
            decimal_fields = {
                '15天粉丝增长率 (fans_increment_rate_within_15d)', '近30天互动率 (interact_rate_within_30d)',
                '30天播放完成率 (play_over_rate_within_30d)', '90天星图视频互动率 (star_video_interact_rate_90d)',
                '90天星图视频完播率 (star_video_finish_vv_rate_90d)', '星图指数 (star_index)',
                '1-20秒预期CPM (prospective_1_20_cpm)', '20-60秒预期CPM (prospective_20_60_cpm)',
                '60秒以上预期CPM (prospective_60_cpm)', '推广1-20秒预期CPM (promotion_prospective_1_20_cpm)',
                '推广20-60秒预期CPM (promotion_prospective_20_60_cpm)', '推广60秒以上预期CPM (promotion_prospective_60_cpm)',
                '链接转化指数 (link_convert_index)', '行业链接转化指数 (link_convert_index_by_industry)',
                '购物指数 (link_shopping_index)', '传播指数 (link_spread_index)',
                '行业传播指数 (link_spread_index_by_industry)', '链接星图指数 (link_star_index)',
                '行业链接星图指数 (link_star_index_by_industry)', '行业推荐指数 (link_recommend_index_by_industry)',
                '搜索后观看指数 (search_after_view_index_by_industry)', '爆文率 (burst_text_rate)'
            }
            
            # 按字段顺序处理数据
            for field in field_order:
                value = author_data.get(field)
                
                if value is None or str(value).lower() == 'nan':
                    if field in numeric_fields:
                        clean_data[field] = 0
                    elif field in decimal_fields:
                        clean_data[field] = 0.0
                    else:
                        clean_data[field] = ''
                else:
                    clean_data[field] = value
            
            # 线程安全的文件写入
            with self.file_lock:
                try:
                    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.DictWriter(f, fieldnames=field_order)
                        writer.writeheader()
                        writer.writerow(clean_data)
                        
                    self.logger.debug(f"保存达人数据: {filepath}")
                    
                except Exception as e:
                    self.logger.error(f"保存文件失败 {filepath}: {e}")
                    
                    
    def process_page(self, page_num: int, thread_id: int, domain_filter: str = None, crawl_date: str = None) -> tuple:
        """处理单页数据（线程工作函数）"""
        try:
            # 获取数据
            raw_data = self.fetch_page_data(page_num, thread_id)
            
            if not raw_data or raw_data.get('base_resp', {}).get('status_code') != 0:
                self.logger.warning(f"[线程{thread_id}] 第 {page_num} 页请求失败")
                return page_num, 0, 0, 1
                
            # 解析数据
            authors = raw_data.get('authors', [])
            page_success = 0
            page_failed = 0
            
            for author in authors:
                try:
                    parsed = self.parse_author_data(author, page_num)
                    
                    # 如果设置了类型筛选，检查是否匹配
                    if domain_filter:
                        author_tags = parsed.get("达人类型 (tags)", [])
                        filter_tags = [tag.strip() for tag in domain_filter.split(',')]
                        if not any(tag in author_tags for tag in filter_tags):
                            continue
                            
                    self.save_author_to_type_folder(parsed, page_num, crawl_date)
                    page_success += 1
                    
                except Exception as e:
                    self.logger.error(f"[线程{thread_id}] 处理达人数据失败: {e}")
                    page_failed += 1
                    
            # 更新统计信息
            with self.stats_lock:
                self.total_authors += len(authors)
                self.success_authors += page_success
                self.failed_authors += page_failed
                
            self.logger.info(f"[线程{thread_id}] ✅ 第 {page_num} 页处理完成，成功: {page_success}, 总计: {len(authors)}")
            
            # 随机延迟防反爬
            delay = random.uniform(
                float(os.getenv('CRAWL_DELAY_MIN', 0.5)),
                float(os.getenv('CRAWL_DELAY_MAX', 1.5))
            )
            time.sleep(delay)
            
            return page_num, len(authors), page_success, page_failed
            
        except Exception as e:
            self.logger.error(f"[线程{thread_id}] 处理第 {page_num} 页时发生错误: {e}")
            return page_num, 0, 0, 1
            
    def crawl_pages_async(self, start_page: int, end_page: int, task_name: str = None, 
                         domain_filter: str = None, resume_from: int = None, account_id: int = None):
        """异步爬取指定页面范围的数据"""
        
        # 启动性能监控
        start_monitoring()
        
        # 加载账号（所有账号或指定账号）
        accounts = self.load_all_accounts(account_id)
        if not accounts:
            self.logger.error("没有可用账号，无法开始爬取")
            stop_monitoring()
            return
            
        # 创建任务
        if not task_name:
            task_name = f"异步爬取_{start_page}到{end_page}页_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        self.create_task(task_name, start_page, end_page, domain_filter)
        
        crawl_date = date.today().strftime("%Y%m%d")
        
        # 确定起始页码（支持断点续爬）
        actual_start_page = resume_from if resume_from else start_page
        
        self.logger.info(f"开始异步爬取任务: {task_name}")
        self.logger.info(f"页面范围: {actual_start_page} - {end_page}")
        self.logger.info(f"使用 {self.max_workers} 个线程，{len(accounts)} 个账号")
        
        try:
            # 使用线程池执行爬取任务
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有页面任务
                future_to_page = {
                    executor.submit(self.process_page, page, thread_id % self.max_workers, domain_filter, crawl_date): page
                    for thread_id, page in enumerate(range(actual_start_page, end_page + 1))
                }
                
                completed_pages = 0
                empty_pages = 0
                page_results = {}  # 存储页面结果，用于按顺序检查连续空页面
                
                # 处理完成的任务
                for future in as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        page_num, total_count, success_count, failed_count = future.result()
                        completed_pages += 1
                        
                        # 存储页面结果
                        page_results[page_num] = total_count
                        
                        # 统计空页面
                        if total_count == 0:
                            empty_pages += 1
                            
                        # 检查是否有连续的空页面（按页码顺序）
                        consecutive_empty = 0
                        max_page_checked = min(page_results.keys()) if page_results else actual_start_page
                        
                        # 从最小页码开始检查连续空页面
                        for check_page in range(max_page_checked, end_page + 1):
                            if check_page in page_results:
                                if page_results[check_page] == 0:
                                    consecutive_empty += 1
                                else:
                                    consecutive_empty = 0
                                    
                                # 如果连续5页都是空的，且已经爬取了至少10页，可能已经到达数据末尾
                                if consecutive_empty >= 5 and completed_pages >= 10:
                                    self.logger.info(f"连续 {consecutive_empty} 页无数据，可能已到达数据末尾")
                                    # 取消剩余任务
                                    for remaining_future in future_to_page:
                                        if not remaining_future.done():
                                            remaining_future.cancel()
                                    break
                            else:
                                break  # 还有页面未完成，无法判断连续性
                                
                        # 如果触发了提前停止，跳出主循环
                        if consecutive_empty >= 5 and completed_pages >= 10:
                            break
                            
                        # 定期更新进度
                        if completed_pages % 10 == 0:
                            self.update_task_progress(page_num)
                            
                    except Exception as e:
                        self.logger.error(f"处理页面 {page_num} 结果时发生错误: {e}")
                        
            # 完成任务
            self.complete_task('completed')
            self.logger.info(f"🎉 异步爬取任务完成！总计处理 {self.total_authors} 位达人，成功 {self.success_authors}，失败 {self.failed_authors}")
            self.logger.info(f"空页面数量: {empty_pages}")
            
            # 输出性能报告
            self._print_performance_report()
            
        except KeyboardInterrupt:
            self.logger.info("用户中断爬取")
            self.complete_task('paused', '用户中断')
        except Exception as e:
            self.logger.error(f"异步爬取过程中发生错误: {e}")
            self.complete_task('failed', str(e))
        finally:
            # 停止性能监控
            stop_monitoring()
            
    def _print_performance_report(self):
        """打印性能报告"""
        try:
            from monitor import get_performance_report, get_optimization_suggestions
            
            print("\n" + "="*60)
            print("🚀 异步爬虫性能报告")
            print("="*60)
            
            report = get_performance_report()
            if 'error' not in report:
                print(f"\n📊 系统资源使用情况:")
                print(f"  CPU平均使用率: {report['CPU使用率']['平均值']}")
                print(f"  内存平均使用率: {report['内存使用率']['平均值']}")
                print(f"  平均响应时间: {report['响应时间']['平均值']}")
                print(f"  平均成功率: {report['成功率']['平均值']}")
                
                current_stats = report['当前统计']
                print(f"\n📈 爬取统计:")
                print(f"  运行时间: {current_stats['运行时间']}")
                print(f"  总请求数: {current_stats['总请求数']}")
                print(f"  成功率: {current_stats['成功率']}")
                print(f"  平均请求速率: {current_stats['平均请求速率']}")
                
                if current_stats['错误统计']:
                    print(f"\n⚠️ 错误统计:")
                    for error_type, count in current_stats['错误统计'].items():
                        print(f"  {error_type}: {count}次")
                        
            # 优化建议
            suggestions = get_optimization_suggestions()
            if suggestions:
                print(f"\n💡 性能优化建议:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
                    
            print("\n" + "="*60)
            
        except Exception as e:
            self.logger.error(f"生成性能报告失败: {e}")
            
def main():
    parser = argparse.ArgumentParser(description='异步达人数据爬取工具')
    parser.add_argument('--start', type=int, required=True, help='起始页码')
    parser.add_argument('--end', type=int, required=True, help='结束页码')
    parser.add_argument('--workers', type=int, default=5, help='线程数量 (默认: 5)')
    parser.add_argument('--domain-filter', type=str, help='达人类型筛选，多个用逗号分隔')
    parser.add_argument('--task-name', type=str, help='任务名称')
    parser.add_argument('--resume-from', type=int, help='从指定页码恢复爬取')
    parser.add_argument('--account-id', type=int, help='指定使用的账号ID')
    
    args = parser.parse_args()
    
    # 创建异步爬虫实例
    crawler = AsyncDarenCrawler(max_workers=args.workers)
    
    # 开始爬取
    crawler.crawl_pages_async(
        start_page=args.start,
        end_page=args.end,
        task_name=args.task_name,
        domain_filter=args.domain_filter,
        resume_from=args.resume_from,
        account_id=args.account_id
    )

if __name__ == "__main__":
    main()