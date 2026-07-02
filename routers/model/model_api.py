from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from datetime import date, timedelta
import os
import json
from datetime import date, timedelta

# 引入你的数据库连接
from config.connect_db import connect_db

router = APIRouter(prefix="/api/model", tags=["model"])

# ==========================================
# 0. 初始化 OpenAI 客户端 (适配最新 DeepSeek 官方 API)
# ==========================================
# 强烈建议将 API KEY 放在环境变量或配置字典中
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY', "sk-3ec2308955134a51b7e6c2ae50bec60c"), # 替换为你的真实 Key
    base_url="https://api.deepseek.com"
)

# ==========================================
# 1. 定义请求和响应的数据模型 (Pydantic)
# ==========================================
class ChatRequest(BaseModel):
    prompt: str

class AgentPlanRequest(BaseModel):
    user_id: int
    prompt: str
    direct_add_plan: bool = False

# ==========================================
# 2. 基础对话接口
# ==========================================
@router.post("")
async def chat_with_model(request: ChatRequest):
    """普通非流式对话"""
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="提示词不能为空")

        completion = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": request.prompt}],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )
        # 直接返回最终回答内容（这里不返回思考过程给前端，只返回最终结果）
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"大模型调用失败: {str(e)}")


def sse_pack(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def chat_with_model_stream(request: ChatRequest):
    """流式对话接口（SSE）"""
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="提示词不能为空")

    def gen():
        try:
            stream = client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=[{"role": "user", "content": request.prompt}],
                stream=True,
                extra_body={"thinking": {"type": "disabled"}} # 流式也可以开启思考
            )
            yield sse_pack({"type": "start"})
            for event in stream:
                delta = event.choices[0].delta

                # 如果你想把思考过程也推给前端，可以检测 reasoning_content
                # if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                #     yield sse_pack({"type": "thinking", "content": delta.reasoning_content})

                # 推送正式内容
                if getattr(delta, "content", None):
                    yield sse_pack({"type": "delta", "content": delta.content})
            yield sse_pack({"type": "done"})
        except Exception as e:
            yield sse_pack({"type": "error", "message": str(e)})

    return StreamingResponse(gen(), media_type="text/event-stream")

# ==========================================
# 3. Agent 核心接口：生成 JSON 并写入数据库
# ==========================================
AGENT_SYSTEM_PROMPT = """
你是一个专业的旅游行程规划Agent。你需要根据用户的需求生成一份详细行程，必须以严格的JSON格式返回，不要包含任何Markdown标记。

必须包含的JSON字段：
{
  "reply_text": "亲切的回复话语...",
  "trip_title": "行程标题，如：'广州3日游'",
  "destination": "目的地城市名称",
  "total_days": 3,
  "overview": "100字内概述",
  "best_time": "推荐季节及原因",
  "budget": "预算区间",
  "accommodation": "推荐的住宿地点/商圈/酒店类型",
  "food": "推荐的美食及特色商圈",
  "packing": ["必带物品1", "必带物品2", "必带物品3"],
  "tips": ["避坑提示1", "避坑提示2"],
  "days": [
    {
      "day_index": 1,
      "note": "第一天的整体规划说明",
      "items": [
        {"title": "广州塔", "place_type": "景点"},
        {"title": "陶陶居", "place_type": "餐厅"}
      ]
    }
  ]
}
"""

def safe_json_load(s: str):
    """
    即使大模型输出了带有 markdown 甚至 <think> 标签的内容，
    这个函数也能尝试精准截取并解析最外层的 JSON 结构。
    """
    if not s:
        raise ValueError("模型返回为空")

    # 尝试直接解析
    s = s.strip()
    try:
        if s.startswith("{") and s.endswith("}"):
            return json.loads(s)
    except json.JSONDecodeError:
        pass

    # 截取第一个 '{' 到最后一个 '}'
    l = s.find("{")
    r = s.rfind("}")
    if l != -1 and r != -1 and r > l:
        try:
            return json.loads(s[l:r+1])
        except json.JSONDecodeError as e:
            raise ValueError(f"截取JSON后解析仍失败: {str(e)}")

    raise ValueError("模型输出未包含有效JSON格式")

@router.post("/agent_plan")
async def generate_and_save_plan(request: AgentPlanRequest):
    """
    智能体行程规划接口
    根据 direct_add_plan 决定是否自动落库
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="提示词不能为空")

    try:
        # 1. 仅聊天模式
        if not request.direct_add_plan:
            completion = client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=[{"role": "user", "content": request.prompt}],
                stream=False,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}}
            )
            return {
                "reply": completion.choices[0].message.content,
                "trip_id": None
            }

        # 2. Agent 工作模式：强制系统提示词输出 JSON
        completion = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": request.prompt}
            ],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
            # 如果 DeepSeek API 报错不支持 response_format="json_object"，可以注释掉下一行
            # response_format={"type": "json_object"}
        )

        content = completion.choices[0].message.content
        ai_data = safe_json_load(content)

        # 3. 开启数据库事务，进行插入操作
        db_conn = connect_db()
        if not db_conn:
            raise HTTPException(status_code=500, detail="数据库连接失败")

        cursor = db_conn.cursor()
        trip_id = None

        try:
            # 默认从今天开始排期
            start_date = date.today()
            total_days = ai_data.get("total_days", 1)
            end_date = start_date + timedelta(days=total_days - 1)

            # 🌟 核心修改：将 AI 生成的锦囊数据打包成标准字典
            remarks_dict = {
                "overview": ai_data.get("overview", "一场说走就走的旅行"),
                "best_time": ai_data.get("best_time", "四季皆宜"),
                "budget": ai_data.get("budget", "丰俭由人"),
                "accommodation": ai_data.get("accommodation", "建议根据行程安排选择交通便利的商圈"),
                "food": ai_data.get("food", "探索当地特色美食"),
                "packing": ai_data.get("packing", []),
                "tips": ai_data.get("tips", [])
            }
            # 转为 JSON 字符串准备存入数据库
            remarks_json = json.dumps(remarks_dict, ensure_ascii=False)

            # 插入 trip 表 (默认设为草稿状态 draft)
            insert_trip_sql = """
                INSERT INTO trip (owner_user_id, title, destination, start_date, end_date, publish_status, is_public, remarks)
                VALUES (%s, %s, %s, %s, %s, 'draft', 0, %s)
            """
            cursor.execute(insert_trip_sql, (
                request.user_id,
                ai_data.get("trip_title", "未命名行程"),
                ai_data.get("destination", "未知目的地"),
                start_date,
                end_date,
                remarks_json  # <--- 存入 JSON 格式的 remarks
            ))
            trip_id = cursor.lastrowid

            # 遍历插入每日计划 trip_day_plan
            for day in ai_data.get("days", []):
                insert_day_sql = """
                    INSERT INTO trip_day_plan (trip_id, day_index, note)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_day_sql, (
                    trip_id,
                    day.get("day_index", 1),
                    day.get("note", "")
                ))
                day_plan_id = cursor.lastrowid

                # 遍历插入每日具体项目 trip_day_item
                sort_order = 1
                for item in day.get("items", []):
                    insert_item_sql = """
                        INSERT INTO trip_day_item (day_plan_id, title, place_type, sort_order)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_item_sql, (
                        day_plan_id,
                        item.get("title", "未知地点"),
                        item.get("place_type", "景点"),
                        sort_order
                    ))
                    sort_order += 1

            db_conn.commit()

        except Exception as db_e:
            db_conn.rollback()
            raise ValueError(f"数据库写入失败: {str(db_e)}")
        finally:
            cursor.close()
            db_conn.close()

        # 4. 成功返回
        return {
            "reply": ai_data.get("reply_text", "已经为您规划好行程并保存至草稿箱。"),
            "trip_id": trip_id,
            # 将生成的结构化数据带回去给前端，方便调试或做即时渲染的 fallback
            "structured_data": ai_data
        }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"大模型调用失败: {str(e)}")