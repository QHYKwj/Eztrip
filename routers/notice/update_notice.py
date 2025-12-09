# routers/notice/create_notice.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/notice", tags=["notice"])
@router.post("/update_notice")
async def update_notice(notice_id: int = Form(...), title: str = Form(...), content: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if notice_id <= 0:
            raise HTTPException(
                status_code = 400,
                detail = "Invalid notice ID"
            ) 
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

        # 3.更新公告到数据库
        update_query = "UPDATE notice SET notice_title = %s, notice_content = %s WHERE notice_id = %s;"
        cursor.execute(update_query, (title, content, notice_id))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400, 
                detail="Update notice unsuccessful or notice not found"
            )
        
        db_conn.commit()

        return {"message":"Update notice successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"更新公告失败: {str(e)}"
        )  
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()