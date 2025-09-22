# 达人数据爬取与管理系统

一个功能完整的达人数据爬取与管理系统，支持多平台达人数据采集、智能分类、多账号管理、任务调度等功能。

## 🚀 功能特性

### 核心功能
- **智能爬取**: 支持多页面并发爬取，自动处理反爬机制
- **数据分类**: 基于内容标签自动分类达人类型（美食、时尚、旅游等）
- **断点续爬**: 支持爬取进度保存，意外中断后可继续爬取
- **多账号管理**: 智能账号轮换，避免单账号频繁请求被封
- **任务调度**: 支持定时任务、任务队列、失败重试机制
- **数据入库**: 自动将爬取数据导入MySQL数据库
- **监控报警**: 实时监控爬取状态，异常情况及时报警

### 技术特点
- **高性能**: 多线程并发处理，支持大规模数据爬取
- **高可靠**: 完善的错误处理和重试机制
- **易扩展**: 模块化设计，支持自定义扩展
- **易部署**: 支持Docker部署，一键启动

## 📋 系统要求

- Python 3.8+
- MySQL 5.7+
- 内存: 建议2GB+
- 磁盘: 建议10GB+可用空间

## 🛠️ 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd 达人数据爬取与管理系统

# 安装依赖
pip install -r requirements.txt

# 或使用Makefile
make install
```

### 2. 配置数据库

```bash
# 生成配置文件
make generate-config

# 编辑.env文件，配置数据库连接信息
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=influencer_crawler

# 初始化数据库
make setup-db
```

### 3. 配置账号信息

```bash
# 添加爬取账号
python account_manager.py add --name "账号1" --cookies "your_cookies_here"

# 查看账号列表
python account_manager.py list
```

### 4. 开始爬取

```bash
# 方式1: 直接运行爬虫
python crawler_main.py --start-page 1 --end-page 10

# 方式2: 使用任务调度器
python task_scheduler.py start

# 方式3: 使用Makefile
make run-crawler
```

## 📖 详细使用指南

### 爬虫使用

#### 基本爬取
```bash
# 爬取指定页面范围
python crawler_main.py --start-page 1 --end-page 100

# 指定达人类型
python crawler_main.py --types 美食博主 时尚博主

# 使用指定账号
python crawler_main.py --account-id 1

# 设置并发数
python crawler_main.py --concurrent 5
```

#### 高级选项
```bash
# 启用断点续爬
python crawler_main.py --resume

# 设置请求间隔
python crawler_main.py --interval 3

# 指定输出目录
python crawler_main.py --output-dir ./data/custom
```

### 账号管理

#### 添加账号
```bash
# 基本添加
python account_manager.py add --name "测试账号" --cookies "cookie_string"

# 添加带请求头的账号
python account_manager.py add --name "账号2" --cookies "cookies" --headers '{"User-Agent": "custom"}'

# 批量导入账号
python account_manager.py import --file accounts.json
```

#### 账号维护
```bash
# 查看账号状态
python account_manager.py list --status active

# 账号统计信息
python account_manager.py stats

# 健康检查
python account_manager.py health-check

# 更新账号信息
python account_manager.py update --id 1 --status inactive
```

### 任务调度

#### 创建任务
```bash
# 创建爬取任务
python task_scheduler.py create --type crawl_daoren --name "每日爬取" \
  --params '{"start_page": 1, "end_page": 50}'

# 创建定时任务
python task_scheduler.py create --type crawl_daoren --name "定时爬取" \
  --schedule "2025-01-24 02:00:00"

# 创建数据导入任务
python task_scheduler.py create --type import_data --name "数据导入" \
  --params '{"csv_file": "data/daoren_data.csv"}'
```

#### 任务管理
```bash
# 查看任务列表
python task_scheduler.py list

# 查看任务统计
python task_scheduler.py stats

# 取消任务
python task_scheduler.py cancel --id 123

# 重试失败任务
python task_scheduler.py retry --id 123
```

### 数据导入

#### CSV导入MySQL
```bash
# 基本导入
python import_to_mysql.py --file data/daoren_data.csv

# 指定批次大小
python import_to_mysql.py --file data/daoren_data.csv --batch-size 500

# 跳过重复数据
python import_to_mysql.py --file data/daoren_data.csv --skip-duplicates
```

## 🗂️ 项目结构

```
达人数据爬取与管理系统/
├── crawler_main.py          # 主爬虫脚本
├── import_to_mysql.py       # 数据导入脚本
├── account_manager.py       # 账号管理脚本
├── task_scheduler.py        # 任务调度脚本
├── init_db.sql             # 数据库初始化脚本
├── requirements.txt        # Python依赖
├── config.yaml            # 配置文件
├── setup.py              # 安装配置
├── Makefile             # 项目管理命令
├── .env                # 环境变量配置
├── README.md          # 项目说明
├── data/             # 数据存储目录
│   ├── 美食博主/
│   ├── 时尚博主/
│   └── ...
├── logs/            # 日志文件目录
├── backup/         # 数据备份目录
└── scripts/       # 辅助脚本目录
```

## 🔧 配置说明

### 环境变量配置 (.env)

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
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

### 高级配置 (config.yaml)

详细配置选项请参考 `config.yaml` 文件，包括：
- 数据库连接池配置
- 爬虫请求参数
- 账号轮换策略
- 任务调度规则
- 日志输出配置
- 监控报警设置

## 📊 数据库结构

### 核心表结构

1. **daoren_types** - 达人类型表
2. **daoren_data** - 达人数据主表
3. **daoren_task_log** - 任务日志表
4. **daoren_account** - 账号管理表
5. **crawl_history** - 爬取历史记录表
6. **data_export_log** - 数据导出记录表

### 数据视图

1. **v_daoren_stats_by_type** - 按类型统计达人数据
2. **v_task_execution_stats** - 任务执行统计

详细表结构请参考 `init_db.sql` 文件。

## 🚀 部署指南

### 开发环境部署

```bash
# 1. 安装依赖
make install-dev

# 2. 配置环境
make generate-config
# 编辑.env文件

# 3. 初始化数据库
make setup-db

# 4. 运行测试
make test

# 5. 启动服务
make run-scheduler
```

### 生产环境部署

```bash
# 1. 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 2. 安装生产依赖
pip install -r requirements.txt

# 3. 配置生产环境变量
cp .env.example .env
# 编辑.env文件

# 4. 初始化数据库
make setup-db

# 5. 安装系统服务 (Linux)
make install-service

# 6. 启动服务
sudo systemctl start daoren-scheduler
```

### Docker部署

```bash
# 构建镜像
docker build -t daoren-crawler .

# 运行容器
docker run -d --name daoren-crawler \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  daoren-crawler
```

## 📈 监控和维护

### 日常监控

```bash
# 查看系统状态
make task-stats
make list-accounts

# 查看日志
tail -f logs/crawler_main_$(date +%Y%m%d).log
tail -f logs/task_scheduler_$(date +%Y%m%d).log

# 健康检查
make health-check
```

### 数据备份

```bash
# 备份数据库
make backup

# 备份配置文件
cp .env .env.backup
cp config.yaml config.yaml.backup
```

### 性能优化

1. **数据库优化**
   - 定期清理历史日志
   - 优化索引结构
   - 调整连接池大小

2. **爬虫优化**
   - 调整并发数量
   - 优化请求间隔
   - 使用代理池

3. **系统优化**
   - 监控内存使用
   - 清理临时文件
   - 日志轮转

## 🔍 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查数据库配置
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(f'DB: {os.getenv(\"DB_HOST\")}:{os.getenv(\"DB_PORT\")}')"
   
   # 测试连接
   mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD
   ```

2. **账号被封禁**
   ```bash
   # 查看账号状态
   python account_manager.py list
   
   # 更新账号状态
   python account_manager.py update --id 1 --status active
   ```

3. **任务执行失败**
   ```bash
   # 查看任务详情
   python task_scheduler.py list --status failed
   
   # 重试失败任务
   python task_scheduler.py retry --id 123
   ```

4. **内存不足**
   ```bash
   # 减少并发数
   export MAX_WORKER_THREADS=1
   
   # 清理临时文件
   make clean
   ```

### 日志分析

```bash
# 查看错误日志
grep "ERROR" logs/*.log

# 查看爬取统计
grep "爬取完成" logs/crawler_main_*.log | wc -l

# 查看账号使用情况
grep "账号轮换" logs/*.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如果您在使用过程中遇到问题，可以通过以下方式获取帮助：

1. 查看文档和FAQ
2. 提交Issue
3. 联系开发者

## 🔄 更新日志

### v1.0.0 (2025-01-23)
- ✨ 初始版本发布
- 🚀 支持基本爬取功能
- 📊 支持数据分类和入库
- 👥 支持多账号管理
- ⏰ 支持任务调度
- 📝 完善的日志系统
- 🛠️ 丰富的配置选项

---

**注意**: 请确保遵守相关网站的robots.txt和使用条款，合理使用爬虫功能。