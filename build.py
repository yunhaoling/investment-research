#!/usr/bin/env python3
"""
Convert all markdown research reports to HTML.
Usage: python build.py
Requires: pip install markdown pygments
"""

import os
import re
import markdown
from pathlib import Path

# Directories to skip
SKIP_DIRS = {"template", ".git", "node_modules"}

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
  <a href="../" class="back-link">← index</a>
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
    """Find all .md files, skipping excluded directories."""
    results = []
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        results.append(path)
    return sorted(results)


def main():
    root = Path(__file__).parent
    md_files = find_md_files(root)

    if not md_files:
        print("No markdown files found.")
        return

    print(f"Found {len(md_files)} markdown file(s):\n")
    for md_path in md_files:
        rel = md_path.relative_to(root)
        out = md_to_html(md_path)
        print(f"  {rel}  →  {out.relative_to(root)}")

    print(f"\nDone. {len(md_files)} file(s) converted.")


if __name__ == "__main__":
    main()
