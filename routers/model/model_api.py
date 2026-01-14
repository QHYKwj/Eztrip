# from openai import OpenAI
# import os

# # 初始化OpenAI客户端
# client = OpenAI(
#     # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
#     api_key="sk-addf3b464df84505837675c2af684f83",
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )

# messages = [{"role": "user", "content": "请问从北京到广州可以选择哪些交通方式？"}]
# completion = client.chat.completions.create(
#     model="deepseek-v3.2",
#     messages=messages,
#     # 通过 extra_body 设置 enable_thinking 开启思考模式
#     extra_body={"enable_thinking": True},
#     stream=True,
#     stream_options={
#         "include_usage": True
#     },
# )

# reasoning_content = ""  # 完整思考过程
# answer_content = ""  # 完整回复
# is_answering = False  # 是否进入回复阶段
# print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

# for chunk in completion:
#     if not chunk.choices:
#         print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
#         print(chunk.usage)
#         continue

#     delta = chunk.choices[0].delta

#     # 只收集思考内容
#     if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
#         if not is_answering:
#             print(delta.reasoning_content, end="", flush=True)
#         reasoning_content += delta.reasoning_content

#     # 收到content，开始进行回复
#     if hasattr(delta, "content") and delta.content:
#         if not is_answering:
#             print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
#             is_answering = True
#         print(delta.content, end="", flush=True)
#         answer_content += delta.content

# from openai import OpenAI
# import os

# # 初始化OpenAI客户端
# client = OpenAI(
#     # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
#     api_key="sk-addf3b464df84505837675c2af684f83",
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
# )

# messages = [{"role": "user", "content": "请问从北京到广州可以选择哪些交通方式？"}]

# # 非流式调用，去掉stream相关参数
# completion = client.chat.completions.create(
#     model="deepseek-v3.2",
#     messages=messages,
#     stream=False,  # 设置为False表示非流式输出
#     extra_body={"enable_thinking": True}  # 思考模式仍然有效
# )

# # 直接获取完整回复
# if hasattr(completion.choices[0].message, 'reasoning_content') and completion.choices[0].message.reasoning_content:
#     print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")
#     print(completion.choices[0].message.reasoning_content)
    
#     print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
#     print(completion.choices[0].message.content)
# else:
#     print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
#     print(completion.choices[0].message.content)

# # 打印token使用情况
# if hasattr(completion, 'usage'):
#     print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
#     print(completion.usage)

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os
import json

router = APIRouter(prefix="/api/model", tags=["model"])

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-addf3b464df84505837675c2af684f83",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

@router.post("")
async def chat_with_model(prompt: str = Form(...)):
    """
    与大模型对话接口
    
    参数说明：
    - prompt: 用户输入的提示词
    """
    try:
        # 验证输入参数
        if not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail="提示词不能为空"
            )

        # 调用大模型
        completion = client.chat.completions.create(
            model="deepseek-v3.2",
            messages=[{"role": "user", "content": prompt}],
            stream=False  # 非流式，直接获取完整结果
        )

        # 返回大模型的回答
        return {
            "response": completion.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"大模型调用失败: {str(e)}"
        )

def sse_pack(data: dict) -> str:
    """
    把 dict 打包成 SSE 格式
    """
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

@router.post("/stream")
async def chat_with_model_stream(prompt: str = Form(...)):
    """
    流式对话接口（SSE）
    前端通过 fetch 读取 stream 并实时显示
    """
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="提示词不能为空")

    def gen():
        try:
            # ✅ stream=True 开启流式
            stream = client.chat.completions.create(
                model="deepseek-v3.2",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            # 可选：先告诉前端“开始了”
            yield sse_pack({"type": "start"})

            for event in stream:
                # OpenAI-compatible 流式增量：delta.content
                delta = event.choices[0].delta
                if delta and getattr(delta, "content", None):
                    yield sse_pack({"type": "delta", "content": delta.content})

            yield sse_pack({"type": "done"})
        except Exception as e:
            # SSE 里也要把错误返回给前端，否则前端只会断流
            yield sse_pack({"type": "error", "message": str(e)})

    return StreamingResponse(gen(), media_type="text/event-stream")


SYSTEM_PROMPT = """
你是“旅游行程推荐平台”的行程规划专家。你的任务是根据用户输入，生成可直接在前端渲染的行程方案。
必须遵守：
1) 输出必须是严格 JSON（不要 Markdown，不要多余文本）。
2) 必须包含：best_time（推荐季节/月份+原因）、days（天数）、overview（100字内概述）、
   schedule（每天：day、morning/afternoon/evening，每段包含：title、spots、duration_hours、transport、notes）、
   food（当地必吃/推荐商圈）、tips（至少5条）、packing（行李清单）、budget（按经济/舒适两档给区间）。
3) 如果用户信息不足（例如：城市、天数、出行时间、预算、偏好），不要反问一堆；你要做“合理默认”，
   同时在 tips 里列出你采用了哪些默认假设。
4) 景点必须尽量具体（如“外滩”“豫园”“迪士尼”这类），并给出建议游玩时段与预计用时。
5) 时间安排要现实：一天最多3-4个核心点；要考虑交通与排队；热门点提示“建议预约/错峰”。
"""

def safe_json_load(s: str):
    """
    处理偶发的模型输出前后夹杂文本的情况，尽量截取 JSON。
    """
    s = s.strip()
    if s.startswith("{") and s.endswith("}"):
        return json.loads(s)
    # 尝试截取第一个 { 到最后一个 }
    l = s.find("{")
    r = s.rfind("}")
    if l != -1 and r != -1 and r > l:
        return json.loads(s[l:r+1])
    raise ValueError("模型未返回有效JSON")

@router.post("/struct")
async def chat_with_model(prompt: str = Form(...)):
    try:
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="提示词不能为空")

        completion = client.chat.completions.create(
            model="deepseek-v3.2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )

        content = completion.choices[0].message.content

        # ✅ 强制解析成 JSON，前端更稳
        data = safe_json_load(content)

        return {"response": data}

    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"模型输出解析失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"大模型调用失败: {str(e)}")