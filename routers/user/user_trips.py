# routers/trip.py
from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional
from pydantic import BaseModel, Field
from config.connect_db import connect_db

# 创建一个新的APIRouter实例
router = APIRouter(prefix="/api/user/trips",tags=["user_trips"])

CLASS_MAP = {
    1: "休闲",
    2: "美食",
    3: "商务",
    4: "家庭",
}

@router.get("/list")
async def list_trips(user_id: int = Query(..., description="当前登录用户 user_id")):
    """
    返回当前用户相关的行程列表：
    - 用户自己创建的行程（trip.owner_user_id = user_id）
    - 用户收藏的行程（trip_favorite.user_id = user_id）
    每条记录包含：
    - is_collected（是否被当前用户收藏）
    - class / class_text（分类）
    - days（end_date - start_date + 1）
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        sql = """
            SELECT
                t.trip_id,
                t.title,
                t.destination,
                t.start_date,
                t.end_date,
                t.owner_user_id,
                t.class AS class_type,
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

        trips: List[Dict[str, Any]] = []
        for r in rows:
            # 计算天数：包含首尾
            days = None
            try:
                if r["start_date"] and r["end_date"]:
                    days = (r["end_date"] - r["start_date"]).days + 1
            except Exception:
                days = None

            cls = r.get("class_type")
            cls_int = int(cls) if cls is not None else None

            trips.append({
                "trip_id": r["trip_id"],
                "trip_name": r["title"],
                "destination": r["destination"],
                "start_date": str(r["start_date"]),
                "end_date": str(r["end_date"]),
                "days": days,  # ✅ 新增
                "owner_user_id": r["owner_user_id"],
                "is_collected": bool(r["is_collected"]),
                "class": cls_int,  # ✅ 新增
                "class_text": CLASS_MAP.get(cls_int) if cls_int else None,  # ✅ 新增
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


from typing import Optional, Dict, Any
import json
class TripCreateBody(BaseModel):
    owner_user_id: int
    title: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    is_public: int = 0
    class_type: int = Field(..., ge=1, le=4)
    remarks: Optional[Dict[str, Any]] = None  # ✅ 成功接收前端传来的字典

@router.post("/create")
async def create_trip(body: TripCreateBody):
    """
    创建一个新的行程。
    写入 remarks（可选，若包含则转 JSON 存入）。
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        if body.class_type not in CLASS_MAP:
            raise HTTPException(status_code=400, detail="Invalid class_type")

        # 🌟 序列化 remarks
        default_remarks = {
            "overview": "", "best_time": "", "budget": "",
            "accommodation": "", "food": "", "packing": [], "tips": []
        }
        final_remarks = body.remarks if body.remarks else default_remarks
        remarks_json_str = json.dumps(final_remarks, ensure_ascii=False)

        # ✅ 致命错误修复：对保留关键字 class 添加反引号 `class`
        sql = """
            INSERT INTO trip
              (owner_user_id, title, destination, start_date, end_date, `class`, publish_status, is_public, remarks)
            VALUES
              (%s, %s, %s, %s, %s, %s, 'draft', %s, %s);
        """
        cursor.execute(sql, (
            body.owner_user_id,
            body.title,
            body.destination,
            body.start_date,
            body.end_date,
            body.class_type,
            body.is_public,
            remarks_json_str  # ✅ 落库时转为 JSON 字符串
        ))

        trip_id = cursor.lastrowid
        db_conn.commit()

        return {
            "message": "Trip created successfully",
            "trip_id": trip_id,
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