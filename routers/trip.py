# routers/trip.py
from fastapi import APIRouter, HTTPException, Body,Query
from pydantic import BaseModel
from config.connect_db import connect_db
from datetime import date
from typing import Optional

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
            elif "冒险" in first_tag: class_val = 3
            elif "文化" in first_tag: class_val = 4

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

# ---------------------------------------------------------
# 新增：行程搜索/筛选接口
# ---------------------------------------------------------
@router.get("/search")
async def search_trips(
    destination: Optional[str] = None,
    style: Optional[str] = None,  # 接收前端传来的 'leisure', 'food' 等
    days: Optional[str] = None    # 接收前端传来的 '1', '2', '3', '4-7', '7+'
):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. 构建基础 SQL (只查公开的行程)
        sql = """
            SELECT
                trip_id, title, destination, start_date, end_date,
                class, remarks, avatar, username
            FROM trip
            JOIN user_info ON trip.owner_user_id = user_info.user_id
            WHERE is_public = 1
        """
        params = []

        # 2. 动态拼接筛选条件

        # --- A. 地点筛选 (模糊查询) ---
        if destination:
            sql += " AND destination LIKE %s"
            params.append(f"%{destination}%")

        # --- B. 风格筛选 (将英文转数字) ---
        style_map = {
            'leisure': 1,
            'food': 2,
            'adventure': 3,
            'culture': 4,
        }

        if style and style in style_map:
            sql += " AND class = %s"
            params.append(style_map[style])

        # --- C. 时间天数筛选 ---
        if days:
            duration_sql = "DATEDIFF(end_date, start_date) + 1"

            if days == '7+':
                sql += f" AND {duration_sql} > 7"
            elif '-' in days: # 处理 '4-7' 这种情况
                start_d, end_d = days.split('-')
                sql += f" AND {duration_sql} BETWEEN %s AND %s"
                params.append(start_d)
                params.append(end_d)
            else: # 处理单天 '1', '2', '3'
                sql += f" AND {duration_sql} = %s"
                params.append(days)

        # 按创建时间倒序排列
        sql += " ORDER BY trip.created_at DESC"

        # 3. 执行查询
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()

        # 4. 数据处理 (处理日期对象，防止JSON报错)
        trips = []
        for row in results:
            # 计算天数返回给前端展示用
            d_start = row['start_date']
            d_end = row['end_date']
            duration = (d_end - d_start).days + 1

            trips.append({
                "id": row['trip_id'],
                "title": row['title'],
                "destination": row['destination'],
                "startDate": d_start.isoformat(), # 转字符串
                "endDate": d_end.isoformat(),     # 转字符串
                "days": duration,
                "author": {
                    "name": row['username'],
                    "avatar": row['avatar'] or ""
                },
                "image": "" # 后面可以加封面图字段
            })

        return {"trips": trips}

    except Exception as e:
        print(f"Search Error: {e}")
        # 返回空列表而不是报错，体验更好
        return {"trips": []}
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------
# 新增：获取单个行程详情接口
# ---------------------------------------------------------
@router.get("/detail/{trip_id}")
async def get_trip_detail(trip_id: int):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # 查询行程信息，同时关联查询作者信息
        sql = """
            SELECT
                t.trip_id, t.title, t.destination, t.start_date, t.end_date,
                t.class, t.remarks, t.publish_status, t.is_public, t.owner_user_id,
                u.username, u.avatar
            FROM trip t
            JOIN user_info u ON t.owner_user_id = u.user_id
            WHERE t.trip_id = %s
        """
        cursor.execute(sql, (trip_id,))
        trip = cursor.fetchone()

        if not trip:
            raise HTTPException(status_code=404, detail="行程不存在")

        # 格式化日期
        if trip['start_date']: trip['start_date'] = trip['start_date'].isoformat()
        if trip['end_date']: trip['end_date'] = trip['end_date'].isoformat()

        return {"data": trip}

    except Exception as e:
        print(f"Get Detail Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()