# routers/notice/create_notice.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db
import pymysql
from datetime import datetime

router = APIRouter(prefix="/api/notice", tags=["notice"])

# ------------------------------
# 工具函数：给所有用户发送公告消息（发布公告时调用）
# ------------------------------
def send_notice_to_all_users(notice_title: str, notice_content: str, admin_id: int):
    """
    发布公告时，给所有用户发送系统消息（插入message表）
    :param notice_title: 公告标题
    :param notice_content: 公告内容
    :param admin_id: 发送者（管理员ID，对应message.sender_id）
    """
    db_conn = None
    cursor = None
    try:
        # 1. 连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise Exception("数据库连接失败")
        cursor = db_conn.cursor()

        # 2. 查询所有用户的user_id（用于批量发送）
        cursor.execute("SELECT user_id FROM user_info;")
        users = cursor.fetchall()  # 结果格式：[(1,), (2,), ...]
        if not users:
            return  # 无用户时无需发送

        # 3. 批量插入消息（优化效率，避免循环执行SQL）
        message_list = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for (user_id,) in users:
            message_list.append((
                admin_id,  # sender_id（管理员ID）
                user_id,   # receiver_id（每个用户ID）
                f"公告通知：{notice_title}",  # message标题
                f"公告内容：{notice_content}\n发布时间：{now}",  # message内容
                now,  # created_at
                0,    # is_read（默认未读）
                None  # read_at（默认空）
            ))

        # 批量插入SQL
        insert_msg_sql = """
            INSERT INTO message 
            (sender_id, receiver_id, title, content, created_at, is_read, read_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(insert_msg_sql, message_list)
        db_conn.commit()

    except Exception as e:
        print(f"发送公告消息失败：{str(e)}")
        if db_conn:
            db_conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

# ------------------------------
# 1. 创建公告（默认草稿状态：is_active=0）
# ------------------------------
@router.post("/create", summary="创建公告（草稿）")
async def create_notice(
    title: str = Form(...),
    content: str = Form(...),
    created_by: int = Form(...)  # 管理员ID（对应notice.created_by）
):
    db_conn = None
    cursor = None
    try:
        # 1. 参数校验
        if not title.strip() or not content.strip():
            raise HTTPException(status_code=400, detail="标题和内容不能为空")
        if created_by <= 0:
            raise HTTPException(status_code=400, detail="无效的管理员ID")

        # 2. 连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor()

        # 3. 插入草稿公告（严格对应notice表字段）
        # 字段顺序：title, content, created_at, created_by, is_active
        insert_sql = """
            INSERT INTO notice 
            (title, content, created_at, created_by, is_active)
            VALUES (%s, %s, CURRENT_TIMESTAMP, %s, 0);
        """
        cursor.execute(insert_sql, (title.strip(), content.strip(), created_by))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=400, detail="创建公告失败")
        db_conn.commit()

        return {
            "success": True,
            "message": "公告草稿创建成功",
            "data": {"notice_id": cursor.lastrowid}  # 返回新建公告ID
        }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建公告失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

# ------------------------------
# 2. 发布公告（更新is_active=1 + 给所有用户发消息）
# ------------------------------
@router.post("/publish", summary="发布公告")
async def publish_notice(
    notice_id: int = Form(...),
    admin_id: int = Form(...)  # 发送消息的管理员ID（对应message.sender_id）
):
    db_conn = None
    cursor = None
    try:
        # 1. 参数校验
        if notice_id <= 0 or admin_id <= 0:
            raise HTTPException(status_code=400, detail="无效的公告ID或管理员ID")

        # 2. 连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 3. 检查公告是否存在且为草稿状态
        cursor.execute("""
            SELECT title, content FROM notice 
            WHERE notice_id = %s AND is_active = 0;
        """, (notice_id,))
        notice = cursor.fetchone()
        if not notice:
            raise HTTPException(status_code=404, detail="公告不存在或已发布")

        # 4. 更新公告状态为“已发布”（is_active=1）
        cursor.execute("""
            UPDATE notice SET is_active = 1 WHERE notice_id = %s;
        """, (notice_id,))
        db_conn.commit()

        # 5. 给所有用户发送公告消息（同步执行，简单可靠；高并发可改用异步）
        send_notice_to_all_users(
            notice_title=notice["title"],
            notice_content=notice["content"],
            admin_id=admin_id
        )

        return {"success": True, "message": "公告发布成功，已通知所有用户"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"发布公告失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

# ------------------------------
# 3. 取消发布公告（更新is_active=0）
# ------------------------------
@router.post("/unpublish", summary="取消发布公告")
async def unpublish_notice(notice_id: int = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1. 参数校验
        if notice_id <= 0:
            raise HTTPException(status_code=400, detail="无效的公告ID")

        # 2. 连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 3. 检查公告是否存在且为已发布状态
        cursor.execute("""
            SELECT notice_id FROM notice 
            WHERE notice_id = %s AND is_active = 1;
        """, (notice_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="公告不存在或未发布")

        # 4. 更新公告状态为“草稿”（is_active=0）
        cursor.execute("""
            UPDATE notice SET is_active = 0 WHERE notice_id = %s;
        """, (notice_id,))
        db_conn.commit()

        return {"success": True, "message": "公告已取消发布"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"取消发布失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

# ------------------------------
# 4. 删除公告
# ------------------------------
@router.post("/delete", summary="删除公告")
async def delete_notice(notice_id: int = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1. 参数校验
        if notice_id <= 0:
            raise HTTPException(status_code=400, detail="无效的公告ID")

        # 2. 连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor()

        # 3. 检查公告是否存在
        cursor.execute("SELECT notice_id FROM notice WHERE notice_id = %s;", (notice_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="公告不存在")

        # 4. 删除公告
        cursor.execute("DELETE FROM notice WHERE notice_id = %s;", (notice_id,))
        db_conn.commit()

        return {"success": True, "message": "公告删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除公告失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

# ------------------------------
# 5. 获取所有公告列表（用于前端展示）
# ------------------------------
@router.get("/list", summary="获取所有公告列表")
async def get_all_notices():
    db_conn = None
    cursor = None
    try:
        # 1. 连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 2. 查询核心字段：notice_id、title、created_at、is_active
        # 可选关联user_info获取管理员名称（enhancement）
        cursor.execute("""
            SELECT 
                notice_id,
                title,
                created_at,
                is_active,
                u.username AS created_by_name  -- 关联管理员名称（可选，提升体验）
            FROM notice n
            LEFT JOIN user_info u ON n.created_by = u.user_id
            ORDER BY created_at DESC;
        """)
        notices = cursor.fetchall()

        # 3. 格式化时间（确保前端显示友好）
        for notice in notices:
            if notice["created_at"]:
                notice["created_at"] = notice["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return {
            "success": True,
            "data": {
                "notices": notices,
                "count": len(notices)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公告列表失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()