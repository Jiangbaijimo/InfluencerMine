# 达人数据爬取与管理系统

一个功能完整的抖音达人数据爬取与管理系统，支持多账号管理、智能任务调度、数据库存储和实时监控。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 5.7+
- 8GB+ RAM（推荐）
- 稳定的网络连接

### 安装步骤

#### 1. 创建Conda环境
```bash
# 创建新环境
conda create -n influencer-crawler3.12  python=3.12

# 激活环境
conda activate influencer-crawler3.12 
```

#### 2. 安装依赖
```bash
# 安装Python包
pip install -r requirements.txt

# 或者使用setup.py安装
pip install -e .
```

#### 3. 数据库初始化
```bash
# 登录MySQL并创建数据库
mysql -u root -p
CREATE DATABASE daren_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入数据库结构
mysql -u root -p daren_data < init_db.sql
```

#### 4. 配置文件
复制并编辑配置文件：
```bash
cp .env.example .env
# 编辑.env文件，填入数据库连接信息
```

### 示例命令

#### 添加账号（重要示例）
```bash
python account_manager.py add --name "账号1" --cookies "passport_csrf_token=33f5045ce4fe4ba2e09cccbec4b1e17f; passport_csrf_token_default=33f5045ce4fe4ba2e09cccbec4b1e17f; s_v_web_id=verify_mfuljt01_gF8mZL5R_1KOh_4rGm_8J7j_KIWAeP3JgrR7; ttwid=1%7CvpsigHXS7IvNfJeWE0nhrw6JYtkdmbswloHzF3Z5CJw%7C1758513533%7C72930dea96afc3501c158787f6dc2760dfb95733d7bdf589766a3baafb9007e5; ttcid=f12eab976ad3485b86a9acd966469e8473; tt_scid=.dSzIFCs3b4XkxbN1bxgMIxNH71rPI3vBAYx8.g9I5tgtF18kFtcs3JRYC4JenN26caa; passport_mfa_token=CjETG%2Bc5U5O8x3zViwk%2FZnTvz%2FTL8fyE%2B%2F4rly8mAkaTu8YwbbKYer1Gl8YAR1voqacKGkoKPAAAAAAAAAAAAABPgX8WhRcjEfGJUyvhveKLGoWjdhSbTcCBFexkWZxoODWE70ht5LYy62ENElBj4WBYiBD17PwNGPax0WwgAiIBA01KXlA%3D; d_ticket=ea4bcb3f8b00727dfff456d42d37311050ab0; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sso_uid_tt=9b55e6674c0feb81917302882313e13a; sso_uid_tt_ss=9b55e6674c0feb81917302882313e13a; toutiao_sso_user=a0fb0fe8655c45aec723842b573ab98b; toutiao_sso_user_ss=a0fb0fe8655c45aec723842b573ab98b; sid_ucp_sso_v1=1.0.0-KDE2MWFkZGI4Y2VkMTBmZmNlYmI3MDNhMmJhNzBmOGQ5YjIzNGJjZjcKHwipvsCV9qyEAhCMk8PGBhiwDyAMMJzX2MMGOAFA6wcaAmxmIiBhMGZiMGZlODY1NWM0NWFlYzcyMzg0MmI1NzNhYjk4Yg; ssid_ucp_sso_v1=1.0.0-KDE2MWFkZGI4Y2VkMTBmZmNlYmI3MDNhMmJhNzBmOGQ5YjIzNGJjZjcKHwipvsCV9qyEAhCMk8PGBhiwDyAMMJzX2MMGOAFA6wcaAmxmIiBhMGZiMGZlODY1NWM0NWFlYzcyMzg0MmI1NzNhYjk4Yg; odin_tt=5822bd4aad9df0039fdcd0f0fda98c987e8d1112e4cb9a1b43301650475aa15345b36143a0778bf55fcd38bb5a1fe590d7b4b22f7b113e8c40b6fc6a0e16702a; sid_guard=e061eee277459504379f60e7d44dc144%7C1758513549%7C5184001%7CFri%2C+21-Nov-2025+03%3A59%3A10+GMT; uid_tt=7cabd613d640b48b5dbebd349c0e51de; uid_tt_ss=7cabd613d640b48b5dbebd349c0e51de; sid_tt=e061eee277459504379f60e7d44dc144; sessionid=e061eee277459504379f60e7d44dc144; sessionid_ss=e061eee277459504379f60e7d44dc144; session_tlb_tag=sttt%7C1%7C4GHu4ndFlQQ3n2Dn1E3BRP________-h3Myfxdg2qHlOQuuBXl495_QB5EuSej-FB7whms824sQ%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGRhZjk3YmRiYjMwZDRlZmM5OWYxMzM2ZjZlZmE2OWIyMmZjOWZmODUKGQipvsCV9qyEAhCNk8PGBhiwDyAMOAFA6wcaAmxmIiBlMDYxZWVlMjc3NDU5NTA0Mzc5ZjYwZTdkNDRkYzE0NA; ssid_ucp_v1=1.0.0-KGRhZjk3YmRiYjMwZDRlZmM5OWYxMzM2ZjZlZmE2OWIyMmZjOWZmODUKGQipvsCV9qyEAhCNk8PGBhiwDyAMOAFA6wcaAmxmIiBlMDYxZWVlMjc3NDU5NTA0Mzc5ZjYwZTdkNDRkYzE0NA; gd_random=eyJtYXRjaCI6dHJ1ZSwicGVyY2VudCI6MC44MDc0Njc1NzA2NTg4NzI5fQ==.B3L/nSHH1P9E2lIR13hNSMLvsVNCdpMpMrLz9MdUimk=; acsessionid=a2bb88fa534d43218bcb6aca866ce14b" --notes "从2.txt提取的最新cookie，2025年1月添加"
```

#### 开始爬取
```bash
# 爬取指定页面范围（正确参数）
python crawler_main.py --start 1 --end 10

# 指定任务名称
python crawler_main.py --start 1 --end 5 --task-name "美妆达人数据"

# 使用特定账号
python crawler_main.py --start 1 --end 3 --account-id 2

# 恢复中断的任务
python crawler_main.py --resume-task "task_20250101_123456"
```

#### 账号管理
```bash
# 查看所有账号
python account_manager.py list

# 测试账号状态
python account_manager.py test --account-id 1

# 删除账号
python account_manager.py delete --account-id 1

# 更新账号cookie
python account_manager.py update --account-id 1 --cookies "new_cookies_here"
```

#### 任务调度
```bash
# 启动任务调度器
python task_scheduler.py

# 查看任务状态
python task_scheduler.py --status

# 停止所有任务
python task_scheduler.py --stop-all
```

#### 数据导入MySQL
```bash
# 导入CSV数据到MySQL
python import_to_mysql.py --csv-file "data_by_type/美妆/美妆-达人名称-第1页-20250101.csv"

# 批量导入整个目录
python import_to_mysql.py --directory "data_by_type/美妆/"

# 指定数据库表名
python import_to_mysql.py --csv-file "data.csv" --table-name "custom_table"
```

## 📁 项目结构

```
达人数据爬取与管理系统/
├── .env                    # 环境配置文件
├── config.yaml            # 系统配置文件
├── requirements.txt       # Python依赖包
├── setup.py              # 安装脚本
├── Makefile              # 自动化构建脚本
├── init_db.sql           # 数据库初始化脚本
├── README.md             # 项目文档（本文件）
│
├── crawler_main.py       # 主爬虫程序
├── account_manager.py    # 账号管理工具
├── task_scheduler.py     # 任务调度器
├── import_to_mysql.py    # 数据导入工具
│
├── data_by_type/         # 按类型分类的数据文件
│   ├── 美妆/
│   ├── 时尚/
│   ├── 生活/
│   └── ...
├── exports/              # 导出的数据文件
├── logs/                 # 系统日志文件
├── temp/                 # 临时文件目录
└── backups/              # 数据备份目录
```

## ⚙️ 配置说明

### .env 文件配置
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=daren_data

# 爬虫配置
REQUEST_DELAY=2
MAX_RETRIES=3
TIMEOUT=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/crawler.log
```

### config.yaml 配置
```yaml
crawler:
  max_pages_per_task: 50
  concurrent_tasks: 3
  data_export_format: csv
  
database:
  connection_pool_size: 10
  query_timeout: 30
  
monitoring:
  enable_metrics: true
  alert_email: admin@example.com
```

## 🗄️ 数据库结构

### 主要数据表
- `daren_profiles`: 达人基本信息
- `daren_videos`: 视频数据
- `daren_stats`: 统计数据
- `accounts`: 爬虫账号管理
- `tasks`: 任务记录
- `system_logs`: 系统日志

## 🔧 高级功能

### 1. 智能重试机制
- 自动检测网络异常
- 智能调整请求频率
- 账号轮换策略

### 2. 数据质量控制
- 重复数据检测
- 数据完整性验证
- 异常数据标记

### 3. 监控与告警
- 实时性能监控
- 异常情况告警
- 数据统计报告

### 4. 扩展性设计
- 模块化架构
- 插件系统支持
- 分布式部署就绪

## 🚨 常见问题

### Q: 爬取时出现"unrecognized arguments"错误？
A: 请使用正确的参数名：`--start` 和 `--end`，而不是 `--start-page` 和 `--end-page`

### Q: Cookie失效怎么办？
A: 使用 `python account_manager.py update` 命令更新cookie，或添加新账号

### Q: 数据库连接失败？
A: 检查.env文件中的数据库配置，确保MySQL服务正在运行

### Q: 爬取速度太慢？
A: 调整config.yaml中的并发任务数和请求延迟设置

## 📊 性能优化

### 系统调优建议
1. **内存优化**: 建议8GB+内存，可处理大规模数据
2. **网络优化**: 使用稳定网络，避免频繁断线
3. **数据库优化**: 定期清理日志，建立适当索引
4. **并发控制**: 根据网络状况调整并发数

### 监控指标
- 爬取成功率
- 平均响应时间
- 数据质量得分
- 系统资源使用率

## 🔒 安全考虑

- Cookie信息加密存储
- 请求频率智能控制
- 用户代理随机化
- IP代理池支持（可选）

## 📝 更新日志

### v1.0.0 (2025-01-01)
- ✨ 完整的爬虫系统实现
- 🔧 多账号管理功能
- 📊 数据库存储和管理
- 🚀 任务调度系统
- 📈 监控和日志系统
- 📚 完整的文档和示例

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 获取帮助

- 📧 邮箱: support@example.com
- 💬 QQ群: 123456789
- 📖 文档: [在线文档](https://docs.example.com)
- 🐛 问题反馈: [GitHub Issues](https://github.com/username/repo/issues)

---

**注意**: 请遵守相关网站的robots.txt和服务条款，合理使用爬虫功能。