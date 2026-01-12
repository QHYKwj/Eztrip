from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from datetime import datetime
from config.connect_db import connect_db

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/trips/pending")
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

@router.post("/trips/review")
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

@router.get("/all_user_info")
async def all_user_info():
    db_conn = None
    cursor = None

    try:
        # 1.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code=500,
                detail="数据库连接失败"
            )

        cursor = db_conn.cursor(dictionary=True)

        # 2.查询用户信息
        query = """
            SELECT 
                user_id,
                username,
                email,
                avatar,
                admin_id,
                status
            FROM user_info 
        """
        cursor.execute(query)
        users = cursor.fetchall()

        # 3.返回结果
        return {
            "success": True,
            "data": {
                "users": users,
                "count": len(users)
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询用户失败: {str(e)}"
        )
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.get("/content_count")  # 修改为GET请求，因为这是获取数据而不是创建数据
async def get_content_count():
    db_conn = None
    cursor = None
    try:
        # 1.连接数据库
        db_conn = connect_db()
        # 连接失败
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )

        cursor = db_conn.cursor(dictionary=True)  # 修改为布尔值True

        # 2.查看内容总数
        select_query = "SELECT COUNT(*) as total_count FROM trip;"
        cursor.execute(select_query)

        # 获取查询结果
        result = cursor.fetchone()

        if result:
            content_count = result.get('total_count', 0)

            # 返回内容数
            return {
                "success": True,
                "data": {
                    "content_count": content_count
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "content_count": 0
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"获取内容数失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.post("/delete_user")
async def delete_user(user_id: str = Form(...)):
    db_conn = None
    cursor = None

    try:
        # 1.验证输入参数
        if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=400,
                detail="用户ID不能为空"
            )

        # 转换为整数
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="用户ID必须是数字"
            )

        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code=500,
                detail="数据库连接失败"
            )

        cursor = db_conn.cursor(dictionary=True)

        # 3. 先检查用户是否存在
        check_query = "SELECT user_id, username FROM user_info WHERE user_id = %s;"
        cursor.execute(check_query, (user_id_int,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="用户不存在"
            )

        print(f"找到用户: {user}")

        # 4. 开始事务
        cursor.execute("START TRANSACTION")

        try:
            # 5. 步骤1：将用户审核过的行程的reviewed_by置为NULL
            update_review_query = "UPDATE trip SET reviewed_by = NULL WHERE reviewed_by = %s;"
            cursor.execute(update_review_query, (user_id_int,))
            reviewed_updated = cursor.rowcount
            print(f"将 {reviewed_updated} 条行程的审核人置为NULL")

            # 6. 步骤2：删除与该用户相关的消息记录
            # 删除该用户发送的消息
            delete_sent_messages_query = "DELETE FROM message WHERE sender_id = %s;"
            cursor.execute(delete_sent_messages_query, (user_id_int,))
            sent_messages_deleted = cursor.rowcount
            print(f"删除用户发送的消息: {sent_messages_deleted} 条")

            # 删除该用户接收的消息
            delete_received_messages_query = "DELETE FROM message WHERE receiver_id = %s;"
            cursor.execute(delete_received_messages_query, (user_id_int,))
            received_messages_deleted = cursor.rowcount
            print(f"删除用户接收的消息: {received_messages_deleted} 条")

            # 7. 步骤3：找出用户创建的所有行程ID
            get_user_trips_query = "SELECT trip_id FROM trip WHERE owner_user_id = %s;"
            cursor.execute(get_user_trips_query, (user_id_int,))
            user_trips = cursor.fetchall()
            user_trip_ids = [trip['trip_id'] for trip in user_trips]
            print(f"用户创建的行程ID: {user_trip_ids}")

            # 8. 步骤4：删除其他用户收藏了该用户行程的记录
            if user_trip_ids:
                # 构建参数占位符
                placeholders = ', '.join(['%s'] * len(user_trip_ids))

                # 删除收藏记录
                delete_other_fav_query = f"""
                    DELETE FROM trip_favorite 
                    WHERE trip_id IN ({placeholders})
                """
                cursor.execute(delete_other_fav_query, user_trip_ids)
                other_fav_deleted = cursor.rowcount
                print(f"删除其他用户收藏该用户行程的记录: {other_fav_deleted} 条")
            else:
                other_fav_deleted = 0

            # 9. 步骤5：删除该用户收藏别人的记录
            delete_user_fav_query = "DELETE FROM trip_favorite WHERE user_id = %s;"
            cursor.execute(delete_user_fav_query, (user_id_int,))
            user_fav_deleted = cursor.rowcount
            print(f"删除该用户收藏别人的记录: {user_fav_deleted} 条")

            # 10. 步骤6：删除用户创建的行程
            delete_trip_query = "DELETE FROM trip WHERE owner_user_id = %s;"
            cursor.execute(delete_trip_query, (user_id_int,))
            trip_deleted = cursor.rowcount
            print(f"删除用户创建的行程: {trip_deleted} 条")

            # 11. 步骤7：最后删除用户信息
            delete_user_query = "DELETE FROM user_info WHERE user_id = %s;"
            cursor.execute(delete_user_query, (user_id_int,))
            user_deleted = cursor.rowcount

            if user_deleted == 0:
                cursor.execute("ROLLBACK")
                raise HTTPException(
                    status_code=500,
                    detail="删除用户失败"
                )

            # 12. 提交事务
            cursor.execute("COMMIT")
            print(f"删除用户成功: ID={user_id_int}")

        except Exception as e:
            cursor.execute("ROLLBACK")
            raise e

        # 13. 返回删除成功信息
        return {
            "success": True,
            "message": "删除用户成功",
            "deleted_user_id": user_id_int,
            "details": {
                "user_info_deleted": user_deleted,
                "user_trips_deleted": trip_deleted,
                "user_favorites_deleted": user_fav_deleted,
                "other_user_favorites_deleted": other_fav_deleted,
                "trips_review_cleared": reviewed_updated,
                "sent_messages_deleted": sent_messages_deleted,
                "received_messages_deleted": received_messages_deleted
            }
        }

    except HTTPException as he:
        if db_conn:
            db_conn.rollback()
        raise he
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"删除用户失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.get("/pending_review_count")  # 修改为GET请求，因为这是获取数据而不是创建数据
async def get_pending_review_count():
    db_conn = None
    cursor = None
    try:
        # 1.连接数据库
        db_conn = connect_db()
        # 连接失败
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )

        cursor = db_conn.cursor(dictionary=True)  # 修改为布尔值True

        # 2.查看待审核总数
        select_query = "SELECT COUNT(*) as total_count FROM trip where publish_status = 'pending';"
        cursor.execute(select_query)

        # 获取查询结果
        result = cursor.fetchone()

        if result:
            user_count = result.get('total_count', 0)

            # 返回待审核数
            return {
                "success": True,
                "data": {
                    "pending_review_count": user_count
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "pending_review_count": 0
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"获取待审核数失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.post("/update_user_status")
async def update_user_status(user_id: str = Form(...), status: str = Form(...)):
    db_conn = None
    cursor = None

    try:
        # 1.验证输入参数
        if not user_id.strip():
            raise HTTPException(
                status_code=400,
                detail="用户ID不能为空"
            )

        if not status.strip():
            raise HTTPException(
                status_code=400,
                detail="状态不能为空"
            )

        # 转换为整数
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="用户ID必须是数字"
            )

        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code=500,
                detail="数据库连接失败"
            )

        cursor = db_conn.cursor(dictionary=True)

        # 3. 检查用户是否存在
        check_query = """
            SELECT user_id, username, status as current_status 
            FROM user_info 
            WHERE user_id = %s;
        """
        cursor.execute(check_query, (user_id_int,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="用户不存在"
            )

        print(f"找到用户: {user['username']} (ID: {user['user_id']}), 当前状态: {user['current_status']}")

        # 4. 检查是否已经是目标状态
        if user['current_status'] == status:
            raise HTTPException(
                status_code=400,
                detail=f"用户已经是 {status} 状态，无需修改"
            )

        # 5. 修改用户状态
        update_query = """
            UPDATE user_info
            SET status = %s
            WHERE user_id = %s;
        """
        cursor.execute(update_query, (status, user_id_int))

        # 使用rowcount检查是否更新成功
        affected_rows = cursor.rowcount

        if affected_rows == 0:
            # 理论上不会走到这里，因为前面已经检查过用户存在
            raise HTTPException(
                status_code=500,
                detail="更新状态失败"
            )

        # 6. 提交事务
        db_conn.commit()

        print(f"用户状态更新成功: ID={user_id_int}, 状态: {status}")

        # 7. 获取更新后的用户信息
        get_updated_query = """
            SELECT user_id, username, email, status
            FROM user_info
            WHERE user_id = %s;
        """
        cursor.execute(get_updated_query, (user_id_int,))
        updated_user = cursor.fetchone()

        # 8. 返回成功信息
        return {
            "success": True,
            "message": "用户状态更新成功",
            "data": {
                "user": updated_user,
                "changes": {
                    "previous_status": user['current_status'],
                    "new_status": status
                }
            }
        }

    except HTTPException as he:
        if db_conn:
            db_conn.rollback()
        raise he
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"更新用户状态失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

@router.get("/user_count")  # 修改为GET请求，因为这是获取数据而不是创建数据
async def get_user_count():
    db_conn = None
    cursor = None
    try:
        # 1.连接数据库
        db_conn = connect_db()
        # 连接失败
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )

        cursor = db_conn.cursor(dictionary=True)  # 修改为布尔值True

        # 2.查看用户总数
        select_query = "SELECT COUNT(*) as total_count FROM user_info;"
        cursor.execute(select_query)

        # 获取查询结果
        result = cursor.fetchone()

        if result:
            user_count = result.get('total_count', 0)

            # 返回用户数
            return {
                "success": True,
                "data": {
                    "user_count": user_count
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "user_count": 0
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"获取用户数失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
