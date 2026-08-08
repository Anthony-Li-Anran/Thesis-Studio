"""Skill implementations for EXPLORING phase."""

import json
import re
from collections.abc import AsyncIterator
from typing import Any

from ...domain.agent.researcher import GraphEdge, LiteratureReview, Paper, PaperCluster
from ...domain.exceptions import AnalysisError, LiteratureError
from ...domain.ports.llm_port import LLMProvider
from ...domain.skill.base import Skill, SkillConfig, SkillResult
from ...domain.skill.interfaces import (
    AcademicSearchInput,
    AcademicSearchOutput,
    ClusterInput,
    ClusterOutput,
    PaperParserInput,
    PaperParserOutput,
    ReviewGenInput,
    ReviewGenOutput,
)
from ..logging import get_logger
from ..search import ArxivClient
from .review_html import ReviewHTMLGenerator

logger = get_logger(__name__)


class AcademicSearchSkill(Skill):
    """Search academic databases via Semantic Scholar and arXiv."""

    config: SkillConfig = SkillConfig(name="academic_search")

    async def execute(self, **kwargs: Any) -> SkillResult:
        inp = AcademicSearchInput(**kwargs)
        all_papers: list[dict[str, Any]] = []
        arxiv = ArxivClient()
        try:
            for query in inp.queries:
                if "arxiv" in inp.sources:
                    results = await arxiv.search(query)
                    all_papers.extend(results)
            return SkillResult(
                success=True,
                data=AcademicSearchOutput(
                    papers=all_papers, total_count=len(all_papers)
                ).model_dump(),
            )
        except LiteratureError as e:
            return SkillResult(success=False, error=str(e))
        finally:
            await arxiv.close()


class PaperParserSkill(Skill):
    """Parse raw paper dicts into Paper domain objects, deduplicate."""

    config: SkillConfig = SkillConfig(name="paper_parser")

    async def execute(self, **kwargs: Any) -> SkillResult:
        inp = PaperParserInput(**kwargs)
        seen: set[str] = set()
        papers: list[Paper] = []
        duplicates = 0
        for raw in inp.raw_papers:
            pid = raw.get("paperId", "")
            if not pid:
                continue
            if pid in seen:
                duplicates += 1
                continue
            seen.add(pid)
            authors = [
                a.get("name", "") if isinstance(a, dict) else str(a)
                for a in raw.get("authors", [])
            ]
            papers.append(Paper(
                paper_id=pid,
                title=raw.get("title", ""),
                abstract=raw.get("abstract") or "",
                authors=authors,
                year=raw.get("year"),
                url=raw.get("url", ""),
                source=raw.get("source", "semantic_scholar"),
                citation_count=raw.get("citationCount", 0),
            ))
        return SkillResult(
            success=True,
            data=PaperParserOutput(
                papers=papers, duplicates_removed=duplicates
            ).model_dump(),
        )


class ClusterSkill(Skill):
    """AI-judged paper clustering by theme, using LLM."""

    config: SkillConfig = SkillConfig(name="cluster")

    def __init__(self, llm: LLMProvider) -> None:
        super().__init__()
        self._llm = llm

    async def execute(self, **kwargs: Any) -> SkillResult:
        inp = ClusterInput(**kwargs)
        lang = kwargs.get("lang", "en")
        zh = lang == "zh"
        if len(inp.papers) <= 3:
            label = "全部文献" if zh else "All Papers"
            desc = "文献数量较少，未分组" if zh else "Too few papers to cluster"
            cl = PaperCluster(theme=label, description=desc)
            cl.papers = inp.papers
            return SkillResult(
                success=True, data=ClusterOutput(clusters=[cl]).model_dump(),
            )
        prompt = self._build_cluster_prompt(inp.papers, inp.topic, lang)
        try:
            system = "你是学术文献分析专家，始终用中文回复。" if lang == "zh" else "You are an academic literature analyst. Always respond in English."
            response = await self._llm.generate(prompt, system=system, temperature=0.3)
            clusters = self._parse_clusters(response, inp.papers, lang)
            return SkillResult(
                success=True, data=ClusterOutput(clusters=clusters).model_dump(),
            )
        except Exception as e:
            logger.error("Cluster failed: %s", e)
            return SkillResult(success=False, error=str(e))

    def _build_cluster_prompt(
        self, papers: list[Paper], topic: str, lang: str = "en"
    ) -> str:
        entries = []
        for i, p in enumerate(papers):
            abstract = (p.abstract or "")[:200]
            entries.append(f"[{i}] {p.title} | {abstract}")
        paper_list = "\n".join(entries)
        if lang == "zh":
            return (
                f'你是学术文献分析专家。\n\n'
                f'任务：将以下与"{topic}"相关的文献按研究主题进行聚类分组。\n\n'
                f"文献列表：\n{paper_list}\n\n"
                f"要求：\n"
                f"- 你必须在2-5个主题之间聚类，每个主题3-10篇论文。\n"
                f"- 每个主题名必须简洁（2-6字），描述必须清晰说明该主题的研究重点（15-30字）。\n"
                f"- 每篇论文必须且只能属于一个主题。\n"
                f'- 不要创建"其他"或"杂项"类别。\n\n'
                f"输出格式：只返回JSON，不要其他内容：\n"
                '{"clusters": [{"theme": "主题名", "description": "该主题研究重点的描述", "paper_indices": [0,1,2]}]}\n\n'
                f"请尽力做好，这对学术研究很重要。"
            )
        return (
            f'You are an academic literature analysis expert.\n\n'
            f'TASK: Group the following papers related to "{topic}" into thematic clusters.\n\n'
            f"Papers:\n{paper_list}\n\n"
            f'REQUIREMENTS:\n'
            f'- You MUST create between 2 and 5 clusters, each with 3-10 papers.\n'
            f'- Each theme name MUST be concise (2-6 words).\n'
            f'- Each description MUST clearly explain the research focus (15-30 words).\n'
            f'- Each paper MUST belong to exactly one cluster.\n'
            f'- Do NOT create an "Other" or "Miscellaneous" category.\n\n'
            f'OUTPUT FORMAT: Return ONLY JSON, no other text:\n'
            '{"clusters": [{"theme": "Theme Name", "description": "Description of research focus", "paper_indices": [0,1,2]}]}\n\n'
            f'Please do your best, this is important for academic research.'
        )

    def _parse_clusters(self, response: str, papers: list[Paper], lang: str = "en") -> list[PaperCluster]:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if not json_match:
            raise AnalysisError("LLM returned invalid JSON" if lang == "en" else "LLM 未返回有效 JSON")
        data = json.loads(json_match.group())
        clusters: list[PaperCluster] = []
        assigned: set[int] = set()
        for c in data.get("clusters", []):
            cluster = PaperCluster(
                theme=c.get("theme", ""), description=c.get("description", "")
            )
            for idx in c.get("paper_indices", []):
                if 0 <= idx < len(papers):
                    cluster.papers.append(papers[idx])
                    assigned.add(idx)
            clusters.append(cluster)
        unassigned = [p for i, p in enumerate(papers) if i not in assigned]
        if unassigned:
            # Note: lang not available here, use neutral labels
            label = "Other" if lang == "en" else "其他"
            desc = "Unassigned papers" if lang == "en" else "未分配论文"
            other = PaperCluster(theme=label, description=desc)
            other.papers = unassigned
            clusters.append(other)
        return clusters


class ReviewGenSkill(Skill):
    """Generate structured literature review from clusters, using LLM."""

    config: SkillConfig = SkillConfig(name="review_gen")

    def __init__(self, llm: LLMProvider) -> None:
        super().__init__()
        self._llm = llm
        self._html_gen = ReviewHTMLGenerator()

    async def execute(self, **kwargs: Any) -> SkillResult:
        inp = ReviewGenInput(**kwargs)
        lang = kwargs.get("lang", "en")
        prompt = self._build_review_prompt(inp.topic, inp.clusters, lang)
        try:
            system = "你是学术文献综述专家，始终用中文回复。" if lang == "zh" else "You are an academic literature review expert. Always respond in English."
            response = await self._llm.generate(prompt, system=system, temperature=0.5)
            review = self._parse_review(response, inp.topic, inp.clusters, lang)
            html = self._html_gen.generate(review, inp.topic, lang)
            return SkillResult(
                success=True,
                data=ReviewGenOutput(
                    review=review, raw_text=response, html_content=html,
                ).model_dump(),
            )
        except Exception as e:
            logger.error("ReviewGen failed: %s", e)
            return SkillResult(success=False, error=str(e))

    def _build_review_prompt(
        self, topic: str, clusters: list[PaperCluster], lang: str = "en"
    ) -> str:
        cluster_text = ""
        for c in clusters:
            rev_entries = []
            for p in c.papers[:5]:
                abstract = (p.abstract or "")[:150]
                rev_entries.append(
                    f"  - {p.title} ({p.year or 'unknown'}) | {abstract}"
                )
            papers_text = "\n".join(rev_entries)
            cluster_text += f"\n## {c.theme}: {c.description}\n{papers_text}\n"
        if lang == "zh":
            return (
                f'【重要：你必须用中文回答！所有输出必须是中文！】\n\n'
                f'你是学术文献综述专家，为 Thesis Studio 撰写高质量中文文献综述。\n\n'
                f'研究主题："{topic}"\n\n'
                f"文献聚类数据：\n{cluster_text}\n\n"
                f'任务：基于以上文献，撰写一份全中文的学术文献综述。\n\n'
                f'要求：\n'
                f'- 所有内容必须用中文撰写。论文标题和作者名保留英文原文。\n'
                f'- 引言必须用中文说明研究背景、问题重要性和综述范围（200-300字）。\n'
                f'- 方法学必须说明检索策略、数据库、筛选标准（100-200字）。\n'
                f'- 综述总述必须概括各主题核心发现，体现综合分析（300-400字）。\n'
                f'- 跨主题分析必须指出共性趋势、方法演进和理论分歧（200-300字）。\n'
                f'- 研究空白必须指出未解决的问题及其研究意义。\n'
                f'- 关键争议必须详细说明学术界的不同观点。\n'
                f'- 未来方向必须基于研究空白提出可行的研究方向。\n'
                f'- 结论必须总结核心发现和学术贡献（100-200字）。\n'
                f'- 不要使用"本文"、"本研究"等第一人称。\n'
                f'- 不要编造不存在的论文或数据。\n\n'
                f'输出格式：只返回JSON，不要其他内容：\n'
                '{\n'
                '  "keywords": ["中文关键词1", "中文关键词2", "中文关键词3", "中文关键词4", "中文关键词5"],\n'
                '  "introduction": "研究背景、问题重要性、综述范围（200-300字）",\n'
                '  "methodology": "检索策略：数据库、关键词、筛选标准（100-200字）",\n'
                '  "summary": "综述总述：各主题核心发现与综合分析（300-400字）",\n'
                '  "cross_cutting": "跨主题分析：趋势、方法演进、理论分歧（200-300字）",\n'
                '  "research_gaps": ["研究空白1及意义", "研究空白2及意义"],\n'
                '  "key_debates": ["争议点1详细说明", "争议点2详细说明"],\n'
                '  "future_directions": ["未来方向1", "未来方向2", "未来方向3"],\n'
                '  "conclusion": "核心发现与学术贡献总结（100-200字）",\n'
                '  "edges": [{"source_id": "paper_id", "target_id": "paper_id",'
                ' "relation": "同主题/矛盾/继承/扩展", "description": "关系说明"}]\n'
                '}\n\n'
                f'请尽力做好，这对学术研究非常重要。假设当前日期是{__import__("datetime").datetime.now().strftime("%Y年%m月%d日")}。'
            )
        return (
            f'You are an academic literature review expert writing for Thesis Studio.\n\n'
            f'RESEARCH TOPIC: "{topic}"\n\n'
            f"CLUSTER DATA:\n{cluster_text}\n\n"
            f'TASK: Write a structured academic literature review based on the above data.\n\n'
            f'REQUIREMENTS:\n'
            f'- Introduction MUST explain research background, significance, and scope (200-300 words).\n'
            f'- Methodology MUST describe search strategy, databases, and inclusion criteria (100-200 words).\n'
            f'- Summary MUST synthesize core findings across all themes (300-400 words).\n'
            f'- Cross-cutting analysis MUST identify trends, methodological evolution, and theoretical debates (200-300 words).\n'
            f'- Research gaps MUST identify unsolved problems and their significance.\n'
            f'- Key debates MUST detail differing academic viewpoints.\n'
            f'- Future directions MUST propose actionable research opportunities based on gaps.\n'
            f'- Conclusion MUST summarize core findings and contributions (100-200 words).\n'
            f'- Do NOT use first-person pronouns (I, we, our).\n'
            f'- Do NOT fabricate papers or data not present in the provided clusters.\n\n'
            f'OUTPUT FORMAT: Return ONLY JSON, no other text:\n'
            '{\n'
            '  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],\n'
            '  "introduction": "background, significance, scope (200-300 words)",\n'
            '  "methodology": "search strategy, databases, criteria (100-200 words)",\n'
            '  "summary": "synthesis of core findings across themes (300-400 words)",\n'
            '  "cross_cutting": "trends, methodological evolution, theoretical debates (200-300 words)",\n'
            '  "research_gaps": ["gap 1 with significance", "gap 2 with significance"],\n'
            '  "key_debates": ["debate 1 detail", "debate 2 detail"],\n'
            '  "future_directions": ["direction 1", "direction 2", "direction 3"],\n'
            '  "conclusion": "core findings and contributions (100-200 words)",\n'
            '  "edges": [{"source_id": "paper_id", "target_id": "paper_id",'
            ' "relation": "same_topic/contradiction/extends/builds_on", "description": "..."}]\n'
            '}\n\n'
            f'Please do your best, this is very important for academic research. '
            f'Assume the current date is {__import__("datetime").datetime.now().strftime("%Y-%m-%d")}.'
        )

    def _parse_review(
        self, response: str, topic: str, clusters: list[PaperCluster], lang: str = "en"
    ) -> LiteratureReview:
        paper_ids = {p.paper_id for c in clusters for p in c.papers}
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if not json_match:
            raise AnalysisError("LLM returned invalid JSON" if lang == "en" else "LLM 未返回有效 JSON")
        data = json.loads(json_match.group())
        edges: list[GraphEdge] = []
        for e in data.get("edges", []):
            sid = e.get("source_id", "")
            tid = e.get("target_id", "")
            if sid in paper_ids and tid in paper_ids:
                edges.append(GraphEdge(
                    source_id=sid, target_id=tid,
                    relation=e.get("relation", "相关"),
                    description=e.get("description", ""),
                ))
        return LiteratureReview(
            topic=topic,
            clusters=clusters,
            edges=edges,
            introduction=data.get("introduction", ""),
            methodology=data.get("methodology", ""),
            summary=data.get("summary", ""),
            cross_cutting=data.get("cross_cutting", ""),
            research_gaps=data.get("research_gaps", []),
            key_debates=data.get("key_debates", []),
            future_directions=data.get("future_directions", []),
            conclusion=data.get("conclusion", ""),
            keywords=data.get("keywords", []),
        )

    async def execute_stream(self, **kwargs: Any) -> AsyncIterator[str]:
        result = await self.execute(**kwargs)
        yield json.dumps(result.model_dump(), ensure_ascii=False)
