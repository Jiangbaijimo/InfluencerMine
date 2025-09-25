-- 达人数据爬取与管理系统 - 数据库初始化脚本
-- 创建时间: 2025-01-23
-- 数据库版本: MySQL 8.0+

-- 创建数据库
CREATE DATABASE IF NOT EXISTS influencer_crawler 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE influencer_crawler;

-- 1. 达人类型/领域主表
CREATE TABLE IF NOT EXISTS daoren_domain (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL COMMENT '类型名称，如"美妆"、"时尚"、"测评"',
    description VARCHAR(255) COMMENT '类型描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='达人类型/领域主表';

-- 2. 达人主表（核心表）
CREATE TABLE IF NOT EXISTS daoren_author (
    -- 基础身份信息
    star_id BIGINT PRIMARY KEY COMMENT '达人唯一ID',
    nick_name VARCHAR(255) NOT NULL COMMENT '昵称',
    core_user_id VARCHAR(50) COMMENT '核心用户ID',
    avatar_uri TEXT COMMENT '头像链接URL',
    gender TINYINT COMMENT '性别(1=男,2=女)',
    city VARCHAR(100) COMMENT '城市',
    province VARCHAR(100) COMMENT '省份',
    author_type TINYINT COMMENT '达人类型(1=个人,3=机构)',
    author_status TINYINT COMMENT '账号状态',
    grade TINYINT DEFAULT 0 COMMENT '达人等级',
    
    -- 粉丝与影响力数据
    follower BIGINT DEFAULT 0 COMMENT '粉丝总数',
    fans_increment_within_15d BIGINT DEFAULT 0 COMMENT '15天粉丝增长数',
    fans_increment_within_30d BIGINT DEFAULT 0 COMMENT '30天粉丝增长数',
    fans_increment_rate_within_15d DECIMAL(10,8) DEFAULT 0 COMMENT '15天粉丝增长率',
    interact_rate_within_30d DECIMAL(8,6) DEFAULT 0 COMMENT '30天互动率',
    interaction_median_30d BIGINT DEFAULT 0 COMMENT '30天互动中位数',
    play_over_rate_within_30d DECIMAL(8,6) DEFAULT 0 COMMENT '30天播放完成率',
    vv_median_30d BIGINT DEFAULT 0 COMMENT '30天播放量中位数',
    
    -- 内容创作数据
    star_item_count_within_30d INT DEFAULT 0 COMMENT '30天内星图视频数量',
    star_video_cnt_90d INT DEFAULT 0 COMMENT '90天星图视频总数',
    star_video_interact_rate_90d DECIMAL(8,6) DEFAULT 0 COMMENT '90天星图视频互动率',
    star_video_finish_vv_rate_90d DECIMAL(8,6) DEFAULT 0 COMMENT '90天星图视频完播率',
    star_video_median_vv_90d BIGINT DEFAULT 0 COMMENT '90天星图视频播放中位数',
    content_theme_labels_180d JSON COMMENT '180天内容主题标签',
    tags_relation JSON COMMENT '达人标签关系JSON',
    
    -- 商业价值数据
    price_1_20 DECIMAL(12,2) DEFAULT 0 COMMENT '1-20秒视频报价',
    price_20_60 DECIMAL(12,2) DEFAULT 0 COMMENT '20-60秒视频报价',
    price_60 DECIMAL(12,2) DEFAULT 0 COMMENT '60秒以上视频报价',
    assign_task_price_list VARCHAR(200) COMMENT '指派任务价格区间',
    expected_play_num BIGINT DEFAULT 0 COMMENT '预期播放量',
    expected_natural_play_num BIGINT DEFAULT 0 COMMENT '预期自然播放量',
    star_index DECIMAL(10,6) DEFAULT 0 COMMENT '星图指数',
    
    -- CPM成本数据
    prospective_1_20_cpm DECIMAL(10,4) DEFAULT 0 COMMENT '1-20秒预期CPM',
    prospective_20_60_cpm DECIMAL(10,4) DEFAULT 0 COMMENT '20-60秒预期CPM',
    prospective_60_cpm DECIMAL(10,4) DEFAULT 0 COMMENT '60秒以上预期CPM',
    promotion_prospective_1_20_cpm DECIMAL(10,4) DEFAULT 0 COMMENT '推广1-20秒预期CPM',
    promotion_prospective_20_60_cpm DECIMAL(10,4) DEFAULT 0 COMMENT '推广20-60秒预期CPM',
    promotion_prospective_60_cpm DECIMAL(10,4) DEFAULT 0 COMMENT '推广60秒以上预期CPM',
    promotion_prospective_vv BIGINT DEFAULT 0 COMMENT '推广预期播放量',
    
    -- 电商数据
    e_commerce_enable TINYINT DEFAULT 0 COMMENT '是否开通电商功能',
    author_ecom_level VARCHAR(10) COMMENT '电商等级(L1-L6)',
    ecom_gmv_30d_range VARCHAR(50) COMMENT '30天GMV范围',
    ecom_avg_order_value_30d_range VARCHAR(50) COMMENT '30天平均订单价值',
    ecom_gpm_30d_range VARCHAR(50) COMMENT '30天毛利率范围',
    ecom_video_product_num_30d INT DEFAULT 0 COMMENT '30天带货视频数',
    star_ecom_video_num_30d INT DEFAULT 0 COMMENT '30天星图带货视频数',
    
    -- 性能指标
    link_convert_index DECIMAL(8,2) DEFAULT 0 COMMENT '链接转化指数',
    link_convert_index_by_industry DECIMAL(8,2) DEFAULT 0 COMMENT '行业链接转化指数',
    link_shopping_index DECIMAL(8,2) DEFAULT 0 COMMENT '购物指数',
    link_spread_index DECIMAL(8,2) DEFAULT 0 COMMENT '传播指数',
    link_spread_index_by_industry DECIMAL(8,2) DEFAULT 0 COMMENT '行业传播指数',
    link_star_index DECIMAL(8,2) DEFAULT 0 COMMENT '链接星图指数',
    link_star_index_by_industry DECIMAL(8,2) DEFAULT 0 COMMENT '行业链接星图指数',
    link_recommend_index_by_industry DECIMAL(8,2) DEFAULT 0 COMMENT '行业推荐指数',
    search_after_view_index_by_industry DECIMAL(8,2) DEFAULT 0 COMMENT '搜索后观看指数',
    
    -- 认证与等级
    is_excellenct_author TINYINT DEFAULT 0 COMMENT '是否优质达人',
    star_excellent_author TINYINT DEFAULT 0 COMMENT '星图优质达人标识',
    author_avatar_frame_icon VARCHAR(20) COMMENT '头像框等级',
    is_black_horse_author TINYINT DEFAULT 0 COMMENT '是否黑马达人',
    is_cocreate_author TINYINT DEFAULT 0 COMMENT '是否共创达人',
    is_cpm_project_author TINYINT DEFAULT 0 COMMENT '是否CPM项目达人',
    is_short_drama TINYINT DEFAULT 0 COMMENT '是否短剧达人',
    star_whispers_author TINYINT DEFAULT 0 COMMENT '星图私信达人',
    local_lower_threshold_author TINYINT DEFAULT 0 COMMENT '本地低门槛达人',
    
    -- 其他数据
    burst_text_rate DECIMAL(6,4) DEFAULT 0 COMMENT '爆文率',
    brand_boost_vv BIGINT DEFAULT 0 COMMENT '品牌提升播放量',
    video_brand_boost TINYINT DEFAULT 0 COMMENT '视频品牌提升',
    video_brand_boost_vv BIGINT DEFAULT 0 COMMENT '视频品牌提升播放量',
    expected_cpa3_level TINYINT DEFAULT 0 COMMENT '预期CPA3等级',
    game_type VARCHAR(100) COMMENT '游戏类型',
    
    -- 组件数据
    star_component_install_finish_cnt_90d INT DEFAULT 0 COMMENT '90天组件安装完成数',
    star_component_link_click_cnt_90d INT DEFAULT 0 COMMENT '90天组件链接点击数',
    star_video_install_ge_1_cnt_90d INT DEFAULT 0 COMMENT '90天视频安装>=1次数',
    
    -- 最新视频数据
    last_10_items JSON COMMENT '最近10个视频详细数据',
    items JSON COMMENT '热门视频列表',
    task_infos JSON COMMENT '任务信息和价格列表',
    
    -- 系统字段
    crawled_at DATE NOT NULL COMMENT '爬取日期',
    page_num INT DEFAULT 0 COMMENT '来源页码',
    source_url VARCHAR(500) COMMENT '来源URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引优化
    INDEX idx_nick_name (nick_name),
    INDEX idx_follower (follower DESC),
    INDEX idx_city (city),
    INDEX idx_province (province),
    INDEX idx_author_type (author_type),
    INDEX idx_author_ecom_level (author_ecom_level),
    INDEX idx_star_index (star_index DESC),
    INDEX idx_price_composite (price_1_20, price_20_60, price_60),
    INDEX idx_interact_rate (interact_rate_within_30d DESC),
    INDEX idx_vv_median (vv_median_30d DESC),
    INDEX idx_crawled_at (crawled_at DESC),
    INDEX idx_page_num (page_num),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_tags_relation ((CAST(tags_relation AS CHAR(255) ARRAY))),
    INDEX idx_is_excellent (is_excellenct_author, star_excellent_author),
    INDEX idx_ecommerce (e_commerce_enable, author_ecom_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='达人完整数据表-包含所有API字段';

-- 为 tags 字段创建多值索引（MySQL 8.0.17+）
ALTER TABLE daoren_author ADD INDEX idx_tags ((CAST(tags AS CHAR(255) ARRAY)));

-- 3. 任务日志表（支持断点续爬）
CREATE TABLE IF NOT EXISTS daoren_task_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL COMMENT '任务名称',
    domain_filter VARCHAR(255) COMMENT '本次任务筛选的类型，如"美妆,时尚"',
    start_page INT NOT NULL DEFAULT 1 COMMENT '起始页码',
    end_page INT NOT NULL DEFAULT 1 COMMENT '结束页码',
    current_page INT DEFAULT 0 COMMENT '当前处理页码',
    status ENUM('pending', 'running', 'completed', 'failed', 'paused') DEFAULT 'pending' COMMENT '任务状态',
    total_authors INT DEFAULT 0 COMMENT '总达人数',
    success_authors INT DEFAULT 0 COMMENT '成功处理达人数',
    failed_authors INT DEFAULT 0 COMMENT '失败达人数',
    error_message TEXT COMMENT '错误信息',
    start_time TIMESTAMP NULL COMMENT '开始时间',
    end_time TIMESTAMP NULL COMMENT '结束时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_status (status),
    INDEX idx_domain_filter (domain_filter),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='任务日志表';

-- 4. 账号管理表（支持多账号轮换）
CREATE TABLE IF NOT EXISTS daoren_account (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL COMMENT '账号名称',
    cookies TEXT COMMENT 'Cookie信息',
    headers JSON COMMENT '请求头信息',
    status ENUM('active', 'inactive', 'banned', 'cooldown') DEFAULT 'active' COMMENT '账号状态',
    last_used_at TIMESTAMP NULL COMMENT '最后使用时间',
    success_count INT DEFAULT 0 COMMENT '成功请求次数',
    failed_count INT DEFAULT 0 COMMENT '失败请求次数',
    cooldown_until TIMESTAMP NULL COMMENT '冷却结束时间',
    notes TEXT COMMENT '备注信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_account_name (account_name),
    INDEX idx_status (status),
    INDEX idx_last_used_at (last_used_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账号管理表';

-- 5. 爬取历史记录表
CREATE TABLE IF NOT EXISTS daoren_crawl_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL COMMENT '关联任务ID',
    star_id BIGINT NOT NULL COMMENT '达人ID',
    page_num INT NOT NULL COMMENT '页码',
    account_id INT COMMENT '使用的账号ID',
    status ENUM('success', 'failed', 'skipped') DEFAULT 'success' COMMENT '处理状态',
    error_message TEXT COMMENT '错误信息',
    response_time INT DEFAULT 0 COMMENT '响应时间(毫秒)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_task_id (task_id),
    INDEX idx_star_id (star_id),
    INDEX idx_page_num (page_num),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    
    -- 外键约束
    FOREIGN KEY (task_id) REFERENCES daoren_task_log(id) ON DELETE CASCADE,
    FOREIGN KEY (star_id) REFERENCES daoren_author(star_id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES daoren_account(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爬取历史记录表';

-- 6. 数据导出记录表
CREATE TABLE IF NOT EXISTS daoren_export_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    export_type ENUM('csv', 'excel', 'json') NOT NULL COMMENT '导出类型',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    domain_filter VARCHAR(255) COMMENT '导出的类型筛选',
    date_range_start DATE COMMENT '日期范围开始',
    date_range_end DATE COMMENT '日期范围结束',
    total_records INT DEFAULT 0 COMMENT '导出记录数',
    file_size BIGINT DEFAULT 0 COMMENT '文件大小(字节)',
    status ENUM('processing', 'completed', 'failed') DEFAULT 'processing' COMMENT '导出状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    INDEX idx_export_type (export_type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='数据导出记录表';

-- 插入默认的达人类型数据
INSERT IGNORE INTO daoren_domain (name, description) VALUES
('美妆', '美妆护肤相关内容创作者'),
('时尚', '时尚穿搭相关内容创作者'),
('测评', '产品测评相关内容创作者'),
('生活', '生活方式相关内容创作者'),
('才艺技能', '才艺技能展示相关内容创作者'),
('颜值达人', '颜值类内容创作者'),
('未分类', '未明确分类的达人');

-- 插入默认账号（示例）
INSERT IGNORE INTO daoren_account (account_name, status, notes) VALUES
('default_account', 'active', '默认账号，需要配置Cookie和Headers');

-- 创建视图：按类型统计达人数据
CREATE OR REPLACE VIEW v_daoren_stats_by_type AS
SELECT 
    tag_value AS domain_name,
    COUNT(*) AS total_count,
    AVG(follower) AS avg_follower,
    AVG(price) AS avg_price,
    AVG(star_index) AS avg_star_index,
    MAX(crawled_at) AS last_crawled_date
FROM daoren_author da
CROSS JOIN JSON_TABLE(da.tags, '$[*]' COLUMNS (tag_value VARCHAR(50) PATH '$')) AS jt
GROUP BY tag_value
ORDER BY total_count DESC;

-- 创建视图：任务执行统计
CREATE OR REPLACE VIEW v_task_stats AS
SELECT 
    DATE(created_at) AS task_date,
    COUNT(*) AS total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_tasks,
    SUM(total_authors) AS total_authors_processed,
    AVG(TIMESTAMPDIFF(MINUTE, start_time, end_time)) AS avg_duration_minutes
FROM daoren_task_log
GROUP BY DATE(created_at)
ORDER BY task_date DESC;

-- 显示创建结果
SELECT 'Database initialization completed successfully!' AS message;
SELECT 'Tables created:' AS info;
SHOW TABLES;