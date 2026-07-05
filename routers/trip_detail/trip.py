# routers/trip_detail/trip.py
# routers/trip_detail/trip.py
from fastapi import APIRouter, HTTPException, Query
from config.connect_db import connect_db
import httpx
from datetime import datetime, date
from settings import AMAP_WEB_KEY
from fastapi import APIRouter, HTTPException, Query
import os
import urllib.parse
from pydantic import BaseModel
from config.connect_db import connect_db
from datetime import datetime
import json # 确保顶部引入了 json
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/trip", tags=["trip_details"])

# 🌟 行程分类映射字典
CLASS_MAP = {
    1: "休闲",
    2: "美食",
    3: "商务",
    4: "家庭",
}
async def geocode_destination(destination: str):
    """destination -> (lng, lat) via AMap geocode"""
    if not destination or not destination.strip():
        return None, None

    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {"key": AMAP_WEB_KEY, "address": destination, "output": "JSON"}

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return None, None

    if str(data.get("status")) != "1":
        return None, None

    geocodes = data.get("geocodes") or []
    if not geocodes:
        return None, None

    loc = geocodes[0].get("location")
    if not loc or "," not in loc:
        return None, None

    lng_str, lat_str = loc.split(",", 1)
    try:
        return float(lng_str), float(lat_str)
    except Exception:
        return None, None


def to_str(x):
    """把 date/datetime 转字符串"""
    if x is None:
        return None
    if isinstance(x, datetime):
        return x.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(x, date):
        return x.strftime("%Y-%m-%d")
    return str(x)


from fastapi import APIRouter, HTTPException, Query
from config.connect_db import connect_db

router = APIRouter(prefix="/api/trip", tags=["trip_details"])

@router.get("/detail")
async def trip_detail(
        user_id: int = Query(..., description="当前登录用户 user_id"),
        trip_id: int = Query(..., description="行程 id"),
):
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        # ✅ 关键：可见性 = owner 或收藏过 或（公开且已发布）
        sql = """
            SELECT
                t.trip_id,
                t.owner_user_id,
                t.title,
                t.destination,
                t.start_date,
                t.end_date,
                t.created_at,
                t.updated_at,
                t.publish_status,
                t.review_comment,
                t.is_public,
                t.class,
                t.remarks,
                t.is_ai,

                tf.user_id AS fav_user_id,
                IF(tf.user_id IS NULL, 0, 1) AS is_collected

            FROM trip t
            LEFT JOIN trip_favorite tf
              ON tf.trip_id = t.trip_id AND tf.user_id = %s
            WHERE t.trip_id = %s
              AND (
                    t.owner_user_id = %s
                 OR tf.user_id IS NOT NULL
                 OR (t.is_public = 1 AND t.publish_status = 'published')
              )
            LIMIT 1;
        """
        cursor.execute(sql, (user_id, trip_id, user_id))
        trip = cursor.fetchone()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or no permission")

        lng, lat = await geocode_destination(trip["destination"])

        owner_id = int(trip["owner_user_id"])
        uid = int(user_id)

        # 🌟 核心修改：尝试解析 JSON 格式的 remarks
        parsed_remarks = None
        if trip.get("remarks"):
            try:
                parsed_remarks = json.loads(trip["remarks"])
            except json.JSONDecodeError:
                # 如果解析失败（兼容以前存入的纯 Markdown 文本），直接返回原字符串
                parsed_remarks = trip["remarks"]

        # 🌟 处理 class 分类并返回 class_text
        cls_int = (
            int(trip["class"]) if trip.get("class") is not None else 1
        )  # 默认给1休闲

        return {
            "trip_id": int(trip["trip_id"]),
            "owner_user_id": owner_id,

            "trip_name": trip["title"],
            "destination": trip["destination"],
            "start_date": to_str(trip["start_date"]),
            "end_date": to_str(trip["end_date"]),
            "created_at": to_str(trip["created_at"]),
            "updated_at": to_str(trip["updated_at"]),

            "publish_status": trip["publish_status"],
            "review_comment": trip.get("review_comment"),
            "is_public": int(trip["is_public"]) == 1,
            "is_ai": int(trip["is_ai"]) if trip.get("is_ai") is not None else 0, # ✅ 返回 is_ai 字段

            "is_collected": bool(trip["is_collected"]),
            "is_owner": owner_id == uid,        # ✅ owner 才能编辑
            "is_favorited": trip["fav_user_id"] is not None,

            "class": int(trip["class"]) if trip["class"] is not None else None,
            "class_text": CLASS_MAP.get(cls_int, "休闲"),  # 🌟 返回文本
            "remarks": parsed_remarks, # <--- 给前端透传解析好的字典或原始字符串
            "lng": lng,
            "lat": lat,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取行程详情失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()



# 高德静态地图基础 URL
AMAP_STATIC_BASE_URL = "https://restapi.amap.com/v3/staticmap"


@router.get("/map/url")
async def get_map_url(
        lng: float = Query(..., description="地图中心点经度，如 116.397428"),
        lat: float = Query(..., description="地图中心点纬度，如 39.90923"),
        zoom: int = Query(14, ge=1, le=18, description="缩放等级 1-18"),
        width: int = Query(600, ge=1, le=1024, description="图片宽度，最大 1024"),
        height: int = Query(300, ge=1, le=1024, description="图片高度，最大 1024"),
        label: str = Query("A", description="标记点上的文本，如 A/B/1"),
):
    """
    返回一个高德静态地图 URL，前端直接用 <img :src="url"> 即可显示。
    """

    # 1. 检查 key 是否正确配置
    if not AMAP_WEB_KEY or AMAP_WEB_KEY == "YOUR_AMAP_WEB_SERVICE_KEY_HERE":
        raise HTTPException(
            status_code=500,
            detail="高德 Web 服务 Key 未配置，请在环境变量 AMAP_WEB_KEY 中设置，或者修改 routers/map.py 中 AMAP_WEB_KEY。",
        )

    # 2. 组装静态地图参数
    center = f"{lng},{lat}"            # 中心点坐标
    size = f"{width}*{height}"         # 图片大小
    label = label or "A"

    # markers 格式：
    # markers=mid,0xFF0000,A:116.397428,39.90923
    marker_style = f"mid,0xFF0000,{label}"
    markers = f"{marker_style}:{center}"

    query_params = {
        "key": AMAP_WEB_KEY,
        "location": center,
        "zoom": str(zoom),
        "size": size,
        "markers": markers,
        # 以后如果要加 paths、labels 等，可以继续往这里加
    }

    url = f"{AMAP_STATIC_BASE_URL}?{urllib.parse.urlencode(query_params)}"

    # 统一返回格式
    return {"url": url}


class TripUpdateBody(BaseModel):
    user_id: int
    trip_id: int
    trip_name: str
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    is_public: int   # 0/1
    publish_action: str  # keep / submit / unpublish
    class_type: Optional[int] = 1  # 🌟 增加分类字段更新
    remarks: Optional[Dict[str, Any]] = None  # ✅ 允许前端传回整个 JSON 对象


def _parse_ymd(s: str) -> datetime:
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        raise HTTPException(status_code=400, detail="日期格式应为 YYYY-MM-DD")


@router.put("/update")
async def update_trip(body: TripUpdateBody):
    db_conn = None
    cursor = None
    try:
        if body.publish_action not in ("keep", "submit", "unpublish"):
            raise HTTPException(status_code=400, detail="Invalid publish_action")

        # ✅ 日期校验
        start_dt = _parse_ymd(body.start_date)
        end_dt = _parse_ymd(body.end_date)
        if end_dt < start_dt:
            raise HTTPException(status_code=400, detail="结束日期不能早于开始日期")

        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        # ✅ 1) 权限：必须是 owner 才能改（收藏行程直接禁止）
        cursor.execute(
            "SELECT owner_user_id, publish_status FROM trip WHERE trip_id=%s",
            (body.trip_id,)
        )
        t = cursor.fetchone()
        if not t:
            raise HTTPException(status_code=404, detail="Trip not found")

        if int(t["owner_user_id"]) != int(body.user_id):
            raise HTTPException(status_code=403, detail="No permission (favorite trip is read-only)")

        current_status = t["publish_status"]

        # ✅ 2) 处理 publish_action -> publish_status
        new_status = None
        if body.publish_action == "submit":
            # 只允许 draft/rejected 提交审核（你也可以放宽）
            if current_status not in ("draft", "rejected"):
                raise HTTPException(status_code=400, detail="当前状态不可提交审核")
            new_status = "pending"
        elif body.publish_action == "unpublish":
            new_status = "draft"

        # ✅ 将前端传来的字典转回 JSON 字符串
        remarks_str = json.dumps(body.remarks, ensure_ascii=False) if body.remarks else None

        # 🌟 SQL 更新语句中同步更新 `class` 字段
        if new_status:
            cursor.execute(
                """
                UPDATE trip
                SET title=%s, destination=%s, start_date=%s, end_date=%s,
                    is_public=%s, publish_status=%s, `class`=%s, remarks=%s
                WHERE trip_id=%s
            """,
                (
                    body.trip_name,
                    body.destination,
                    body.start_date,
                    body.end_date,
                    int(body.is_public),
                    new_status,
                    body.class_type,
                    remarks_str,
                    body.trip_id,
                ),
            )
        else:
            cursor.execute("""
                UPDATE trip
                SET title=%s, destination=%s, start_date=%s, end_date=%s,
                    is_public=%s, remarks=%s
                WHERE trip_id=%s
            """, (
                body.trip_name, body.destination, body.start_date, body.end_date,
                int(body.is_public), remarks_str, body.trip_id
            ))

        db_conn.commit()
        # 🌟 核心修复：加上 "code": 200 防止 axios 前端拦截器报异常！
        return {"message": "Trip updated successfully", "code": 200}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新行程失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.get("/favorite-count", summary="获取行程收藏人数")
async def favorite_count(trip_id: int = Query(...)):
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS cnt FROM trip_favorite WHERE trip_id=%s", (trip_id,))
        row = cursor.fetchone() or {"cnt": 0}
        return {"trip_id": trip_id, "count": int(row["cnt"])}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏人数失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.delete("/delete", summary="删除行程")
async def delete_trip(
        trip_id: int = Query(..., description="要删除的行程 ID"),
        user_id: int = Query(..., description="当前操作的用户 ID")
):
    """
    删除行程 API
    逻辑：先判断是否存在及是否有权限（仅属主和管理员可删），然后先清空收藏记录，最后删除行程主表记录。
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        # 1. 校验行程是否存在及归属权
        cursor.execute("SELECT owner_user_id FROM trip WHERE trip_id = %s", (trip_id,))
        trip_record = cursor.fetchone()

        if not trip_record:
            raise HTTPException(status_code=404, detail="行程不存在")

        # 权限校验：只有创建者本身，或者管理员（设定 admin_id = 1）可以删除
        if int(trip_record["owner_user_id"]) != int(user_id) and int(user_id) != 1:
            raise HTTPException(status_code=403, detail="无权删除该行程")

        # 2. 安全删除机制
        # 因为收藏表 trip_favorite 没有设置 ON DELETE CASCADE，必须先手动解除关联
        cursor.execute("DELETE FROM trip_favorite WHERE trip_id = %s", (trip_id,))

        # 3. 删除主表 (trip_day_plan 和 trip_day_item 有 CASCADE 级联约束，会自动销毁)
        cursor.execute("DELETE FROM trip WHERE trip_id = %s", (trip_id,))

        db_conn.commit()
        return {"message": "行程删除成功", "code": 200}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除行程失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()