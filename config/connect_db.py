import mysql.connector
from mysql.connector import Error
import json

# 获取json配置
def get_db_config(config_file="setting.json"):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f).get("mysql", {})

# 链接MySQL数据库
def connect_db():
    db_config = get_db_config()
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
