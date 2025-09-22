# 达人数据爬取与管理系统 - 手动安装命令

本文档提供达人数据爬取与管理系统的手动安装命令，包含conda环境初始化和pip包安装。

## 📋 前置要求

- 已安装 Anaconda 或 Miniconda
- 已安装 MySQL 5.7+ 
- Python 3.8+ 支持

## 🔧 手动安装命令

### 1. 创建并激活conda环境

```bash
# 创建新的conda环境（Python 3.9）
conda create -n daoren_crawler python=3.9 -y

# 激活环境
conda activate daoren_crawler

# 验证Python版本
python --version
```

### 2. 升级pip和安装基础工具

```bash
# 升级pip到最新版本
python -m pip install --upgrade pip

# 安装setuptools和wheel
pip install --upgrade setuptools wheel
```

### 3. 安装核心依赖包

```bash
# 网络请求相关
pip install requests==2.31.0
pip install urllib3==2.0.7

# 数据库连接
pip install pymysql==1.1.0
pip install sqlalchemy==2.0.23

# 数据处理
pip install pandas==2.1.4
pip install numpy==1.24.4

# 配置文件处理
pip install python-dotenv==1.0.0
pip install pyyaml==6.0.1

# 任务调度
pip install schedule==1.2.0
pip install apscheduler==3.10.4

# 日志处理
pip install colorlog==6.8.0

# 命令行工具
pip install click==8.1.7
pip install rich==13.7.0
pip install tqdm==4.66.1

# JSON处理增强
pip install ujson==5.9.0

# 时间处理
pip install python-dateutil==2.8.2

# 数据验证
pip install cerberus==1.3.5

# 系统监控
pip install psutil==5.9.6
```

### 4. 安装开发和测试工具（可选）

```bash
# 代码格式化
pip install black==23.12.0
pip install isort==5.13.2

# 代码检查
pip install flake8==6.1.0
pip install pylint==3.0.3

# 测试框架
pip install pytest==7.4.3
pip install pytest-cov==4.1.0

# 类型检查
pip install mypy==1.8.0
```

### 5. 验证安装

```bash
# 验证核心包安装
python -c "import requests, pymysql, pandas, yaml; print('核心依赖安装成功')"

# 验证数据库连接包
python -c "import pymysql; print('数据库连接包安装成功')"

# 验证任务调度包
python -c "import schedule, apscheduler; print('任务调度包安装成功')"

# 查看已安装包列表
pip list
```

### 6. 配置环境变量

```bash
# 创建.env配置文件
echo "# 数据库配置" > .env
echo "DB_HOST=localhost" >> .env
echo "DB_PORT=3306" >> .env
echo "DB_USER=crawler_user" >> .env
echo "DB_PASSWORD=your_password" >> .env
echo "DB_NAME=influencer_crawler" >> .env
echo "" >> .env
echo "# 日志配置" >> .env
echo "LOG_LEVEL=INFO" >> .env
echo "LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s" >> .env
```

### 7. 初始化数据库

```bash
# 连接MySQL并创建数据库
mysql -u root -p -e "CREATE DATABASE influencer_crawler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 创建用户并授权
mysql -u root -p -e "CREATE USER 'crawler_user'@'localhost' IDENTIFIED BY 'your_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON influencer_crawler.* TO 'crawler_user'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"

# 导入数据库结构
mysql -u crawler_user -p influencer_crawler < init_db.sql
```

### 8. 测试系统功能

```bash
# 测试数据库连接
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
    print('数据库连接测试成功')
    conn.close()
except Exception as e:
    print(f'数据库连接失败: {e}')
"

# 测试账号管理功能
python account_manager.py --help

# 测试任务调度功能
python task_scheduler.py --help

# 测试爬虫功能
python crawler_main.py --help
```

### 9. 添加第一个爬取账号

```bash
# 添加爬取账号（需要替换为真实的cookie）
python account_manager.py add --name "主账号" --cookies "your_cookie_string_here" --notes "主要爬取账号"

# 查看账号列表
python account_manager.py list

# 检查账号状态
python account_manager.py stats
```

### 10. 运行第一次爬取测试

```bash
# 测试模式爬取（只爬取少量数据）
python crawler_main.py --test-mode --start-page 1 --end-page 2

# 查看爬取结果
ls -la data/

# 导入数据到数据库（如果有数据文件）
python import_to_mysql.py --file data/daoren_data_*.csv
```

## 🔄 日常使用命令

### 启动任务调度器

```bash
# 激活环境
conda activate daoren_crawler

# 启动调度器
python task_scheduler.py start
```

### 执行爬取任务

```bash
# 爬取指定页面范围
python crawler_main.py --start-page 1 --end-page 100

# 使用指定账号爬取
python crawler_main.py --account "主账号" --start-page 1 --end-page 50

# 断点续爬
python crawler_main.py --resume --task-id 12345
```

### 管理账号

```bash
# 查看所有账号
python account_manager.py list

# 添加新账号
python account_manager.py add --name "账号2" --cookies "cookie_string"

# 更新账号cookie
python account_manager.py update --name "主账号" --cookies "new_cookie"

# 健康检查
python account_manager.py health-check
```

### 数据管理

```bash
# 导入CSV数据到数据库
python import_to_mysql.py --file data/daoren_data.csv

# 批量导入目录下所有CSV
python import_to_mysql.py --directory data/

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
print(f'总达人数量: {cursor.fetchone()[0]}')
conn.close()
"
```

## 🛠️ 故障排除命令

### 环境问题

```bash
# 重新创建环境
conda deactivate
conda remove -n daoren_crawler --all -y
conda create -n daoren_crawler python=3.9 -y
conda activate daoren_crawler

# 清理pip缓存
pip cache purge

# 重新安装依赖
pip install -r requirements.txt
```

### 数据库问题

```bash
# 检查MySQL服务状态
# Windows
net start mysql

# 重置数据库
mysql -u root -p -e "DROP DATABASE IF EXISTS influencer_crawler;"
mysql -u root -p -e "CREATE DATABASE influencer_crawler CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u crawler_user -p influencer_crawler < init_db.sql
```

### 权限问题

```bash
# 创建必要目录
mkdir -p data logs backup

# 设置目录权限（Linux/macOS）
chmod 755 data logs backup
chmod 644 *.py *.sql *.md *.yaml *.txt
```

## 📝 注意事项

1. **Cookie获取**: 需要从浏览器开发者工具中获取有效的Cookie字符串
2. **数据库密码**: 请使用强密码并妥善保管
3. **请求频率**: 建议设置合理的请求间隔，避免被反爬虫机制封禁
4. **数据备份**: 定期备份重要数据和配置文件
5. **环境隔离**: 建议使用conda虚拟环境避免包冲突

## 🔗 相关文档

- [README.md](README.md) - 项目介绍
- [INSTALL.md](INSTALL.md) - 详细安装指南
- [USAGE.md](USAGE.md) - 使用说明
- [FAQ.md](FAQ.md) - 常见问题解答

---

如有问题，请参考FAQ文档或联系技术支持。