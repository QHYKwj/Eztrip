# routers/trip_detail/trip_plan.py
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from config.connect_db import connect_db
from datetime import timedelta
import httpx
from settings import AMAP_WEB_KEY

router = APIRouter(prefix="/api/trip_plan", tags=["trip_plan"])


def to_str(d):
    return d.strftime("%Y-%m-%d") if d else None


async def geocode_address(city: str, address: str):
    """辅助函数：根据城市和景点名称解析经纬度"""
    if not address or not address.strip():
        return None, None
    url = "https://restapi.amap.com/v3/geocode/geo"
    full_address = f"{city}{address}" if city and city not in address else address
    params = {"key": AMAP_WEB_KEY, "address": full_address, "output": "JSON"}
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url, params=params)
            data = resp.json()
            if str(data.get("status")) == "1" and data.get("geocodes"):
                loc = data["geocodes"][0].get("location")
                if loc and "," in loc:
                    lng, lat = loc.split(",", 1)
                    return float(lng), float(lat)
    except Exception as e:
        print(f"地理编码解析失败 [{full_address}]: {e}")
    return None, None


@router.get("/get")
async def get_trip_plan(
        user_id: int = Query(...),
        trip_id: int = Query(...),
):
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 1) 取 trip 基本信息（带上 destination）
        cursor.execute("""
            SELECT trip_id, owner_user_id, destination, start_date, end_date
            FROM trip WHERE trip_id=%s LIMIT 1
        """, (trip_id,))
        trip = cursor.fetchone()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        destination_city = trip.get("destination") or ""
        start_date = trip["start_date"]
        end_date = trip["end_date"]
        total_days = (end_date - start_date).days + 1

        # 2) 拉出已有 day_plan
        cursor.execute("SELECT id, day_index, plan_date, note FROM trip_day_plan WHERE trip_id=%s ORDER BY day_index ASC", (trip_id,))
        day_rows = cursor.fetchall() or []
        day_map = {int(r["day_index"]): r for r in day_rows}

        # 3) 自动补齐缺失天数
        for di in range(1, total_days + 1):
            if di not in day_map:
                plan_date = start_date + timedelta(days=di - 1)
                cursor.execute("INSERT INTO trip_day_plan (trip_id, day_index, plan_date, note) VALUES (%s, %s, %s, %s)", (trip_id, di, plan_date, None))
                db_conn.commit()
                day_map[di] = {"id": cursor.lastrowid, "day_index": di, "plan_date": plan_date, "note": None}

        # 4) 拉出所有 items（直接把表里的 lng, lat 查出来）
        day_ids = [day_map[di]["id"] for di in range(1, total_days + 1)]
        format_ids = ",".join(["%s"] * len(day_ids))
        cursor.execute(f"""
            SELECT id, day_plan_id, title, place_type, sort_order, lng, lat
            FROM trip_day_item
            WHERE day_plan_id IN ({format_ids})
            ORDER BY day_plan_id ASC, sort_order ASC, id ASC
        """, tuple(day_ids))
        item_rows = cursor.fetchall() or []

        # 🌟 5) 自动查漏补缺：对于旧数据缺失经纬度的，立刻计算并回写持久化到数据库
        items_by_day = {}
        for it in item_rows:
            lng = it.get("lng")
            lat = it.get("lat")

            # 如果数据库里还是空值，去查高德并回写数据库
            if lng is None or lat is None:
                lng, lat = await geocode_address(destination_city, it["title"])
                if lng is not None and lat is not None:
                    try:
                        cursor.execute("UPDATE trip_day_item SET lng=%s, lat=%s WHERE id=%s", (lng, lat, it["id"]))
                        db_conn.commit()
                    except Exception as err:
                        print(f"回写经纬度失败: {err}")

            items_by_day.setdefault(int(it["day_plan_id"]), []).append({
                "id": int(it["id"]),
                "title": it["title"],
                "place_type": it.get("place_type"),
                "sort_order": int(it["sort_order"]),
                "lng": float(lng) if lng is not None else None,
                "lat": float(lat) if lat is not None else None,
            })

        days = []
        for di in range(1, total_days + 1):
            r = day_map[di]
            days.append({
                "day_index": di,
                "plan_date": to_str(r.get("plan_date")),
                "note": r.get("note"),
                "items": items_by_day.get(int(r["id"]), []),
            })

        return {"trip_id": int(trip_id), "days": days, "total_days": total_days}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行程计划失败: {str(e)}")
    finally:
        if cursor: cursor.close()
        if db_conn and db_conn.is_connected(): db_conn.close()


@router.post("/item/add")
async def add_day_item(
        user_id: int = Body(...),
        trip_id: int = Body(...),
        day_index: int = Body(...),
        title: str = Body(...),
        place_type: Optional[str] = Body("景点"),
        lng: Optional[float] = Body(None),  # 🌟 新增：可选前端直接传回经度
        lat: Optional[float] = Body(None),  # 🌟 新增：可选前端直接传回纬度
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

        # 1) 权限校验并查出 destination
        cursor.execute("SELECT owner_user_id, destination FROM trip WHERE trip_id=%s", (trip_id,))
        t = cursor.fetchone()
        if not t:
            raise HTTPException(status_code=404, detail="Trip not found")
        if int(t["owner_user_id"]) != int(user_id):
            raise HTTPException(status_code=403, detail="无权限编辑该行程计划")

        destination_city = t.get("destination") or ""

        # 2) 找 day_plan_id
        cursor.execute("SELECT id FROM trip_day_plan WHERE trip_id=%s AND day_index=%s LIMIT 1", (trip_id, day_index))
        d = cursor.fetchone()
        if not d:
            raise HTTPException(status_code=404, detail="未找到对应天数的计划")
        day_plan_id = int(d["id"])

        # 3) 计算当前天末尾的 sort_order = MAX + 1
        cursor.execute("SELECT COALESCE(MAX(sort_order), 0) AS mx FROM trip_day_item WHERE day_plan_id=%s", (day_plan_id,))
        mx = int(cursor.fetchone()["mx"])
        new_order = mx + 1

        # 🌟 4) 智能处理经纬度：如果前端没有直接传精准点选坐标，才去调高德解析
        final_lng, final_lat = lng, lat
        if final_lng is None or final_lat is None:
            final_lng, final_lat = await geocode_address(destination_city, title)

        # 5) 落库保存
        cursor.execute("""
            INSERT INTO trip_day_item (day_plan_id, title, place_type, sort_order, lng, lat)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (day_plan_id, title, place_type, new_order, final_lng, final_lat))
        db_conn.commit()

        item_id = cursor.lastrowid

        return {
            "code": 200,
            "message": "添加成功",
            "data": {
                "id": item_id,
                "day_index": day_index,
                "title": title,
                "place_type": place_type,
                "sort_order": new_order,
                "lng": float(final_lng) if final_lng is not None else None,
                "lat": float(final_lat) if final_lat is not None else None,
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