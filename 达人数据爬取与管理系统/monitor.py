# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 性能监控模块
提供实时监控、统计分析、性能优化建议
创建时间: 2025-01-23
"""

import os
import time
import json
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from pathlib import Path

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    active_threads: int
    requests_per_second: float
    success_rate: float
    avg_response_time: float
    queue_size: int
    error_count: int
    
class CrawlerMonitor:
    """爬虫性能监控器"""
    
    def __init__(self, log_interval: int = 60):
        self.log_interval = log_interval
        self.start_time = datetime.now()
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 统计数据
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = deque(maxlen=1000)  # 保留最近1000次请求的响应时间
        self.error_counts = defaultdict(int)
        
        # 性能历史数据
        self.metrics_history = deque(maxlen=1440)  # 保留24小时的数据（每分钟一条）
        
        # 线程安全锁
        self.stats_lock = threading.Lock()
        
        # 设置日志
        self.setup_logging()
        
    def setup_logging(self):
        """设置监控日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_filename = f"monitor_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = log_dir / log_filename
        
        self.logger = logging.getLogger(f"{__name__}.monitor")
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            handler = logging.FileHandler(log_path, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("性能监控已启动")
        
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("性能监控已停止")
        
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self._log_metrics(metrics)
                self._check_alerts(metrics)
                
                time.sleep(self.log_interval)
                
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(5)
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        # 系统资源
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / 1024 / 1024
        
        # 线程信息
        active_threads = threading.active_count()
        
        # 请求统计
        with self.stats_lock:
            total_time = (datetime.now() - self.start_time).total_seconds()
            requests_per_second = self.total_requests / max(total_time, 1)
            success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
            
            # 平均响应时间
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            active_threads=active_threads,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            queue_size=0,  # 需要从外部传入
            error_count=self.failed_requests
        )
        
    def _log_metrics(self, metrics: PerformanceMetrics):
        """记录性能指标"""
        self.logger.info(
            f"性能指标 - CPU: {metrics.cpu_percent:.1f}%, "
            f"内存: {metrics.memory_percent:.1f}% ({metrics.memory_used_mb:.1f}MB), "
            f"线程: {metrics.active_threads}, "
            f"请求/秒: {metrics.requests_per_second:.2f}, "
            f"成功率: {metrics.success_rate:.1f}%, "
            f"平均响应时间: {metrics.avg_response_time:.2f}ms"
        )
        
    def _check_alerts(self, metrics: PerformanceMetrics):
        """检查告警条件"""
        alerts = []
        
        # CPU使用率告警
        if metrics.cpu_percent > 80:
            alerts.append(f"CPU使用率过高: {metrics.cpu_percent:.1f}%")
            
        # 内存使用率告警
        if metrics.memory_percent > 85:
            alerts.append(f"内存使用率过高: {metrics.memory_percent:.1f}%")
            
        # 成功率告警
        if metrics.success_rate < 90 and self.total_requests > 100:
            alerts.append(f"请求成功率过低: {metrics.success_rate:.1f}%")
            
        # 响应时间告警
        if metrics.avg_response_time > 5000:  # 5秒
            alerts.append(f"平均响应时间过长: {metrics.avg_response_time:.0f}ms")
            
        # 线程数告警
        if metrics.active_threads > 50:
            alerts.append(f"活跃线程数过多: {metrics.active_threads}")
            
        for alert in alerts:
            self.logger.warning(f"⚠️ 性能告警: {alert}")
            
    def record_request(self, success: bool, response_time: float, error_type: str = None):
        """记录请求结果"""
        with self.stats_lock:
            self.total_requests += 1
            
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
                if error_type:
                    self.error_counts[error_type] += 1
                    
            self.response_times.append(response_time)
            
    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息"""
        with self.stats_lock:
            total_time = (datetime.now() - self.start_time).total_seconds()
            
            return {
                "运行时间": str(timedelta(seconds=int(total_time))),
                "总请求数": self.total_requests,
                "成功请求数": self.successful_requests,
                "失败请求数": self.failed_requests,
                "成功率": f"{(self.successful_requests / max(self.total_requests, 1)) * 100:.2f}%",
                "平均请求速率": f"{self.total_requests / max(total_time, 1):.2f} req/s",
                "平均响应时间": f"{sum(self.response_times) / len(self.response_times) if self.response_times else 0:.2f}ms",
                "错误统计": dict(self.error_counts),
                "活跃线程数": threading.active_count()
            }
            
    def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.metrics_history:
            return {"error": "暂无性能数据"}
            
        # 计算统计指标
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_percent for m in self.metrics_history]
        response_times = [m.avg_response_time for m in self.metrics_history]
        success_rates = [m.success_rate for m in self.metrics_history]
        
        return {
            "数据时间范围": {
                "开始时间": self.metrics_history[0].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "结束时间": self.metrics_history[-1].timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "数据点数量": len(self.metrics_history)
            },
            "CPU使用率": {
                "平均值": f"{sum(cpu_values) / len(cpu_values):.2f}%",
                "最大值": f"{max(cpu_values):.2f}%",
                "最小值": f"{min(cpu_values):.2f}%"
            },
            "内存使用率": {
                "平均值": f"{sum(memory_values) / len(memory_values):.2f}%",
                "最大值": f"{max(memory_values):.2f}%",
                "最小值": f"{min(memory_values):.2f}%"
            },
            "响应时间": {
                "平均值": f"{sum(response_times) / len(response_times):.2f}ms",
                "最大值": f"{max(response_times):.2f}ms",
                "最小值": f"{min(response_times):.2f}ms"
            },
            "成功率": {
                "平均值": f"{sum(success_rates) / len(success_rates):.2f}%",
                "最大值": f"{max(success_rates):.2f}%",
                "最小值": f"{min(success_rates):.2f}%"
            },
            "当前统计": self.get_current_stats()
        }
        
    def export_metrics(self, filepath: str):
        """导出性能指标到文件"""
        try:
            metrics_data = [
                asdict(metric) for metric in self.metrics_history
            ]
            
            # 转换datetime为字符串
            for metric in metrics_data:
                metric['timestamp'] = metric['timestamp'].isoformat()
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "export_time": datetime.now().isoformat(),
                    "metrics": metrics_data,
                    "summary": self.get_performance_report()
                }, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"性能指标已导出到: {filepath}")
            
        except Exception as e:
            self.logger.error(f"导出性能指标失败: {e}")
            
    def get_optimization_suggestions(self) -> List[str]:
        """获取性能优化建议"""
        suggestions = []
        
        if not self.metrics_history:
            return ["暂无足够数据进行分析"]
            
        latest_metrics = self.metrics_history[-1]
        
        # CPU优化建议
        if latest_metrics.cpu_percent > 70:
            suggestions.append("CPU使用率较高，建议减少并发线程数或优化算法")
            
        # 内存优化建议
        if latest_metrics.memory_percent > 80:
            suggestions.append("内存使用率较高，建议增加数据清理频率或减少缓存大小")
            
        # 响应时间优化建议
        if latest_metrics.avg_response_time > 3000:
            suggestions.append("响应时间较长，建议检查网络连接或增加请求超时设置")
            
        # 成功率优化建议
        if latest_metrics.success_rate < 95 and self.total_requests > 50:
            suggestions.append("请求成功率较低，建议检查账号状态或增加重试机制")
            
        # 线程数优化建议
        if latest_metrics.active_threads > 20:
            suggestions.append("活跃线程数较多，建议使用线程池管理或减少并发数")
            
        # 错误率分析
        with self.stats_lock:
            if self.error_counts:
                most_common_error = max(self.error_counts.items(), key=lambda x: x[1])
                suggestions.append(f"最常见错误: {most_common_error[0]} ({most_common_error[1]}次)，建议针对性优化")
                
        if not suggestions:
            suggestions.append("当前性能表现良好，无需特别优化")
            
        return suggestions

# 全局监控实例
_global_monitor = None

def get_monitor() -> CrawlerMonitor:
    """获取全局监控实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = CrawlerMonitor()
    return _global_monitor

def start_monitoring():
    """启动全局监控"""
    monitor = get_monitor()
    monitor.start_monitoring()
    
def stop_monitoring():
    """停止全局监控"""
    monitor = get_monitor()
    monitor.stop_monitoring()
    
def record_request(success: bool, response_time: float, error_type: str = None):
    """记录请求（便捷函数）"""
    monitor = get_monitor()
    monitor.record_request(success, response_time, error_type)
    
def get_current_stats() -> Dict[str, Any]:
    """获取当前统计信息（便捷函数）"""
    monitor = get_monitor()
    return monitor.get_current_stats()
    
def get_performance_report() -> Dict[str, Any]:
    """获取性能报告（便捷函数）"""
    monitor = get_monitor()
    return monitor.get_performance_report()

if __name__ == "__main__":
    # 测试监控功能
    import random
    
    monitor = CrawlerMonitor(log_interval=5)
    monitor.start_monitoring()
    
    try:
        # 模拟请求
        for i in range(100):
            success = random.random() > 0.1  # 90%成功率
            response_time = random.uniform(100, 2000)  # 100-2000ms响应时间
            error_type = None if success else random.choice(['timeout', 'connection_error', 'auth_error'])
            
            monitor.record_request(success, response_time, error_type)
            time.sleep(0.1)
            
            if i % 20 == 0:
                print(f"\n=== 统计信息 (第{i}次请求) ===")
                stats = monitor.get_current_stats()
                for key, value in stats.items():
                    print(f"{key}: {value}")
                    
        print("\n=== 性能报告 ===")
        report = monitor.get_performance_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
        print("\n=== 优化建议 ===")
        suggestions = monitor.get_optimization_suggestions()
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
            
    finally:
        monitor.stop_monitoring()