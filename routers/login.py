# routers/login.py
from fastapi import APIRouter, Form, HTTPException

router = APIRouter(prefix="/api/login", tags=["login"])

@router.post("")
async def login(username: str = Form(...), password: str = Form(...)):
    # 模拟验证逻辑
    if username == "123@qq.com" and password == "123456":
        return {"message": "Login successful!"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")
