# routers/trip_detail/trip_update.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.connect_db import connect_db
from datetime import datetime

router = APIRouter(prefix="/api/trip", tags=["trip_update"])


class TripUpdateBody(BaseModel):
    user_id: int
    trip_id: int
    trip_name: str
    destination: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    is_public: int   # 0/1
    publish_action: str  # keep / submit / unpublish


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

        # ✅ 3) 更新
        if new_status:
            cursor.execute("""
                UPDATE trip
                SET title=%s, destination=%s, start_date=%s, end_date=%s,
                    is_public=%s, publish_status=%s
                WHERE trip_id=%s
            """, (
                body.trip_name, body.destination, body.start_date, body.end_date,
                int(body.is_public), new_status, body.trip_id
            ))
        else:
            cursor.execute("""
                UPDATE trip
                SET title=%s, destination=%s, start_date=%s, end_date=%s,
                    is_public=%s
                WHERE trip_id=%s
            """, (
                body.trip_name, body.destination, body.start_date, body.end_date,
                int(body.is_public), body.trip_id
            ))

        db_conn.commit()
        return {"message": "Trip updated successfully"}

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
