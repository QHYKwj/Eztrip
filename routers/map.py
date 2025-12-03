# routers/map.py
from fastapi import APIRouter, HTTPException, Query
import os
import urllib.parse
from settings import AMAP_WEB_KEY

router = APIRouter(prefix="/api/map", tags=["map"])

# ✅ 高德 Web 服务 KEY（必须是 Web 服务 key，不是 JS key）
# 推荐：在系统环境变量里配置 AMAP_WEB_KEY
# AMAP_WEB_KEY = os.getenv("AMAP_WEB_KEY", "YOUR_AMAP_WEB_SERVICE_KEY_HERE")

# 高德静态地图基础 URL
AMAP_STATIC_BASE_URL = "https://restapi.amap.com/v3/staticmap"


@router.get("/url")
async def get_map_url(
        lng: float = Query(..., description="地图中心点经度，如 116.397428"),
        lat: float = Query(..., description="地图中心点纬度，如 39.90923"),
        zoom: int = Query(14, ge=1, le=18, description="缩放等级 1-18"),
        width: int = Query(600, ge=1, le=1024, description="图片宽度，最大 1024"),
        height: int = Query(300, ge=1, le=1024, description="图片高度，最大 1024"),
        label: str = Query("A", description="标记点上的文本，如 A/B/1"),
):
    """
    返回一个高德静态地图 URL，前端直接用 <img :src="url"> 即可显示。
    """

    # 1. 检查 key 是否正确配置
    if not AMAP_WEB_KEY or AMAP_WEB_KEY == "YOUR_AMAP_WEB_SERVICE_KEY_HERE":
        raise HTTPException(
            status_code=500,
            detail="高德 Web 服务 Key 未配置，请在环境变量 AMAP_WEB_KEY 中设置，或者修改 routers/map.py 中 AMAP_WEB_KEY。",
        )

    # 2. 组装静态地图参数
    center = f"{lng},{lat}"            # 中心点坐标
    size = f"{width}*{height}"         # 图片大小
    label = label or "A"

    # markers 格式：
    # markers=mid,0xFF0000,A:116.397428,39.90923
    marker_style = f"mid,0xFF0000,{label}"
    markers = f"{marker_style}:{center}"

    query_params = {
        "key": AMAP_WEB_KEY,
        "location": center,
        "zoom": str(zoom),
        "size": size,
        "markers": markers,
        # 以后如果要加 paths、labels 等，可以继续往这里加
    }

    url = f"{AMAP_STATIC_BASE_URL}?{urllib.parse.urlencode(query_params)}"

    # 统一返回格式
    return {"url": url}
