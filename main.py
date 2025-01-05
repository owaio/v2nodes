import os
import requests
from bs4 import BeautifulSoup
import time
import json

# 基础网址
BASE_URL = "https://zh.v2nodes.com"

# 通过赋值的形式动态生成需要抓取的页面 URL 列表
PAGE_START = 1  # 起始页
PAGE_END = 3    # 结束页

PAGES = [f"{BASE_URL}/?page={i}" for i in range(PAGE_START, PAGE_END + 1)]

# 从环境变量中获取 GitHub Token 和 Gist ID
GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')  # 从环境变量中读取
GIST_ID = os.getenv('MY_GIST_ID')  # 从环境变量中读取

# 用于提取每个服务器页面的基本信息
def extract_server_info(server_url):
    # 获取服务器页面的内容
    response = requests.get(server_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找包含配置信息的 textarea 标签
    config_div = soup.find("textarea", {"id": "config"})
    
    # 提取 config 属性
    if config_div:
        return config_div.get("data-config")
    return None

# 获取页面中的服务器 ID 和链接
def extract_server_links(page_url):
    # 获取页面的内容
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找所有服务器项
    servers = soup.find_all("div", class_="col-md-12 servers")
    
    server_links = []
    for server in servers:
        # 提取服务器 ID
        server_id = server.get("data-id")
        if server_id:
            # 生成服务器页面的完整链接
            server_url = f"{BASE_URL}/servers/{server_id}/"
            server_links.append(server_url)
    
    return server_links

# 上传文件到 GitHub Gist
def upload_to_gist(content, gist_id=None):
    url = "https://api.github.com/gists"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 如果是更新 Gist
    if gist_id:
        url = f"https://api.github.com/gists/{gist_id}"
        # 获取现有 Gist 的信息
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch Gist: {response.text}")
        gist_data = response.json()
        gist_data['files']['server_configs.txt']['content'] = content
        response = requests.patch(url, headers=headers, data=json.dumps(gist_data))
    else:
        # 创建新的 Gist
        gist_data = {
            "description": "V2Nodes Server Configurations",
            "public": True,
            "files": {
                "server_configs.txt": {
                    "content": content
                }
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(gist_data))
    
    if response.status_code == 201:
        print(f"成功上传 Gist: {response.json()['html_url']}")
    else:
        print(f"上传失败，响应: {response.text}")

    return response.json()

# 主程序
def main():
    all_server_configs = []
    
    # 遍历所有页面
    for page in PAGES:
        print(f"正在抓取页面: {page}")
        
        # 获取当前页面中所有服务器链接
        server_links = extract_server_links(page)
        
        # 提取每个服务器的配置信息
        for server_url in server_links:
            print(f"正在抓取服务器: {server_url}")
            
            # 提取并打印服务器的配置信息
            config = extract_server_info(server_url)
            if config:
                all_server_configs.append(config)
                print(f"抓取到的配置: {config}")  # 打印配置信息
            else:
                print(f"未能提取配置：{server_url}")
            
            # 给服务器请求加个延时，避免过于频繁的访问
            time.sleep(1)  # 暂停 1 秒钟
    
    # 所有配置信息拼接成一个字符串
    content = "\n".join(all_server_configs)
    
    # 上传配置信息到 GitHub Gist
    gist_response = upload_to_gist(content, GIST_ID)
    
    if 'html_url' in gist_response:
        print(f"配置信息已上传到 GitHub Gist: {gist_response['html_url']}")
    else:
        print("上传失败", gist_response)

if __name__ == "__main__":
    main()
