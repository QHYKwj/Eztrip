import requests

url = "http://127.0.0.1:8000/api/admin/pending_review_count"


# 发送 GET 请求
response = requests.get(url)

print("状态码:", response.status_code)
print("响应内容:", response.text)
print("JSON 响应:", response.json())