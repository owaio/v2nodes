import requests
import base64

def generate_country_link(country_abbr):
    base_url = "https://www.v2nodes.com/subscriptions/country/"
    return base_url + country_abbr.lower() + "/"

# 国家缩写列表
countries = [
    "AQ", "AR", "AU", "AT", "BH", "BY", "BE", "BO", "BR", "BG",
    "CA", "CN", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HK",
    "HU", "IS", "IN", "IR", "IE", "IL", "IT", "JP", "KZ", "KE", "LV",
    "LT", "LU", "MX", "MD", "MA", "NP", "NG", "NO", "PL", "PR", "RO",
    "RU", "RS", "SG", "SK", "KR", "ES", "SE", "CH", "TW", "TH", "NL",
    "TR", "UA", "GB", "AE", "US", "VN"
]

def fetch_country_data(country_abbr):
    url = generate_country_link(country_abbr)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text  # 返回页面内容
        else:
            return None  # 如果没有成功获取数据，返回 None
    except requests.exceptions.RequestException as e:
        return None  # 请求失败时返回 None

def decode_base64(encoded_str):
    try:
        # Base64 解码
        decoded_data = base64.b64decode(encoded_str).decode('utf-8')
        return decoded_data
    except Exception as e:
        return None  # 解码失败时返回 None

# 获取每个国家的页面内容并解码
decoded_country_data = []
for country in countries:
    country_data = fetch_country_data(country)
    
    # 检查是否成功获取页面数据
    if country_data:
        # 假设页面数据中包含 Base64 编码的字符串
        # 这里可以根据页面的具体结构进行调整
        if "vless://" in country_data:  # 检查页面中是否包含 vless:// 或 ss:// 格式的数据
            decoded_country_data.append(country_data.strip())  # 直接添加这个行数据
        
        # 检查是否包含 Base64 编码数据
        elif "dmxlc3M6" in country_data:  # 假设 Base64 编码字符串以 "dmxlc3M6" 开头
            start_index = country_data.find("dmxlc3M6")  # 获取 Base64 编码数据的起始位置
            end_index = country_data.find("=", start_index) + 1  # 获取 Base64 编码数据的结束位置
            
            # 提取 Base64 编码数据并解码
            base64_encoded_str = country_data[start_index:end_index]
            decoded_str = decode_base64(base64_encoded_str)
            
            # 如果成功解码，添加解码后的数据到列表中
            if decoded_str:
                decoded_country_data.append(decoded_str)

# 输出所有解码后的数据，每条信息换行分隔
if decoded_country_data:
    output = "\n".join(decoded_country_data)
    print(output)
