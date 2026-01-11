# routers/delete_user.py  管理员删除用户
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/admin/delete_user", tags=["delete_user"])

@router.post("")
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