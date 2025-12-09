# routers/notice/delete_notice.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/notice", tags=["notice"])
@router.post("/delete_notice")
async def delete_notice(notice_id: int = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if notice_id <= 0:
            raise HTTPException(
                status_code = 400,
                detail = "Invalid notice ID"
            ) 
        
        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        cursor = db_conn.cursor()

        # 3.删除公告从数据库
        delete_query = "DELETE FROM notice WHERE notice_id = %s;"
        cursor.execute(delete_query, (notice_id,))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400, 
                detail="Delete notice unsuccessful or notice not found"
            )
        
        db_conn.commit()

        return {"message":"Delete notice successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"删除公告失败: {str(e)}"
        )  
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()