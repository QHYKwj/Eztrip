# routers/register.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

register_router = APIRouter(prefix="/api/register", tags=["register"])

# 设置路由标识
@register_router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not all([username.strip(), password.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Username and password are not null"
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
        check_query = "SELECT username FROM user_info WHERE username = %s"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already existed")
        
        # 4.将用户信息插入数据库中
        insert_query = "INSERT INTO user_info (username, password) values(%s, %s)"
        cursor.execute(insert_query, (username, password))
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
    