# routers/trip.py
from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional
from config.connect_db import connect_db

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.get("")
async def list_trips(user_id: int = Query(..., description="当前登录用户 user_id")):
    """
    返回当前用户相关的行程列表：
    - 用户自己创建的行程（trip.owner_user_id = user_id）
    - 用户收藏的行程（trip_favorite.user_id = user_id）
    每条记录包含 is_collected 字段（是否被当前用户收藏）
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        # 查询：用户的自有行程 + 用户收藏的行程
        # 使用 LEFT JOIN + 条件限制当前 user 收藏记录
        sql = """
            SELECT
                t.trip_id,
                t.title,
                t.destination,
                t.start_date,
                t.end_date,
                t.owner_user_id,
                IF(tf.user_id IS NULL, 0, 1) AS is_collected
            FROM trip t
            LEFT JOIN trip_favorite tf
              ON t.trip_id = tf.trip_id
             AND tf.user_id = %s
            WHERE t.owner_user_id = %s
               OR tf.user_id IS NOT NULL
            ORDER BY t.trip_id ASC;
        """
        cursor.execute(sql, (user_id, user_id))
        rows = cursor.fetchall() or []

        # 转成前端友好格式
        trips = []
        for r in rows:
            trips.append({
                "trip_id": r["trip_id"],
                "trip_name": r["title"],  # 前端期望的字段名：trip_name
                "destination": r["destination"],
                "start_date": str(r["start_date"]),
                "end_date": str(r["end_date"]),
                "owner_user_id": r["owner_user_id"],
                "is_collected": bool(r["is_collected"]),
            })

        return trips

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行程列表失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()


@router.post("")
async def create_trip(
        owner_user_id: int = Form(...),
        title: str = Form(...),
        destination: str = Form(...),
        start_date: str = Form(...),  # 'YYYY-MM-DD'
        end_date: str = Form(...),    # 'YYYY-MM-DD'
        template_id: Optional[int] = Form(None),
):
    """
    创建一个新的行程（草稿状态）。
    可以和前端的 CreateTripDialog 对接。
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        sql = """
            INSERT INTO trip
              (owner_user_id, template_id, title, destination, start_date, end_date, publish_status)
            VALUES
              (%s, %s, %s, %s, %s, %s, 'draft');
        """
        cursor.execute(sql, (owner_user_id, template_id, title, destination, start_date, end_date))
        db_conn.commit()

        new_id = cursor.lastrowid

        return {
            "message": "Trip created successfully",
            "trip_id": new_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建行程失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
