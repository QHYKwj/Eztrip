from fastapi import APIRouter, HTTPException, Query
from config.connect_db import connect_db

router = APIRouter(prefix="/api/trip", tags=["trip_favorite"])

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
