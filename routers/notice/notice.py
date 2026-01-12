# routers/notice/create_notice.py
from fastapi import APIRouter, Form, HTTPException
from config.connect_db import connect_db

router = APIRouter(prefix="/api/notice", tags=["notice"])
@router.post("/update_notice", summary="更新公告")
async def update_notice(notice_id: int = Form(...), title: str = Form(...), content: str = Form(...), is_active: int = Form(...)):
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
        update_query = "UPDATE notice SET notice_title = %s, notice_content = %s, is_active = %s WHERE notice_id = %s;"
        cursor.execute(update_query, (title, content, is_active, notice_id))
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

@router.post("/delete_notice", summary="删除公告")
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

@router.post("/create_notice", summary="创建公告")
async def create_notice(title: str = Form(...), content: str = Form(...), admin_id: int = Form(...), is_active: int = Form(...)):
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
        insert_query = "INSERT INTO notice (notice_title, notice_content, create_at, admin_id, is_active) VALUES (%s, %s, %s, %s, %s);"
        cursor.execute(insert_query, (title, content, admin_id, is_active))
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

@router.get("/all_notice_info", summary="获取所有公告信息")
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