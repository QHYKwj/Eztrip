import requests

url = "http://127.0.0.1:8000/api/create_trip"
data = {
    "user_id": 4,
    "trip_name":"南京一日游",
    "destination":"南京",
    "start_date":"2025-10-21",
    "end_date":"2025-10-22",
    "create_time":"2025-10-21 12:00:05"
}

# 发送 POST 请求
response = requests.post(url, data=data)

print("状态码:", response.status_code)
print("响应内容:", response.text)
print("JSON 响应:", response.json())