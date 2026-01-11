# routers/all_user_info.py
from fastapi import APIRouter, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/notice/all_notice_info", tags=["all_notice_info"])

@router.get("", summary="获取所有公告信息")
async def all_user_info():
    db_conn = None
    cursor = None
    
    try:
        # 1.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code=500,
                detail="数据库连接失败"
            )
        
        cursor = db_conn.cursor(dictionary=True)

        # 2.查询用户信息
        query = """
            SELECT 
                notice_id,
                title,
                content,
                created_at
            FROM notice
        """
        cursor.execute(query)
        notice = cursor.fetchall()
        
        # 3.返回结果
        return {
            "success": True,
            "data": {
                "notice": notice,
                "count": len(notice)
            }
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"查询公告失败: {str(e)}"
        )  
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()