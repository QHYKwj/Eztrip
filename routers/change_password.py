# routers/change_password.py
from fastapi import APIRouter, Form, HTTPException, Depends
from config.connect_db import connect_db

router = APIRouter(prefix="/api/change_password", tags=["change_password"])
@router.post("")
async def change_password(username: str = Form(...), email: str = Form() , new_password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not all([username.strip(), email.strip(), new_password.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Username,email and new_password are allowed to be null"
            ) 
        
        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        # 3.更新数据库
        cursor = db_conn.cursor()
        update_query = "UPDATE user_info SET password = %s WHERE username = %s and email = %s;"
        cursor.execute(update_query, (new_password, username, email,))

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400, 
                detail="Username or email wrong"
            )
        
        db_conn.commit()

        return {"message":"Change password successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"修改密码失败: {str(e)}"
        )  
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

