# routers/finduser.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/finduser", tags=["finduser"])
@router.post("")
async def find_user(username: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数是否为空
        if not username.strip():
            raise HTTPException(
                status_code = 400,
                detail = "Username is not null"
            ) 
        
        # 2.连接数据库
        db_conn = connect_db()
        # 连接失败
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        cursor = db_conn.cursor(dictionary="true")

        # 3.查询用户信息
        query = "SELECT username,avatar,email FROM user_info WHERE username = %s ;"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        # 4.返回用户信息
        return {"message": "User found", "user": user}
        
    except HTTPException:
        # 重新抛出已知的HTTP异常
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"查询用户失败: {str(e)}"
        )  
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()