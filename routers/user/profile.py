# routers/exit.py
from fastapi import APIRouter, HTTPException, Form
from config.connect_db import connect_db
from datetime import date

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/{user_id}")
async def get_profile(user_id: int):
    """
    获取用户个人信息 + 行程统计：
    - 基本信息来自 user_info（含 phone_num, birthday）
    - 统计来自 trip / trip_favorite：
        trip.owner_user_id = user_id:
            end_date < 今天      -> 已完成行程
            start_date > 今天    -> 待出发行程
        trip_favorite.user_id = user_id:
            -> 收藏行程数量
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        # 1. 查询用户基本信息
        cursor.execute(
            """
            SELECT user_id, username, email, avatar, admin_id, phone_num, birthday
            FROM user_info
            WHERE user_id = %s
            """,
            (user_id,),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. 统计行程信息来自 trip（这个行程属于该用户）
        # end_date < CURDATE()  -> 已完成
        # start_date > CURDATE() -> 待出发
        cursor.execute(
            """
            SELECT
              SUM(CASE WHEN end_date < CURDATE() THEN 1 ELSE 0 END) AS completed_trips,
              SUM(CASE WHEN start_date > CURDATE() THEN 1 ELSE 0 END) AS upcoming_trips
            FROM trip
            WHERE owner_user_id = %s
            """,
            (user_id,),
        )
        trip_stats = cursor.fetchone() or {}

        # 3. 收藏行程数量来自 trip_favorite
        cursor.execute(
            """
            SELECT COUNT(*) AS collected_trips
            FROM trip_favorite
            WHERE user_id = %s
            """,
            (user_id,),
        )
        fav_stats = cursor.fetchone() or {}

        # birthday 转成字符串
        birthday_val = user.get("birthday")
        if isinstance(birthday_val, date):
            user["birthday"] = birthday_val.isoformat()

        result = {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "avatar": user.get("avatar"),
            "admin_id": user.get("admin_id"),
            "phone_num": user.get("phone_num"),
            "birthday": user.get("birthday"),
            "stats": {
                "completed_trips": int(trip_stats.get("completed_trips") or 0),
                "upcoming_trips": int(trip_stats.get("upcoming_trips") or 0),
                "collected_trips": int(fav_stats.get("collected_trips") or 0),
            },
        }
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取个人信息失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()


@router.put("/{user_id}")
async def update_profile(
        user_id: int,
        phone_num: str = Form(None),
        birthday: str = Form(None),    # 'YYYY-MM-DD'
        avatar: str = Form(None),
        email: str = Form(None),
):
    """
    编辑用户基本信息（可更新 phone_num / birthday / avatar / email）。
    前端用 FormData 提交这些字段，有则更新，无则忽略。
    """
    db_conn = None
    cursor = None
    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")

        cursor = db_conn.cursor(dictionary=True)

        # 检查用户是否存在
        cursor.execute("SELECT user_id FROM user_info WHERE user_id = %s", (user_id,))
        exists = cursor.fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="User not found")

        updates = []
        params = []

        if phone_num is not None:
            updates.append("phone_num = %s")
            params.append(phone_num)

        if birthday is not None and birthday != "":
            updates.append("birthday = %s")
            params.append(birthday)

        if avatar is not None:
            updates.append("avatar = %s")
            params.append(avatar)

        if email is not None:
            updates.append("email = %s")
            params.append(email)

        if not updates:
            return {"message": "No fields to update"}

        params.append(user_id)
        sql = "UPDATE user_info SET " + ", ".join(updates) + " WHERE user_id = %s"
        cursor.execute(sql, tuple(params))
        db_conn.commit()

        return {"message": "Profile updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新个人信息失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
