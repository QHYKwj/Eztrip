# main.py
from fastapi import FastAPI
import uvicorn
from settings import SERVER_HOST, SERVER_PORT

# 导入配置
from config.connect_db import connect_db

# 进入后端网址： http://127.0.0.1:8000/docs
# 导入路由
from routers.user import change_password, profile, register, login
from routers.innessory import create_trip, collect_trip, finduser
from routers.trip_detail.map import router as map_router
from routers.trip_detail.trip_details import router as trip_detail_router
from routers.trip_detail.trip_update import router as trip_update_router
from routers.notice import create_notice
from routers.default import trips
from routers.user_message import notifications
from routers import trip
from routers.collect import trip_favourite_count
app = FastAPI(title="FastAPI Login Example")


# 注册登录路由
app.include_router(login.router)
app.include_router(register.router)
app.include_router(change_password.router)
app.include_router(finduser.router)
app.include_router(create_trip.router)
app.include_router(collect_trip.router)
app.include_router(map_router)
app.include_router(profile.router)
app.include_router(create_notice.router)
app.include_router(trips.router)
app.include_router(notifications.router)
app.include_router(trip.router, prefix="/api/trip", tags=["trip"])
# 使用示例
if __name__ == "__main__":
    db_conn = connect_db()
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
    if db_conn:
        db_conn.close()

