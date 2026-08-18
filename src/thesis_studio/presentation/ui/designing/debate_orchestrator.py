"""Debate orchestrator for DESIGNING phase."""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable
from enum import Enum, auto

from ....infrastructure.bootstrap import get_llm_for_agent
from .chat_renderer import AGENT_LABELS, AGENT_LIST

_LLM_TIMEOUT: int = 120


class _ChatState(Enum):
    IDLE = auto()
    RESPONDING = auto()
    DEBATING = auto()
    PROPOSING = auto()


def _loading_text(agent: str, round: int = 0, stage: str = "") -> str:
    labels_cn = {"researcher": "研究员", "debater": "辩手", "reviewer": "审稿人"}
    if stage == "proposing":
        return "研究员正在整理修改建议..."
    if round:
        return f"[第{round}轮] {labels_cn.get(agent, agent)}思考中..."
    return f"{labels_cn.get(agent, agent)}思考中..."


class DebateOrchestrator:
    """Manages multi-agent debate state machine. UI-agnostic."""

    def __init__(self, outline_getter: Callable[[], str], max_rounds: int = 3) -> None:
        self._outline_getter = outline_getter
        self._max_rounds = max_rounds
        self._state: _ChatState = _ChatState.IDLE
        self._current_task: asyncio.Task | None = None
        self._pending_message: str | None = None
        self._on_add_message: Callable[[str, str, str], None] | None = None
        self._on_add_system: Callable[[str], None] | None = None
        self._on_replace_last: Callable[[str, str, str], None] | None = None
        self._on_suggestions: Callable[[list[dict[str, str]]], None] | None = None

    def on_add_message(self, cb: Callable[[str, str, str], None]) -> None:
        self._on_add_message = cb

    def on_add_system(self, cb: Callable[[str], None]) -> None:
        self._on_add_system = cb

    def on_replace_last(self, cb: Callable[[str, str, str], None]) -> None:
        self._on_replace_last = cb

    def on_suggestions(self, cb: Callable[[list[dict[str, str]]], None]) -> None:
        self._on_suggestions = cb

    @property
    def state(self) -> _ChatState:
        return self._state

    def request_stop(self) -> None:
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

    def queue_message(self, text: str) -> None:
        self._pending_message = text

    def take_pending(self) -> str | None:
        msg = self._pending_message
        self._pending_message = None
        return msg

    async def handle_user_input(self, user_text: str) -> None:
        targets = self._parse_mentions(user_text)
        if "all" in targets or len(targets) > 1:
            self._state = _ChatState.DEBATING
            await self._run_debate(user_text)
        else:
            agent = targets[0]
            self._state = _ChatState.RESPONDING
            self._emit_message("agent", _loading_text(agent), agent)
            try:
                llm = await get_llm_for_agent(agent)
                task = asyncio.ensure_future(
                    llm.generate(self._build_prompt(user_text, agent))
                )
                self._current_task = task
                response = await asyncio.wait_for(task, timeout=_LLM_TIMEOUT)
                self._emit_replace("agent", response, agent)
                if agent == "researcher":
                    self._check_suggestions(response)
            except asyncio.TimeoutError:
                self._emit_system("响应超时，请重试。")
            except asyncio.CancelledError:
                self._emit_system("已停止。")
            except Exception as e:
                self._emit_replace("agent", f"Error: {e}", agent)
            finally:
                self._current_task = None
                self._state = _ChatState.IDLE

    def _emit_message(self, role: str, content: str, agent: str) -> None:
        if self._on_add_message:
            self._on_add_message(role, content, agent)

    def _emit_system(self, content: str) -> None:
        if self._on_add_system:
            self._on_add_system(content)

    def _emit_replace(self, role: str, content: str, agent: str) -> None:
        if self._on_replace_last:
            self._on_replace_last(role, content, agent)

    def _parse_mentions(self, text: str) -> list[str]:
        mentions = re.findall(r"@([\w\u4e00-\u9fff]+)", text)
        if not mentions:
            return ["all"]
        cn_map = {
            "研究员": "researcher", "researcher": "researcher",
            "辩手": "debater", "debater": "debater",
            "审稿人": "reviewer", "reviewer": "reviewer",
        }
        targets = []
        for m in mentions:
            ml = m.lower()
            if ml in ("all", "全部"):
                return ["all"]
            mapped = cn_map.get(ml)
            if mapped:
                targets.append(mapped)
        return targets if targets else ["all"]

    async def _run_debate(self, user_text: str) -> None:
        self._state = _ChatState.DEBATING
        context = user_text
        round = 0
        concluded = False
        try:
            while round < self._max_rounds and not concluded:
                round += 1
                for agent in AGENT_LIST:
                    self._emit_message("agent", _loading_text(agent, round), agent)
                    try:
                        llm = await get_llm_for_agent(agent)
                        task = asyncio.ensure_future(
                            llm.generate(self._build_debate_prompt(context, agent, round))
                        )
                        self._current_task = task
                        response = await asyncio.wait_for(task, timeout=_LLM_TIMEOUT)
                        self._emit_replace("agent", response, agent)
                        context += f"\n\n{AGENT_LABELS[agent]}: {response}"
                        context = self._trim_context(context)
                        if agent == "reviewer" and self._reviewer_passes(response):
                            self._emit_system("审稿人批准。辩论结束。")
                            concluded = True
                            break
                        await asyncio.sleep(0.3)
                    except asyncio.TimeoutError:
                        self._emit_replace("agent", "超时，跳过此轮。", agent)
                        continue
                    except Exception as e:
                        self._emit_replace("agent", f"Error: {e}", agent)
                        continue
            if not concluded:
                self._emit_system(f"已达最大轮次（{self._max_rounds}）。研究员将整理修改建议。")
            self._state = _ChatState.PROPOSING
            await self._propose_final_changes(context)
        except asyncio.CancelledError:
            self._emit_system("已停止辩论。")
        finally:
            self._current_task = None
            self._state = _ChatState.IDLE

    async def _propose_final_changes(self, context: str) -> None:
        self._emit_system("研究员正在整理最终修改建议...")
        outline = self._outline_getter()
        json_example = (
            '{"suggestions": [{"section": "章节标题", "old": "旧文本", "new": "新文本"}]}'
        )
        prompt = (
            f"你是研究员（Researcher），研究设计专家。\n"
            f"基于以上辩论讨论，为大纲提出具体的修改建议。\n\n"
            f"当前大纲：\n```\n{outline}\n```\n\n"
            f"讨论摘要：\n{context}\n\n"
            f"只输出一个JSON块，包含你的修改建议：\n"
            f"```json\n{json_example}\n```\n"
            f"如果无需修改，输出：```json\n{{\"suggestions\": []}}\n```"
        )
        self._emit_message("agent", _loading_text("researcher", stage="proposing"), "researcher")
        try:
            llm = await get_llm_for_agent("researcher")
            task = asyncio.ensure_future(llm.generate(prompt))
            self._current_task = task
            response = await asyncio.wait_for(task, timeout=_LLM_TIMEOUT)
            self._emit_replace("agent", response, "researcher")
            self._check_suggestions(response)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self._emit_replace("agent", f"Error: {e}", "researcher")

    def _reviewer_passes(self, response: str) -> bool:
        import json as _json
        json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
        if json_match:
            try:
                data = _json.loads(json_match.group(1))
                decision = data.get("decision", "")
                if decision in ("pass", "approved"):
                    return True
                if decision in ("continue", "needs_more"):
                    return False
            except _json.JSONDecodeError:
                pass
        lower = response.lower()
        has_pass = any(
            p in lower
            for p in [
                "looks good", "approved", "pass", "no major issue",
                "well structured", "ready", "comprehensive",
                "通过", "批准", "没问题", "完善", "合格", "可行",
            ]
        )
        granularity_ok = "granularity pass" in lower or "粒度检查通过" in lower
        return has_pass and granularity_ok

    def _check_suggestions(self, response: str) -> None:
        import logging
        _log = logging.getLogger(__name__)

        # Try ```json fences first
        json_match = re.search(r"```json\s*\n(.*?)\n\s*```", response, re.DOTALL)
        if not json_match:
            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)

        json_str = None
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: bare JSON object containing "suggestions" key
            bare = re.search(r'\{\s*"suggestions"\s*:\s*\[.*?\]\s*\}', response, re.DOTALL)
            if bare:
                json_str = bare.group()
                _log.debug("_check_suggestions: found bare JSON (no fences)")
            else:
                _log.debug("_check_suggestions: no JSON block or bare JSON found")
                return

        try:
            data = json.loads(json_str)
            suggestions = data.get("suggestions", [])
            _log.debug("_check_suggestions: parsed %d suggestions", len(suggestions))
            if suggestions and self._on_suggestions:
                _log.debug("_check_suggestions: calling callback")
                self._on_suggestions(suggestions)
            elif not suggestions:
                _log.debug("_check_suggestions: empty suggestions")
            elif not self._on_suggestions:
                _log.warning("_check_suggestions: callback is None!")
        except (json.JSONDecodeError, AttributeError) as e:
            _log.warning("Failed to parse suggestions JSON: %s", e)

    def _build_prompt(self, user_text: str, agent: str) -> str:
        outline = self._outline_getter()
        labels_cn = {"researcher": "研究员", "debater": "辩手", "reviewer": "审稿人"}
        cn = labels_cn.get(agent, "研究设计专家")
        en = AGENT_LABELS.get(agent, "assistant")
        json_example = (
            '{"suggestions": [{"section": "章节标题", "old": "旧文本", "new": "新文本"}]}'
        )
        return (
            f"你是{cn}（{en}），一位学术研究设计专家。\n\n"
            f"当前大纲：\n```\n{outline}\n```\n\n"
            f"用户：{user_text}\n\n"
            f"请用中文回复，简洁专业。\n"
            f"如需建议大纲修改，请输出JSON块：\n"
            f"```json\n{json_example}\n```\n"
            f"你可以在回复中 @mention 其他 agent 或 @user。"
        )

    def _build_debate_prompt(self, context: str, agent: str, round: int) -> str:
        outline = self._outline_getter()
        role_desc = {
            "researcher": (
                "研究员（Researcher）：文献与方法论专家。"
                "请提供基于证据的建议。"
                "你可以 @mention @Debater 或 @Reviewer。"
            ),
            "debater": (
                "辩手（Debater）：批判性思维者。质疑假设，指出漏洞。"
                "你可以 @mention @Researcher 或 @Reviewer。"
            ),
            "reviewer": (
                "审稿人（Reviewer）：学术审稿人。检查完整性、严谨性、可行性，\n"
                "以及大纲粒度。\n"
                "粒度规则：每个章节必须描述\'研究什么\'\n"
                "（例如 3.1 基于随机傅里叶特征的Softmax核），\n"
                "不能太粗（例如 3.1 方法论），\n"
                "也不能太细（例如 3.1 用PyTorch实现RFF）。\n"
                "如果方案完全满意且粒度通过，输出JSON：\n"
                "```json\n{\"decision\": \"pass\"}\n```\n"
                "如果还需要改进，输出JSON：\n"
                "```json\n{\"decision\": \"continue\"}\n```\n"
                "你必须在回复中声明：\'粒度检查通过\' 或 \'粒度检查不通过\'。\n"
                "你可以 @mention @Researcher 或 @Debater。"
            ),
        }
        return (
            f"{role_desc.get(agent, '研究设计专家')}\n\n"
            f"当前大纲：\n```\n{outline}\n```\n\n"
            f"辩论第 {round}/{self._max_rounds} 轮：\n{context}\n\n"
            f"请以中文回复。简洁专业。"
        )

    @staticmethod
    def _trim_context(context: str, max_chars: int = 8000) -> str:
        if len(context) <= max_chars:
            return context
        keep_head = max_chars // 5
        keep_tail = max_chars - keep_head
        return context[:keep_head] + "\n\n[... 上下文已截断 ...]\n\n" + context[-keep_tail:]


ChatState = _ChatState
