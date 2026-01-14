from fastapi import APIRouter, HTTPException, Form
from config.connect_db import connect_db
from datetime import date

router = APIRouter(prefix="/api/user", tags=["user"])

@router.post("/login", summary="用户登录")
async def login(username: str = Form(...), password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not username.strip() or not password.strip():
            raise HTTPException(
                status_code=400,
                detail="Username and password are not null"
            )

        # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code=500,
                detail="Failed to connect database"
            )

        # 注意：不同驱动写法略有区别，你原来用的是 dictionary="true"，我保留原样
        cursor = db_conn.cursor(dictionary=True)

        # 3.查询用户信息
        query = """
            SELECT user_id, username, password, admin_id
            FROM user_info
            WHERE username = %s AND password = %s;
        """
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Username or password are wrong"
            )

        db_conn.commit()

        # 4.返回登录成功信息：带上 user_id 和 admin_id
        return {
            "message": "Login successful",
            "username": user["username"],
            "user_id": user["user_id"],
            "admin_id": user["admin_id"],   # 普通用户这里是 None
        }

    except HTTPException:
        # 重新抛出已知的 HTTP 异常
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"登录失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()


@router.get("/profile/{user_id}",summary="用户基本信息获取")
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


@router.put("/profile/{user_id}",summary="用户信息更改")
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

@router.post("/register", summary="用户注册")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数是否全不为空
        if not all([username.strip(), email.strip(), password.strip(), confirm_password.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Username,email,password and confirm_password are allowed to be null"
            )

            # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )

        cursor = db_conn.cursor()

        # 3. 检查用户名是否已存在
        check_name_query = "SELECT username FROM user_info WHERE username = %s"
        cursor.execute(check_name_query, (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already existed")

        # 4. 检查邮箱是否使用过
        check_email_query = "SELECT email FROM user_info WHERE email = %s"
        cursor.execute(check_email_query, (email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email is already used")

        # 5.检查两次密码输入是否一致
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="The password and confirm_password are different")

        # 6.将用户信息插入数据库中
        insert_query = "INSERT INTO user_info (username, email, password) values(%s, %s, %s)"
        cursor.execute(insert_query, (username, email, password))
        db_conn.commit()

        return {"message":"Register successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"注册失败: {str(e)}"
        )  # 包含具体错误信息)
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()


@router.post("/change_password", summary="修改用户密码")
async def change_password(username: str = Form(...), email: str = Form() , new_password: str = Form(...)):
    db_conn = None
    cursor = None
    try:
        # 1.验证输入参数
        if not all([username.strip(), email.strip(), new_password.strip()]):
            raise HTTPException(
                status_code = 400,
                detail = "Username,email and new_password are allowed to be null"
            )

            # 2.连接数据库
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(
                status_code = 500,
                detail = "Failed to connect database"
            )

        cursor = db_conn.cursor()

        # 3.检查用户名和邮箱是否正确
        select_query = "SELECT * FROM user_info WHERE username = %s and email = %s;"
        cursor.execute(select_query, (username, email))

        if not cursor.fetchone():
            raise HTTPException(
                status_code = 404,
                detail = "Username or email wrong"
            )

        # 4.更新数据库修改用户密码
        update_query = "UPDATE user_info SET password = %s WHERE username = %s and email = %s"
        cursor.execute(update_query, (new_password, username, email))
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=400,
                detail="Change password unsuccessful"
            )

        db_conn.commit()

        return {"message":"Change password successful"}
    except HTTPException:
        raise
    except Exception as e:
        if db_conn:
            db_conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"修改密码失败: {str(e)}"
        )
    finally:
        # 确保资源被正确释放
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()

