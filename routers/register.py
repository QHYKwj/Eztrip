# routers/register.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

register_router = APIRouter(prefix="/api/register", tags=["register"])

# 设置路由标识
@register_router.post("")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not all([username.strip(), email.strip(), password.strip(), confirm_password.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Username,email,password and confirm_password are allowed to be null"
            ) 
        
        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        cursor = db_conn.cursor()

        # 3. 检查用户名是否已存在
        check_name_query = "SELECT username FROM user_info WHERE username = %s"
        cursor.execute(check_name_query, (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already existed")
        
        # 4. 检查邮箱是否使用过
        check_email_query = "SELECT email FROM user_info WHERE email = %s"
        cursor.execute(check_email_query, (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already used")
        
        # 5.检查两次密码输入是否一致
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="The password and confirm_password are different")
        
        # 6.将用户信息插入数据库中
        insert_query = "INSERT INTO user_info (username, email, password) values(%s, %s, %s)"
        cursor.execute(insert_query, (username, email, password))
        db_conn.commit()

        return {"message":"Register successful"}
    except HTTPException:
        raise 
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"注册失败: {str(e)}"
        )  # 包含具体错误信息)
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
    