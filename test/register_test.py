import requests

url = "http://127.0.0.1:8000/api/register/register"
data = {
    "username": "zhang4",
    "email": "zhanghz3@mail2.sysu.edu.cn",
    "password": "050129",
    "confirm_password": "050129",
}

# 发送 POST 请求
response = requests.post(url, data=data)

print("状态码:", response.status_code)
print("响应内容:", response.text)
print("JSON 响应:", response.json())