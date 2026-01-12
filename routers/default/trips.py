from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from config.connect_db import connect_db

router = APIRouter(prefix="/api/public_trips", tags=["public_trips"])


@router.get("/search_trips")
async def search_public_trips(
        limit: int = Query(50, ge=1, le=200, description="返回条数"),
        offset: int = Query(0, ge=0, description="分页偏移"),

        # ✅ 搜索条件
        destination: Optional[str] = Query(None, description="可选：目的地关键词（模糊匹配）"),
        class_type: Optional[int] = Query(None, ge=1, le=4, description="可选：按分类过滤 1-4"),
        days: Optional[int] = Query(None, ge=1, le=365, description="可选：按天数过滤（end-start+1）"),
):
    """
    搜索公开行程（广场）：
    - 只返回 is_public=1 的行程
    - 默认也限制 publish_status='published'（如需公开但未审核也展示，可注释掉该行）
    - 支持 destination 模糊、class、days 精确过滤
    - 返回：分类信息（class + class_text）、创建者、tripid/标题/目的地、days、created_at
    """
    db_conn = None
    cursor = None

    CLASS_MAP = {
        1: "休闲",
        2: "美食",
        3: "商务",
        4: "家庭",
    }

    try:
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="Failed to connect database")
        cursor = db_conn.cursor(dictionary=True)

        where_parts = ["t.is_public = 1"]
        params: List[Any] = []

        # ✅ 建议：广场通常只展示已发布
        # 如果你想“公开但未审核也要展示”，就把下一行注释掉
        where_parts.append("t.publish_status = 'published'")

        # destination 模糊
        if destination is not None and destination.strip():
            where_parts.append("t.destination LIKE %s")
            params.append(f"%{destination.strip()}%")

        # class 过滤
        if class_type is not None:
            where_parts.append("t.class = %s")
            params.append(class_type)

        # days 过滤：DATEDIFF + 1（包含首尾）
        if days is not None:
            where_parts.append("(DATEDIFF(t.end_date, t.start_date) + 1) = %s")
            params.append(days)

        where_sql = " AND ".join(where_parts)

        sql = f"""
            SELECT
                t.trip_id,
                t.owner_user_id,
                u.username AS creator_username,
                t.title,
                t.destination,
                t.start_date,
                t.end_date,
                t.created_at,
                t.class
            FROM trip t
            JOIN user_info u ON u.user_id = t.owner_user_id
            WHERE {where_sql}
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s;
        """
        params.extend([limit, offset])

        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []

        result: List[Dict[str, Any]] = []
        for r in rows:
            # days = end - start + 1（包含首尾）
            try:
                days_val = (r["end_date"] - r["start_date"]).days + 1
            except Exception:
                days_val = None

            cls = r.get("class")
            result.append({
                "trip_id": r["trip_id"],
                "owner_user_id": r["owner_user_id"],
                "creator_username": r.get("creator_username"),
                "title": r["title"],
                "destination": r["destination"],
                "class": cls,
                "class_text": CLASS_MAP.get(int(cls)) if cls is not None else None,
                "days": days_val,
                "created_at": str(r["created_at"]),
            })

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索公开行程失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
