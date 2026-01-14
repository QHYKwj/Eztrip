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
from openai import OpenAI

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
  

import requests

# url = "http://127.0.0.1:8000/api/model"


# # 发送 GET 请求
# response = requests.post(url, data={"prompt": "请问从北京到广州可以选择哪些交通方式？"})

# print("状态码:", response.status_code)
# print("响应内容:", response.text)
# print("JSON 响应:", response.json())