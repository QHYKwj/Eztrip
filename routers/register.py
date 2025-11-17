# routers/register.py
from fastapi import APIRouter, Form, HTTPException

register_router = APIRouter(prefix="/api/register", tags=["register"])

# 设置路由标识
@register_router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    if username =="Luo" and password == "050129":
        return {"message":"Register successful"}
    else:
        raise HTTPException(status_code=401,detail="Register Failed!")
    