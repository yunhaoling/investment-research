#!/usr/bin/env python3
"""
Convert all markdown research reports to HTML and update index.html.
Usage: python build.py
Requires: pip install markdown pygments
"""

import re
import markdown
from pathlib import Path

# Directories to skip when scanning for reports
SKIP_DIRS = {"template", ".git", "node_modules", ".github", ".claude"}


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500&family=Noto+Serif+SC:wght@400;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:     #0b0d12;
  --bg2:    #10131a;
  --bg3:    #161923;
  --bg4:    #1d2130;
  --border: #222638;
  --border2:#2a2f45;
  --text:   #dde3f0;
  --text2:  #8a93b0;
  --text3:  #505878;
  --accent: #5b6af0;
  --green:  #2ed380;
  --amber:  #f5c542;
  --red:    #ff5566;
  --mono:   'DM Mono', monospace;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 15px;
  line-height: 1.8;
}}

/* ── Header ── */
.site-header {{
  position: sticky; top: 0; z-index: 100;
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 0 40px;
  display: flex; align-items: center; gap: 16px; height: 52px;
}}
.back-link {{
  color: var(--text3); text-decoration: none; font-size: 13px;
  font-family: var(--mono); transition: color .2s;
}}
.back-link:hover {{ color: var(--text2); }}
.header-sep {{ color: var(--border2); }}
.header-title {{ font-size: 13px; color: var(--text2); }}

/* ── Layout ── */
.layout {{
  display: grid;
  grid-template-columns: 220px 1fr;
  min-height: calc(100vh - 52px);
}}

/* ── TOC Sidebar ── */
.toc {{
  position: sticky; top: 52px; align-self: start;
  height: calc(100vh - 52px); overflow-y: auto;
  padding: 28px 0;
  border-right: 1px solid var(--border);
  background: var(--bg2);
}}
.toc-title {{
  font-size: 10px; text-transform: uppercase; letter-spacing: .1em;
  color: var(--text3); font-family: var(--mono);
  padding: 0 20px 12px;
}}
.toc ul {{ list-style: none; }}
.toc a {{
  display: block; padding: 5px 20px;
  font-size: 12.5px; color: var(--text3);
  text-decoration: none; transition: color .15s, background .15s;
  border-left: 2px solid transparent;
}}
.toc a:hover {{ color: var(--text2); background: var(--bg3); }}
.toc a.active {{ color: var(--accent); border-left-color: var(--accent); }}
.toc .toc-h2 {{ padding-left: 20px; }}
.toc .toc-h3 {{ padding-left: 34px; font-size: 11.5px; }}

/* ── Article ── */
.article {{
  max-width: 860px;
  padding: 48px 60px 80px;
  margin: 0 auto;
  width: 100%;
}}

/* Headings */
.article h1 {{
  font-family: 'Noto Serif SC', serif;
  font-size: 26px; font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
  line-height: 1.4;
}}
.article h2 {{
  font-family: 'Noto Serif SC', serif;
  font-size: 18px; font-weight: 600;
  color: var(--text);
  margin: 40px 0 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
}}
.article h2::before {{
  content: ''; display: block;
  width: 3px; height: 18px; border-radius: 2px;
  background: var(--accent); flex-shrink: 0;
}}
.article h3 {{
  font-size: 15px; font-weight: 500;
  color: var(--text2);
  margin: 28px 0 12px;
}}
.article h4 {{
  font-size: 13px; font-weight: 500;
  color: var(--text3); text-transform: uppercase; letter-spacing: .06em;
  margin: 20px 0 8px;
}}

/* Body text */
.article p {{ margin-bottom: 14px; color: var(--text2); }}
.article strong {{ color: var(--text); font-weight: 500; }}
.article em {{ color: var(--amber); font-style: normal; }}
.article hr {{ border: none; border-top: 1px solid var(--border); margin: 32px 0; }}

/* Blockquote */
.article blockquote {{
  margin: 20px 0;
  padding: 14px 20px;
  background: var(--bg3);
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
}}
.article blockquote p {{
  color: var(--text2); margin: 0;
  font-size: 13.5px; line-height: 1.8;
}}

/* Tables */
.article table {{
  width: 100%; border-collapse: collapse;
  margin: 20px 0 28px; font-size: 13px;
}}
.article thead th {{
  padding: 8px 12px;
  text-align: right;
  font-size: 10px; font-weight: 500;
  text-transform: uppercase; letter-spacing: .07em;
  color: var(--text3);
  background: var(--bg3);
  border-bottom: 1px solid var(--border2);
  font-family: var(--mono);
}}
.article thead th:first-child {{ text-align: left; }}
.article tbody td {{
  padding: 8px 12px;
  text-align: right;
  border-bottom: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--mono);
  font-size: 12.5px;
}}
.article tbody td:first-child {{
  text-align: left;
  color: var(--text);
  font-family: 'Noto Sans SC', sans-serif;
}}
.article tbody tr:hover td {{ background: var(--bg3); }}

/* Lists */
.article ul, .article ol {{
  padding-left: 20px; margin-bottom: 14px;
}}
.article li {{ color: var(--text2); margin-bottom: 4px; }}
.article li strong {{ color: var(--text); }}

/* Inline code */
.article code {{
  font-family: var(--mono);
  font-size: 12.5px;
  background: var(--bg3);
  border: 1px solid var(--border);
  padding: 1px 5px; border-radius: 4px;
  color: var(--amber);
}}
.article pre {{
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px 20px;
  overflow-x: auto;
  margin-bottom: 20px;
}}
.article pre code {{
  background: none; border: none; padding: 0;
  color: var(--text2); font-size: 13px;
}}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border2); border-radius: 3px; }}

/* Responsive */
@media (max-width: 768px) {{
  .layout {{ grid-template-columns: 1fr; }}
  .toc {{ display: none; }}
  .article {{ padding: 32px 20px 60px; }}
  .site-header {{ padding: 0 20px; }}
}}
</style>
</head>
<body>

<header class="site-header">
  <a href="../../" class="back-link">← index</a>
  <span class="header-sep">/</span>
  <span class="header-title">{ticker}</span>
</header>

<div class="layout">
  <nav class="toc">
    <div class="toc-title">Contents</div>
    <ul id="toc-list"></ul>
  </nav>

  <main>
    <article class="article" id="article">
      {body}
    </article>
  </main>
</div>

<script>
// Build TOC from headings
const tocList = document.getElementById('toc-list');
const headings = document.querySelectorAll('.article h2, .article h3');
headings.forEach((h, i) => {{
  if (!h.id) h.id = 'h-' + i;
  const li = document.createElement('li');
  const a = document.createElement('a');
  a.href = '#' + h.id;
  a.textContent = h.textContent.replace(/^[# ]+/, '');
  a.className = 'toc-' + h.tagName.toLowerCase();
  li.appendChild(a);
  tocList.appendChild(li);
}});

// Highlight active TOC item on scroll
const tocLinks = tocList.querySelectorAll('a');
const observer = new IntersectionObserver(entries => {{
  entries.forEach(e => {{
    if (e.isIntersecting) {{
      tocLinks.forEach(a => a.classList.remove('active'));
      const active = tocList.querySelector(`a[href="#${{e.target.id}}"]`);
      if (active) active.classList.add('active');
    }}
  }});
}}, {{ rootMargin: '-20% 0px -70% 0px' }});
headings.forEach(h => observer.observe(h));
</script>
</body>
</html>
"""


def extract_title(md_text: str, filepath: Path) -> str:
    """Extract H1 title from markdown, fall back to filename."""
    match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return filepath.stem


def md_to_html(md_path: Path) -> Path:
    """Convert a markdown file to HTML and return the output path."""
    md_text = md_path.read_text(encoding="utf-8")

    title = extract_title(md_text, md_path)
    ticker = md_path.parent.name  # e.g. BABA

    md_ext = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "codehilite",
            "toc",
            "nl2br",
            "sane_lists",
        ],
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": False},
        },
    )
    body = md_ext.convert(md_text)

    html = HTML_TEMPLATE.format(title=title, ticker=ticker, body=body)

    out_path = md_path.with_suffix(".html")
    out_path.write_text(html, encoding="utf-8")
    return out_path


def find_md_files(root: Path) -> list[Path]:
    """Find all .md files under companies/, skipping excluded directories."""
    companies_dir = root / "companies"
    results = []
    for path in companies_dir.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        results.append(path)
    return sorted(results)


def find_html_reports(root: Path) -> dict[str, list[Path]]:
    """
    Scan companies/ subdirectories for .html report files.
    Returns {ticker: [sorted list of html paths]}.
    """
    reports: dict[str, list[Path]] = {}
    companies_dir = root / "companies"
    for subdir in sorted(companies_dir.iterdir()):
        if not subdir.is_dir():
            continue
        if subdir.name in SKIP_DIRS or subdir.name.startswith("."):
            continue
        html_files = sorted(
            f for f in subdir.glob("*.html")
            if "template" not in f.stem.lower()
        )
        if html_files:
            reports[subdir.name] = html_files
    return reports


def format_period(stem: str) -> str:
    """Turn '2025Q4' into '2025 Q4', leave other names as-is."""
    m = re.match(r"^(\d{4})(Q\d)$", stem, re.IGNORECASE)
    if m:
        return f"{m.group(1)} {m.group(2).upper()}"
    return stem


def build_nav_html(reports: dict[str, list[Path]], root: Path) -> str:
    """Render the full <ul class="tree-body"> ... </ul> block."""
    tickers = list(reports.keys())
    lines = ['    <!-- AUTO-NAV-START -->', '    <ul class="tree-body">', ""]

    for i, ticker in enumerate(tickers):
        is_last_ticker = i == len(tickers) - 1
        ticker_connector = "└──" if is_last_ticker else "├──"
        desc = ticker
        html_files = reports[ticker]

        lines.append(f'      <li class="tree-ticker">')
        lines.append(f'        <div class="tree-ticker-row">')
        lines.append(f'          <span class="tree-connector">{ticker_connector}</span>')
        lines.append(f'          <span class="ticker-name">{ticker}</span>')
        lines.append(f'          <span class="ticker-desc">{desc}</span>')
        lines.append(f'        </div>')
        lines.append(f'        <ul class="tree-reports">')

        for j, html_path in enumerate(html_files):
            is_last_report = j == len(html_files) - 1
            if is_last_ticker:
                indent = "    └── " if is_last_report else "    ├── "
            else:
                indent = "│   └── " if is_last_report else "│   ├── "

            period = format_period(html_path.stem)
            href = f"companies/{ticker}/{html_path.name}"

            lines.append(f'          <li class="tree-report-row">')
            lines.append(f'            <span class="tree-indent">{indent}</span>')
            lines.append(f'            <a class="report-link" href="{href}">')
            lines.append(f'              <span class="report-period">{period}</span>')
            lines.append(f'              <span class="report-title">护城河追踪 · Moat Tracker</span>')
            lines.append(f'              <span class="report-type">Earnings</span>')
            lines.append(f'            </a>')
            lines.append(f'          </li>')

        lines.append(f'        </ul>')
        lines.append(f'      </li>')
        lines.append("")

    lines.append("    </ul>")
    lines.append("    <!-- AUTO-NAV-END -->")
    return "\n".join(lines)


def update_index(root: Path) -> None:
    """Regenerate the AUTO-NAV section in index.html."""
    index_path = root / "index.html"
    if not index_path.exists():
        print("  index.html not found, skipping.")
        return

    content = index_path.read_text(encoding="utf-8")

    reports = find_html_reports(root)
    nav_html = build_nav_html(reports, root)

    # Replace everything between the marker comments (inclusive)
    pattern = r"[ \t]*<!-- AUTO-NAV-START -->.*?<!-- AUTO-NAV-END -->"
    new_content, count = re.subn(pattern, nav_html, content, flags=re.DOTALL)

    if count == 0:
        print("  WARNING: AUTO-NAV markers not found in index.html — skipping update.")
        return

    index_path.write_text(new_content, encoding="utf-8")
    print(f"  index.html updated ({len(reports)} tickers, {sum(len(v) for v in reports.values())} reports)")


def main():
    root = Path(__file__).parent
    md_files = find_md_files(root)

    if not md_files:
        print("No markdown files found.")
    else:
        print(f"Found {len(md_files)} markdown file(s):\n")
        for md_path in md_files:
            rel = md_path.relative_to(root)
            out = md_to_html(md_path)
            print(f"  {rel}  →  {out.relative_to(root)}")

    print("\nUpdating index.html...")
    update_index(root)
    print("\nDone.")


if __name__ == "__main__":
    main()
