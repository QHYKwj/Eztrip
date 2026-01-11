from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.connect_db import connect_db

router = APIRouter(prefix="/api/collect", tags=["trip_favorite"])

# 收藏/取消收藏的请求体模型（用于接收用户ID和行程ID）
class TripFavoriteRequest(BaseModel):
    user_id: int  # 收藏/取消收藏的用户ID
    trip_id: int  # 目标行程ID

# 接口1： 添加行程收藏（用户收藏行程）
@router.post("/favorite/add", summary="收藏行程")
async def add_trip_favorite(favorite_data: TripFavoriteRequest):
    db_conn = None
    cursor = None
    user_id = favorite_data.user_id
    trip_id = favorite_data.trip_id

    try:
        # 1. 建立数据库连接
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 2. 校验：用户是否存在（查询user_info表）
        cursor.execute("SELECT user_id FROM user_info WHERE user_id=%s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")

        # 3. 校验：行程是否存在且状态合法（查询trip表，仅已发布行程可收藏）
        cursor.execute("""
            SELECT trip_id FROM trip 
            WHERE trip_id=%s AND publish_status='published' AND is_public=1
        """, (trip_id,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, 
                detail=f"行程ID {trip_id} 不存在，或未发布/未公开，无法收藏"
            )

        # 4. 校验：是否已收藏（避免重复插入，利用trip_favorite联合主键特性，也可主动查询）
        cursor.execute("""
            SELECT user_id, trip_id FROM trip_favorite 
            WHERE user_id=%s AND trip_id=%s
        """, (user_id, trip_id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="已收藏该行程，无需重复操作")

        # 5. 插入收藏记录（trip_favorite表）
        cursor.execute("""
            INSERT INTO trip_favorite (user_id, trip_id, created_at) 
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        """, (user_id, trip_id))
        # 提交事务
        db_conn.commit()

        # 6. 返回成功响应（明确返回行程ID和用户ID，优化格式可读性）
        return {
            "code": 200,
            "message": "收藏行程成功",
            "data": {
                "user_id": user_id,  # 明确返回操作用户ID
                "trip_id": trip_id   # 明确返回被收藏的行程ID
            }
        }

    except HTTPException:
        # 保留自定义HTTP异常，直接抛出
        raise
    except Exception as e:
        # 捕获未知异常，返回500错误
        if db_conn:
            db_conn.rollback()  # 异常时回滚事务
        raise HTTPException(status_code=500, detail=f"添加收藏失败：{str(e)}")
    finally:
        # 释放数据库资源，无论成功与否都执行
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

# 接口2：取消行程收藏（用户取消已收藏行程）
@router.post("/favorite/remove", summary="取消收藏行程")
async def remove_trip_favorite(favorite_data: TripFavoriteRequest):
    db_conn = None
    cursor = None
    user_id = favorite_data.user_id
    trip_id = favorite_data.trip_id

    try:
        # 1. 建立数据库连接
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")
        cursor = db_conn.cursor(dictionary=True)

        # 2. 校验：用户是否存在
        cursor.execute("SELECT user_id FROM user_info WHERE user_id=%s", (user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"用户ID {user_id} 不存在")

        # 3. 校验：是否已收藏（未收藏则无法取消）
        cursor.execute("""
            SELECT user_id, trip_id FROM trip_favorite 
            WHERE user_id=%s AND trip_id=%s
        """, (user_id, trip_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="未收藏该行程，无需取消")

        # 4. 删除收藏记录（trip_favorite表）
        cursor.execute("""
            DELETE FROM trip_favorite 
            WHERE user_id=%s AND trip_id=%s
        """, (user_id, trip_id))
        # 提交事务
        db_conn.commit()

        # 5. 校验是否删除成功（影响行数判断）
        if cursor.rowcount == 0:
            raise HTTPException(status_code=500, detail="取消收藏失败!")

        # 6. 返回成功响应（明确返回行程ID和用户ID，优化格式可读性）
        return {
            "code": 200,
            "message": "取消行程收藏成功",
            "data": {
                "user_id": user_id,  # 明确返回操作用户ID
                "trip_id": trip_id   # 明确返回被取消收藏的行程ID
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"取消收藏失败：{str(e)}")
    finally:
        # 释放数据库资源
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()