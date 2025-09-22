# 达人数据爬取与管理系统 - 安装指南

本文档提供详细的安装和配置指南，帮助您快速部署达人数据爬取与管理系统。

## 📋 系统要求

### 最低要求
- **操作系统**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **MySQL**: 5.7 或更高版本
- **内存**: 2GB RAM
- **磁盘空间**: 10GB 可用空间

### 推荐配置
- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 8
- **Python**: 3.9+
- **MySQL**: 8.0+
- **内存**: 4GB+ RAM
- **磁盘空间**: 50GB+ 可用空间
- **网络**: 稳定的互联网连接

## 🚀 快速安装

### 方法一：使用Makefile（推荐）

```bash
# 1. 下载项目
git clone <repository-url>
cd 达人数据爬取与管理系统

# 2. 一键安装
make full-setup

# 3. 编辑配置文件
nano .env

# 4. 启动系统
make run-scheduler
```

### 方法二：手动安装

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 配置数据库
# 参考下面的详细步骤

# 3. 初始化数据库
python -c "exec(open('init_db.sql').read())"

# 4. 配置环境变量
cp .env.example .env
```

## 🔧 详细安装步骤

### 步骤1：环境准备

#### 1.1 安装Python

**Windows:**
```bash
# 下载并安装Python 3.9+
# https://www.python.org/downloads/windows/

# 验证安装
python --version
pip --version
```

**macOS:**
```bash
# 使用Homebrew安装
brew install python@3.9

# 或下载官方安装包
# https://www.python.org/downloads/mac-osx/
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv
```

**CentOS/RHEL:**
```bash
sudo yum install python39 python39-pip
```

#### 1.2 安装MySQL

**Windows:**
```bash
# 下载MySQL Installer
# https://dev.mysql.com/downloads/installer/

# 或使用Chocolatey
choco install mysql
```

**macOS:**
```bash
# 使用Homebrew
brew install mysql

# 启动MySQL服务
brew services start mysql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server mysql-client

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql
```

**CentOS/RHEL:**
```bash
sudo yum install mysql-server mysql

# 启动MySQL服务
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

#### 1.3 配置MySQL

```bash
# 安全配置
sudo mysql_secure_installation

# 创建数据库用户
mysql -u root -p
```

```sql
-- 创建数据库
CREATE DATABASE influencer_crawler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'crawler_user'@'localhost' IDENTIFIED BY 'your_strong_password';

-- 授权
GRANT ALL PRIVILEGES ON influencer_crawler.* TO 'crawler_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

### 步骤2：项目安装

#### 2.1 获取项目代码

```bash
# 方法1：Git克隆
git clone <repository-url>
cd 达人数据爬取与管理系统

# 方法2：下载压缩包
# 下载并解压到目标目录
```

#### 2.2 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 2.3 安装Python依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -e .[dev]

# 验证安装
python -c "import requests, pymysql, pandas; print('依赖安装成功')"
```

### 步骤3：配置系统

#### 3.1 创建配置文件

```bash
# 生成.env配置文件
make generate-config

# 或手动创建
cp .env.example .env
```

#### 3.2 编辑配置文件

编辑 `.env` 文件：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=crawler_user
DB_PASSWORD=your_strong_password
DB_NAME=influencer_crawler

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# 爬虫配置
REQUEST_TIMEOUT=30
MAX_RETRIES=3
REQUEST_INTERVAL=2

# 账号管理配置
ACCOUNT_ROTATION_INTERVAL=1800
ACCOUNT_COOLDOWN_PERIOD=300

# 任务调度配置
MAX_WORKER_THREADS=3
```

#### 3.3 初始化数据库

```bash
# 方法1：使用Makefile
make setup-db

# 方法2：手动执行
mysql -h localhost -u crawler_user -p influencer_crawler < init_db.sql
```

#### 3.4 验证数据库

```bash
# 连接数据库
mysql -h localhost -u crawler_user -p influencer_crawler

# 查看表结构
SHOW TABLES;
DESCRIBE daoren_data;
```

### 步骤4：配置账号

#### 4.1 添加爬取账号

```bash
# 添加第一个账号
python account_manager.py add \
  --name "主账号" \
  --cookies "your_cookie_string_here" \
  --notes "主要爬取账号"

# 验证账号
python account_manager.py list
```

#### 4.2 批量导入账号（可选）

创建 `accounts.json` 文件：

```json
[
  {
    "account_name": "账号1",
    "cookies": "cookie_string_1",
    "headers": "{\"User-Agent\": \"Mozilla/5.0...\"}",
    "notes": "备用账号1"
  },
  {
    "account_name": "账号2",
    "cookies": "cookie_string_2",
    "notes": "备用账号2"
  }
]
```

导入账号：

```bash
python account_manager.py import --file accounts.json
```

### 步骤5：测试安装

#### 5.1 环境检查

```bash
# 使用Makefile检查
make check-env

# 手动检查
python --version
mysql --version
python -c "import requests, pymysql, pandas; print('环境检查通过')"
```

#### 5.2 功能测试

```bash
# 测试数据库连接
python -c "
from dotenv import load_dotenv
import pymysql
import os
load_dotenv()
conn = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT')),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)
print('数据库连接成功')
conn.close()
"

# 测试账号管理
python account_manager.py stats

# 测试任务调度
python task_scheduler.py stats
```

#### 5.3 小规模爬取测试

```bash
# 测试爬取1页数据
python crawler_main.py --start-page 1 --end-page 1 --test-mode

# 检查输出文件
ls -la data/
```

## 🐳 Docker安装

### 使用Docker Compose（推荐）

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: influencer_crawler
      MYSQL_USER: crawler_user
      MYSQL_PASSWORD: user_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql

  crawler:
    build: .
    depends_on:
      - mysql
    environment:
      DB_HOST: mysql
      DB_USER: crawler_user
      DB_PASSWORD: user_password
      DB_NAME: influencer_crawler
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env

volumes:
  mysql_data:
```

启动服务：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec crawler bash
```

### 使用单独的Docker容器

```bash
# 构建镜像
docker build -t daoren-crawler .

# 运行MySQL容器
docker run -d --name mysql-crawler \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=influencer_crawler \
  -e MYSQL_USER=crawler_user \
  -e MYSQL_PASSWORD=user_password \
  -p 3306:3306 \
  mysql:8.0

# 运行爬虫容器
docker run -d --name daoren-crawler \
  --link mysql-crawler:mysql \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/.env:/app/.env \
  daoren-crawler
```

## 🔧 高级配置

### 性能优化配置

编辑 `config.yaml`：

```yaml
# 数据库连接池
database:
  pool_size: 20
  pool_recycle: 3600

# 爬虫并发配置
crawler:
  concurrent_requests: 5
  request_interval: 1

# 任务调度配置
scheduler:
  workers:
    max_workers: 5
```

### 监控配置

```yaml
# 监控配置
monitoring:
  performance:
    enabled: true
    metrics_interval: 300
  
  alerts:
    enabled: true
    email:
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your_email@gmail.com"
      password: "your_app_password"
      recipients: ["admin@example.com"]
```

### 安全配置

```yaml
# 安全配置
security:
  access_control:
    ip_whitelist: ["127.0.0.1", "192.168.1.0/24"]
    rate_limiting:
      enabled: true
      requests_per_minute: 60
```

## 🚀 生产环境部署

### 系统服务配置

创建系统服务文件 `/etc/systemd/system/daoren-scheduler.service`：

```ini
[Unit]
Description=Daoren Crawler Scheduler
After=network.target mysql.service

[Service]
Type=simple
User=crawler
Group=crawler
WorkingDirectory=/opt/daoren-crawler
Environment=PATH=/opt/daoren-crawler/venv/bin
ExecStart=/opt/daoren-crawler/venv/bin/python task_scheduler.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable daoren-scheduler

# 启动服务
sudo systemctl start daoren-scheduler

# 查看状态
sudo systemctl status daoren-scheduler
```

### Nginx反向代理（可选）

如果启用了Web界面，配置Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 日志轮转配置

创建 `/etc/logrotate.d/daoren-crawler`：

```
/opt/daoren-crawler/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 crawler crawler
    postrotate
        systemctl reload daoren-scheduler
    endscript
}
```

## 🔍 故障排除

### 常见安装问题

#### 1. Python依赖安装失败

```bash
# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 单独安装问题包
pip install pymysql --no-cache-dir
```

#### 2. MySQL连接问题

```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 检查端口监听
netstat -tlnp | grep 3306

# 测试连接
mysql -h localhost -u root -p

# 检查用户权限
mysql -u root -p -e "SELECT User, Host FROM mysql.user;"
```

#### 3. 权限问题

```bash
# 创建专用用户
sudo useradd -m -s /bin/bash crawler

# 设置目录权限
sudo chown -R crawler:crawler /opt/daoren-crawler
sudo chmod -R 755 /opt/daoren-crawler
```

#### 4. 防火墙问题

```bash
# Ubuntu/Debian
sudo ufw allow 3306/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --reload
```

### 安装验证清单

- [ ] Python 3.8+ 已安装
- [ ] MySQL 5.7+ 已安装并运行
- [ ] 项目依赖已安装
- [ ] 数据库已创建并初始化
- [ ] 配置文件已正确设置
- [ ] 至少一个账号已添加
- [ ] 基本功能测试通过
- [ ] 日志文件正常生成
- [ ] 系统服务已配置（生产环境）

## 📞 获取帮助

如果在安装过程中遇到问题：

1. 查看日志文件：`logs/` 目录下的相关日志
2. 检查配置文件：确保 `.env` 和 `config.yaml` 配置正确
3. 运行诊断命令：`make check-env`
4. 查看FAQ文档
5. 提交Issue或联系技术支持

---

安装完成后，请参考 [README.md](README.md) 了解详细的使用方法。