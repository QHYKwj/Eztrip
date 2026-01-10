# routers/trip_detail/trip_details.py
from fastapi import APIRouter, HTTPException, Query
from config.connect_db import connect_db
import httpx
from datetime import datetime, date
from settings import AMAP_WEB_KEY

router = APIRouter(prefix="/api/trip", tags=["trip_details"])

# ... geocode_destination / to_str 保持不变 ...

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
                tf.user_id AS fav_user_id,
                IF(tf.user_id IS NULL, 0, 1) AS is_collected
            FROM trip t
            LEFT JOIN trip_favorite tf
              ON tf.trip_id = t.trip_id AND tf.user_id = %s
            WHERE t.trip_id = %s
              AND (t.owner_user_id = %s OR tf.user_id IS NOT NULL)
            LIMIT 1;
        """
        cursor.execute(sql, (user_id, trip_id, user_id))
        trip = cursor.fetchone()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found or no permission")

        lng, lat = await geocode_destination(trip["destination"])

        owner_id = int(trip["owner_user_id"])
        uid = int(user_id)

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

            "is_collected": bool(trip["is_collected"]),
            "is_owner": owner_id == uid,              # ✅ 关键：这里必须正确
            "is_favorited": trip["fav_user_id"] is not None,

            "class": str(trip["class"]) if trip["class"] is not None else None,
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
