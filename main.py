import os
import requests
from bs4 import BeautifulSoup
import time
import json

BASE_URL = "https://zh.v2nodes.com"
PAGE_START = 1
PAGE_END = 4
PAGES = [f"{BASE_URL}/?page={i}" for i in range(PAGE_START, PAGE_END + 1)]
GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')  # 从环境变量中读取
GIST_ID = os.getenv('MY_GIST_ID')  # 从环境变量中读取

def extract_server_info(server_url):
    response = requests.get(server_url)
    soup = BeautifulSoup(response.text, "html.parser")
    config_div = soup.find("textarea", {"id": "config"})
    if config_div:
        return config_div.get("data-config")
    return None

def extract_server_links(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    servers = soup.find_all("div", class_="col-md-12 servers")
    server_links = []
    for server in servers:
        server_id = server.get("data-id")
        if server_id:
            server_url = f"{BASE_URL}/servers/{server_id}/"
            server_links.append(server_url)
    return server_links

def upload_to_gist(content, gist_id=None):
    url = "https://api.github.com/gists"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    if gist_id:
        # 读取现有的 Gist 数据
        url = f"https://api.github.com/gists/{gist_id}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            gist_data = response.json()
            # 如果 Gist 中没有 V2Nodes_config.txt 文件，则添加该文件
            if 'V2Nodes_config.txt' not in gist_data['files']:
                gist_data['files']['V2Nodes_config.txt'] = {'content': content}
            else:
                gist_data['files']['V2Nodes_config.txt']['content'] = content
            response = requests.patch(url, headers=headers, data=json.dumps(gist_data))
        else:
            print(f"读取 Gist 时出错，状态码: {response.status_code}")
    else:
        # 创建新的 Gist
        gist_data = {
            "description": "V2Nodes Server Configurations",
            "public": True,
            "files": {
                "V2Nodes_config.txt": {
                    "content": content
                }
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(gist_data))

    # 这里添加详细的调试信息
    if response.status_code != 200 and response.status_code != 201:
        print(f"上传 Gist 失败，响应代码: {response.status_code}")
        print(f"响应内容: {response.text}")
    
    return response.json()

def main():
    all_server_configs = []
    for page in PAGES:
        print(f"正在抓取页面: {page}")
        server_links = extract_server_links(page)
        for server_url in server_links:
            print(f"正在抓取服务器: {server_url}")
            config = extract_server_info(server_url)
            if config:
                all_server_configs.append(config)
                print(config)
            else:
                print(f"未能提取配置：{server_url}")
            time.sleep(1)

    content = "\n".join(all_server_configs)
    gist_response = upload_to_gist(content, GIST_ID)

    if 'html_url' in gist_response:
        print(f"配置信息已上传到 GitHub Gist: {gist_response['html_url']}")
    else:
        print("上传失败", gist_response)

if __name__ == "__main__":
    main()
