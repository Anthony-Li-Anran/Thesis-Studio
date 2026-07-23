"""Chainlit 对话交互界面。"""

import chainlit as cl

from ..api.dependencies import get_llm_provider


@cl.on_chat_start  # type: ignore[untyped-decorator]
async def on_chat_start() -> None:
    """初始化对话：创建 LLM 实例并问候。"""
    cl.user_session.set("llm", get_llm_provider())
    await cl.Message(
        content="你好！我是 ThesisOS 研究助手。我可以帮你：\n"
        "🔍 检索文献\n"
        "📝 撰写论文\n"
        "📊 分析数据\n"
        "✨ 润色文本\n\n"
        "请告诉我你需要什么帮助？"
    ).send()


@cl.on_message  # type: ignore[untyped-decorator]
async def on_message(message: cl.Message) -> None:
    """处理用户消息，调用 LLM 生成回复。"""
    llm = cl.user_session.get("llm")
    if llm is None:
        llm = get_llm_provider()
        cl.user_session.set("llm", llm)

    try:
        response = await llm.generate(message.content)
        await cl.Message(content=response).send()
    except Exception as e:
        await cl.Message(content=f"抱歉，处理出错了：{e}").send()
