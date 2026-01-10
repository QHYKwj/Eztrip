# routers/create_trip.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/create_trip", tags=["create_trip"])

@router.post("")

async def create_trip(user_id:int = Form(...),trip_name: str = Form(...), destination: str = Form(...), start_date: str = Form(...), end_date: str = Form(...), create_time: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数是否为空
        if not all([str(user_id).strip(), trip_name.strip(), destination.strip(), start_date.strip(), end_date.strip(), create_time.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Trip_name,destination,start_date,end_date and create_time are not allowed to be null"
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

        # 3.检查user_id是否在于用户表中
        select_query = "SELECT * from user_info WHERE user_id = %s"
        cursor.execute(select_query, (user_id,))

        if not cursor.fetchone():
            raise HTTPException(
                status_code = 404,
                detail = "User_id not found in user_info"
            )

        # 4.将数据插入行程表
        insert_query = "INSERT INTO trip (user_id, trip_name, destination, start_date, end_date, create_time) " \
        "values(%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (user_id, trip_name, destination, start_date, end_date, create_time,))

        db_conn.commit()
        
        return {"message":"Create trip successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"创建行程失败: {str(e)}"
        ) 
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()



        

        
