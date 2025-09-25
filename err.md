influencer-crawler3.12) PS C:\Users\GIMC 23F\Desktop\新建文件夹\达人数据爬取与管理系统> python crawler_async.py --start 1 --end 1 --account-id 3
2025-09-25 18:00:34,291 - monitor.monitor - INFO - 性能监控已启动
2025-09-25 18:00:34,351 - __main__ - INFO - 尝试加载指定账号 ID: 3
2025-09-25 18:00:34,352 - __main__ - INFO - 加载了 1 个可用账号
2025-09-25 18:00:34,553 - __main__ - INFO - 创建任务 ID: 11, 名称: 异步爬取_1到1页_20250925_180034
2025-09-25 18:00:34,553 - __main__ - INFO - 开始异步爬取任务: 异步爬取_1到1页_20250925_180034
2025-09-25 18:00:34,553 - __main__ - INFO - 页面范围: 1 - 1
2025-09-25 18:00:34,553 - __main__ - INFO - 使用 5 个线程，1 个账号
2025-09-25 18:00:34,553 - __main__ - INFO - [线程0] 正在请求第 1 页数据...
2025-09-25 18:00:35,293 - monitor.monitor - INFO - 性能指标 - CPU: 12.8%, 内存: 85.3% (13713.8MB), 线程: 3, 请求/秒: 0.00, 成功率: 0.0%, 平均响应时间: 0.00ms
2025-09-25 18:00:35,293 - monitor.monitor - WARNING - ⚠️ 性能告警: 内存使用率过高: 85.3%

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[200000,250000,250000,280000,320544,320544,343440,343440,350000,366336,366336,366340,415000,427600,457920,457920,457920,457920,457920,480000,550000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "3",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_c150001e6de3d8e4e65.jpeg?from=4010531038",
    "avg_sale_amount_range": "1000-5000",
    "brand_boost_vv": "1000000",
    "burst_text_rate": "0.9091",
    "city": "昆明市",
    "content_theme_labels_180d": "[\"陈翔短剧\",\"搞笑剧情\",\"有趣剧情创作\",\"职场趣闻\",\"剧情反转\",\"生活喜剧情节\",\"恋爱剧情\",\"恋爱故事\",\"家庭幽默演绎\",\"亲情剧集\"]",
    "core_user_id": "6556303280",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": ">100w",
    "ecom_gpm_30d_range": "1000-3000",
    "ecom_gpm_30days_range": "0",
    "ecom_score": "76",
    "ecom_video_ctr_30d_range": "0",
 ...
attribute_datas存在: True
nick_name字段: 陈翔六点半
follower字段: 56822262
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[378000,550000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "3",
    "avatar_uri": "https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_dbf9db949a342a1df0f22720a9112bb1.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "burst_text_rate": "0.5",
    "city": "",
    "content_theme_labels_180d": "[\"亲子活动\",\"校园生活\",\"宝宝喂养\"]",
    "core_user_id": "93532893350",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "10-50",
    "ecom_gmv_30d_range": "1k-3w",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "12099846",
    "expected_play_num": "15474227",
    "fans_increment_rate_within_15d": "0.0013344772038537739",
    "fans_increment_within_15d": "27027",
    "fans_increment_within_30d": "-1520",
    "follower": "20278964",
    "game_type"...
attribute_datas存在: True
nick_name字段: 瑶一瑶小肉包
follower字段: 20278964
tags_relation字段: {"母婴亲子":["亲子互动"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[544000,544000,557600,680000,680000,680000,680000,750000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "1",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_317ea000ac7521220a215.jpeg?from=4010531038",
    "brand_boost_vv": "1000000",
    "burst_text_rate": "1",
    "city": "朝阳区",
    "content_theme_labels_180d": "[\"美食探店\",\"地方美食\",\"辣味美食\",\"烧烤\",\"海鲜美食\",\"美食吃播\",\"东北美食\",\"深夜美食\",\"广东美食\",\"美食探索\"]",
    "core_user_id": "77243783127",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "10-50",
    "ecom_gmv_30d_range": "3w-20w",
    "ecom_gpm_30d_range": "<=80",
    "ecom_score": "92",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "7089178",
    "expected_play_num": "8812610",
    "fans_increment_rate_within_15d": "0.003178932434392834",
    "fa...
attribute_datas存在: True
nick_name字段: 特别乌啦啦
follower字段: 19583789
tags_relation字段: {"美食":["美食探店"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "13",
    "assign_task_price_list": "[196000,224000,224000,224000,280000,280000,280000,280000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_c926d20a93941472003ca9d67a412251.jpeg?from=4010531038",
    "brand_boost_vv": "1000000",
    "city": "成都市",
    "content_theme_labels_180d": "[\"搞笑剧情\",\"有趣剧情创作\",\"友情故事\",\"国内旅行趣闻\",\"剧情反转\",\"健身挑战\",\"国内旅行\",\"健身增肌\",\"家庭旅行\",\"减脂饮食\"]",
    "core_user_id": "4239343268935933",
    "e_commerce_enable": "1",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "4153442",
    "expected_play_num": "10347692",
    "fans_increment_rate_within_15d": "0.0007751240850615614",
    "fans_increment_within_15d": "6835",
    "fans_increment_within_30d": "107038",
    "follower": "8824264",
  ...
attribute_datas存在: True
nick_name字段: 池野林Club
follower字段: 8824264
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[350000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_65a900303b98c7375b53.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "burst_text_rate": "1",
    "city": "",
    "content_theme_labels_180d": "[\"有趣剧情创作\",\"恐怖演绎\",\"奇幻剧情\",\"搞笑剧情\",\"生存挑战\",\"搞笑挑战\",\"剧情反转\",\"意外结局\",\"大学宿舍趣事\",\"青春期烦恼\"]",
    "core_user_id": "63626436304",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": "<=1k",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "5254429",
    "expected_play_num": "7468504",
    "fans_increment_rate_within_15d": "-0.0002224516920277862",
    "fans_increment_within_15d": "-2416",
    "fans_increment_within_30d": "12645",...
attribute_datas存在: True
nick_name字段: 天舒很硬-天舒班
follower字段: 10894067
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[54400,78400,78400,98000]",
    "author_avatar_frame_icon": "0",
    "author_ecom_level": "L0",
    "author_status": "1",
    "author_type": "3",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_c08f707ef3d8ef23bdf7f0ed93273465.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "burst_text_rate": "1",
    "city": "河源市",
    "content_theme_labels_180d": "[\"有趣剧情创作\",\"搞笑剧情\",\"剧情反转\",\"闺蜜短剧\",\"短剧豪门恩怨\",\"恋爱剧情\",\"恋爱故事\",\"友情故事\",\"情感短剧\",\"亲情剧集\"]",
    "core_user_id": "2616482972580196",
    "e_commerce_enable": "0",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "5382879",
    "expected_play_num": "6065473",
    "fans_increment_rate_within_15d": "0.004974900006653901",
    "fans_increment_within_15d": "6729",
    "fans_increment_within_30d": "68604",
    "follower": "1359212",
    "game_type": "{\"MOBA\": 1.0}",
    "gender": "1"...
attribute_datas存在: True
nick_name字段: 周周的周
follower字段: 1359212
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[158400,158400,158400,198000,198000,198000,198000,198000,207840,259800]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "1",
    "avatar_uri": "https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_4cdda96773eb5310a25d1c95340e4077.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "burst_text_rate": "0.7143",
    "city": "朝阳区",
    "content_theme_labels_180d": "[\"荤菜教程\",\"家常菜教程\",\"传统美食\",\"家常菜谱\",\"自制美食\",\"下饭菜教程\",\"辣味美食\",\"海鲜烹饪\",\"地方美食\",\"夏日饮品\"]",
    "core_user_id": "2273413469048935",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "10-50",
    "ecom_gmv_30d_range": "3w-20w",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "7395520",
    "expected_play_num": "6319786",
    "fans_increment_rate_within_15d": "0.004098571400284879...
attribute_datas存在: True
nick_name字段: 夏叔厨房
follower字段: 20131850
tags_relation字段: {"美食":["美食教程"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[368000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "3",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_2dc4600008ea167e64d11.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "city": "厦门市",
    "content_theme_labels_180d": "[\"启蒙阅读\"]",
    "core_user_id": "3671985629168663",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": "3w-20w",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "8429782",
    "expected_play_num": "10460227",
    "fans_increment_rate_within_15d": "0.0012894793629592734",
    "fans_increment_within_15d": "33732",
    "fans_increment_within_30d": "70722",
    "follower": "26193488",
    "game_type": "",
    "gender": "0",
    "grade": "0",
    "id": "6767...
attribute_datas存在: True
nick_name字段: 这不科学啊
follower字段: 26193488
tags_relation字段: {"艺术文化":["自然科学"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "22",
    "assign_task_price_list": "[180000,200000,200000,200000]",
    "author_avatar_frame_icon": "0",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p26.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_2751f1fa85afeacd6c33acd5f6e6a510.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "city": "成都市",
    "content_theme_labels_180d": "[\"美食探店\",\"地方美食\",\"美食探索\",\"异域风情\",\"美食之旅\",\"海鲜美食\",\"美食吃播\",\"辣味美食\",\"家庭生活记录\",\"东北旅行\"]",
    "core_user_id": "2524905476466910",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "10-50",
    "ecom_gmv_30d_range": "<=1k",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "3629856",
    "expected_play_num": "4069894",
    "fans_increment_rate_within_15d": "0.002219625699958714",
    "fans_increment_within_15d": "26...
attribute_datas存在: True
nick_name字段: 老王在中国
follower字段: 12001236
tags_relation字段: {"美食":["美食探店"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "14",
    "assign_task_price_list": "[240000]",
    "author_avatar_frame_icon": "20",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_05a7b98c63e31a2d6979808b8a00d688.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "city": "杭州市",
    "content_theme_labels_180d": "[\"搞笑剧情\",\"有趣剧情创作\",\"明星演绎\",\"恋爱剧情\",\"恋爱演绎\",\"儿童安全教育\",\"生活喜剧情节\",\"意外结局\"]",
    "core_user_id": "2296215279504366",
    "e_commerce_enable": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "5457596",
    "expected_play_num": "13514493",
    "fans_increment_rate_within_15d": "0.007349074259914598",
    "fans_increment_within_15d": "41266",
    "fans_increment_within_30d": "46485",
    "follower": "5656165",
    "game_item_count_90d": "1",
    "game_type": "",
    "gender": "1",
    "grade": "0",
    "id": "7099027245091520549",
    "interact_rate_w...
attribute_datas存在: True
nick_name字段: 榴莲阿
follower字段: 5656165
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[72000,90000]",
    "author_avatar_frame_icon": "0",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_4edb624c1c376c0c5bff3a1a02b66bbb.jpeg?from=4010531038",
    "burst_text_rate": "1",
    "city": "广州",
    "content_theme_labels_180d": "[\"职场趣闻\",\"搞笑剧情\",\"有趣剧情创作\",\"剧情反转\",\"搞笑挑战\",\"智能家居\",\"照明科技\",\"办公神器\",\"健身增肌\",\"生活喜剧情节\"]",
    "core_user_id": "1834456702269915",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "1374202",
    "expected_play_num": "1936879",
    "fans_increment_rate_within_15d": "0.011897225521951603",
    "fans_increment_within_15d": "24187",
    "fans_increment_within_30d": "75755",
    "follower": "2057061",
    "game_type": "",
    "gender": "1",
    "grade": "0",
    "id": "7412512379650441253",
    "interact_rate_within_30d": "0.0302",
    "interaction_median_30d": "51240.5",
    "is_ad_star_cur...
attribute_datas存在: True
nick_name字段: 姚哲禹⁰⁷²⁹
follower字段: 2057061
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[240000,240000,240000,240000,240000,270000,300000,300000,320000]",
    "author_avatar_frame_icon": "0",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p3.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_316620003a7a600560121.jpeg?from=4010531038",
    "avg_search_after_view_rate_30d": "0.0082",
    "brand_boost_vv": "0",
    "burst_text_rate": "1",
    "city": "沈阳市",
    "content_theme_labels_180d": "[\"搞笑剧情\",\"口腔护理\",\"邮轮旅行\",\"友情故事\",\"手机评测\",\"大学宿舍趣事\",\"电子产品测评\",\"智能家居\",\"牙膏评测\"]",
    "core_user_id": "58836756092",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": "20w-100w",
    "ecom_gpm_30d_range": "400-1000",
    "ecom_video_product_num_30d": "0",
    "ecom_watch_pv_30d": "1.4",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "4713440",
    "expected_play_num": "5447615",
    "fans_...
attribute_datas存在: True
nick_name字段: 张凤霞
follower字段: 12250372
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[69150,110640,200000,250000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_b8eefa2248b106e7f6a3c4869250d018.jpeg?from=4010531038",
    "brand_boost_vv": "1000000",
    "burst_text_rate": "1",
    "city": "朝阳区",
    "content_theme_labels_180d": "[\"美食探店\",\"地方美食\",\"美食之旅\",\"消费体验\",\"美食趣闻\",\"海鲜美食\",\"国内旅行\",\"广东美食\",\"美食探索\",\"澳门旅行\"]",
    "core_user_id": "3518878936472975",
    "e_commerce_enable": "1",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "6459921",
    "expected_play_num": "7179774",
    "fans_increment_rate_within_15d": "0.011109220860219824",
    "fans_increment_within_15d": "164298",
    "fans_increment_within_30d": "303467",
    "follower": "14954231",
    "game_type": "",
    "gender": "1",
   ...
attribute_datas存在: True
nick_name字段: 真探唐仁杰
follower字段: 14954231
tags_relation字段: {"美食":["美食探店"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "30",
    "assign_task_price_list": "[300000,320000,400000,400000,400000,560000,700000]",
    "author_avatar_frame_icon": "0",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_b87628a6a656b8ed2db14a95bc5b8a85.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "burst_text_rate": "1",
    "city": "成都市",
    "content_theme_labels_180d": "[\"淡妆教程\",\"妆前技巧\",\"通勤妆容\",\"底妆测评\",\"消费体验\",\"明星妆容\",\"定妆测评\",\"夏日妆容\",\"创意妆容\",\"卸妆测评\"]",
    "core_user_id": "58015764377",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": ">100w",
    "ecom_gpm_30d_range": "1000-3000",
    "ecom_score": "94",
    "ecom_video_product_num_30d": "0",
    "ecom_watch_pv_30d": "1.7",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "4759027",
    "expected_play_num": "652...
attribute_datas存在: True
nick_name字段: 陈圆圆超可爱
follower字段: 15064537
tags_relation字段: {"时尚":["穿搭"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "8",
    "assign_task_price_list": "[230400,230400,230400,288000,288000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L5",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_73655eb1bc13144842657c857b3f89e8.jpeg?from=4010531038",
    "brand_boost_vv": "1000000",
    "burst_text_rate": "1",
    "city": "深圳市",
    "content_theme_labels_180d": "[\"恋爱剧情\",\"恋爱演绎\",\"恋爱故事\",\"大学宿舍趣事\",\"友情故事\",\"闺蜜短剧\",\"游戏趣闻\"]",
    "core_user_id": "4416086914907516",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": ">100w",
    "ecom_gpm_30d_range": "80-400",
    "ecom_score": "82",
    "ecom_video_product_num_30d": "0",
    "ecom_watch_pv_30d": "1.7",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "7889010",
    "expected_play_num": "4133765",
    "fans_increment_rate...
attribute_datas存在: True
nick_name字段: 周三拾
follower字段: 4944456
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[102200,112000,140000,140000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p26.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_31acc00049ecbe729862a.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "city": "肇庆市",
    "content_theme_labels_180d": "[\"搞笑剧情\",\"有趣剧情创作\",\"意外结局\",\"剧情反转\",\"搞笑挑战\",\"大学宿舍趣事\",\"亲子教育\",\"青春期烦恼\",\"职场趣闻\"]",
    "core_user_id": "536212578252463",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": ">200",
    "ecom_gmv_30d_range": "20w-100w",
    "ecom_gpm_30d_range": ">3000",
    "ecom_video_product_num_30d": "0",
    "ecom_watch_pv_30d": "1.3",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "3984855",
    "expected_play_num": "8418919",
    "fans_increment_rate_within_15d": "0.001514943082867288",
    "fans_increment_within_15d": "18446",
    "fans_incre...
attribute_datas存在: True
nick_name字段: 倒霉泰哥
follower字段: 12194028
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "74",
    "assign_task_price_list": "[480000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L5",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_7e493ea6bb9552ea2fa4d54029155c10.jpeg?from=4010531038",
    "brand_boost_vv": "1000000",
    "city": "广州市",
    "content_theme_labels_180d": "[\"海滨旅行\",\"环球旅行\",\"奶制品测评\",\"海外旅行\"]",
    "core_user_id": "62677606580",
    "e_commerce_enable": "0",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "3086012",
    "expected_play_num": "4668388",
    "fans_increment_rate_within_15d": "0.0024286147224055516",
    "fans_increment_within_15d": "11676",
    "fans_increment_within_30d": "43165",
    "follower": "4819329",
    "game_type": "",
    "gender": "2",
    "grade": "0",
    "id": "6629659487894503431",
    "interact_rate_wit...
attribute_datas存在: True
nick_name字段: 原来是陶阿狗君
follower字段: 4819329
tags_relation字段: {"颜值达人":["美女"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[127500,136000,136000,136000,136000,145715,170000,170000,170000,170000,170000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p11.douyinpic.com/aweme/1080x1080/aweme-avatar/mosaic-legacy_1ca2100058252e27e1073.jpeg?from=4010531038",
    "brand_boost_vv": "0",
    "burst_text_rate": "1",
    "city": "怀化市",
    "content_theme_labels_180d": "[\"搞笑剧情\",\"有趣剧情创作\",\"生活喜剧情节\",\"剧情反转\",\"大学宿舍趣事\",\"亲子活动\",\"青春期烦恼\",\"友情故事\",\"游戏趣闻\",\"恋爱剧情\"]",
    "core_user_id": "58710120676",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "10-50",
    "ecom_gmv_30d_range": "<=1k",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "4023621",
    "expected_play_num": "5436565",
    "fans_increment_rate_within_15d": "0.001809563578616573",
    "fans...
attribute_datas存在: True
nick_name字段: 无敌灏克
follower字段: 19123107
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_cpm_suggest_price": "22",
    "assign_task_price_list": "[118500,126400,126400,126400,158000]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L2",
    "author_status": "1",
    "author_type": "3",
    "avatar_uri": "https://p26.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_1071dde4375fbe3c985b3f97895c37c1.jpeg?from=4010531038",
    "burst_text_rate": "1",
    "city": "杭州",
    "content_theme_labels_180d": "[\"有趣剧情创作\",\"欢乐演绎\",\"家庭幽默演绎\",\"个人成长\",\"搞笑剧情\",\"女性穿搭\",\"古风剧情\",\"职场规则\",\"剧情反转\",\"中式穿搭\"]",
    "core_user_id": "2959517465984567",
    "e_commerce_enable": "1",
    "ecom_score": "79",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "2381219",
    "expected_play_num": "3403225",
    "fans_increment_rate_within_15d": "0.009848153601915776",
    "fans_increment_within_15d": "15068",
    "fans_increment_within_30d": "32004",
    "follower": "1545158",
    "g...
attribute_datas存在: True
nick_name字段: 曾老师的小世界
follower字段: 1545158
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================

=== 调试信息 - 第1页达人数据 ===
原始author数据结构: {
  "attribute_datas": {
    "assign_task_price_list": "[128050,128050,128050,157600,157600,157600]",
    "author_avatar_frame_icon": "20",
    "author_ecom_level": "L6",
    "author_status": "1",
    "author_type": "2",
    "avatar_uri": "https://p26.douyinpic.com/aweme/1080x1080/aweme-avatar/tos-cn-avt-0015_b9493d9cacfe4d9a7a023caf25362da1.jpeg?from=4010531038",
    "brand_boost_vv": "1000000",
    "burst_text_rate": "0.6667",
    "city": "西安市",
    "content_theme_labels_180d": "[\"亲情剧集\",\"乡村亲情故事\",\"情感演绎\",\"感人短剧\",\"家庭幽默演绎\",\"乡村短剧\",\"有趣剧情创作\",\"情感短剧\",\"生活喜剧情节\",\"搞笑剧情\"]",
    "core_user_id": "2422929288873708",
    "e_commerce_enable": "1",
    "ecom_avg_order_value_30d_range": "50-200",
    "ecom_gmv_30d_range": "3w-20w",
    "ecom_gpm_30d_range": "<=80",
    "ecom_video_ctr_30d_range": "2%-4%",
    "ecom_video_mid_click_pv_30d_range": "5000-1万",
    "ecom_video_product_num_30d": "0",
    "expected_cpa3_level": "4",
    "expected_natural_play_num": "8468621",
    "expected_pl...
attribute_datas存在: True
nick_name字段: 三根葱
follower字段: 14026659
tags_relation字段: {"剧情搞笑":["剧情"]}
==================================================
2025-09-25 18:00:35,756 - __main__ - INFO - [线程0] ✅ 第 1 页处理完成，成功: 20, 总计: 20
2025-09-25 18:00:36,806 - __main__ - INFO - 任务 11 状态更新为: completed
2025-09-25 18:00:36,808 - __main__ - INFO - 🎉 异步爬取任务完成！总计处理 20 位达人，成功 20，失败 0
2025-09-25 18:00:36,808 - __main__ - INFO - 空页面数量: 0
2025-09-25 18:00:36,808 - __main__ - ERROR - 生成性能报告失败: cannot import name 'get_optimization_suggestions' from 'monitor' (C:\Users\GIMC 23F\Desktop\新建文件夹\达人数据爬取与管理系统\monitor.py)
2025-09-25 18:00:41,813 - monitor.monitor - INFO - 性能监控已停止