from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/admin/content_count", tags=["content_count"])

@router.get("")  # 修改为GET请求，因为这是获取数据而不是创建数据
async def get_content_count():
    db_conn = None
    cursor = None
    try:
        # 1.连接数据库
        db_conn = connect_db()
        # 连接失败
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        cursor = db_conn.cursor(dictionary=True)  # 修改为布尔值True

        # 2.查看内容总数
        select_query = "SELECT COUNT(*) as total_count FROM trip;"
        cursor.execute(select_query)
        
        # 获取查询结果
        result = cursor.fetchone()
        
        if result:
            content_count = result.get('total_count', 0)
            
            # 返回内容数
            return {
                "success": True,
                "data": {
                    "content_count": content_count
                }
            }
        else:
            return {
                "success": True,
                "data": {
                    "content_count": 0
                }
            }

    except HTTPException:
        raise 
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"获取内容数失败: {str(e)}"
        ) 
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
