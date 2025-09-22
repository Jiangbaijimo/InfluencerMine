# 达人数据爬取与管理系统 - 常见问题解答 (FAQ)

本文档收集了用户在使用达人数据爬取与管理系统时经常遇到的问题及其解决方案。

## 📋 目录

- [安装相关问题](#安装相关问题)
- [配置相关问题](#配置相关问题)
- [爬取相关问题](#爬取相关问题)
- [数据库相关问题](#数据库相关问题)
- [账号管理问题](#账号管理问题)
- [性能相关问题](#性能相关问题)
- [错误处理问题](#错误处理问题)
- [部署相关问题](#部署相关问题)

## 🔧 安装相关问题

### Q1: 安装Python依赖时出现错误怎么办？

**A**: 常见的解决方案：

```bash
# 1. 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 2. 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 3. 如果是特定包安装失败，单独安装
pip install pymysql --no-cache-dir

# 4. 在Windows上可能需要安装Visual C++构建工具
# 下载并安装 Microsoft C++ Build Tools
```

### Q2: MySQL安装后无法连接怎么办？

**A**: 检查以下几个方面：

```bash
# 1. 检查MySQL服务是否运行
# Windows
net start mysql

# Linux
sudo systemctl status mysql

# 2. 检查端口是否监听
netstat -tlnp | grep 3306

# 3. 检查防火墙设置
# Windows防火墙允许3306端口
# Linux
sudo ufw allow 3306/tcp

# 4. 测试连接
mysql -h localhost -u root -p
```

### Q3: 虚拟环境创建失败怎么办？

**A**: 尝试以下解决方案：

```bash
# 1. 确保Python版本正确
python --version  # 应该是3.8+

# 2. 使用完整路径创建虚拟环境
python -m venv venv

# 3. 如果还是失败，尝试使用virtualenv
pip install virtualenv
virtualenv venv

# 4. 在Windows上可能需要执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## ⚙️ 配置相关问题

### Q4: .env文件配置错误怎么办？

**A**: 检查配置格式：

```bash
# 正确的.env格式（注意没有空格）
DB_HOST=localhost
DB_PORT=3306
DB_USER=crawler_user
DB_PASSWORD=your_password
DB_NAME=influencer_crawler

# 错误格式（有空格）
DB_HOST = localhost  # 错误
DB_PASSWORD="password"  # 不需要引号
```

### Q5: 如何验证配置是否正确？

**A**: 使用以下命令验证：

```bash
# 1. 检查环境变量加载
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('DB_HOST:', os.getenv('DB_HOST'))
print('DB_USER:', os.getenv('DB_USER'))
"

# 2. 测试数据库连接
python -c "
from dotenv import load_dotenv
import pymysql
import os
load_dotenv()
try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    print('数据库连接成功')
    conn.close()
except Exception as e:
    print('连接失败:', e)
"
```

### Q6: config.yaml文件格式错误怎么办？

**A**: YAML格式要求严格：

```yaml
# 正确格式（注意缩进）
database:
  host: localhost
  port: 3306
  
crawler:
  interval: 2
  timeout: 30

# 错误格式
database:
host: localhost  # 缺少缩进
port:3306        # 缺少空格
```

验证YAML格式：

```bash
python -c "
import yaml
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    print('配置文件格式正确')
    print(config)
"
```

## 🕷️ 爬取相关问题

### Q7: 爬取时出现403/429错误怎么办？

**A**: 这通常是反爬虫机制触发：

```bash
# 1. 增加请求间隔
python crawler_main.py --interval 5 --start-page 1 --end-page 10

# 2. 检查Cookie是否有效
python account_manager.py health-check

# 3. 更换账号
python account_manager.py add --name "新账号" --cookies "new_cookie"

# 4. 使用代理（如果配置了）
python account_manager.py update --name "账号1" --proxy "http://proxy:8080"
```

### Q8: 爬取的数据不完整怎么办？

**A**: 检查以下几个方面：

```bash
# 1. 查看日志文件
tail -f logs/crawler.log

# 2. 使用测试模式验证
python crawler_main.py --test-mode --verbose

# 3. 检查网络连接
curl -I "https://www.xiaohongshu.com"

# 4. 验证Cookie有效性
# 在浏览器中访问目标页面，确认Cookie未过期
```

### Q9: 如何处理爬取中断？

**A**: 使用断点续爬功能：

```bash
# 1. 查看中断的任务ID
python task_scheduler.py list

# 2. 续爬指定任务
python crawler_main.py --resume --task-id 12345

# 3. 如果没有任务ID，从指定页面开始
python crawler_main.py --start-page 150 --end-page 500
```

### Q10: 爬取速度太慢怎么办？

**A**: 优化爬取性能：

```bash
# 1. 减少请求间隔（注意不要太激进）
python crawler_main.py --interval 1.5

# 2. 增加并发数（修改config.yaml）
crawler:
  concurrent_requests: 3

# 3. 使用多个账号并行
python account_manager.py add --name "账号2" --cookies "cookie2"
python account_manager.py add --name "账号3" --cookies "cookie3"
```

## 🗄️ 数据库相关问题

### Q11: 数据库连接池耗尽怎么办？

**A**: 优化连接池配置：

```yaml
# 在config.yaml中调整
database:
  pool_size: 20
  pool_recycle: 3600
  pool_timeout: 30
```

或者重启MySQL服务：

```bash
# Linux
sudo systemctl restart mysql

# Windows
net stop mysql
net start mysql
```

### Q12: 数据导入时出现编码错误怎么办？

**A**: 确保编码一致：

```bash
# 1. 检查CSV文件编码
file -i data/daoren_data.csv

# 2. 转换编码（如果需要）
iconv -f gbk -t utf-8 data/daoren_data.csv > data/daoren_data_utf8.csv

# 3. 指定编码导入
python import_to_mysql.py --file data/daoren_data.csv --encoding utf-8
```

### Q13: 数据库表损坏怎么办？

**A**: 修复数据库表：

```sql
-- 检查表状态
CHECK TABLE daoren_data;

-- 修复表
REPAIR TABLE daoren_data;

-- 如果修复失败，重建表
CREATE TABLE daoren_data_backup AS SELECT * FROM daoren_data;
DROP TABLE daoren_data;
-- 重新运行init_db.sql创建表结构
INSERT INTO daoren_data SELECT * FROM daoren_data_backup;
```

### Q14: 如何处理重复数据？

**A**: 清理重复数据：

```sql
-- 查找重复数据
SELECT daoren_id, COUNT(*) as count 
FROM daoren_data 
GROUP BY daoren_id 
HAVING count > 1;

-- 删除重复数据（保留最新的）
DELETE d1 FROM daoren_data d1
INNER JOIN daoren_data d2 
WHERE d1.id < d2.id AND d1.daoren_id = d2.daoren_id;

-- 添加唯一索引防止重复
ALTER TABLE daoren_data ADD UNIQUE INDEX idx_unique_daoren_id (daoren_id);
```

## 👤 账号管理问题

### Q15: 账号被封怎么办？

**A**: 处理被封账号：

```bash
# 1. 禁用被封账号
python account_manager.py disable --name "被封账号"

# 2. 添加新账号
python account_manager.py add --name "新账号" --cookies "new_cookie"

# 3. 检查所有账号状态
python account_manager.py health-check

# 4. 调整爬取策略
# 增加请求间隔，减少并发数
```

### Q16: 如何批量管理账号？

**A**: 使用批量操作：

```bash
# 1. 导出现有账号
python account_manager.py export --file backup_accounts.json

# 2. 编辑accounts.json文件添加新账号
# 3. 批量导入
python account_manager.py import --file accounts.json

# 4. 批量健康检查
python account_manager.py health-check
```

### Q17: Cookie过期怎么办？

**A**: 更新Cookie：

```bash
# 1. 从浏览器获取新Cookie
# 打开开发者工具 -> Network -> 找到请求 -> 复制Cookie

# 2. 更新账号Cookie
python account_manager.py update --name "账号1" --cookies "new_cookie_string"

# 3. 验证更新
python account_manager.py show --name "账号1"
```

## 🚀 性能相关问题

### Q18: 系统内存使用过高怎么办？

**A**: 优化内存使用：

```bash
# 1. 减少批量处理大小
python import_to_mysql.py --batch-size 100

# 2. 调整并发数
# 编辑config.yaml
crawler:
  concurrent_requests: 1

# 3. 清理临时文件
find data/ -name "*.tmp" -delete

# 4. 重启服务
python task_scheduler.py stop
python task_scheduler.py start
```

### Q19: 磁盘空间不足怎么办？

**A**: 清理磁盘空间：

```bash
# 1. 清理日志文件
find logs/ -name "*.log" -mtime +7 -delete

# 2. 压缩旧数据文件
gzip data/*.csv

# 3. 清理数据库日志
mysql -u root -p -e "PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 7 DAY);"

# 4. 清理系统临时文件
# Windows
del /q /s %TEMP%\*

# Linux
sudo apt-get clean
```

### Q20: 数据库查询慢怎么办？

**A**: 优化数据库性能：

```sql
-- 1. 添加索引
ALTER TABLE daoren_data ADD INDEX idx_fans_count (fans_count);
ALTER TABLE daoren_data ADD INDEX idx_created_at (created_at);

-- 2. 分析表
ANALYZE TABLE daoren_data;

-- 3. 优化表
OPTIMIZE TABLE daoren_data;

-- 4. 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
```

## ❌ 错误处理问题

### Q21: 如何查看详细错误信息？

**A**: 启用详细日志：

```bash
# 1. 使用verbose模式
python crawler_main.py --verbose

# 2. 查看错误日志
tail -f logs/error.log

# 3. 查看特定时间的日志
grep "2024-01-01 12:00" logs/crawler.log

# 4. 统计错误类型
grep "ERROR" logs/crawler.log | cut -d' ' -f4- | sort | uniq -c
```

### Q22: 程序崩溃怎么办？

**A**: 诊断和恢复：

```bash
# 1. 查看崩溃日志
tail -n 100 logs/error.log

# 2. 检查系统资源
top
df -h

# 3. 重启服务
python task_scheduler.py stop
python task_scheduler.py start

# 4. 如果是数据库问题
sudo systemctl restart mysql
```

### Q23: 网络连接错误怎么办？

**A**: 检查网络连接：

```bash
# 1. 测试网络连接
ping www.xiaohongshu.com
curl -I https://www.xiaohongshu.com

# 2. 检查DNS解析
nslookup www.xiaohongshu.com

# 3. 使用代理（如果需要）
export http_proxy=http://proxy:8080
export https_proxy=http://proxy:8080

# 4. 检查防火墙设置
```

## 🚀 部署相关问题

### Q24: 如何在生产环境部署？

**A**: 生产环境部署步骤：

```bash
# 1. 创建专用用户
sudo useradd -m -s /bin/bash crawler

# 2. 安装到系统目录
sudo cp -r . /opt/daoren-crawler
sudo chown -R crawler:crawler /opt/daoren-crawler

# 3. 创建系统服务
sudo cp scripts/daoren-scheduler.service /etc/systemd/system/
sudo systemctl enable daoren-scheduler
sudo systemctl start daoren-scheduler

# 4. 配置日志轮转
sudo cp scripts/logrotate.conf /etc/logrotate.d/daoren-crawler
```

### Q25: 如何设置开机自启动？

**A**: 配置自启动服务：

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/daoren-scheduler.service

# 2. 服务文件内容
[Unit]
Description=Daoren Crawler Scheduler
After=network.target mysql.service

[Service]
Type=simple
User=crawler
WorkingDirectory=/opt/daoren-crawler
ExecStart=/opt/daoren-crawler/venv/bin/python task_scheduler.py start
Restart=always

[Install]
WantedBy=multi-user.target

# 3. 启用服务
sudo systemctl enable daoren-scheduler
sudo systemctl start daoren-scheduler
```

### Q26: 如何监控系统运行状态？

**A**: 设置监控：

```bash
# 1. 查看服务状态
sudo systemctl status daoren-scheduler

# 2. 查看实时日志
sudo journalctl -u daoren-scheduler -f

# 3. 设置邮件报警
# 编辑config.yaml
monitoring:
  alerts:
    enabled: true
    email:
      smtp_server: "smtp.gmail.com"
      recipients: ["admin@example.com"]

# 4. 使用监控脚本
nohup python scripts/monitor.py &
```

## 🔧 其他常见问题

### Q27: 如何备份和恢复数据？

**A**: 数据备份恢复：

```bash
# 备份
mysqldump -u crawler_user -p influencer_crawler > backup.sql
tar -czf data_backup.tar.gz data/

# 恢复
mysql -u crawler_user -p influencer_crawler < backup.sql
tar -xzf data_backup.tar.gz
```

### Q28: 如何升级系统？

**A**: 系统升级步骤：

```bash
# 1. 备份数据
make backup

# 2. 停止服务
python task_scheduler.py stop

# 3. 更新代码
git pull origin main

# 4. 更新依赖
pip install -r requirements.txt --upgrade

# 5. 运行数据库迁移（如果有）
python scripts/migrate.py

# 6. 重启服务
python task_scheduler.py start
```

### Q29: 如何获取技术支持？

**A**: 获取帮助的方式：

1. **查看文档**：README.md, INSTALL.md, USAGE.md
2. **检查日志**：logs/ 目录下的日志文件
3. **运行诊断**：`make check-env`
4. **社区支持**：GitHub Issues
5. **联系开发者**：通过邮件或即时通讯工具

### Q30: 如何贡献代码？

**A**: 参与项目开发：

```bash
# 1. Fork项目
git clone your-fork-url

# 2. 创建功能分支
git checkout -b feature/new-feature

# 3. 提交更改
git commit -m "Add new feature"

# 4. 推送分支
git push origin feature/new-feature

# 5. 创建Pull Request
```

## 📞 联系我们

如果以上FAQ没有解决您的问题，请通过以下方式联系我们：

- **GitHub Issues**: 提交bug报告或功能请求
- **邮件支持**: support@example.com
- **技术文档**: 查看完整的技术文档
- **社区讨论**: 加入用户交流群

---

本FAQ会持续更新，如果您遇到新的问题或有好的解决方案，欢迎贡献到这个文档中。