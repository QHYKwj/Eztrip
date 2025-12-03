# main.py
from fastapi import FastAPI
import uvicorn
from settings import SERVER_HOST, SERVER_PORT
from fastapi.middleware.cors import CORSMiddleware
# 导入配置
from config.connect_db import connect_db

# 进入后端网址： http://127.0.0.1:8000/docs
# 导入路由
from routers import login
from routers import register
from routers import change_password
from routers import finduser
from routers import create_trip
from routers import collect_trip
from routers import map
app = FastAPI(title="FastAPI Login Example")


# 注册登录路由
app.include_router(login.router)
app.include_router(register.router)
app.include_router(change_password.router)
app.include_router(finduser.router)
app.include_router(create_trip.router)
app.include_router(collect_trip.router)
app.include_router(map.router)
# 使用示例
if __name__ == "__main__":
    db_conn = connect_db()
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
    if db_conn:
        db_conn.close()

