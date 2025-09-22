import requests
import json
import csv
from typing import List, Dict, Any

# --- 配置区域 ---
# 设置您想要爬取的起始页和结束页
START_PAGE = 2  # 例如，从第2页开始
END_PAGE = 5    # 例如，爬取到第5页结束 (包含第5页)
# -----------------

def fetch_daren_data_by_page(page_num: int) -> Dict[str, Any]:
    """
    模拟 cURL 请求，从巨量星图获取指定页码的达人数据。

    Args:
        page_num (int): 要获取的页码。

    Returns:
        dict: 包含达人数据的 JSON 响应。
    """
    url = "https://agent.oceanengine.com/star/mirror/gw/api/gsearch/search_for_author_square"

    # 从 1.txt 文件中提取的关键 Headers
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'agw-js-conv': 'str',
        'content-type': 'application/json',
        'origin': 'https://agent.oceanengine.com',
        'priority': 'u=1, i',
        'referer': 'https://agent.oceanengine.com/admin/star-agent/vue2/market',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'x-login-source': '1',
        'x-tt-possess-scene': '2',
        'x-tt-possess-star-id': '1843934177451019',
        # 使用 1.txt 中 -b 参数后的完整 Cookie 字符串
        'cookie': 'passport_csrf_token=33f5045ce4fe4ba2e09cccbec4b1e17f; passport_csrf_token_default=33f5045ce4fe4ba2e09cccbec4b1e17f; s_v_web_id=verify_mfuljt01_gF8mZL5R_1KOh_4rGm_8J7j_KIWAeP3JgrR7; ttwid=1%7CvpsigHXS7IvNfJeWE0nhrw6JYtkdmbswloHzF3Z5CJw%7C1758513533%7C72930dea96afc3501c158787f6dc2760dfb95733d7bdf589766a3baafb9007e5; ttcid=f12eab976ad3485b86a9acd966469e8473; tt_scid=.dSzIFCs3b4XkxbN1bxgMIxNH71rPI3vBAYx8.g9I5tgtF18kFtcs3JRYC4JenN26caa; passport_mfa_token=CjETG%2Bc5U5O8x3zViwk%2FZnTvz%2FTL8fyE%2B%2F4rly8mAkaTu8YwbbKYer1Gl8YAR1voqacKGkoKPAAAAAAAAAAAAABPgX8WhRcjEfGJUyvhveKLGoWjdhSbTcCBFexkWZxoODWE70ht5LYy62ENElBj4WBYiBD17PwNGPax0WwgAiIBA01KXlA%3D; d_ticket=ea4bcb3f8b00727dfff456d42d37311050ab0; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sso_uid_tt=9b55e6674c0feb81917302882313e13a; sso_uid_tt_ss=9b55e6674c0feb81917302882313e13a; toutiao_sso_user=a0fb0fe8655c45aec723842b573ab98b; toutiao_sso_user_ss=a0fb0fe8655c45aec723842b573ab98b; sid_ucp_sso_v1=1.0.0-KDE2MWFkZGI4Y2VkMTBmZmNlYmI3MDNhMmJhNzBmOGQ5YjIzNGJjZjcKHwipvsCV9qyEAhCMk8PGBhiwDyAMMJzX2MMGOAFA6wcaAmxmIiBhMGZiMGZlODY1NWM0NWFlYzcyMzg0MmI1NzNhYjk4Yg; ssid_ucp_sso_v1=1.0.0-KDE2MWFkZGI4Y2VkMTBmZmNlYmI3MDNhMmJhNzBmOGQ5YjIzNGJjZjcKHwipvsCV9qyEAhCMk8PGBhiwDyAMMJzX2MMGOAFA6wcaAmxmIiBhMGZiMGZlODY1NWM0NWFlYzcyMzg0MmI1NzNhYjk4Yg; odin_tt=5822bd4aad9df0039fdcd0f0fda98c987e8d1112e4cb9a1b43301650475aa15345b36143a0778bf55fcd38bb5a1fe590d7b4b22f7b113e8c40b6fc6a0e16702a; sid_guard=e061eee277459504379f60e7d44dc144%7C1758513549%7C5184001%7CFri%2C+21-Nov-2025+03%3A59%3A10+GMT; uid_tt=7cabd613d640b48b5dbebd349c0e51de; uid_tt_ss=7cabd613d640b48b5dbebd349c0e51de; sid_tt=e061eee277459504379f60e7d44dc144; sessionid=e061eee277459504379f60e7d44dc144; sessionid_ss=e061eee277459504379f60e7d44dc144; session_tlb_tag=sttt%7C1%7C4GHu4ndFlQQ3n2Dn1E3BRP________-h3Myfxdg2qHlOQuuBXl495_QB5EuSej-FB7whms824sQ%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGRhZjk3YmRiYjMwZDRlZmM5OWYxMzM2ZjZlZmE2OWIyMmZjOWZmODUKGQipvsCV9qyEAhCNk8PGBhiwDyAMOAFA6wcaAmxmIiBlMDYxZWVlMjc3NDU5NTA0Mzc5ZjYwZTdkNDRkYzE0NA; ssid_ucp_v1=1.0.0-KGRhZjk3YmRiYjMwZDRlZmM5OWYxMzM2ZjZlZmE2OWIyMmZjOWZmODUKGQipvsCV9qyEAhCNk8PGBhiwDyAMOAFA6wcaAmxmIiBlMDYxZWVlMjc3NDU5NTA0Mzc5ZjYwZTdkNDRkYzE0NA; gd_random=eyJtYXRjaCI6dHJ1ZSwicGVyY2VudCI6MC44MDc0Njc1NzA2NTg4NzI5fQ==.B3L/nSHH1P9E2lIR13hNSMLvsVNCdpMpMrLz9MdUimk=; x-web-secsdk-uid=d60bf1a3-ba3c-4cfb-b7b1-83c3cfb2f85f; acsessionid=802dfc49df404352b359dfd8965f1ce0'
    }

    # 从 1.txt 文件中提取的 POST 数据，并动态修改页码
    payload = {
        "scene_param": {
            "platform_source": 1,
            "search_scene": 1,
            "display_scene": 1,
            "marketing_target": 1,
            "task_category": 1,
            "first_industry_id": 0,
            "task_status": 3
        },
        "search_param": {
            "seach_type": 2
        },
        "sort_param": {
            "sort_type": 2,
            "sort_field": {
                "field_name": "score"
            }
        },
        "page_param": {
            "page": page_num,  # 动态设置页码
            "limit": 20
        },
        "attribute_filter": [
            {
                "field": {
                    "field_name": "tag_level_two"
                },
                "field_value": "[2]"
            },
            {
                "field": {
                    "field_name": "price_by_video_type__ge",
                    "rel_id": "2"
                },
                "field_value": "0"
            }
        ]
    }

    try:
        print(f"正在请求第 {page_num} 页数据...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # 如果响应状态码不是200，将抛出异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求第 {page_num} 页失败: {e}")
        return {}

def parse_author_data(author: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析单个达人的数据，提取我们关心的字段。

    Args:
        author (dict): 原始的达人数据字典。

    Returns:
        dict: 提取后的达人数据。
    """
    attr_data = author.get('attribute_datas', {})
    task_info = author.get('task_infos', [{}])[0]  # 取第一个任务信息
    price_info = task_info.get('price_infos', [{}])[0]  # 取第一个报价信息

    # 提取核心字段
    parsed_data = {
        "达人ID (star_id)": author.get('star_id', ''),
        "昵称 (nick_name)": attr_data.get('nick_name', ''),
        "粉丝数 (follower)": attr_data.get('follower', ''),
        "所在地 (city)": attr_data.get('city', ''),
        "近30天平均播放量 (vv_median_30d)": attr_data.get('vv_median_30d', ''),
        "近30天互动率 (interact_rate_within_30d)": attr_data.get('interact_rate_within_30d', ''),
        "报价 (price)": price_info.get('price', ''),
        "星图指数 (star_index)": attr_data.get('star_index', ''),
        "电商等级 (author_ecom_level)": attr_data.get('author_ecom_level', ''),
        "内容主题标签 (content_theme_labels_180d)": attr_data.get('content_theme_labels_180d', ''),
    }
    return parsed_data

def save_to_csv(data: List[Dict[str, Any]], filename: str = "daren_data_test.csv"):
    """
    将解析后的数据保存到 CSV 文件。

    Args:
        data (list): 达人数据列表。
        filename (str): 保存的文件名。
    """
    if not data:
        print("没有数据可保存。")
        return

    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = data[0].keys()  # 使用第一个字典的键作为表头
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"数据已成功保存到 '{filename}'")

def main():
    """
    主函数：执行多页数据抓取、解析和保存。
    """
    print("开始测试爬取达人数据...")

    all_parsed_authors = []  # 用于存储所有页面的数据

    # 循环爬取从 START_PAGE 到 END_PAGE 页的数据
    for page in range(START_PAGE, END_PAGE + 1):
        # 1. 获取数据
        raw_data = fetch_daren_data_by_page(page)

        if not raw_data:
            print(f"第 {page} 页数据获取失败，跳过此页。")
            continue

        # 2. 检查请求是否成功
        if raw_data.get('base_resp', {}).get('status_code') != 0:
            print(f"第 {page} 页 API 返回错误: {raw_data.get('base_resp', {}).get('status_message')}")
            continue

        # 3. 解析数据
        authors = raw_data.get('authors', [])
        parsed_authors = [parse_author_data(author) for author in authors]

        print(f"第 {page} 页成功获取并解析了 {len(parsed_authors)} 位达人数据。")
        all_parsed_authors.extend(parsed_authors)  # 将当前页数据添加到总列表中

        # 检查是否还有更多数据，如果没有则提前退出循环
        has_more = raw_data.get('pagination', {}).get('has_more', False)
        if not has_more:
            print("已到达最后一页，停止爬取。")
            break

    print(f"总共成功获取并解析了 {len(all_parsed_authors)} 位达人数据。")

    # 4. 保存到 CSV
    save_to_csv(all_parsed_authors)

    print("多页数据爬取测试完成！")

if __name__ == "__main__":
    main()