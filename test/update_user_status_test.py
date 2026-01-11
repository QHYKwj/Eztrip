import requests

url = "http://127.0.0.1:8000/api/admin/update_user_status"
data = {
    "user_id": "2",
    "status": "active"
}

# 发送 POST 请求
response = requests.post(url, data=data)

print("状态码:", response.status_code)
print("响应内容:", response.text)
print("JSON 响应:", response.json())