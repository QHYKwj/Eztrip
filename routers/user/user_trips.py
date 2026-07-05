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


@router.post("/{trip_id}/fork")
async def fork_trip(
        trip_id: int,
        user_id: int = Query(..., description="当前执行复刻操作的用户 user_id")
):
    """
    一键复刻（Fork）行程：深度复制 trip 主表、trip_day_plan 和 trip_day_item
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        # 开启事务
        db_conn.start_transaction()
        cursor = db_conn.cursor(dictionary=True)

        # 1. 查询原行程主信息
        cursor.execute("SELECT * FROM trip WHERE trip_id = %s", (trip_id,))
        old_trip = cursor.fetchone()
        if not old_trip:
            raise HTTPException(status_code=404, detail="原行程不存在")

        # 不能自己复刻自己的行程（可选判断，防呆设计）
        if int(old_trip["owner_user_id"]) == int(user_id):
            raise HTTPException(status_code=400, detail="您已经是该行程的创建者，无需复刻")

        # 2. 插入新行程主表 (默认转为私有草稿或发起的行程)
        new_title = f"{old_trip['title']} (复刻)"
        sql_insert_trip = """
            INSERT INTO trip (owner_user_id, title, destination, start_date, end_date, class, remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(sql_insert_trip, (
            user_id,
            new_title,
            old_trip["destination"],
            old_trip["start_date"],
            old_trip["end_date"],
            old_trip.get("class", 1),
            old_trip.get("remarks")
        ))
        new_trip_id = cursor.lastrowid

        # 3. 查询原行程的每日规划 (trip_day_plan)
        cursor.execute("SELECT * FROM trip_day_plan WHERE trip_id = %s ORDER BY day_index ASC", (trip_id,))
        old_day_plans = cursor.fetchall() or []

        # 记录 旧 day_plan_id -> 新 day_plan_id 的映射字典
        day_plan_map = {}

        for dp in old_day_plans:
            sql_insert_day = """
                INSERT INTO trip_day_plan (trip_id, day_index, plan_date, note)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(sql_insert_day, (
                new_trip_id,
                dp["day_index"],
                dp.get("plan_date"),
                dp.get("note")
            ))
            day_plan_map[dp["id"]] = cursor.lastrowid

        # 4. 如果存在每日规划，批量复制每天的具体节点 (trip_day_item)
        if day_plan_map:
            old_day_ids = list(day_plan_map.keys())
            # 拼接 IN (%s, %s...) 语句
            placeholders = ",".join(["%s"] * len(old_day_ids))
            cursor.execute(f"SELECT * FROM trip_day_item WHERE day_plan_id IN ({placeholders}) ORDER BY sort_order ASC", tuple(old_day_ids))
            old_items = cursor.fetchall() or []

            for item in old_items:
                new_day_id = day_plan_map.get(item["day_plan_id"])
                if new_day_id:
                    sql_insert_item = """
                        INSERT INTO trip_day_item (day_plan_id, title, place_type, sort_order)
                        VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(sql_insert_item, (
                        new_day_id,
                        item["title"],
                        item.get("place_type"),
                        item.get("sort_order", 1)
                    ))

        # 提交整个事务
        db_conn.commit()

        return {
            "message": "复刻成功！已添加到您的行程列表中",
            "new_trip_id": new_trip_id
        }

    except HTTPException:
        if db_conn:
            db_conn.rollback()
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"复刻行程失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()