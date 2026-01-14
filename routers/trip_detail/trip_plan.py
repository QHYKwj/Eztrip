# routers/trip_plan.py
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from config.connect_db import connect_db
from datetime import timedelta

router = APIRouter(prefix="/api/trip_plan", tags=["trip_plan"])


def to_str(d):
    return d.strftime("%Y-%m-%d") if d else None


@router.get("/get")
async def get_trip_plan(
        user_id: int = Query(...),
        trip_id: int = Query(...),
):
    """
    获取行程计划：
    - 不要求收藏才能看：只要 trip 可见（你可按需加权限）
    - 自动根据 trip.start_date/end_date 补齐 N 天（如果 trip_day_plan 缺数据就插空）
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 1) 取 trip 基本信息（用于算天数/日期）
        cursor.execute("""
            SELECT trip_id, owner_user_id, start_date, end_date
            FROM trip
            WHERE trip_id=%s
            LIMIT 1
        """, (trip_id,))
        trip = cursor.fetchone()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        start_date = trip["start_date"]
        end_date = trip["end_date"]
        total_days = (end_date - start_date).days + 1
        if total_days <= 0:
            raise HTTPException(status_code=400, detail="Invalid trip dates")

        # 2) 拉出已有 day_plan
        cursor.execute("""
            SELECT id, day_index, plan_date, note
            FROM trip_day_plan
            WHERE trip_id=%s
            ORDER BY day_index ASC
        """, (trip_id,))
        day_rows = cursor.fetchall() or []

        # 建 day_index -> day_plan
        day_map = {int(r["day_index"]): r for r in day_rows}

        # 3) 补齐缺失的天（可选：也可以只返回已有的）
        for di in range(1, total_days + 1):
            if di not in day_map:
                plan_date = start_date + timedelta(days=di - 1)
                cursor.execute("""
                    INSERT INTO trip_day_plan (trip_id, day_index, plan_date, note)
                    VALUES (%s, %s, %s, %s)
                """, (trip_id, di, plan_date, None))
                db_conn.commit()
                day_id = cursor.lastrowid
                day_map[di] = {"id": day_id, "day_index": di, "plan_date": plan_date, "note": None}

        # 4) 拉出所有 item
        day_ids = [day_map[di]["id"] for di in range(1, total_days + 1)]
        format_ids = ",".join(["%s"] * len(day_ids))
        cursor.execute(f"""
            SELECT id, day_plan_id, title, place_type, sort_order
            FROM trip_day_item
            WHERE day_plan_id IN ({format_ids})
            ORDER BY day_plan_id ASC, sort_order ASC, id ASC
        """, tuple(day_ids))
        item_rows = cursor.fetchall() or []

        items_by_day = {}
        for it in item_rows:
            items_by_day.setdefault(int(it["day_plan_id"]), []).append({
                "id": int(it["id"]),
                "title": it["title"],
                "place_type": it.get("place_type"),
                "sort_order": int(it["sort_order"]),
            })

        # 5) 组装返回
        days = []
        for di in range(1, total_days + 1):
            r = day_map[di]
            day_id = int(r["id"])
            days.append({
                "day_index": di,
                "plan_date": to_str(r.get("plan_date")),
                "note": r.get("note"),
                "items": items_by_day.get(day_id, []),
            })

        return {
            "trip_id": int(trip_id),
            "days": days,
            "total_days": total_days
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行程计划失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.post("/item/add")
async def add_day_item(
        user_id: int = Body(...),
        trip_id: int = Body(...),
        day_index: int = Body(...),
        title: str = Body(...),
        place_type: Optional[str] = Body(None),
):
    db_conn = None
    cursor = None
    try:
        title = (title or "").strip()
        if not title:
            raise HTTPException(status_code=400, detail="title 不能为空")

        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 权限：只有 owner 才能编辑计划（你想收藏者也能写的话这里放开）
        cursor.execute("SELECT owner_user_id FROM trip WHERE trip_id=%s", (trip_id,))
        t = cursor.fetchone()
        if not t:
            raise HTTPException(status_code=404, detail="Trip not found")
        if int(t["owner_user_id"]) != int(user_id):
            raise HTTPException(status_code=403, detail="无权限编辑该行程计划")

        # 找 day_plan_id
        cursor.execute("""
            SELECT id FROM trip_day_plan WHERE trip_id=%s AND day_index=%s LIMIT 1
        """, (trip_id, day_index))
        d = cursor.fetchone()
        if not d:
            raise HTTPException(status_code=404, detail="Day plan not found")
        day_plan_id = int(d["id"])

        # 计算 sort_order = 当前最大 + 1
        cursor.execute("""
            SELECT COALESCE(MAX(sort_order), 0) AS mx
            FROM trip_day_item
            WHERE day_plan_id=%s
        """, (day_plan_id,))
        mx = int(cursor.fetchone()["mx"])
        new_order = mx + 1

        cursor.execute("""
            INSERT INTO trip_day_item (day_plan_id, title, place_type, sort_order)
            VALUES (%s, %s, %s, %s)
        """, (day_plan_id, title, place_type, new_order))
        db_conn.commit()

        return {
            "code": 200,
            "message": "添加成功",
            "data": {
                "id": cursor.lastrowid,
                "day_index": day_index,
                "title": title,
                "place_type": place_type,
                "sort_order": new_order,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.post("/item/delete")
async def delete_day_item(
        user_id: int = Body(...),
        trip_id: int = Body(...),
        item_id: int = Body(...),
):
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        cursor = db_conn.cursor(dictionary=True)

        cursor.execute("SELECT owner_user_id FROM trip WHERE trip_id=%s", (trip_id,))
        t = cursor.fetchone()
        if not t:
            raise HTTPException(status_code=404, detail="Trip not found")
        if int(t["owner_user_id"]) != int(user_id):
            raise HTTPException(status_code=403, detail="无权限编辑该行程计划")

        # item 必须属于该 trip
        cursor.execute("""
            SELECT i.id
            FROM trip_day_item i
            JOIN trip_day_plan d ON d.id=i.day_plan_id
            WHERE i.id=%s AND d.trip_id=%s
            LIMIT 1
        """, (item_id, trip_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Item not found")

        cursor.execute("DELETE FROM trip_day_item WHERE id=%s", (item_id,))
        db_conn.commit()

        return {"code": 200, "message": "删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
