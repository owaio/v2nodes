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
            return f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def decode_base64(encoded_str):
    try:
        # Base64 解码
        decoded_data = base64.b64decode(encoded_str).decode('utf-8')
        return decoded_data
    except Exception as e:
        return f"Decoding failed: {e}"

# 获取每个国家的页面内容并解码
decoded_country_data = []
for country in countries:
    country_data = fetch_country_data(country)
    
    # 假设页面数据中包含 Base64 编码的字符串
    # 这里可以根据页面的具体结构进行调整
    if "dmxlc3M6" in country_data:  # 检查页面中是否包含 Base64 编码数据
        start_index = country_data.find("dmxlc3M6")  # 获取 Base64 编码数据的起始位置
        end_index = country_data.find("=", start_index) + 1  # 获取 Base64 编码数据的结束位置
        
        # 提取 Base64 编码数据并解码
        base64_encoded_str = country_data[start_index:end_index]
        decoded_str = decode_base64(base64_encoded_str)
        
        # 将解码后的信息添加到列表中
        decoded_country_data.append(decoded_str)
    else:
        decoded_country_data.append(f"No Base64 data found for {country}")

# 输出所有解码后的数据，每条信息换行分隔
output = "\n".join(decoded_country_data)
print(output)
