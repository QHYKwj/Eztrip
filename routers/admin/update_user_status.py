# routers/login.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/admin/update_user_status", tags=["update_user_status"])

@router.post("")
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