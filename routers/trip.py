# routers/trip.py
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from config.connect_db import connect_db
from datetime import date

router = APIRouter()

# 1. 定义接收前端数据的模型 (Pydantic)
class TripCreate(BaseModel):
    tripName: str       # 对应前端的 title
    destination: str
    startDate: date
    endDate: date
    description: str = None # 数据库暂时没这个字段，先接收但不存
    tags: list = []       # 同上
    owner_user_id: int = 1  # 暂时默认是管理员(id=1)，后续可以从登录Token里获取

# 2. 创建行程的接口
@router.post("/create")
async def create_trip(trip: TripCreate):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # 简单的标签转换逻辑 (假设只能选一个主要标签，或者取第一个)
        # 1:休闲, 2:美食, 3:商务, 4:家庭
        class_val = None
        if trip.tags:
            first_tag = trip.tags[0]
            if "休闲" in first_tag: class_val = 1
            elif "美食" in first_tag: class_val = 2
            elif "商务" in first_tag: class_val = 3
            elif "家庭" in first_tag: class_val = 4

        # SQL 插入语句 (增加了 class 和 remarks)
        # 注意: 字段名 `class` 最好加反引号，防止 SQL 解析错误
        sql = """
            INSERT INTO trip
            (owner_user_id, title, destination, start_date, end_date, `class`, remarks, publish_status, is_public)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'draft', 1)
        """

        cursor.execute(sql, (
            trip.owner_user_id,
            trip.tripName,
            trip.destination,
            trip.startDate,
            trip.endDate,
            class_val,        # 对应 class
            trip.description  # 对应 remarks (前端的备注)
        ))

        conn.commit() # 提交事务
        new_trip_id = cursor.lastrowid # 获取新生成的 ID

        return {
            "message": "行程创建成功",
            "trip_id": new_trip_id,
            "data": trip
        }

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# 3. 获取我的行程列表接口 (给侧边栏用的)
@router.get("/my_trips")
async def get_my_trips(user_id: int = 1):
    conn = connect_db()
    cursor = conn.cursor() # 默认返回元组，如果你想要字典，需要配置 DictCursor
    try:
        sql = "SELECT trip_id, title, destination FROM trip WHERE owner_user_id = %s ORDER BY created_at DESC"
        cursor.execute(sql, (user_id,))
        results = cursor.fetchall()

        # 手动把数据转成字典格式返回给前端
        trips = []
        for row in results:
            trips.append({
                "id": row[0],
                "title": row[1],
                "destination": row[2]
            })

        return {"trips": trips}
    finally:
        cursor.close()
        conn.close()