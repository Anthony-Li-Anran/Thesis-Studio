"""EXPLORING workflow graph - step-by-step conversational flow.

Each intent does ONE step. No auto-pipeline.
After each step, generates suggestion buttons for the next step.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from langgraph.graph import END, StateGraph

from ..agent.researcher import Paper, PaperCluster
from ..exceptions import LLMError
from ..skill.interfaces import SearchQuery
from .exploring_state import ExploringState, NodeContext, Suggestion, classify_intent


def _l(ctx: NodeContext, en: str, zh: str) -> str:
    return zh if ctx.lang == "zh" else en


def _system(ctx: NodeContext) -> str:
    if ctx.lang == "zh":
        return (
            "你是 Researcher，Thesis Studio 中的学术文献探索助手。"
            "你必须始终用中文回复。你的工作流程：搜索论文 -> 聚类分析 -> 生成综述 -> 最终报告。"
        )
    return (
        "You are Researcher, an academic literature exploration assistant in Thesis Studio. "
        "You must always reply in English. Your workflow: search -> cluster -> review -> final report."
    )


def _make_nodes(ctx: NodeContext):
    async def intent_router(state):
        await ctx.emit({"type": "thinking", "content": _l(ctx, "Analyzing your query...", "正在分析你的问题...")})
        result = await classify_intent(state, ctx.llm)
        topic = result.topic or state.get("topic") or state["current_message"]
        await ctx.emit({"type": "thinking", "content": f"Intent: {result.intent}" + (f" | Topic: {topic}" if topic else "")})
        return {"intent": result.intent, "intent_params": result.params, "topic": topic}

    async def query_expand(state):
        topic = state["topic"]
        await ctx.emit({"type": "thinking", "content": _l(ctx, f'Expanding "{topic}" into search queries...', f'正在将"{topic}" 扩展为搜索查询...')})
        prompt = (
            "You are a research librarian helping to find academic papers on arXiv.\n\n"
            f'TASK: Generate 3 search queries for the research topic: "{topic}".\n\n'
            "REQUIREMENTS:\n"
            "- You MUST use English keywords only (arXiv requires English).\n"
            + (f'- First translate "{topic}" to English academic terms if not already in English.\n' if ctx.lang == "zh" else "")
            + "- Each query MUST cover a different angle or sub-topic.\n"
            "- Each query MUST be a concise phrase, 4-8 words.\n"
            "- Do NOT use search operators like AND, OR, site:, filetype:.\n"
            "- Do NOT include numbering or bullet points.\n\n"
            "OUTPUT: One query per line, exactly 3 lines, no other text.\n\n"
            "Please do your best to find comprehensive coverage of this topic."
        )
        try:
            resp = await ctx.llm.generate(prompt, system=_system(ctx), temperature=0.5)
            queries = [SearchQuery(keywords=line.strip(), max_results=15).model_dump() for line in resp.strip().split("\n") if line.strip()]
            default = [SearchQuery(keywords=topic, max_results=20).model_dump()]
            final = queries[:3] if queries else default
            await ctx.emit({"type": "thinking", "content": _l(ctx, f"Generated {len(final)} queries.", f"生成了 {len(final)} 个查询")})
            return {"search_queries": final}
        except LLMError:
            await ctx.emit({"type": "thinking", "content": _l(ctx, "Skipping query expansion, using topic directly.", "跳过查询扩展，直接使用主题搜索")})
            return {"search_queries": [SearchQuery(keywords=topic, max_results=20).model_dump()]}

    async def search(state):
        queries = state.get("search_queries", [])
        if not queries:
            return {"raw_papers": []}
        q_objs = [SearchQuery(**q) for q in queries]
        await ctx.emit({"type": "searching", "content": _l(ctx, "Searching arXiv...", "正在搜索 arXiv...")})
        result = await ctx.search_skill.execute(queries=q_objs, sources=["arxiv"])
        if not result.success:
            await ctx.emit({"type": "error", "content": f"Search failed: {result.error}"})
            return {"error": f"Search failed: {result.error}", "raw_papers": []}
        papers = result.data.get("papers", [])
        await ctx.emit({"type": "found", "content": _l(ctx, f"Found {len(papers)} papers on arXiv.", f"在 arXiv 找到 {len(papers)} 篇论文")})
        return {"raw_papers": papers}

    async def parse(state):
        raw = state.get("raw_papers", [])
        if not raw:
            return {"papers": []}
        await ctx.emit({"type": "thinking", "content": _l(ctx, f"Parsing {len(raw)} papers...", f"正在解析 {len(raw)} 篇论文...")})
        result = await ctx.parser_skill.execute(raw_papers=raw)
        if not result.success:
            return {"error": f"Parse failed: {result.error}", "papers": []}
        papers = result.data.get("papers", [])
        paper_dicts = [p if isinstance(p, dict) else asdict(p) for p in papers]
        return {"papers": paper_dicts}

    async def cluster(state):
        papers = state.get("papers", [])
        if not papers:
            return {"response": _l(ctx, "No papers to cluster. Please search first.", "没有论文可以聚类，请先搜索论文。"), "suggestions": []}
        paper_objs = [Paper(**p) for p in papers]
        await ctx.emit({"type": "clustering", "content": _l(ctx, f"Clustering {len(paper_objs)} papers into themes...", f"正在将 {len(paper_objs)} 篇论文聚类...")})
        result = await ctx.cluster_skill.execute(papers=paper_objs, topic=state["topic"], lang=ctx.lang)
        if not result.success:
            return {"error": f"Clustering failed: {result.error}"}
        clusters = result.data.get("clusters", [])
        cluster_dicts = [c if isinstance(c, dict) else asdict(c) for c in clusters]
        await ctx.emit({"type": "clustering", "content": _l(ctx, f"Found {len(cluster_dicts)} clusters.", f"发现 {len(cluster_dicts)} 个主题簇")})
        return {"clusters": cluster_dicts}

    async def review(state):
        topic = state["topic"]
        clusters = [PaperCluster(**c) for c in state.get("clusters", [])]
        if not clusters:
            return {"response": _l(ctx, "No clusters yet. Cluster papers first.", "还没有聚类，请先聚类论文。"), "suggestions": []}
        await ctx.emit({"type": "writing", "content": _l(ctx, "Generating literature review...", "正在生成文献综述...")})
        result = await ctx.review_skill.execute(topic=topic, clusters=[asdict(c) for c in clusters], lang=ctx.lang)
        if not result.success:
            await ctx.emit({"type": "error", "content": f"Review failed: {result.error}"})
            return {"error": f"Review generation failed: {result.error}"}
        data = result.data
        await ctx.emit({"type": "writing", "content": _l(ctx, "Review complete.", "综述完成")})
        return {"review": data.get("review", data), "html_content": data.get("html_content", ""), "response": data.get("review", {}).get("summary", "") if isinstance(data.get("review"), dict) else "", "topic": topic}

    async def final_report(state):
        html = state.get("html_content", "")
        zh = ctx.lang == "zh"
        if not html:
            clusters = [PaperCluster(**c) for c in state.get("clusters", [])]
            if not clusters:
                return {"response": _l(ctx, "No review yet. Please cluster papers and generate a review first.", "请先聚类论文并生成综述。"), "suggestions": []}
            await ctx.emit({"type": "writing", "content": _l(ctx, "Generating final report...", "正在生成最终报告...")})
            result = await ctx.review_skill.execute(topic=state["topic"], clusters=[asdict(c) for c in clusters], lang=ctx.lang)
            if result.success:
                data = result.data
                html = data.get("html_content", "")
                state["review"] = data.get("review", data)
                state["html_content"] = html
            else:
                return {"error": "Report generation failed."}
        await ctx.emit({"type": "writing", "content": _l(ctx, "Report ready for download.", "报告已就绪！")})
        return {"response": _l(ctx, "Your final report is ready! Click the Download button below.", "最终报告已生成！点击下方下载按钮保存。"), "html_content": html, "review": state.get("review", {})}

    async def explain_paper(state):
        papers = state.get("papers", [])
        idx = state.get("intent_params", {}).get("paper_index", 0)
        if idx >= len(papers):
            return {"response": _l(ctx, "Paper not found. Which paper would you like me to explain?", "未找到该论文，想让我解释哪篇？")}
        p = papers[idx]
        await ctx.emit({"type": "thinking", "content": _l(ctx, f"Explaining: {p.get('title', '')[:60]}...", f"正在解释: {p.get('title', '')[:60]}...")})
        lang_instr = _l(ctx, "in English", "用中文")
        prompt = f"Explain the following academic paper {lang_instr}, including research problem, method, key findings, and limitations:\n\nTitle: {p.get('title', '')}\nAbstract: {p.get('abstract', '')}\nAuthors: {', '.join(p.get('authors', []))}\nYear: {p.get('year', 'unknown')}"
        try:
            return {"response": await ctx.llm.generate(prompt, system=_system(ctx), temperature=0.5)}
        except LLMError as e:
            return {"error": str(e)}

    async def compare_papers(state):
        papers = state.get("papers", [])
        indices = state.get("intent_params", {}).get("paper_indices", [0, 1])
        selected = [papers[i] for i in indices if i < len(papers)]
        if len(selected) < 2:
            return {"response": _l(ctx, "Need at least 2 papers to compare. Which ones?", "需要至少2篇论文才能对比，想对比哪几篇？")}
        titles = [p.get("title", "")[:60] for p in selected]
        await ctx.emit({"type": "thinking", "content": _l(ctx, f"Comparing: {' vs '.join(titles)}", f"正在对比: {' vs '.join(titles)}")})
        paper_text = "\n\n".join(f"[{i}] {p.get('title', '')}\n{p.get('abstract', '')}" for i, p in enumerate(selected))
        lang_instr = _l(ctx, "in English", "用中文")
        prompt = f"Compare and contrast the following papers {lang_instr}. Highlight similarities, differences in methodology, findings, and contributions:\n\n" + paper_text
        try:
            return {"response": await ctx.llm.generate(prompt, system=_system(ctx), temperature=0.5)}
        except LLMError as e:
            return {"error": str(e)}

    async def chat_response(state):
        papers = state.get("papers", [])
        clusters = state.get("clusters", [])
        has_review = bool(state.get("review", {}))
        msg = state["current_message"]
        zh = ctx.lang == "zh"

        state_ctx = ""
        if has_review:
            names = [c.get("theme", "") for c in clusters[:3]]
            state_ctx = f"Current session: {len(papers)} papers, {len(clusters)} clusters ({', '.join(names)}), review complete."
        elif clusters:
            names = [c.get("theme", "") for c in clusters[:3]]
            state_ctx = f"Current session: {len(papers)} papers, {len(clusters)} clusters ({', '.join(names)})."
        elif papers:
            state_ctx = f"Current session: {len(papers)} papers loaded."

        system = (
            "You are Researcher, an academic literature exploration assistant in Thesis Studio. "
            "Your role: help researchers discover papers on arXiv, cluster them by theme, "
            "generate literature reviews, and produce final HTML reports.\n\n"
            "WORKFLOW: search -> cluster -> review -> final report\n\n"
            "RULES:\n"
            "- You MUST be friendly, concise, and natural.\n"
            "- You MUST vary your responses \u2014 never repeat the same greeting.\n"
            "- If the user says hello, greet them warmly and ask about their research interests.\n"
            "- If asked what you can do, explain the workflow conversationally.\n"
            "- If asked who you are, introduce yourself naturally as Researcher.\n"
            "- Do NOT use markdown formatting in your response unless listing steps.\n"
            "- Do NOT fabricate research claims or paper citations.\n"
            + (f"\n{state_ctx}" if state_ctx else "")
            + ("\n\nYou MUST speak in Chinese (Simplified)." if zh else "\n\nYou MUST speak in English.")
        )
        messages_list = state.get("messages", [])
        history_parts = []
        for m in messages_list[-6:]:
            if hasattr(m, 'type'):
                role = m.type
                content = getattr(m, 'content', '') or ''
            elif isinstance(m, dict):
                role = m.get('role', '')
                content = m.get('content', '')
            else:
                continue
            history_parts.append(f"{role}: {content[:200]}")
        history = "\n".join(history_parts)

        prompt = f"{system}\n\nRecent conversation:\n{history}\nUser: {msg}\n\nResearcher:"
        try:
            resp = await ctx.llm.generate(prompt, system=_system(ctx), temperature=0.7, max_tokens=500)
            return {"response": resp.strip()}
        except LLMError:
            if zh:
                return {"response": "你好！我是 Researcher，你的学术文献探索助手。有什么研究方向想聊聊吗？"}
            return {"response": "Hi! I'm Researcher, your literature exploration assistant. What research topic interests you?"}

    async def format_response(state):
        intent = state.get("intent", "chat")
        error = state.get("error", "")
        papers = state.get("papers", [])
        clusters = state.get("clusters", [])
        has_review = bool(state.get("review", {}))
        has_html = bool(state.get("html_content", ""))
        lang = state.get("lang", "en")
        topic = state.get("topic", "")

        if error:
            return {"response": f"Error: {error}", "suggestions": []}
        if intent in ("chat", "explain", "compare"):
            return {"suggestions": _suggest(papers, clusters, has_review, has_html, lang, topic)}
        if intent == "search":
            return {"response": _fmt_search(state.get("topic", ""), papers, lang), "suggestions": _suggest(papers, clusters, has_review, has_html, lang, topic)}
        if intent == "cluster":
            return {"response": _fmt_cluster(papers, clusters, lang), "suggestions": _suggest(papers, clusters, has_review, has_html, lang, topic)}
        if intent == "review":
            return {"response": _fmt_review_short(topic, papers, clusters, state.get("review", {}), lang), "suggestions": _suggest(papers, clusters, has_review, has_html, lang, topic)}
        if intent == "final_report":
            return {"suggestions": _suggest(papers, clusters, has_review, has_html, lang, topic)}
        return {"suggestions": _suggest(papers, clusters, has_review, has_html, lang, topic)}

    return {
        "intent_router": intent_router, "query_expand": query_expand, "search": search,
        "parse": parse, "cluster": cluster, "review": review, "final_report": final_report,
        "explain_paper": explain_paper, "compare_papers": compare_papers,
        "chat_response": chat_response, "format_response": format_response,
    }


def _suggest(papers, clusters, has_review, has_html, lang="en", topic=""):
    zh = lang == "zh"
    suggestions = []
    topic_ctx = f"{topic} " if topic else ""

    if has_html:
        suggestions = [
            {"label": "📥 下载报告" if zh else "📥 Download Report", "action_text": "生成最终报告" if zh else "Generate final report"},
            {"label": "🔭 探索新方向" if zh else "🔭 Explore New Topic", "action_text": "我想探索新方向" if zh else "I want to explore a new topic"},
            {"label": "💬 讨论发现" if zh else "💬 Discuss Findings", "action_text": f"讨论一下{topic_ctx}的发现" if zh and topic else ("Let's discuss the findings" if not zh else "讨论一下发现")},
        ]
    elif has_review:
        suggestions = [
            {"label": "📫 生成最终报告" if zh else "📫 Generate Final Report", "action_text": "生成最终报告" if zh else "Generate final report"},
            {"label": "✏️ 修改综述" if zh else "✏️ Revise Review", "action_text": f"我想修改{topic_ctx}的综述" if zh and topic else ("I want to revise the review" if not zh else "我想修改综述")},
            {"label": "🔍 查看研究空白" if zh else "🔍 View Research Gaps", "action_text": f"看看{topic_ctx}的研究空白" if zh and topic else ("Show me the research gaps" if not zh else "看看研究空白")},
        ]
    elif clusters:
        theme_names = [c.get("theme", "")[:20] for c in clusters[:2]]
        suggestions = [{"label": "📝 生成综述" if zh else "📝 Generate Review", "action_text": "生成文献综述" if zh else "Generate a literature review"}]
        for tn in theme_names[:2]:
            suggestions.append({"label": f"🔩 {tn}", "action_text": f"深入讲解{tn}方向" if zh else f"Tell me more about {tn}"})
        suggestions.append({"label": "🔄 对比论文" if zh else "🔄 Compare Papers", "action_text": "对比前两篇论文" if zh else "Compare the first two papers"})
    elif papers:
        t1 = papers[0].get("title", "")[:40] if papers else ""
        t2 = papers[1].get("title", "")[:40] if len(papers) > 1 else ""
        suggestions = [{"label": "📊 聚类分析" if zh else "📊 Cluster Papers", "action_text": "聚类分析这些论文" if zh else "Cluster these papers"}]
        if t1:
            suggestions.append({"label": f"📉 {t1}", "action_text": f"解释这篇论文：{t1}" if zh else f"Explain: {t1}"})
        if t2:
            suggestions.append({"label": f"🔄 {t2}", "action_text": f"对比'{t1}'和'{t2}'" if zh else f"Compare '{t1}' vs '{t2}'"})
    else:
        suggestions = [
            {"label": "🔭 搜索论文" if zh else "🔭 Search Papers", "action_text": f"帮我搜索{topic_ctx}相关论文" if zh and topic else ("I want to search for papers" if not zh else "我想搜索论文")},
            {"label": "💬 聊聊研究" if zh else "💬 Chat About Research", "action_text": f"聊聊{topic_ctx}的研究想法" if zh and topic else ("Let's discuss my research ideas" if not zh else "聊聊我的研究想法")},
            {"label": "❓ 怎么用" if zh else "❓ How This Works", "action_text": "这个怎么用？" if zh else "How does this work?"},
        ]
    return [Suggestion(label=s["label"], action_text=s["action_text"]).model_dump() for s in suggestions]


def _fmt_search(topic, papers, lang="en"):
    if lang == "zh":
        if not papers:
            return f"未找到关于'{topic}' 的论文，换个关键词试试？"
        lines = [f"在 arXiv 找到 **{len(papers)} 篇论文**，以下是主要结果：", ""]
    else:
        if not papers:
            return f"No papers found for '{topic}'. Try different keywords?"
        lines = [f"Found **{len(papers)} papers** on arXiv. Here are the top results:", ""]
    for i, p in enumerate(papers[:8]):
        authors = ", ".join(p.get("authors", [])[:2])
        year = p.get("year", "?")
        lines.append(f"{i + 1}. **{p.get('title', '')}** ({year}) \u2014 {authors}")
    if len(papers) > 8:
        lines.append(f"\n... and {len(papers) - 8} more.")
    next_q = "接下来想做什么？" if lang == "zh" else "What would you like to do next?"
    lines.append(f"\n{next_q}")
    return "\n".join(lines)


def _fmt_cluster(papers, clusters, lang="en"):
    if lang == "zh":
        if not clusters:
            return "未创建聚类。"
        lines = [f"将 **{len(papers)} 篇论文** 分为 **{len(clusters)} 个主题**：", ""]
    else:
        if not clusters:
            return "No clusters created."
        lines = [f"Grouped **{len(papers)} papers** into **{len(clusters)} themes**:", ""]
    for c in clusters:
        theme = c.get("theme", "Unknown")
        desc = c.get("description", "")
        n = len(c.get("papers", []))
        lines.append(f"### {theme} ({n} papers)")
        lines.append(f"{desc}")
        lines.append("")
    next_q = "接下来想做什么？" if lang == "zh" else "What would you like to do next?"
    lines.append(next_q)
    return "\n".join(lines)


def _fmt_review_short(topic, papers, clusters, review_data, lang="en"):
    summary = review_data.get("summary", "") if isinstance(review_data, dict) else ""
    gaps = review_data.get("research_gaps", []) if isinstance(review_data, dict) else []
    if lang == "zh":
        lines = [f"## 文献综述: {topic}", "", f"基于 {len(papers)} 篇论文，{len(clusters)} 个主题。", "", f"### 综述\n{summary}"]
        if gaps:
            lines.append("\n### 研究空白\n" + "\n".join(f"- {g}" for g in gaps[:3]))
        lines.append("\n接下来想做什么？")
    else:
        lines = [f"## Literature Review: {topic}", "", f"Based on {len(papers)} papers across {len(clusters)} themes.", "", f"### Summary\n{summary}"]
        if gaps:
            lines.append("\n### Research Gaps\n" + "\n".join(f"- {g}" for g in gaps[:3]))
        lines.append("\nWhat would you like to do next?")
    return "\n".join(lines)


def _route_by_intent(state):
    intent = state.get("intent", "chat")
    return {
        "search": "query_expand", "cluster": "cluster", "review": "review",
        "final_report": "final_report", "explain": "explain_paper",
        "compare": "compare_papers", "chat": "chat_response",
    }.get(intent, "chat_response")


def build_exploring_graph(ctx):
    nodes = _make_nodes(ctx)
    graph = StateGraph(ExploringState)
    for name, fn in nodes.items():
        graph.add_node(name, fn)
    graph.set_entry_point("intent_router")
    graph.add_conditional_edges("intent_router", _route_by_intent, {
        "query_expand": "query_expand", "cluster": "cluster", "review": "review",
        "final_report": "final_report", "explain_paper": "explain_paper",
        "compare_papers": "compare_papers", "chat_response": "chat_response",
    })
    graph.add_edge("query_expand", "search")
    graph.add_edge("search", "parse")
    graph.add_edge("parse", "format_response")
    for node in ["cluster", "review", "final_report", "explain_paper", "compare_papers", "chat_response"]:
        graph.add_edge(node, "format_response")
    graph.add_edge("format_response", END)
    return graph


async def run_exploring(ctx, message, history=None, existing_state=None):
    prev = existing_state or {}
    initial = {
        "messages": history or [], "current_message": message,
        "topic": prev.get("topic") or message, "intent": "", "intent_params": {},
        "search_queries": [], "raw_papers": [],
        "papers": prev.get("papers", []), "clusters": prev.get("clusters", []),
        "review": prev.get("review", {}), "html_content": prev.get("html_content", ""),
        "response": "", "suggestions": [], "lang": ctx.lang, "error": "",
    }
    return await build_exploring_graph(ctx).compile().ainvoke(initial)
