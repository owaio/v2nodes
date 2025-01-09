import os
import requests
from bs4 import BeautifulSoup
import time
import json
import base64
from concurrent.futures import ThreadPoolExecutor
import logging
from tenacity import retry, stop_after_attempt, wait_fixed

# -------------------------- 配置抓取部分 --------------------------
BASE_URL = "https://zh.v2nodes.com"
PAGE_START = 8
PAGE_END = 20
PAGES = [f"{BASE_URL}/?page={i}" for i in range(PAGE_START, PAGE_END + 1)]
GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')
GIST_ID = os.getenv('MY_GIST_ID')

if not GITHUB_TOKEN:
    raise ValueError("环境变量 'MY_GITHUB_TOKEN' 未设置！")

# 设置日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_base64(data):
    """验证 Base64 数据是否合法"""
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, data))

def extract_server_info(server_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(server_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        config_div = soup.find("textarea", {"id": "config"})
        return config_div.get("data-config") if config_div else None
    except Exception as e:
        logging.error(f"提取服务器信息失败: {server_url}, 错误: {e}")
        return None

def extract_server_links(page_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(page_url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return [
            f"{BASE_URL}/servers/{server.get('data-id')}/"
            for server in soup.find_all("div", class_="col-md-12 servers")
            if server.get("data-id")
        ]
    except Exception as e:
        logging.error(f"提取服务器链接失败: {page_url}, 错误: {e}")
        return []

def upload_to_gist(content, gist_id=None):
    url = f"https://api.github.com/gists/{gist_id}" if gist_id else "https://api.github.com/gists"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    gist_data = {
        "description": "V2Nodes Server Configurations",
        "public": True,
        "files": {"V2Nodes_config.txt": {"content": content}}
    }

    try:
        response = requests.patch(url, headers=headers, data=json.dumps(gist_data)) if gist_id else requests.post(url, headers=headers, data=json.dumps(gist_data))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"上传 Gist 失败: {e}")
        return {}

def fetch_country_data(country_abbr):
    url = f"https://www.v2nodes.com/subscriptions/country/{country_abbr.lower()}/"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"获取国家数据失败: {url}, 错误: {e}")
        return ""

def decode_base64_data(data):
    try:
        if not data or not validate_base64(data):
            raise ValueError("无效的 Base64 数据")
        return base64.urlsafe_b64decode(data + '==').decode('utf-8')
    except Exception as e:
        logging.error(f"解码 Base64 数据失败: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def check_gist_access(gist_id):
    url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    if response.status_code == 404:
        raise ValueError("Gist ID 不存在或没有访问权限！")

def process_page(page):
    server_links = extract_server_links(page)
    configs = []
    for server_url in server_links:
        config = extract_server_info(server_url)
        if config:
            configs.append(config)
    return configs

def main():
    all_server_configs = []

    # 第一部分：抓取 V2Nodes 服务器配置
    max_workers = min(32, (os.cpu_count() or 1) * 5)  # 根据硬件环境调整线程数
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_page, PAGES)
        for config_list in results:
            all_server_configs.extend(config_list)

    # 第二部分：抓取国家对应的链接并进行解码
    countries = [
        "AQ", "AR", "AU", "AT", "BH", "BY", "BE", "BO", "BR", "BG",
        "CA", "CN", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HK"
    ]

    for country in countries:
        data = fetch_country_data(country)
        if "vless://" in data:
            try:
                base64_data = data.split("vless://", 1)[1].split("#", 1)[0]
                decoded_data = decode_base64_data(base64_data)
                if decoded_data:
                    all_server_configs.append(decoded_data)
            except (IndexError, ValueError) as e:
                logging.error(f"处理数据时出错: {country}, 错误: {e}")

    # 合并所有配置并上传到 Gist
    content = "\n".join(all_server_configs)

    if GIST_ID:
        check_gist_access(GIST_ID)

    gist_response = upload_to_gist(content, GIST_ID)

    if gist_response.get('html_url'):
        logging.info(f"配置信息已上传到 GitHub Gist: {gist_response['html_url']}")
    else:
        logging.error("上传失败")

if __name__ == "__main__":
    main()
