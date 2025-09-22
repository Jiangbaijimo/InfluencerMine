# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 任务调度脚本
支持定时任务、任务队列管理、任务监控、失败重试
创建时间: 2025-01-23
"""

import os
import json
import time
import logging
import argparse
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from enum import Enum
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import schedule

# 加载环境变量
load_dotenv()

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(Enum):
    CRAWL_DAOREN = "crawl_daoren"
    IMPORT_DATA = "import_data"
    EXPORT_DATA = "export_data"
    HEALTH_CHECK = "health_check"
    CLEANUP = "cleanup"

class TaskScheduler:
    def __init__(self):
        self.setup_logging()
        self.db_config = self.get_db_config()
        self.running = False
        self.worker_threads = []
        self.max_workers = int(os.getenv('MAX_WORKER_THREADS', 3))
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"task_scheduler_{datetime.now().strftime('%Y%m%d')}.log"
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
            
    def create_task(self, task_type: str, task_name: str, parameters: Dict[str, Any] = None,
                   priority: int = 5, scheduled_at: datetime = None, 
                   max_retries: int = 3) -> Optional[int]:
        """创建新任务"""
        conn = self.get_db_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO daoren_task_log 
                    (task_type, task_name, parameters, priority, status, 
                     scheduled_at, max_retries, retry_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
                """, (
                    task_type, task_name, 
                    json.dumps(parameters, ensure_ascii=False) if parameters else None,
                    priority, TaskStatus.PENDING.value,
                    scheduled_at or datetime.now(),
                    max_retries
                ))
                
                conn.commit()
                task_id = cursor.lastrowid
                self.logger.info(f"创建任务成功: {task_name} (ID: {task_id})")
                return task_id
                
        except Exception as e:
            self.logger.error(f"创建任务失败: {e}")
            return None
        finally:
            conn.close()
            
    def update_task_status(self, task_id: int, status: TaskStatus, 
                          result: str = None, error_message: str = None) -> bool:
        """更新任务状态"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                update_fields = ["status = %s"]
                params = [status.value]
                
                if status == TaskStatus.RUNNING:
                    update_fields.append("started_at = %s")
                    params.append(datetime.now())
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    update_fields.append("finished_at = %s")
                    params.append(datetime.now())
                    
                if result:
                    update_fields.append("result = %s")
                    params.append(result)
                    
                if error_message:
                    update_fields.append("error_message = %s")
                    params.append(error_message)
                    
                params.append(task_id)
                
                cursor.execute(f"""
                    UPDATE daoren_task_log 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                """, params)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"更新任务状态失败: {e}")
            return False
        finally:
            conn.close()
            
    def get_pending_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取待执行任务"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM daoren_task_log 
                    WHERE status = %s 
                    AND scheduled_at <= %s
                    ORDER BY priority DESC, scheduled_at ASC
                    LIMIT %s
                """, (TaskStatus.PENDING.value, datetime.now(), limit))
                
                return cursor.fetchall()
                
        except Exception as e:
            self.logger.error(f"获取待执行任务失败: {e}")
            return []
        finally:
            conn.close()
            
    def get_failed_tasks_for_retry(self) -> List[Dict[str, Any]]:
        """获取需要重试的失败任务"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM daoren_task_log 
                    WHERE status = %s 
                    AND retry_count < max_retries
                    AND finished_at < %s
                    ORDER BY priority DESC, finished_at ASC
                """, (
                    TaskStatus.FAILED.value, 
                    datetime.now() - timedelta(minutes=30)  # 30分钟后重试
                ))
                
                return cursor.fetchall()
                
        except Exception as e:
            self.logger.error(f"获取重试任务失败: {e}")
            return []
        finally:
            conn.close()
            
    def retry_task(self, task_id: int) -> bool:
        """重试任务"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE daoren_task_log 
                    SET status = %s, retry_count = retry_count + 1,
                        scheduled_at = %s, error_message = NULL
                    WHERE id = %s AND retry_count < max_retries
                """, (TaskStatus.PENDING.value, datetime.now(), task_id))
                
                conn.commit()
                success = cursor.rowcount > 0
                
                if success:
                    self.logger.info(f"任务 {task_id} 已重新调度")
                    
                return success
                
        except Exception as e:
            self.logger.error(f"重试任务失败: {e}")
            return False
        finally:
            conn.close()
            
    def cancel_task(self, task_id: int) -> bool:
        """取消任务"""
        return self.update_task_status(task_id, TaskStatus.CANCELLED)
        
    def execute_task(self, task: Dict[str, Any]) -> bool:
        """执行任务"""
        task_id = task['id']
        task_type = task['task_type']
        task_name = task['task_name']
        parameters = json.loads(task['parameters']) if task['parameters'] else {}
        
        self.logger.info(f"开始执行任务: {task_name} (ID: {task_id}, Type: {task_type})")
        
        # 更新任务状态为运行中
        if not self.update_task_status(task_id, TaskStatus.RUNNING):
            return False
            
        try:
            result = None
            
            if task_type == TaskType.CRAWL_DAOREN.value:
                result = self.execute_crawl_task(parameters)
            elif task_type == TaskType.IMPORT_DATA.value:
                result = self.execute_import_task(parameters)
            elif task_type == TaskType.EXPORT_DATA.value:
                result = self.execute_export_task(parameters)
            elif task_type == TaskType.HEALTH_CHECK.value:
                result = self.execute_health_check_task(parameters)
            elif task_type == TaskType.CLEANUP.value:
                result = self.execute_cleanup_task(parameters)
            else:
                raise ValueError(f"未知任务类型: {task_type}")
                
            # 任务执行成功
            self.update_task_status(task_id, TaskStatus.COMPLETED, 
                                  json.dumps(result, ensure_ascii=False))
            self.logger.info(f"任务执行成功: {task_name} (ID: {task_id})")
            return True
            
        except Exception as e:
            # 任务执行失败
            error_message = str(e)
            self.update_task_status(task_id, TaskStatus.FAILED, error_message=error_message)
            self.logger.error(f"任务执行失败: {task_name} (ID: {task_id}) - {error_message}")
            return False
            
    def execute_crawl_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行爬取任务"""
        import subprocess
        
        # 构建爬取命令
        cmd = ["python", "crawler_main.py"]
        
        if parameters.get('start_page'):
            cmd.extend(["--start-page", str(parameters['start_page'])])
        if parameters.get('end_page'):
            cmd.extend(["--end-page", str(parameters['end_page'])])
        if parameters.get('daoren_types'):
            cmd.extend(["--types"] + parameters['daoren_types'])
        if parameters.get('account_id'):
            cmd.extend(["--account-id", str(parameters['account_id'])])
            
        # 执行爬取脚本
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            raise Exception(f"爬取脚本执行失败: {result.stderr}")
            
        return {
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "execution_time": datetime.now().isoformat()
        }
        
    def execute_import_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据导入任务"""
        import subprocess
        
        cmd = ["python", "import_to_mysql.py"]
        
        if parameters.get('csv_file'):
            cmd.extend(["--file", parameters['csv_file']])
        if parameters.get('batch_size'):
            cmd.extend(["--batch-size", str(parameters['batch_size'])])
            
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            raise Exception(f"导入脚本执行失败: {result.stderr}")
            
        return {
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "execution_time": datetime.now().isoformat()
        }
        
    def execute_export_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据导出任务"""
        # 这里可以实现数据导出逻辑
        # 暂时返回模拟结果
        return {
            "exported_records": parameters.get('record_count', 0),
            "export_file": parameters.get('output_file', 'export.csv'),
            "execution_time": datetime.now().isoformat()
        }
        
    def execute_health_check_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行健康检查任务"""
        from account_manager import AccountManager
        
        manager = AccountManager()
        stats = manager.health_check_accounts()
        
        return {
            "health_check_stats": stats,
            "execution_time": datetime.now().isoformat()
        }
        
    def execute_cleanup_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行清理任务"""
        cleaned_files = 0
        cleaned_logs = 0
        
        # 清理旧日志文件
        if parameters.get('clean_logs', True):
            log_dir = Path("logs")
            if log_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=parameters.get('log_retention_days', 30))
                
                for log_file in log_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        cleaned_logs += 1
                        
        # 清理临时文件
        if parameters.get('clean_temp', True):
            temp_patterns = ['*.tmp', '*.temp', '*~']
            
            for pattern in temp_patterns:
                for temp_file in Path('.').glob(pattern):
                    temp_file.unlink()
                    cleaned_files += 1
                    
        return {
            "cleaned_files": cleaned_files,
            "cleaned_logs": cleaned_logs,
            "execution_time": datetime.now().isoformat()
        }
        
    def worker_thread(self):
        """工作线程"""
        while self.running:
            try:
                # 获取待执行任务
                tasks = self.get_pending_tasks(1)
                
                if tasks:
                    task = tasks[0]
                    self.execute_task(task)
                else:
                    # 检查是否有需要重试的任务
                    retry_tasks = self.get_failed_tasks_for_retry()
                    if retry_tasks:
                        for retry_task in retry_tasks[:1]:  # 一次只重试一个
                            self.retry_task(retry_task['id'])
                    else:
                        # 没有任务时休眠
                        time.sleep(10)
                        
            except Exception as e:
                self.logger.error(f"工作线程异常: {e}")
                time.sleep(5)
                
    def start_scheduler(self):
        """启动调度器"""
        if self.running:
            self.logger.warning("调度器已在运行")
            return
            
        self.running = True
        self.logger.info(f"启动任务调度器，工作线程数: {self.max_workers}")
        
        # 启动工作线程
        for i in range(self.max_workers):
            thread = threading.Thread(target=self.worker_thread, name=f"Worker-{i+1}")
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
            
        # 设置定时任务
        self.setup_scheduled_tasks()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次定时任务
        except KeyboardInterrupt:
            self.logger.info("收到停止信号")
        finally:
            self.stop_scheduler()
            
    def stop_scheduler(self):
        """停止调度器"""
        if not self.running:
            return
            
        self.logger.info("正在停止任务调度器...")
        self.running = False
        
        # 等待工作线程结束
        for thread in self.worker_threads:
            thread.join(timeout=30)
            
        self.worker_threads.clear()
        self.logger.info("任务调度器已停止")
        
    def setup_scheduled_tasks(self):
        """设置定时任务"""
        # 每天凌晨2点执行健康检查
        schedule.every().day.at("02:00").do(
            self.create_scheduled_health_check
        )
        
        # 每周日凌晨3点执行清理任务
        schedule.every().sunday.at("03:00").do(
            self.create_scheduled_cleanup
        )
        
        # 每小时检查失败任务重试
        schedule.every().hour.do(
            self.check_failed_tasks
        )
        
        self.logger.info("定时任务已设置")
        
    def create_scheduled_health_check(self):
        """创建定时健康检查任务"""
        self.create_task(
            TaskType.HEALTH_CHECK.value,
            "定时健康检查",
            {},
            priority=3
        )
        
    def create_scheduled_cleanup(self):
        """创建定时清理任务"""
        self.create_task(
            TaskType.CLEANUP.value,
            "定时清理",
            {
                "clean_logs": True,
                "log_retention_days": 30,
                "clean_temp": True
            },
            priority=2
        )
        
    def check_failed_tasks(self):
        """检查失败任务并重试"""
        retry_tasks = self.get_failed_tasks_for_retry()
        
        for task in retry_tasks:
            self.retry_task(task['id'])
            
    def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计"""
        conn = self.get_db_connection()
        if not conn:
            return {}
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_tasks,
                        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_tasks,
                        SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_tasks,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
                        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_tasks,
                        AVG(CASE 
                            WHEN finished_at IS NOT NULL AND started_at IS NOT NULL 
                            THEN TIMESTAMPDIFF(SECOND, started_at, finished_at) 
                            ELSE NULL 
                        END) as avg_execution_time
                    FROM daoren_task_log
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                """)
                
                return cursor.fetchone() or {}
                
        except Exception as e:
            self.logger.error(f"获取任务统计失败: {e}")
            return {}
        finally:
            conn.close()
            
    def list_tasks(self, status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """列出任务"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                if status:
                    cursor.execute("""
                        SELECT * FROM daoren_task_log 
                        WHERE status = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (status, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM daoren_task_log 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (limit,))
                    
                return cursor.fetchall()
                
        except Exception as e:
            self.logger.error(f"获取任务列表失败: {e}")
            return []
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description='达人数据爬取系统 - 任务调度器')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 启动调度器
    subparsers.add_parser('start', help='启动任务调度器')
    
    # 创建任务
    create_parser = subparsers.add_parser('create', help='创建新任务')
    create_parser.add_argument('--type', required=True, 
                              choices=[t.value for t in TaskType], 
                              help='任务类型')
    create_parser.add_argument('--name', required=True, help='任务名称')
    create_parser.add_argument('--params', help='任务参数(JSON格式)')
    create_parser.add_argument('--priority', type=int, default=5, help='任务优先级(1-10)')
    create_parser.add_argument('--schedule', help='调度时间(YYYY-MM-DD HH:MM:SS)')
    create_parser.add_argument('--max-retries', type=int, default=3, help='最大重试次数')
    
    # 列出任务
    list_parser = subparsers.add_parser('list', help='列出任务')
    list_parser.add_argument('--status', choices=[s.value for s in TaskStatus], help='筛选状态')
    list_parser.add_argument('--limit', type=int, default=20, help='显示数量')
    
    # 任务统计
    subparsers.add_parser('stats', help='任务统计')
    
    # 取消任务
    cancel_parser = subparsers.add_parser('cancel', help='取消任务')
    cancel_parser.add_argument('--id', type=int, required=True, help='任务ID')
    
    # 重试任务
    retry_parser = subparsers.add_parser('retry', help='重试任务')
    retry_parser.add_argument('--id', type=int, required=True, help='任务ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    scheduler = TaskScheduler()
    
    if args.command == 'start':
        scheduler.start_scheduler()
        
    elif args.command == 'create':
        parameters = None
        if args.params:
            try:
                parameters = json.loads(args.params)
            except json.JSONDecodeError:
                print("参数格式错误，应为有效的JSON")
                return
                
        scheduled_at = None
        if args.schedule:
            try:
                scheduled_at = datetime.strptime(args.schedule, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print("时间格式错误，应为 YYYY-MM-DD HH:MM:SS")
                return
                
        task_id = scheduler.create_task(
            args.type, args.name, parameters, 
            args.priority, scheduled_at, args.max_retries
        )
        
        if task_id:
            print(f"任务创建成功，ID: {task_id}")
        else:
            print("任务创建失败")
            
    elif args.command == 'list':
        tasks = scheduler.list_tasks(args.status, args.limit)
        
        if tasks:
            print(f"{'ID':<5} {'名称':<30} {'类型':<15} {'状态':<10} {'创建时间':<20}")
            print("-" * 90)
            
            for task in tasks:
                created_at = task['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{task['id']:<5} {task['task_name']:<30} {task['task_type']:<15} "
                      f"{task['status']:<10} {created_at:<20}")
        else:
            print("没有找到任务")
            
    elif args.command == 'stats':
        stats = scheduler.get_task_stats()
        
        if stats:
            print("任务统计 (最近7天):")
            print(f"总任务数: {stats['total_tasks']}")
            print(f"待执行: {stats['pending_tasks']}")
            print(f"执行中: {stats['running_tasks']}")
            print(f"已完成: {stats['completed_tasks']}")
            print(f"失败: {stats['failed_tasks']}")
            print(f"已取消: {stats['cancelled_tasks']}")
            
            if stats['avg_execution_time']:
                print(f"平均执行时间: {stats['avg_execution_time']:.2f}秒")
                
    elif args.command == 'cancel':
        if scheduler.cancel_task(args.id):
            print(f"任务 {args.id} 已取消")
        else:
            print(f"取消任务 {args.id} 失败")
            
    elif args.command == 'retry':
        if scheduler.retry_task(args.id):
            print(f"任务 {args.id} 已重新调度")
        else:
            print(f"重试任务 {args.id} 失败")


if __name__ == "__main__":
    main()