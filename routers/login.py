# routers/login.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/login", tags=["login"])

@router.post("")
async def login(username: str = Form(...), password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not username.strip() or not password.strip():
            raise HTTPException(
                status_code=400,
                detail="Username and password are not null"
            )

        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code=500,
                detail="Failed to connect database"
            )

        # 注意：不同驱动写法略有区别，你原来用的是 dictionary="true"，我保留原样
        cursor = db_conn.cursor(dictionary=True)

        # 3.查询用户信息
        query = """
            SELECT user_id, username, password, admin_id
            FROM user_info
            WHERE username = %s AND password = %s;
        """
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Username or password are wrong"
            )

        db_conn.commit()

        # 4.返回登录成功信息：带上 user_id 和 admin_id
        return {
            "message": "Login successful",
            "username": user["username"],
            "user_id": user["user_id"],
            "admin_id": user["admin_id"],   # 普通用户这里是 None
        }

    except HTTPException:
        # 重新抛出已知的 HTTP 异常
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"登录失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
