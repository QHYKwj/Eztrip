from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from config.connect_db import connect_db

router = APIRouter(prefix="/api/admin/trips", tags=["admin_review"])

@router.get("/pending")
async def list_pending_trips():
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
              t.trip_id, t.title, t.destination, t.start_date, t.end_date,
              t.owner_user_id, u.username AS owner_username,
              t.publish_status, t.is_public, t.created_at
            FROM trip t
            JOIN user_info u ON u.user_id = t.owner_user_id
            WHERE t.publish_status IN ('pending', 'published')
            ORDER BY t.created_at DESC
        """)
        rows = cursor.fetchall() or []
        for r in rows:
            r["start_date"] = str(r["start_date"])
            r["end_date"] = str(r["end_date"])
            r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S") if r.get("created_at") else None
        return rows

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取审核列表失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

class ReviewBody(BaseModel):
    admin_user_id: int
    trip_id: int
    action: str  # approve / reject
    comment: str | None = None

@router.post("/review")
async def review_trip(body: ReviewBody):
    db_conn = None
    cursor = None
    try:
        if body.action not in ("approve", "reject"):
            raise HTTPException(status_code=400, detail="Invalid action")

        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        cursor.execute("SELECT publish_status FROM trip WHERE trip_id=%s", (body.trip_id,))
        t = cursor.fetchone()
        if not t:
            raise HTTPException(status_code=404, detail="Trip not found")

        new_status = "published" if body.action == "approve" else "rejected"

        cursor.execute("""
            UPDATE trip
            SET publish_status=%s,
                reviewed_by=%s,
                reviewed_at=NOW(),
                review_comment=%s
            WHERE trip_id=%s
        """, (new_status, body.admin_user_id, body.comment, body.trip_id))

        db_conn.commit()
        return {"message": "Review success", "publish_status": new_status}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"审核失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
