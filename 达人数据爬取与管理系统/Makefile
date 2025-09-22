# 达人数据爬取与管理系统 - Makefile
# 创建时间: 2025-01-23

.PHONY: help install install-dev setup-db test lint format clean run-crawler run-scheduler backup

# 默认目标
help:
	@echo "达人数据爬取与管理系统 - 可用命令:"
	@echo ""
	@echo "安装和设置:"
	@echo "  install      - 安装项目依赖"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  setup-db     - 初始化数据库"
	@echo ""
	@echo "开发工具:"
	@echo "  test         - 运行测试"
	@echo "  lint         - 代码检查"
	@echo "  format       - 代码格式化"
	@echo "  clean        - 清理临时文件"
	@echo ""
	@echo "运行服务:"
	@echo "  run-crawler  - 运行爬虫"
	@echo "  run-scheduler - 运行任务调度器"
	@echo ""
	@echo "数据管理:"
	@echo "  backup       - 备份数据"
	@echo "  import-data  - 导入数据"
	@echo ""
	@echo "账号管理:"
	@echo "  list-accounts - 列出所有账号"
	@echo "  health-check  - 账号健康检查"

# 安装项目依赖
install:
	@echo "安装项目依赖..."
	pip install -r requirements.txt

# 安装开发依赖
install-dev:
	@echo "安装开发依赖..."
	pip install -r requirements.txt
	pip install -e .[dev]

# 初始化数据库
setup-db:
	@echo "初始化数据库..."
	@if [ -f .env ]; then \
		python -c "import os; from dotenv import load_dotenv; load_dotenv(); \
		import pymysql; \
		conn = pymysql.connect(host=os.getenv('DB_HOST', 'localhost'), \
		port=int(os.getenv('DB_PORT', 3306)), \
		user=os.getenv('DB_USER', 'root'), \
		password=os.getenv('DB_PASSWORD', '')); \
		cursor = conn.cursor(); \
		cursor.execute('CREATE DATABASE IF NOT EXISTS ' + os.getenv('DB_NAME', 'influencer_crawler') + ' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci'); \
		conn.close(); \
		print('数据库创建成功')"; \
		mysql -h$$(grep DB_HOST .env | cut -d '=' -f2) \
		      -P$$(grep DB_PORT .env | cut -d '=' -f2) \
		      -u$$(grep DB_USER .env | cut -d '=' -f2) \
		      -p$$(grep DB_PASSWORD .env | cut -d '=' -f2) \
		      $$(grep DB_NAME .env | cut -d '=' -f2) < init_db.sql; \
		echo "数据库表结构创建成功"; \
	else \
		echo "错误: .env 文件不存在，请先配置数据库连接信息"; \
		exit 1; \
	fi

# 运行测试
test:
	@echo "运行测试..."
	python -m pytest tests/ -v --cov=. --cov-report=html

# 代码检查
lint:
	@echo "代码检查..."
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# 代码格式化
format:
	@echo "代码格式化..."
	black . --line-length=100
	isort . --profile black

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.tmp" -delete
	find . -type f -name "*.temp" -delete
	find . -type f -name "*~" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# 运行爬虫
run-crawler:
	@echo "运行爬虫..."
	python crawler_main.py

# 运行任务调度器
run-scheduler:
	@echo "运行任务调度器..."
	python task_scheduler.py start

# 备份数据
backup:
	@echo "备份数据..."
	@mkdir -p backup
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	if [ -f .env ]; then \
		mysqldump -h$$(grep DB_HOST .env | cut -d '=' -f2) \
		          -P$$(grep DB_PORT .env | cut -d '=' -f2) \
		          -u$$(grep DB_USER .env | cut -d '=' -f2) \
		          -p$$(grep DB_PASSWORD .env | cut -d '=' -f2) \
		          $$(grep DB_NAME .env | cut -d '=' -f2) > backup/backup_$$timestamp.sql; \
		echo "数据库备份完成: backup/backup_$$timestamp.sql"; \
	else \
		echo "错误: .env 文件不存在"; \
		exit 1; \
	fi

# 导入数据
import-data:
	@echo "导入数据..."
	@if [ -z "$(FILE)" ]; then \
		echo "用法: make import-data FILE=path/to/file.csv"; \
		exit 1; \
	fi
	python import_to_mysql.py --file $(FILE)

# 列出所有账号
list-accounts:
	@echo "列出所有账号..."
	python account_manager.py list

# 账号健康检查
health-check:
	@echo "账号健康检查..."
	python account_manager.py health-check

# 查看任务状态
task-stats:
	@echo "查看任务统计..."
	python task_scheduler.py stats

# 创建爬取任务
create-crawl-task:
	@echo "创建爬取任务..."
	@if [ -z "$(PAGES)" ]; then \
		echo "用法: make create-crawl-task PAGES=1-100"; \
		exit 1; \
	fi
	@start_page=$$(echo $(PAGES) | cut -d'-' -f1); \
	end_page=$$(echo $(PAGES) | cut -d'-' -f2); \
	python task_scheduler.py create --type crawl_daoren --name "爬取任务_$(PAGES)" \
		--params "{\"start_page\": $$start_page, \"end_page\": $$end_page}"

# 安装系统服务 (Linux)
install-service:
	@echo "安装系统服务..."
	@if [ "$$(uname)" = "Linux" ]; then \
		sudo cp scripts/daoren-scheduler.service /etc/systemd/system/; \
		sudo systemctl daemon-reload; \
		sudo systemctl enable daoren-scheduler; \
		echo "系统服务安装完成，使用 'sudo systemctl start daoren-scheduler' 启动"; \
	else \
		echo "此功能仅支持Linux系统"; \
	fi

# 生成配置文件模板
generate-config:
	@echo "生成配置文件模板..."
	@if [ ! -f .env ]; then \
		echo "# 达人数据爬取与管理系统 - 环境配置" > .env; \
		echo "# 数据库配置" >> .env; \
		echo "DB_HOST=localhost" >> .env; \
		echo "DB_PORT=3306" >> .env; \
		echo "DB_USER=root" >> .env; \
		echo "DB_PASSWORD=" >> .env; \
		echo "DB_NAME=influencer_crawler" >> .env; \
		echo "" >> .env; \
		echo "# 日志配置" >> .env; \
		echo "LOG_LEVEL=INFO" >> .env; \
		echo "LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s" >> .env; \
		echo "" >> .env; \
		echo "# 爬虫配置" >> .env; \
		echo "REQUEST_TIMEOUT=30" >> .env; \
		echo "MAX_RETRIES=3" >> .env; \
		echo "REQUEST_INTERVAL=2" >> .env; \
		echo "" >> .env; \
		echo "# 账号管理配置" >> .env; \
		echo "ACCOUNT_ROTATION_INTERVAL=1800" >> .env; \
		echo "ACCOUNT_COOLDOWN_PERIOD=300" >> .env; \
		echo "" >> .env; \
		echo "# 任务调度配置" >> .env; \
		echo "MAX_WORKER_THREADS=3" >> .env; \
		echo ".env 文件已生成，请根据实际情况修改配置"; \
	else \
		echo ".env 文件已存在"; \
	fi

# 检查环境
check-env:
	@echo "检查环境..."
	@python --version
	@pip --version
	@echo "检查Python包..."
	@python -c "import requests, pymysql, pandas; print('核心依赖包检查通过')"
	@if [ -f .env ]; then \
		echo ".env 配置文件存在"; \
	else \
		echo "警告: .env 配置文件不存在，请运行 'make generate-config'"; \
	fi

# 项目打包
build:
	@echo "项目打包..."
	python setup.py sdist bdist_wheel
	@echo "打包完成，文件位于 dist/ 目录"

# 发布到PyPI (需要配置认证)
publish:
	@echo "发布到PyPI..."
	twine upload dist/*

# 完整安装流程
full-setup: generate-config install setup-db
	@echo "完整安装完成！"
	@echo "请编辑 .env 文件配置数据库连接信息"
	@echo "然后运行 'make run-crawler' 开始爬取数据"