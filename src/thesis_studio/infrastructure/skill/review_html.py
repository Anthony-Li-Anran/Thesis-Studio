"""Generate a standalone, academic-grade HTML literature review."""

from __future__ import annotations

from datetime import datetime

from ...domain.agent.researcher import LiteratureReview, Paper, PaperCluster


class ReviewHTMLGenerator:
    """Generate a self-contained, academically formatted HTML literature review.

    Supports bilingual (zh/en) output with proper academic structure:
    cover, abstract, introduction, methodology, thematic analysis,
    cross-cutting analysis, research gaps, debates, future directions,
    conclusion, and references.
    """

    CSS = """
    :root {
      --bg: #ffffff; --bg-sidebar: #f8f9fa; --text: #1a1a2e;
      --text-secondary: #495057; --accent: #2563eb; --border: #dee2e6;
      --code-bg: #f1f5f9; --table-stripe: #f8fafc; --highlight: #fef3c7;
      --tag-bg: #dbeafe; --tag-text: #1e40af;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "Georgia", "Noto Serif SC", "Times New Roman", serif;
      line-height: 1.8; color: var(--text); background: var(--bg);
      display: flex; min-height: 100vh;
    }
    .sidebar {
      width: 260px; position: fixed; top: 0; left: 0; bottom: 0;
      background: var(--bg-sidebar); border-right: 1px solid var(--border);
      overflow-y: auto; padding: 24px 16px; z-index: 100; font-size: 14px;
    }
    .sidebar h2 { font-size: 15px; color: var(--accent); margin-bottom: 16px;
      padding-bottom: 8px; border-bottom: 2px solid var(--accent); }
    .sidebar nav a {
      display: block; padding: 6px 12px; color: var(--text-secondary);
      text-decoration: none; border-radius: 6px; transition: all .15s; margin: 2px 0;
    }
    .sidebar nav a:hover { background: #e5e7eb; color: var(--text); }
    .main { margin-left: 260px; flex: 1; padding: 48px 64px; max-width: 960px; }
    @media (max-width: 1024px) {
      .sidebar { display: none; } .main { margin-left: 0; padding: 24px 16px; }
    }
    @media print {
      .sidebar { display: none; }
      .main { margin-left: 0; padding: 0; max-width: 100%; }
      body { font-size: 11pt; }
      .cover { break-after: page; }
      h2 { break-before: page; }
    }
    h1 { font-size: 2.2em; margin-bottom: 8px; font-weight: 700; }
    h2 { font-size: 1.5em; margin: 48px 0 20px; padding-bottom: 8px;
      border-bottom: 2px solid var(--accent); font-weight: 600; }
    h3 { font-size: 1.2em; margin: 36px 0 16px; font-weight: 600; }
    p { margin: 12px 0; text-align: justify; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    blockquote {
      margin: 16px 0; padding: 12px 20px; background: var(--highlight);
      border-left: 4px solid #f59e0b; border-radius: 0 6px 6px 0; color: #92400e;
    }
    .cover {
      background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 50%, #7c3aed 100%);
      color: #fff; border-radius: 12px; padding: 48px 56px; margin-bottom: 40px;
    }
    .cover h1 { color: #fff; font-size: 2.4em; margin-bottom: 16px; }
    .cover .abstract { color: rgba(255,255,255,.9); font-size: 1.05em;
      line-height: 1.7; margin: 16px 0; }
    .cover .meta { margin-top: 20px; font-size: 0.9em; opacity: .8; }
    .cover .keywords { margin-top: 12px; }
    .cover .keywords .kw {
      display: inline-block; padding: 3px 12px; margin: 2px 4px;
      background: rgba(255,255,255,.15); border-radius: 12px;
      font-size: 0.85em; color: rgba(255,255,255,.9);
    }
    .card {
      background: var(--bg-sidebar); border: 1px solid var(--border);
      border-radius: 10px; padding: 20px 24px; margin: 16px 0;
    }
    .card h4 { margin-top: 0; font-size: 1.05em; color: var(--accent); }
    .badge {
      display: inline-block; padding: 2px 10px; border-radius: 12px;
      font-size: 0.8em; font-weight: 600; background: var(--tag-bg);
      color: var(--tag-text); margin-right: 4px;
    }
    .badge.gold { background: #fef3c7; color: #92400e; }
    .badge.green { background: #d1fae5; color: #065f46; }
    .gap-card {
      background: #fffbeb; border: 1px solid #fcd34d; border-radius: 10px;
      padding: 16px 20px; margin: 12px 0;
    }
    .gap-card .gap-label { font-weight: 700; color: #92400e;
      font-size: 0.9em; margin-bottom: 6px; }
    .debate-card {
      background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px;
      padding: 16px 20px; margin: 12px 0;
    }
    .debate-card .debate-label { font-weight: 700; color: #991b1b;
      font-size: 0.9em; margin-bottom: 6px; }
    .future-card {
      background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px;
      padding: 16px 20px; margin: 12px 0;
    }
    .future-card .future-label { font-weight: 700; color: #166534;
      font-size: 0.9em; margin-bottom: 6px; }
    .methodology-box {
      background: #f0f4ff; border: 1px solid #93c5fd; border-radius: 10px;
      padding: 16px 20px; margin: 16px 0;
    }
    ol { padding-left: 24px; margin: 8px 0; }
    li { margin: 6px 0; }
    hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }
    .footer { text-align: center; color: var(--text-secondary);
      font-size: 0.9em; margin-top: 48px; padding-bottom: 32px; }
    .stats { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }
    .stat { background: var(--bg-sidebar); border: 1px solid var(--border);
      border-radius: 8px; padding: 12px 20px; text-align: center; min-width: 100px; }
    .stat .num { font-size: 1.5em; font-weight: 700; color: var(--accent); }
    .stat .label { font-size: 0.8em; color: var(--text-secondary); }
    """

    def __init__(self) -> None:
        pass

    def generate(self, review: LiteratureReview, project_title: str = "", lang: str = "en") -> str:
        """Generate complete HTML document from a LiteratureReview."""
        zh = lang == "zh"
        title = review.topic or project_title or ("文献综述" if zh else "Literature Review")
        nav = self._build_nav(review, zh)
        body = self._build_body(review, title, zh)
        lang_attr = "zh-CN" if zh else "en"
        return (
            "<!DOCTYPE html>\n<html lang=\"" + lang_attr + "\">\n<head>\n"
            '<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f"<title>{self._escape(title)}</title>\n"
            f"<style>{self.CSS}</style>\n"
            "</head>\n<body>\n"
            f"{nav}\n"
            f'<div class="main">\n{body}\n</div>\n'
            "</body>\n</html>"
        )

    def _build_nav(self, review: LiteratureReview, zh: bool) -> str:
        toc_title = "目录" if zh else "Contents"
        items = [
            ("overview", "综述总述" if zh else "Abstract"),
            ("introduction", "引言" if zh else "Introduction"),
            ("methodology", "方法学" if zh else "Methodology"),
        ]
        for i, c in enumerate(review.clusters):
            items.append((f"cluster-{i}", self._escape(c.theme)))
        if review.cross_cutting:
            items.append(("cross-cutting", "跨主题分析" if zh else "Cross-cutting Analysis"))
        if review.research_gaps:
            items.append(("gaps", "研究空白" if zh else "Research Gaps"))
        if review.key_debates:
            items.append(("debates", "关键争议" if zh else "Key Debates"))
        if review.future_directions:
            items.append(("future", "未来方向" if zh else "Future Directions"))
        if review.conclusion:
            items.append(("conclusion", "结论" if zh else "Conclusion"))
        items.append(("refs", "参考文献" if zh else "References"))

        links = [f'<a href="#{lid}">{label}</a>' for lid, label in items]
        joined = "\n        ".join(links)
        return (
            '<div class="sidebar">\n'
            f"  <h2>{toc_title}</h2>\n"
            "  <nav>\n"
            f"        {joined}\n"
            "  </nav>\n"
            "</div>"
        )

    def _build_body(self, review: LiteratureReview, title: str, zh: bool) -> str:
        parts: list[str] = []
        parts.append(self._build_cover(review, title, zh))
        parts.append(self._build_stats(review, zh))
        parts.append(self._build_overview(review, zh))
        parts.append(self._build_introduction(review, zh))
        parts.append(self._build_methodology(review, zh))
        for i, c in enumerate(review.clusters):
            parts.append(self._build_cluster_section(i, c, zh))
        parts.append(self._build_cross_cutting(review, zh))
        parts.append(self._build_gaps(review, zh))
        parts.append(self._build_debates(review, zh))
        parts.append(self._build_future(review, zh))
        parts.append(self._build_conclusion(review, zh))
        parts.append(self._build_references(review, zh))
        parts.append(self._build_footer(zh))
        return "\n".join(parts)

    def _build_cover(self, review: LiteratureReview, title: str, zh: bool) -> str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        summary = review.summary[:300] if review.summary else ""
        keywords_html = ""
        if review.keywords:
            kws = "".join(
                f'<span class="kw">{self._escape(k)}</span>'
                for k in review.keywords[:6]
            )
            keywords_html = f'<div class="keywords">{kws}</div>'
        org = "Thesis Studio"
        date_label = "生成日期" if zh else "Generated"
        return (
            '<div class="cover">\n'
            f"  <h1>{self._escape(title)}</h1>\n"
            f'  <p class="abstract">{self._escape(summary)}</p>\n'
            f"  {keywords_html}\n"
            f'  <div class="meta">{date_label}: {date_str} | {org}</div>\n'
            "</div>"
        )

    def _build_stats(self, review: LiteratureReview, zh: bool) -> str:
        total = sum(len(c.papers) for c in review.clusters)
        years = [
            p.year for c in review.clusters for p in c.papers if p.year
        ]
        yr_range = f"{min(years)}-{max(years)}" if years else ("N/A" if not zh else "未知")
        stats = [
            (str(total), "论文" if zh else "Papers"),
            (str(len(review.clusters)), "主题" if zh else "Themes"),
            (yr_range, "年份" if zh else "Year Range"),
        ]
        items = "".join(
            f'<div class="stat"><div class="num">{n}</div><div class="label">{lb}</div></div>'
            for n, lb in stats
        )
        return f'<div class="stats">{items}</div>'

    def _build_overview(self, review: LiteratureReview, zh: bool) -> str:
        title = "综述总述" if zh else "Abstract"
        return (
            f'<h2 id="overview">{title}</h2>\n'
            f"<p>{self._escape(review.summary)}</p>"
        )

    def _build_introduction(self, review: LiteratureReview, zh: bool) -> str:
        if not review.introduction:
            return ""
        title = "引言" if zh else "Introduction"
        return (
            f'<h2 id="introduction">{title}</h2>\n'
            f"<p>{self._escape(review.introduction)}</p>"
        )

    def _build_methodology(self, review: LiteratureReview, zh: bool) -> str:
        if not review.methodology:
            return ""
        title = "方法学" if zh else "Methodology"
        return (
            f'<h2 id="methodology">{title}</h2>\n'
            f'<div class="methodology-box">\n'
            f"  <p>{self._escape(review.methodology)}</p>\n"
            f"</div>"
        )

    def _build_cluster_section(self, index: int, cluster: PaperCluster, zh: bool) -> str:
        lines = [
            f'<h2 id="cluster-{index}">{self._escape(cluster.theme)}</h2>',
            f"<p>{self._escape(cluster.description)}</p>",
        ]
        for p in cluster.papers:
            lines.append(self._paper_card(p, zh))
        return "\n".join(lines)

    def _paper_card(self, paper: Paper, zh: bool) -> str:
        authors = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors += " et al." if not zh else " 等"
        year = str(paper.year) if paper.year else ("未知" if zh else "n.d.")
        url_html = (
            f' <a href="{self._escape(paper.url)}" target="_blank">[链接]</a>'
            if paper.url
            else ""
        )
        abstract = self._escape(paper.abstract[:300]) if paper.abstract else ""
        src_label = f'<span class="badge">{self._escape(paper.source)}</span>'
        return (
            '<div class="card">\n'
            f"  <h4>{self._escape(paper.title)}</h4>\n"
            f'  <p style="font-size:0.9em;color:var(--text-secondary)">'
            f"{authors} &middot; {year} &middot; {src_label}"
            f"{url_html}</p>\n"
            f"  <p>{abstract}</p>\n"
            "</div>"
        )

    def _build_cross_cutting(self, review: LiteratureReview, zh: bool) -> str:
        if not review.cross_cutting:
            return ""
        title = "跨主题分析" if zh else "Cross-cutting Analysis"
        return (
            f'<h2 id="cross-cutting">{title}</h2>\n'
            f"<p>{self._escape(review.cross_cutting)}</p>"
        )

    def _build_gaps(self, review: LiteratureReview, zh: bool) -> str:
        gaps = review.research_gaps
        if not gaps:
            return ""
        title = "研究空白" if zh else "Research Gaps"
        label = "\26A0 研究空白" if zh else "\26A0 Research Gap"
        items = "\n".join(
            f'<div class="gap-card"><div class="gap-label">{label}</div>'
            f"<p>{self._escape(g)}</p></div>"
            for g in gaps
        )
        return f'<h2 id="gaps">{title}</h2>\n{items}'

    def _build_debates(self, review: LiteratureReview, zh: bool) -> str:
        debates = review.key_debates
        if not debates:
            return ""
        title = "关键争议" if zh else "Key Debates"
        label = "\2694 关键争议" if zh else "\2694 Key Debate"
        items = "\n".join(
            f'<div class="debate-card"><div class="debate-label">{label}</div>'
            f"<p>{self._escape(d)}</p></div>"
            for d in debates
        )
        return f'<h2 id="debates">{title}</h2>\n{items}'

    def _build_future(self, review: LiteratureReview, zh: bool) -> str:
        directions = review.future_directions
        if not directions:
            return ""
        title = "未来方向" if zh else "Future Directions"
        label = "\27A1 未来方向" if zh else "\27A1 Future Direction"
        items = "\n".join(
            f'<div class="future-card"><div class="future-label">{label}</div>'
            f"<p>{self._escape(d)}</p></div>"
            for d in directions
        )
        return f'<h2 id="future">{title}</h2>\n{items}'

    def _build_conclusion(self, review: LiteratureReview, zh: bool) -> str:
        if not review.conclusion:
            return ""
        title = "结论" if zh else "Conclusion"
        return (
            f'<h2 id="conclusion">{title}</h2>\n'
            f"<p>{self._escape(review.conclusion)}</p>"
        )

    def _build_references(self, review: LiteratureReview, zh: bool) -> str:
        all_papers: list[Paper] = []
        for c in review.clusters:
            all_papers.extend(c.papers)
        title = "参考文献" if zh else "References"
        if not all_papers:
            empty = "暂无文献" if zh else "No references available"
            return f'<h2 id="refs">{title}</h2>\n<p>{empty}</p>'
        items: list[str] = []
        for _i, p in enumerate(all_papers, 1):
            authors = ", ".join(p.authors)
            year = f"({p.year})" if p.year else ("(n.d.)" if not zh else "(未知)")
            url = f' <a href="{self._escape(p.url)}" target="_blank">[link]</a>' if p.url else ""
            items.append(
                f"<li>{self._escape(authors)} {year}. "
                f"<em>{self._escape(p.title)}</em>.{url}</li>"
            )
        return f'<h2 id="refs">{title}</h2>\n<ol>\n' + "\n".join(items) + "\n</ol>"

    def _build_footer(self, zh: bool) -> str:
        text = "由 Thesis Studio 自动生成" if zh else "Generated by Thesis Studio"
        return (
            '<hr>\n'
            f'<p class="footer">{text} | '
            f'{datetime.now().strftime("%Y-%m-%d")}</p>'
        )

    @staticmethod
    def _escape(text: str) -> str:
        """Basic HTML escape."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
        )
