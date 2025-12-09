# routers/notifications.py
from fastapi import APIRouter, HTTPException, Query
from config.connect_db import connect_db

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(user_id: int = Query(..., description="当前登录用户 user_id")):
    """
    返回用户的消息中心内容（合并 notice + message）：
    - notice：全站公告（不区分已读状态）
    - message：针对个人的消息（支持 is_read）
    统一返回一个数组，前端直接渲染：
    [
      {
        "id": 1,
        "kind": "notice" | "message",
        "sender": "系统通知" / "admin用户名",
        "title": "xxx",
        "content": "xxx",
        "created_at": "2025-12-09T12:00:00",
        "unread": true/false,
        "type": "system" | "service"
      },
      ...
    ]
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        # 1. 公告（notice）- 对所有用户可见
        cursor.execute(
            """
            SELECT
              n.notice_id,
              n.title,
              n.content,
              n.created_at,
              u.username AS creator_name
            FROM notice n
            JOIN user_info u ON n.created_by = u.user_id
            WHERE n.is_active = 1
            ORDER BY n.created_at DESC
            """
        )
        notice_rows = cursor.fetchall() or []

        # 2. 个人消息（message）- 当前用户为接收者
        cursor.execute(
            """
            SELECT
              m.message_id,
              m.title,
              m.content,
              m.created_at,
              m.is_read,
              u.username AS sender_name
            FROM message m
            JOIN user_info u ON m.sender_id = u.user_id
            WHERE m.receiver_id = %s
            ORDER BY m.created_at DESC
            """,
            (user_id,),
        )
        msg_rows = cursor.fetchall() or []

        items = []

        # 映射公告
        for r in notice_rows:
            created_at = r["created_at"]
            items.append({
                "id": r["notice_id"],
                "kind": "notice",
                "sender": r["creator_name"] or "系统通知",
                "title": r["title"],
                "content": r["content"],
                "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
                # 目前没有 per-user 的公告已读表，这里统一当成已读/未读都可以
                "unread": False,
                "type": "system",  # 前端根据 type === 'system' 显示“系统”
            })

        # 映射个人消息
        for r in msg_rows:
            created_at = r["created_at"]
            items.append({
                "id": r["message_id"],
                "kind": "message",
                "sender": r["sender_name"],
                "title": r["title"],
                "content": r["content"],
                "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
                "unread": (r["is_read"] == 0),
                "type": "service",  # 前端会显示为“客服”
            })

        # 按时间倒序统一排序
        items.sort(key=lambda x: x["created_at"], reverse=True)

        return items

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()


@router.put("/messages/{message_id}/read")
async def mark_message_read(
        message_id: int,
        user_id: int = Query(..., description="当前登录用户 user_id"),
):
    """
    将某条 message 标记为已读。
    仅对 message 表生效，不影响 notice。
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        # 确认该消息属于当前用户
        cursor.execute(
            "SELECT message_id FROM message WHERE message_id = %s AND receiver_id = %s",
            (message_id, user_id),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Message not found")

        cursor.execute(
            """
            UPDATE message
            SET is_read = 1,
                read_at = NOW()
            WHERE message_id = %s
              AND receiver_id = %s
            """,
            (message_id, user_id),
        )
        db_conn.commit()

        return {"message": "Message marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"标记消息已读失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()


@router.put("/messages/read-all")
async def mark_all_messages_read(
        user_id: int = Query(..., description="当前登录用户 user_id"),
):
    """
    将当前用户的所有 message 标记为已读。
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        cursor.execute(
            """
            UPDATE message
            SET is_read = 1,
                read_at = NOW()
            WHERE receiver_id = %s
              AND is_read = 0
            """,
            (user_id,),
        )
        db_conn.commit()

        return {"message": "All messages marked as read"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"批量标记消息已读失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
