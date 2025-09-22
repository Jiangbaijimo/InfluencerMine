# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 账号管理脚本
支持多账号管理、账号状态监控、轮换策略、健康检查
创建时间: 2025-01-23
"""

import os
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AccountManager:
    def __init__(self):
        self.setup_logging()
        self.db_config = self.get_db_config()
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"account_manager_{datetime.now().strftime('%Y%m%d')}.log"
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
            
    def add_account(self, account_name: str, cookies: str, headers: str = None, 
                   notes: str = None) -> bool:
        """添加新账号"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # 检查账号是否已存在
                cursor.execute(
                    "SELECT id FROM daoren_account WHERE account_name = %s",
                    (account_name,)
                )
                
                if cursor.fetchone():
                    self.logger.error(f"账号 {account_name} 已存在")
                    return False
                    
                # 插入新账号
                cursor.execute("""
                    INSERT INTO daoren_account 
                    (account_name, cookies, headers, status, notes)
                    VALUES (%s, %s, %s, 'active', %s)
                """, (account_name, cookies, headers, notes))
                
                conn.commit()
                account_id = cursor.lastrowid
                self.logger.info(f"成功添加账号: {account_name} (ID: {account_id})")
                return True
                
        except Exception as e:
            self.logger.error(f"添加账号失败: {e}")
            return False
        finally:
            conn.close()
            
    def update_account(self, account_id: int, **kwargs) -> bool:
        """更新账号信息"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # 构建更新语句
                update_fields = []
                params = []
                
                allowed_fields = ['account_name', 'cookies', 'headers', 'status', 'notes']
                
                for field, value in kwargs.items():
                    if field in allowed_fields:
                        update_fields.append(f"{field} = %s")
                        params.append(value)
                        
                if not update_fields:
                    self.logger.warning("没有有效的更新字段")
                    return False
                    
                params.append(account_id)
                
                cursor.execute(f"""
                    UPDATE daoren_account 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """, params)
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"成功更新账号 ID: {account_id}")
                    return True
                else:
                    self.logger.warning(f"账号 ID {account_id} 不存在")
                    return False
                    
        except Exception as e:
            self.logger.error(f"更新账号失败: {e}")
            return False
        finally:
            conn.close()
            
    def delete_account(self, account_id: int) -> bool:
        """删除账号"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM daoren_account WHERE id = %s",
                    (account_id,)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"成功删除账号 ID: {account_id}")
                    return True
                else:
                    self.logger.warning(f"账号 ID {account_id} 不存在")
                    return False
                    
        except Exception as e:
            self.logger.error(f"删除账号失败: {e}")
            return False
        finally:
            conn.close()
            
    def list_accounts(self, status: str = None) -> List[Dict[str, Any]]:
        """列出所有账号"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                if status:
                    cursor.execute(
                        "SELECT * FROM daoren_account WHERE status = %s ORDER BY id",
                        (status,)
                    )
                else:
                    cursor.execute("SELECT * FROM daoren_account ORDER BY id")
                    
                accounts = cursor.fetchall()
                return accounts
                
        except Exception as e:
            self.logger.error(f"获取账号列表失败: {e}")
            return []
        finally:
            conn.close()
            
    def get_account_stats(self, account_id: int = None) -> Dict[str, Any]:
        """获取账号统计信息"""
        conn = self.get_db_connection()
        if not conn:
            return {}
            
        try:
            with conn.cursor() as cursor:
                if account_id:
                    cursor.execute("""
                        SELECT 
                            id, account_name, status,
                            success_count, failed_count,
                            last_used_at, cooldown_until,
                            CASE 
                                WHEN success_count + failed_count = 0 THEN 0
                                ELSE ROUND(success_count * 100.0 / (success_count + failed_count), 2)
                            END as success_rate
                        FROM daoren_account 
                        WHERE id = %s
                    """, (account_id,))
                    
                    return cursor.fetchone() or {}
                else:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_accounts,
                            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_accounts,
                            SUM(CASE WHEN status = 'inactive' THEN 1 ELSE 0 END) as inactive_accounts,
                            SUM(CASE WHEN status = 'banned' THEN 1 ELSE 0 END) as banned_accounts,
                            SUM(CASE WHEN status = 'cooldown' THEN 1 ELSE 0 END) as cooldown_accounts,
                            SUM(success_count) as total_success,
                            SUM(failed_count) as total_failed,
                            CASE 
                                WHEN SUM(success_count + failed_count) = 0 THEN 0
                                ELSE ROUND(SUM(success_count) * 100.0 / SUM(success_count + failed_count), 2)
                            END as overall_success_rate
                        FROM daoren_account
                    """)
                    
                    return cursor.fetchone() or {}
                    
        except Exception as e:
            self.logger.error(f"获取账号统计失败: {e}")
            return {}
        finally:
            conn.close()
            
    def set_account_cooldown(self, account_id: int, cooldown_minutes: int = None) -> bool:
        """设置账号冷却"""
        if cooldown_minutes is None:
            cooldown_minutes = int(os.getenv('ACCOUNT_COOLDOWN_PERIOD', 300)) // 60
            
        cooldown_until = datetime.now() + timedelta(minutes=cooldown_minutes)
        
        return self.update_account(
            account_id,
            status='cooldown',
            cooldown_until=cooldown_until
        )
        
    def clear_account_cooldown(self, account_id: int) -> bool:
        """清除账号冷却"""
        return self.update_account(
            account_id,
            status='active',
            cooldown_until=None
        )
        
    def health_check_accounts(self) -> Dict[str, int]:
        """健康检查所有账号"""
        conn = self.get_db_connection()
        if not conn:
            return {}
            
        stats = {
            'checked': 0,
            'activated': 0,
            'deactivated': 0,
            'errors': 0
        }
        
        try:
            with conn.cursor() as cursor:
                # 获取所有账号
                cursor.execute("SELECT * FROM daoren_account")
                accounts = cursor.fetchall()
                
                for account in accounts:
                    stats['checked'] += 1
                    
                    try:
                        # 检查冷却时间
                        if (account['status'] == 'cooldown' and 
                            account['cooldown_until'] and 
                            datetime.now() > account['cooldown_until']):
                            
                            cursor.execute("""
                                UPDATE daoren_account 
                                SET status = 'active', cooldown_until = NULL
                                WHERE id = %s
                            """, (account['id'],))
                            
                            stats['activated'] += 1
                            self.logger.info(f"账号 {account['account_name']} 冷却结束，已激活")
                            
                        # 检查失败率
                        total_requests = account['success_count'] + account['failed_count']
                        if total_requests > 0:
                            failure_rate = account['failed_count'] / total_requests
                            max_failure_rate = 0.5  # 50%失败率阈值
                            
                            if (failure_rate > max_failure_rate and 
                                account['status'] == 'active' and
                                total_requests >= 10):  # 至少10次请求
                                
                                cursor.execute("""
                                    UPDATE daoren_account 
                                    SET status = 'inactive', 
                                        notes = CONCAT(IFNULL(notes, ''), 
                                                     '; 自动停用-失败率过高: ', %s, '%%')
                                    WHERE id = %s
                                """, (round(failure_rate * 100, 2), account['id']))
                                
                                stats['deactivated'] += 1
                                self.logger.warning(f"账号 {account['account_name']} 失败率过高({failure_rate:.2%})，已停用")
                                
                    except Exception as e:
                        stats['errors'] += 1
                        self.logger.error(f"检查账号 {account['account_name']} 时出错: {e}")
                        
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            stats['errors'] += 1
        finally:
            conn.close()
            
        return stats
        
    def get_best_account(self, exclude_ids: List[int] = None) -> Optional[Dict[str, Any]]:
        """获取最佳可用账号"""
        conn = self.get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                # 构建排除条件
                exclude_condition = ""
                params = []
                
                if exclude_ids:
                    exclude_condition = f"AND id NOT IN ({','.join(['%s'] * len(exclude_ids))})"
                    params.extend(exclude_ids)
                    
                cursor.execute(f"""
                    SELECT *,
                        CASE 
                            WHEN success_count + failed_count = 0 THEN 1.0
                            ELSE success_count * 1.0 / (success_count + failed_count)
                        END as success_rate,
                        CASE 
                            WHEN last_used_at IS NULL THEN 999999
                            ELSE TIMESTAMPDIFF(MINUTE, last_used_at, NOW())
                        END as minutes_since_last_use
                    FROM daoren_account 
                    WHERE status = 'active' 
                    AND (cooldown_until IS NULL OR cooldown_until < NOW())
                    {exclude_condition}
                    ORDER BY 
                        success_rate DESC,
                        minutes_since_last_use DESC,
                        success_count ASC
                    LIMIT 1
                """, params)
                
                return cursor.fetchone()
                
        except Exception as e:
            self.logger.error(f"获取最佳账号失败: {e}")
            return None
        finally:
            conn.close()
            
    def rotate_accounts(self, current_account_id: int) -> Optional[Dict[str, Any]]:
        """轮换到下一个账号"""
        # 设置当前账号冷却
        cooldown_minutes = int(os.getenv('ACCOUNT_ROTATION_INTERVAL', 1800)) // 60
        self.set_account_cooldown(current_account_id, cooldown_minutes)
        
        # 获取下一个最佳账号
        next_account = self.get_best_account(exclude_ids=[current_account_id])
        
        if next_account:
            self.logger.info(f"账号轮换: {current_account_id} -> {next_account['id']} ({next_account['account_name']})")
        else:
            self.logger.warning("没有可用的账号进行轮换")
            
        return next_account
        
    def import_accounts_from_file(self, filepath: str) -> int:
        """从文件批量导入账号"""
        if not Path(filepath).exists():
            self.logger.error(f"文件不存在: {filepath}")
            return 0
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
                
            if not isinstance(accounts_data, list):
                self.logger.error("文件格式错误，应为账号数组")
                return 0
                
            success_count = 0
            
            for account_data in accounts_data:
                if not isinstance(account_data, dict):
                    continue
                    
                account_name = account_data.get('account_name')
                cookies = account_data.get('cookies')
                headers = account_data.get('headers')
                notes = account_data.get('notes')
                
                if not account_name or not cookies:
                    self.logger.warning(f"跳过无效账号数据: {account_data}")
                    continue
                    
                if isinstance(headers, dict):
                    headers = json.dumps(headers, ensure_ascii=False)
                    
                if self.add_account(account_name, cookies, headers, notes):
                    success_count += 1
                    
            self.logger.info(f"成功导入 {success_count}/{len(accounts_data)} 个账号")
            return success_count
            
        except Exception as e:
            self.logger.error(f"导入账号文件失败: {e}")
            return 0
            
    def export_accounts_to_file(self, filepath: str, include_sensitive: bool = False) -> bool:
        """导出账号到文件"""
        accounts = self.list_accounts()
        
        if not accounts:
            self.logger.warning("没有账号可导出")
            return False
            
        try:
            export_data = []
            
            for account in accounts:
                account_data = {
                    'id': account['id'],
                    'account_name': account['account_name'],
                    'status': account['status'],
                    'success_count': account['success_count'],
                    'failed_count': account['failed_count'],
                    'last_used_at': account['last_used_at'].isoformat() if account['last_used_at'] else None,
                    'notes': account['notes']
                }
                
                if include_sensitive:
                    account_data['cookies'] = account['cookies']
                    account_data['headers'] = account['headers']
                    
                export_data.append(account_data)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"成功导出 {len(export_data)} 个账号到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出账号失败: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='达人数据爬取系统 - 账号管理')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加账号
    add_parser = subparsers.add_parser('add', help='添加新账号')
    add_parser.add_argument('--name', required=True, help='账号名称')
    add_parser.add_argument('--cookies', required=True, help='Cookie字符串')
    add_parser.add_argument('--headers', help='请求头JSON字符串')
    add_parser.add_argument('--notes', help='备注信息')
    
    # 更新账号
    update_parser = subparsers.add_parser('update', help='更新账号')
    update_parser.add_argument('--id', type=int, required=True, help='账号ID')
    update_parser.add_argument('--name', help='账号名称')
    update_parser.add_argument('--cookies', help='Cookie字符串')
    update_parser.add_argument('--headers', help='请求头JSON字符串')
    update_parser.add_argument('--status', choices=['active', 'inactive', 'banned', 'cooldown'], help='账号状态')
    update_parser.add_argument('--notes', help='备注信息')
    
    # 删除账号
    delete_parser = subparsers.add_parser('delete', help='删除账号')
    delete_parser.add_argument('--id', type=int, required=True, help='账号ID')
    
    # 列出账号
    list_parser = subparsers.add_parser('list', help='列出账号')
    list_parser.add_argument('--status', choices=['active', 'inactive', 'banned', 'cooldown'], help='筛选状态')
    
    # 账号统计
    stats_parser = subparsers.add_parser('stats', help='账号统计')
    stats_parser.add_argument('--id', type=int, help='特定账号ID')
    
    # 健康检查
    subparsers.add_parser('health-check', help='健康检查所有账号')
    
    # 导入账号
    import_parser = subparsers.add_parser('import', help='从文件导入账号')
    import_parser.add_argument('--file', required=True, help='JSON文件路径')
    
    # 导出账号
    export_parser = subparsers.add_parser('export', help='导出账号到文件')
    export_parser.add_argument('--file', required=True, help='输出文件路径')
    export_parser.add_argument('--include-sensitive', action='store_true', help='包含敏感信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = AccountManager()
    
    if args.command == 'add':
        manager.add_account(args.name, args.cookies, args.headers, args.notes)
        
    elif args.command == 'update':
        update_data = {}
        if args.name:
            update_data['account_name'] = args.name
        if args.cookies:
            update_data['cookies'] = args.cookies
        if args.headers:
            update_data['headers'] = args.headers
        if args.status:
            update_data['status'] = args.status
        if args.notes:
            update_data['notes'] = args.notes
            
        manager.update_account(args.id, **update_data)
        
    elif args.command == 'delete':
        manager.delete_account(args.id)
        
    elif args.command == 'list':
        accounts = manager.list_accounts(args.status)
        
        if accounts:
            print(f"{'ID':<5} {'名称':<20} {'状态':<10} {'成功':<8} {'失败':<8} {'最后使用':<20}")
            print("-" * 80)
            
            for account in accounts:
                last_used = account['last_used_at'].strftime('%Y-%m-%d %H:%M:%S') if account['last_used_at'] else '从未使用'
                print(f"{account['id']:<5} {account['account_name']:<20} {account['status']:<10} "
                      f"{account['success_count']:<8} {account['failed_count']:<8} {last_used:<20}")
        else:
            print("没有找到账号")
            
    elif args.command == 'stats':
        stats = manager.get_account_stats(args.id)
        
        if args.id:
            if stats:
                print(f"账号统计 - {stats['account_name']} (ID: {stats['id']})")
                print(f"状态: {stats['status']}")
                print(f"成功次数: {stats['success_count']}")
                print(f"失败次数: {stats['failed_count']}")
                print(f"成功率: {stats['success_rate']}%")
                print(f"最后使用: {stats['last_used_at'] or '从未使用'}")
                print(f"冷却结束: {stats['cooldown_until'] or '无'}")
            else:
                print(f"账号 ID {args.id} 不存在")
        else:
            if stats:
                print("整体账号统计:")
                print(f"总账号数: {stats['total_accounts']}")
                print(f"活跃账号: {stats['active_accounts']}")
                print(f"非活跃账号: {stats['inactive_accounts']}")
                print(f"被封账号: {stats['banned_accounts']}")
                print(f"冷却账号: {stats['cooldown_accounts']}")
                print(f"总成功次数: {stats['total_success']}")
                print(f"总失败次数: {stats['total_failed']}")
                print(f"整体成功率: {stats['overall_success_rate']}%")
                
    elif args.command == 'health-check':
        stats = manager.health_check_accounts()
        print("健康检查完成:")
        print(f"检查账号数: {stats['checked']}")
        print(f"激活账号数: {stats['activated']}")
        print(f"停用账号数: {stats['deactivated']}")
        print(f"错误数: {stats['errors']}")
        
    elif args.command == 'import':
        count = manager.import_accounts_from_file(args.file)
        print(f"成功导入 {count} 个账号")
        
    elif args.command == 'export':
        if manager.export_accounts_to_file(args.file, args.include_sensitive):
            print(f"账号已导出到: {args.file}")
        else:
            print("导出失败")


if __name__ == "__main__":
    main()