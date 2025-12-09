import pymysql
pymysql.install_as_MySQLdb()
import mysql.connector
from mysql.connector import Error
import json
import os

# 获取json配置
def get_db_config():
    # 获取当前文件的目录
    current_dir = os.path.dirname(__file__)
    # 构建到项目根目录下 setting.json 的路径
    config_file = os.path.join(current_dir, '..', 'setting.json')
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f).get("mysql", {})
    except FileNotFoundError:
        print(f"错误：找不到配置文件 {config_file}")
        print("请确保 setting.json 文件存在于项目根目录")
        return None
    except json.JSONDecodeError as e:
        print(f"错误：setting.json 格式不正确 - {e}")
        return None

# 链接MySQL数据库
def connect_db():
    db_config = get_db_config()
    print(db_config)
    try:
        connection = mysql.connector.connect(
            host=db_config.get("host"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            database=db_config.get("database"),
            port=db_config.get("port", 3306)
        )
        print("Successfully connected to the database")
        return connection
    except Error as e:
        print(f"Connection failed: {e}")
        return None