# main.py
from fastapi import FastAPI
import uvicorn
from settings import SERVER_HOST, SERVER_PORT

# 导入配置
from config.connect_db import connect_db

# 进入后端网址： http://127.0.0.1:8000/docs
# 导入路由
from routers.user import user,user_trips
from routers.innessory import finduser
from routers.notice import notice
from routers.default import trips
from routers.user_message import notifications
from routers.collect import collect_trip
from routers.admin import admin
from routers.trip_detail import trip,trip_plan
from routers.model import model_api 
app = FastAPI(title="FastAPI Login Example")


# 注册登录路由
app.include_router(user.router)#用户的登录注册等逻辑
app.include_router(finduser.router)#？

# 行程路由
app.include_router(trips.router)#welcome页面展示所有公开的行程和模板
app.include_router(user_trips.router)#内有创建和展示用户的所有行程
app.include_router(collect_trip.router)#收藏和取消收藏逻辑


# 公告路由
app.include_router(notifications.router)#用户是否已读

# 管理员相关路由
app.include_router(admin.router)
app.include_router(notice.router)#管理员的公告操作
# 大模型相关路由
app.include_router(model_api.router)#大模型接口

#trip.vue
app.include_router(trip.router)#行程具体的信息和编辑
app.include_router(trip_plan.router)#行程具体的信息和编辑

# for r in app.routes:
#     if hasattr(r, "methods"):
#         print(r.path, r.methods)

# 启动服务器
if __name__ == "__main__":
    db_conn = connect_db()
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
    if db_conn:
        db_conn.close()

