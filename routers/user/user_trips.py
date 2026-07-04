# routers/user/user_trips.py
from fastapi import APIRouter, HTTPException, Query, Form
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from config.connect_db import connect_db
import json

router = APIRouter(prefix="/api/user/trips", tags=["user_trips"])

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
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        # ✅ 查询中加入 t.is_ai
        sql = """
            SELECT
                t.trip_id,
                t.title,
                t.destination,
                t.start_date,
                t.end_date,
                t.owner_user_id,
                t.class AS class_type,
                t.is_ai,
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
                "days": days,
                "owner_user_id": r["owner_user_id"],
                "is_collected": bool(r["is_collected"]),
                "class": cls_int,
                "class_text": CLASS_MAP.get(cls_int) if cls_int else None,
                "is_ai": int(r["is_ai"]) if r.get("is_ai") is not None else 0, # ✅ 透传 is_ai
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


# ✅ TripCreateBody 增加 is_ai 字段，默认值为 0
class TripCreateBody(BaseModel):
    owner_user_id: int
    title: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    is_public: int = 0
    class_type: int = Field(..., ge=1, le=4)
    is_ai: int = 0   # ✅ 增加 AI 标识入参：1为AI生成，0为人工生成
    remarks: Optional[Dict[str, Any]] = None

@router.post("/create")
async def create_trip(body: TripCreateBody):
    """
    创建一个新的行程。
    写入 remarks 和 is_ai 字段。
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

        default_remarks = {
            "overview": "", "best_time": "", "budget": "",
            "accommodation": "", "food": "", "packing": [], "tips": []
        }
        final_remarks = body.remarks if body.remarks else default_remarks
        remarks_json_str = json.dumps(final_remarks, ensure_ascii=False)

        # ✅ SQL INSERT 中加入 is_ai
        sql = """
            INSERT INTO trip
              (owner_user_id, title, destination, start_date, end_date, `class`, is_ai, publish_status, is_public, remarks)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s);
        """
        cursor.execute(sql, (
            body.owner_user_id,
            body.title,
            body.destination,
            body.start_date,
            body.end_date,
            body.class_type,
            body.is_ai,          # ✅ 写入 is_ai
            body.is_public,
            remarks_json_str
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