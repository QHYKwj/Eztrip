# routers/create_trip.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/collect_trip", tags=["collect_trip"])

@router.post("")

async def collect_trip(user_id: int = Form(...), trip_id: int = Form()):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数不为空
        if not all([user_id, trip_id]):
            raise HTTPException(
                status_code = 400,
                detail = "User_id and trip_id are not allowed to be null"
            )
        
        # 2.连接数据库
        db_conn = connect_db()
        # 连接失败
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )
        
        cursor = db_conn.cursor(dictionary="true")

        # 3.查询user_id和 trip_id是否存在
        select_query = "SELECT * FROM trip where user_id = %s and trip_id = %s"
        cursor.execute(select_query, (user_id, trip_id))

        if not cursor.fetchone():
            raise HTTPException(
                status_code = 404,
                detail = "user_id or trip_id not found"
            )

        # 4.修改收藏状态
        update_query = "UPDATE trip SET is_collect = %s WHERE user_id = %s and trip_id = %s"
        cursor.execute(update_query, ("true", user_id, trip_id, ))

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code = 400,
                detail = "Collect trip unsuccessful"
            )    

        db_conn.commit()

        return {"message":"Collect trip successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"收藏行程失败: {str(e)}"
        ) 
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

