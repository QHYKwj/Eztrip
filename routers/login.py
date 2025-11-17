# routers/login.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/login", tags=["login"])

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    try:
        db_conn = connect_db()
        cursor =db_conn.cursor()
        query = "SELECT * FROM user_info WHERE username = %s;"
        # 元组
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return {"message": "Login successful", "username": username}
        else:
            raise HTTPException(status_code=401, detail="Invalid username or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        db_conn.close()
