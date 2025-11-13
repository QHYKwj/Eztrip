# main.py
from fastapi import FastAPI
import uvicorn
from settings import SERVER_HOST, SERVER_PORT

# 导入路由
from routers import login

app = FastAPI(title="FastAPI Login Example")

# 注册登录路由
app.include_router(login.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
