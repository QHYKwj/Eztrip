# Eztrip后端

## 环境要求

- Python 3.8+
- 依赖库请参考 `requirements.txt`

## 安装

1. 创建虚拟环境并激活：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 配置

项目配置文件位于 `settings.py`，可根据需要修改以下内容：

- `SERVER_HOST`：服务运行的主机地址。
- `SERVER_PORT`：服务运行的端口。
## 运行

启动后端：

```shell
python main.py
```

## 测试
后端测试在对应的url后+/docs即可测试
eg：http://127.0.0.1:8000/docs