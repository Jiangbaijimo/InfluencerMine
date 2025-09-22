# 达人数据爬取与管理系统 - 使用指南

本文档详细介绍如何使用达人数据爬取与管理系统的各项功能。

## 📚 目录

- [快速开始](#快速开始)
- [基础操作](#基础操作)
- [高级功能](#高级功能)
- [命令行工具](#命令行工具)
- [API接口](#api接口)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 🚀 快速开始

### 第一次使用

1. **确认安装完成**
   ```bash
   # 检查环境
   make check-env
   
   # 查看系统状态
   python task_scheduler.py stats
   ```

2. **添加爬取账号**
   ```bash
   # 添加主账号
   python account_manager.py add \
     --name "主账号" \
     --cookies "your_cookie_here" \
     --notes "主要爬取账号"
   ```

3. **开始第一次爬取**
   ```bash
   # 爬取前10页数据
   python crawler_main.py --start-page 1 --end-page 10
   ```

4. **查看爬取结果**
   ```bash
   # 查看数据文件
   ls -la data/
   
   # 导入到数据库
   python import_to_mysql.py --file data/daoren_data_20240101_120000.csv
   ```

## 🔧 基础操作

### 账号管理

#### 添加账号

```bash
# 基本添加
python account_manager.py add --name "账号1" --cookies "cookie_string"

# 完整添加
python account_manager.py add \
  --name "账号1" \
  --cookies "cookie_string" \
  --headers '{"User-Agent": "Mozilla/5.0..."}' \
  --proxy "http://proxy:8080" \
  --notes "备用账号"
```

#### 管理账号

```bash
# 查看所有账号
python account_manager.py list

# 查看账号详情
python account_manager.py show --name "账号1"

# 更新账号
python account_manager.py update --name "账号1" --cookies "new_cookie"

# 禁用账号
python account_manager.py disable --name "账号1"

# 启用账号
python account_manager.py enable --name "账号1"

# 删除账号
python account_manager.py delete --name "账号1"
```

#### 批量操作

```bash
# 批量导入账号
python account_manager.py import --file accounts.json

# 批量导出账号
python account_manager.py export --file backup_accounts.json

# 健康检查
python account_manager.py health-check

# 清除冷却状态
python account_manager.py clear-cooldown --name "账号1"
```

### 数据爬取

#### 基本爬取

```bash
# 爬取指定页面范围
python crawler_main.py --start-page 1 --end-page 100

# 使用指定账号
python crawler_main.py --account "账号1" --start-page 1 --end-page 50

# 测试模式（只爬取少量数据）
python crawler_main.py --test-mode --start-page 1 --end-page 5
```

#### 高级爬取选项

```bash
# 断点续爬
python crawler_main.py --resume --task-id 12345

# 指定输出目录
python crawler_main.py --output-dir /path/to/output --start-page 1 --end-page 50

# 设置请求间隔
python crawler_main.py --interval 3 --start-page 1 --end-page 100

# 启用详细日志
python crawler_main.py --verbose --start-page 1 --end-page 20

# 只爬取特定类型
python crawler_main.py --types "美食,旅游" --start-page 1 --end-page 50
```

#### 批量爬取配置

创建爬取配置文件 `crawl_config.json`：

```json
{
  "tasks": [
    {
      "name": "美食达人爬取",
      "start_page": 1,
      "end_page": 500,
      "types": ["美食", "生活"],
      "account": "账号1",
      "interval": 2
    },
    {
      "name": "旅游达人爬取",
      "start_page": 1,
      "end_page": 300,
      "types": ["旅游", "摄影"],
      "account": "账号2",
      "interval": 3
    }
  ]
}
```

执行批量爬取：

```bash
python crawler_main.py --config crawl_config.json
```

### 数据导入

#### 基本导入

```bash
# 导入单个文件
python import_to_mysql.py --file data/daoren_data_20240101.csv

# 批量导入目录下所有CSV文件
python import_to_mysql.py --directory data/

# 强制重新导入（覆盖已存在数据）
python import_to_mysql.py --file data.csv --force-reimport
```

#### 导入选项

```bash
# 跳过重复数据
python import_to_mysql.py --file data.csv --skip-duplicates

# 设置批量大小
python import_to_mysql.py --file data.csv --batch-size 500

# 启用数据验证
python import_to_mysql.py --file data.csv --validate

# 导入后清理源文件
python import_to_mysql.py --file data.csv --cleanup
```

### 任务调度

#### 启动调度器

```bash
# 启动任务调度器
python task_scheduler.py start

# 后台运行
python task_scheduler.py start --daemon

# 指定工作线程数
python task_scheduler.py start --workers 5
```

#### 任务管理

```bash
# 创建定时任务
python task_scheduler.py create-schedule \
  --name "每日爬取" \
  --cron "0 2 * * *" \
  --command "python crawler_main.py --start-page 1 --end-page 100"

# 查看所有任务
python task_scheduler.py list

# 查看任务状态
python task_scheduler.py status --task-id 12345

# 停止任务
python task_scheduler.py stop --task-id 12345

# 重启失败任务
python task_scheduler.py retry --task-id 12345

# 清理完成的任务
python task_scheduler.py cleanup --days 7
```

## 🎯 高级功能

### 数据分析和统计

#### 基本统计

```bash
# 查看数据库统计
python -c "
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM daoren_data')
total = cursor.fetchone()[0]
print(f'总达人数量: {total}')

cursor.execute('SELECT type_name, COUNT(*) FROM daoren_types GROUP BY type_name')
types = cursor.fetchall()
print('按类型统计:')
for type_name, count in types:
    print(f'  {type_name}: {count}')

conn.close()
"
```

#### 数据导出

```bash
# 导出所有数据
python -c "
import pandas as pd
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

# 导出达人数据
df = pd.read_sql('SELECT * FROM daoren_data', conn)
df.to_excel('export/all_daoren_data.xlsx', index=False)

# 导出统计数据
stats_df = pd.read_sql('SELECT * FROM daoren_stats_by_type', conn)
stats_df.to_excel('export/daoren_statistics.xlsx', index=False)

conn.close()
print('数据导出完成')
"
```

### 监控和报警

#### 系统监控

```bash
# 查看系统状态
python task_scheduler.py monitor

# 查看性能指标
python -c "
import psutil
import pymysql
from dotenv import load_dotenv
import os

print('系统资源使用情况:')
print(f'CPU使用率: {psutil.cpu_percent()}%')
print(f'内存使用率: {psutil.virtual_memory().percent}%')
print(f'磁盘使用率: {psutil.disk_usage(\"/\").percent}%')

# 数据库连接数
load_dotenv()
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
cursor = conn.cursor()
cursor.execute('SHOW STATUS LIKE \"Threads_connected\"')
connections = cursor.fetchone()[1]
print(f'数据库连接数: {connections}')
conn.close()
"
```

#### 日志分析

```bash
# 查看错误日志
tail -f logs/error.log

# 统计错误类型
grep "ERROR" logs/crawler.log | cut -d' ' -f4- | sort | uniq -c | sort -nr

# 查看最近的爬取记录
tail -n 100 logs/crawler.log | grep "爬取完成"

# 分析账号使用情况
grep "使用账号" logs/crawler.log | cut -d' ' -f6 | sort | uniq -c
```

### 数据备份和恢复

#### 数据备份

```bash
# 创建数据库备份
mysqldump -h localhost -u crawler_user -p influencer_crawler > backup/db_backup_$(date +%Y%m%d_%H%M%S).sql

# 备份数据文件
tar -czf backup/data_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/

# 备份配置文件
cp .env config.yaml backup/
```

#### 数据恢复

```bash
# 恢复数据库
mysql -h localhost -u crawler_user -p influencer_crawler < backup/db_backup_20240101_120000.sql

# 恢复数据文件
tar -xzf backup/data_backup_20240101_120000.tar.gz
```

### 性能优化

#### 数据库优化

```sql
-- 添加索引
ALTER TABLE daoren_data ADD INDEX idx_daoren_id (daoren_id);
ALTER TABLE daoren_data ADD INDEX idx_fans_count (fans_count);
ALTER TABLE daoren_data ADD INDEX idx_created_at (created_at);

-- 分析表
ANALYZE TABLE daoren_data;

-- 优化表
OPTIMIZE TABLE daoren_data;
```

#### 爬虫优化

编辑 `config.yaml`：

```yaml
crawler:
  # 并发请求数
  concurrent_requests: 3
  
  # 请求间隔（秒）
  request_interval: 1.5
  
  # 超时设置
  timeout: 30
  
  # 重试次数
  max_retries: 3
  
  # 连接池大小
  connection_pool_size: 10
```

## 📋 命令行工具参考

### crawler_main.py

```bash
python crawler_main.py [选项]

选项:
  --start-page INT        起始页码 (默认: 1)
  --end-page INT         结束页码 (默认: 10)
  --account TEXT         指定使用的账号名称
  --output-dir PATH      输出目录 (默认: data/)
  --interval FLOAT       请求间隔秒数 (默认: 2.0)
  --types TEXT           指定爬取的达人类型，逗号分隔
  --test-mode           测试模式，只爬取少量数据
  --resume              断点续爬模式
  --task-id INT         续爬的任务ID
  --verbose             启用详细日志
  --config PATH         使用配置文件
  --help                显示帮助信息
```

### account_manager.py

```bash
python account_manager.py [命令] [选项]

命令:
  add                   添加新账号
  list                  列出所有账号
  show                  显示账号详情
  update                更新账号信息
  delete                删除账号
  enable                启用账号
  disable               禁用账号
  stats                 显示统计信息
  health-check          健康检查
  clear-cooldown        清除冷却状态
  import                批量导入账号
  export                批量导出账号

选项:
  --name TEXT           账号名称
  --cookies TEXT        Cookie字符串
  --headers TEXT        请求头JSON字符串
  --proxy TEXT          代理地址
  --notes TEXT          备注信息
  --file PATH           文件路径
  --help                显示帮助信息
```

### task_scheduler.py

```bash
python task_scheduler.py [命令] [选项]

命令:
  start                 启动任务调度器
  stop                  停止任务调度器
  status                查看状态
  list                  列出所有任务
  create-schedule       创建定时任务
  cancel                取消任务
  retry                 重试失败任务
  cleanup               清理完成任务
  monitor               监控系统状态
  stats                 显示统计信息

选项:
  --daemon              后台运行
  --workers INT         工作线程数
  --task-id INT         任务ID
  --name TEXT           任务名称
  --cron TEXT           Cron表达式
  --command TEXT        执行命令
  --days INT            清理天数
  --help                显示帮助信息
```

### import_to_mysql.py

```bash
python import_to_mysql.py [选项]

选项:
  --file PATH           CSV文件路径
  --directory PATH      CSV文件目录
  --batch-size INT      批量处理大小 (默认: 1000)
  --skip-duplicates     跳过重复数据
  --force-reimport      强制重新导入
  --validate            启用数据验证
  --cleanup             导入后清理源文件
  --help                显示帮助信息
```

## 🎨 最佳实践

### 爬取策略

1. **合理设置请求间隔**
   ```bash
   # 推荐间隔2-3秒
   python crawler_main.py --interval 2.5 --start-page 1 --end-page 100
   ```

2. **使用多账号轮换**
   ```bash
   # 添加多个账号
   python account_manager.py add --name "账号1" --cookies "cookie1"
   python account_manager.py add --name "账号2" --cookies "cookie2"
   python account_manager.py add --name "账号3" --cookies "cookie3"
   
   # 系统会自动轮换使用
   ```

3. **分批次爬取**
   ```bash
   # 分时段爬取，避免集中请求
   # 上午爬取
   python crawler_main.py --start-page 1 --end-page 200
   
   # 下午爬取
   python crawler_main.py --start-page 201 --end-page 400
   ```

### 数据管理

1. **定期备份**
   ```bash
   # 设置定时备份任务
   python task_scheduler.py create-schedule \
     --name "每日备份" \
     --cron "0 3 * * *" \
     --command "make backup"
   ```

2. **数据清理**
   ```bash
   # 清理7天前的日志
   find logs/ -name "*.log" -mtime +7 -delete
   
   # 清理临时文件
   find data/ -name "*.tmp" -delete
   ```

3. **监控数据质量**
   ```sql
   -- 检查重复数据
   SELECT daoren_id, COUNT(*) as count 
   FROM daoren_data 
   GROUP BY daoren_id 
   HAVING count > 1;
   
   -- 检查异常数据
   SELECT * FROM daoren_data 
   WHERE fans_count < 0 OR fans_count > 100000000;
   ```

### 性能优化

1. **数据库优化**
   ```sql
   -- 定期优化表
   OPTIMIZE TABLE daoren_data;
   OPTIMIZE TABLE task_logs;
   
   -- 更新统计信息
   ANALYZE TABLE daoren_data;
   ```

2. **系统资源监控**
   ```bash
   # 监控脚本
   #!/bin/bash
   while true; do
     echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
     echo "$(date): Memory: $(free | grep Mem | awk '{printf "%.2f%%", $3/$2 * 100.0}')"
     sleep 300
   done > logs/system_monitor.log &
   ```

### 安全建议

1. **保护敏感信息**
   ```bash
   # 设置文件权限
   chmod 600 .env
   chmod 600 config.yaml
   
   # 不要在日志中记录敏感信息
   ```

2. **定期更新Cookie**
   ```bash
   # 定期检查账号状态
   python account_manager.py health-check
   
   # 及时更新失效的Cookie
   python account_manager.py update --name "账号1" --cookies "new_cookie"
   ```

3. **监控异常活动**
   ```bash
   # 监控错误日志
   tail -f logs/error.log | grep -i "blocked\|forbidden\|rate limit"
   ```

## 🔍 故障排除

### 常见问题

#### 1. 爬取失败

**问题**: 请求被拒绝或返回错误

**解决方案**:
```bash
# 检查账号状态
python account_manager.py health-check

# 更新Cookie
python account_manager.py update --name "账号1" --cookies "new_cookie"

# 增加请求间隔
python crawler_main.py --interval 5 --start-page 1 --end-page 10
```

#### 2. 数据库连接失败

**问题**: 无法连接到MySQL数据库

**解决方案**:
```bash
# 检查MySQL服务
sudo systemctl status mysql

# 测试连接
mysql -h localhost -u crawler_user -p

# 检查配置文件
cat .env | grep DB_
```

#### 3. 内存不足

**问题**: 系统内存使用过高

**解决方案**:
```bash
# 减少并发数
# 编辑config.yaml
crawler:
  concurrent_requests: 1

# 减少批量大小
python import_to_mysql.py --batch-size 100

# 清理临时文件
make clean
```

#### 4. 磁盘空间不足

**问题**: 磁盘空间不够

**解决方案**:
```bash
# 清理日志文件
find logs/ -name "*.log" -mtime +7 -delete

# 压缩旧数据
gzip data/*.csv

# 清理数据库日志
mysql -u root -p -e "PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 7 DAY);"
```

### 调试技巧

1. **启用详细日志**
   ```bash
   python crawler_main.py --verbose --start-page 1 --end-page 1
   ```

2. **使用测试模式**
   ```bash
   python crawler_main.py --test-mode
   ```

3. **检查网络连接**
   ```bash
   curl -I "https://www.xiaohongshu.com"
   ```

4. **分析日志文件**
   ```bash
   # 查看最近的错误
   tail -n 50 logs/error.log
   
   # 统计错误类型
   grep "ERROR" logs/crawler.log | cut -d' ' -f4- | sort | uniq -c
   ```

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件：`logs/` 目录
2. 检查配置文件：`.env` 和 `config.yaml`
3. 运行系统检查：`make check-env`
4. 查看任务状态：`python task_scheduler.py stats`
5. 参考故障排除章节
6. 联系技术支持

---

更多详细信息请参考 [README.md](README.md) 和 [INSTALL.md](INSTALL.md)。