"""Chainlit 对话交互界面。"""

import chainlit as cl

from ..llm import create_llm


@cl.on_chat_start  # type: ignore[untyped-decorator]
async def on_chat_start() -> None:
    """初始化对话。"""
    await cl.Message(content="你好！我是 ThesisOS 研究助手。").send()


@cl.on_message  # type: ignore[untyped-decorator]
async def on_message(message: cl.Message) -> None:
    """处理用户消息，调用 LLM 生成回复。"""
    llm = create_llm()
    response = await llm.generate(message.content)
    await cl.Message(content=response).send()
