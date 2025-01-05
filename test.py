import requests

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

# 获取每个国家的页面内容并合并结果
all_country_data = []
for country in countries:
    data = fetch_country_data(country)
    all_country_data.append(data)

# 输出所有数据，每个国家的内容之间用换行分隔
output = "\n".join(all_country_data)
print(output)
