# routers/login.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/login", tags=["login"])

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not username.strip() or not password.strip():
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
        
        cursor = db_conn.cursor(dictionary="true")

        # 3.查询用户信息
        query = "SELECT * FROM user_info WHERE username = %s and password = %s ;"
        # 元组
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Username or password are wrong"
            )
        db_conn.commit()
        # 4.返回登录成功信息
        return {"message": "Login successful", "username": username}
        
    except HTTPException:
        # 重新抛出已知的HTTP异常
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
