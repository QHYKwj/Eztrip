# routers/notice/create_notice.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/notice", tags=["notice"])
@router.post("/create_notice")
async def create_notice(title: str = Form(...), content: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not all([title.strip(), content.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Title and content are allowed to be null"
            ) 
        
        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        cursor = db_conn.cursor()

        # 3.插入公告到数据库
        insert_query = "INSERT INTO notice (notice_title, notice_content) VALUES (%s, %s);"
        cursor.execute(insert_query, (title, content))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400, 
                detail="Create notice unsuccessful"
            )
        
        db_conn.commit()

        return {"message":"Create notice successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"创建公告失败: {str(e)}"
        )  
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()