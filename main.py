# main.py
from fastapi import FastAPI
import uvicorn
from settings import SERVER_HOST, SERVER_PORT

# 导入配置
from config.connect_db import connect_db

# 进入后端网址： http://127.0.0.1:8000/docs
# 导入路由
from routers import login
from routers import register
from routers import change_password
app = FastAPI(title="FastAPI Login Example")

# 注册登录路由
app.include_router(login.router)
app.include_router(register.register_router)
app.include_router(change_password.router)

# 使用示例
if __name__ == "__main__":
    db_conn = connect_db()
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
    if db_conn:
        db_conn.close()
    
