import requests
from bs4 import BeautifulSoup
import time

# 基础网址
BASE_URL = "https://zh.v2nodes.com"

# 需要抓取的页面 URL 列表（例如，第 1 页到第 3 页）
PAGES = [
    "https://zh.v2nodes.com/?page=1",
    "https://zh.v2nodes.com/?page=2",
    "https://zh.v2nodes.com/?page=3"
]

# 用于提取每个服务器页面的基本信息
def extract_server_info(server_url):
    # 获取服务器页面的内容
    response = requests.get(server_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 查找包含配置信息的 div 标签
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
                print(config)  # 打印配置信息
            else:
                print(f"未能提取配置：{server_url}")
            
            # 给服务器请求加个延时，避免过于频繁的访问
            time.sleep(1)  # 暂停 1 秒钟

    # 输出所有提取的配置
    print("\n所有提取的配置信息：")
    for config in all_server_configs:
        print(config)

if __name__ == "__main__":
    main()
