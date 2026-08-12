# -*- coding: utf-8 -*-
"""
content/*.md -> docs/*.html 정적 사이트 빌더.

GitHub Pages는 docs/ 폴더의 결과물만 서빙하면 되므로, 빌드 산출물도 저장소에
함께 커밋한다. (Pages 쪽에 별도 빌드 파이프라인이 필요 없게 하기 위함)

사용법:
    pip install -r requirements.txt
    python build.py
"""

import html as html_lib
import os
import re
import shutil

import markdown

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "docs")

SITE_TITLE = "Spotfire IronPython 2.7 교안"
REPO_URL = "https://github.com/cozytk/spotfire-iron-python-scripts"

# (파일명, 메뉴 라벨, 섹션 그룹)
PAGES = [
    ("index",            "교안 소개",                    "시작하기"),
    ("01-getting-started", "1. 스크립트 실행 환경",       "시작하기"),
    ("02-python-syntax",   "2. IronPython 2.7 문법",     "문법"),
    ("03-dotnet-interop",  "3. .NET 상호운용 문법",       "문법"),
    ("04-api-map",         "4. Spotfire API 객체 모델",   "문법"),
    ("05-examples-bulk",   "5. 예제 A · 일괄 적용",       "예제"),
    ("06-examples-data",   "6. 예제 B · 데이터와 내보내기", "예제"),
    ("07-examples-ui",     "7. 예제 C · 동적 UI 제어",     "예제"),
    ("08-examples-advanced", "8. 예제 D · 심화 자동화",    "예제"),
    ("09-tips",            "9. 실무 팁과 함정",           "레퍼런스"),
    ("10-cheatsheet",      "10. 치트시트 & FAQ",          "레퍼런스"),
]

TEMPLATE = u"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128220;</text></svg>">
</head>
<body>
<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="topbar">
  <button id="navToggle" class="icon-btn" aria-label="목차 열기">&#9776;</button>
  <a class="brand" href="{root}index.html">{site_title}</a>
  <div class="spacer"></div>
  <input id="search" type="search" placeholder="이 교안에서 검색 (/)" aria-label="검색">
  <button id="themeToggle" class="icon-btn" aria-label="라이트/다크 전환"><svg width="15" height="15" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M10 2a8 8 0 0 1 0 16z" fill="currentColor"/></svg></button>
  <a class="icon-btn gh" href="{repo}" target="_blank" rel="noopener" aria-label="GitHub 저장소">&lt;/&gt;</a>
</header>
<div class="layout">
  <nav id="sidebar" class="sidebar" aria-label="교안 목차">
    {nav}
  </nav>
  <main id="main" class="content">
    {body}
    <nav class="pager">{pager}</nav>
    <footer class="foot">
      <p>이 교안의 모든 예제 스크립트는 <a href="{repo}/tree/HEAD/scripts">scripts/ 폴더</a>에 실행 가능한 <code>.py</code> 파일로도 들어 있습니다.</p>
      <p>Spotfire는 Cloud Software Group, Inc.의 상표입니다. 본 교안은 비공식 학습 자료입니다.</p>
    </footer>
  </main>
  <aside class="toc-side" aria-label="현재 문서 목차">{toc}</aside>
</div>
<div id="searchResults" class="search-results" hidden></div>
<script src="{root}assets/app.js"></script>
</body>
</html>
"""


def build_nav(current):
    html, group = [], None
    for slug, label, grp in PAGES:
        if grp != group:
            if group is not None:
                html.append("</ul>")
            html.append('<p class="nav-group">%s</p><ul class="nav-list">' % grp)
            group = grp
        cls = ' class="active"' if slug == current else ""
        html.append('<li><a href="%s.html"%s>%s</a></li>' % (slug, cls, label))
    html.append("</ul>")
    return "\n".join(html)


def build_pager(idx):
    prev_html = nxt_html = ""
    if idx > 0:
        s, l, _ = PAGES[idx - 1]
        prev_html = '<a class="pg prev" href="%s.html"><span>이전</span>%s</a>' % (s, l)
    if idx < len(PAGES) - 1:
        s, l, _ = PAGES[idx + 1]
        nxt_html = '<a class="pg next" href="%s.html"><span>다음</span>%s</a>' % (s, l)
    return prev_html + nxt_html


def first_paragraph(md_text):
    for line in md_text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith(">"):
            return re.sub(r"[*`\[\]]|\(.*?\)", "", line)[:150]
    return SITE_TITLE


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)

    search_index = []

    for idx, (slug, label, _grp) in enumerate(PAGES):
        src = os.path.join(CONTENT, slug + ".md")
        with open(src, encoding="utf-8") as fh:
            text = fh.read()

        md = markdown.Markdown(
            extensions=["fenced_code", "codehilite", "tables", "toc",
                        "attr_list", "def_list", "admonition", "sane_lists"],
            extension_configs={
                "codehilite": {"guess_lang": False, "linenums": False},
                "toc": {"toc_depth": "2-3"},
            },
        )
        body = md.convert(text)
        title = re.search(r"^#\s+(.+)$", text, re.M)
        title = title.group(1).strip() if title else label

        page_title = title if slug == "index" else u"%s · %s" % (title, SITE_TITLE)
        html = TEMPLATE.format(
            page_title=page_title,
            description=first_paragraph(text),
            site_title=SITE_TITLE,
            repo=REPO_URL,
            root="",
            nav=build_nav(slug),
            body=body,
            toc=md.toc if md.toc.count("<li>") > 1 else "",
            pager=build_pager(idx),
        )
        with open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8") as fh:
            fh.write(html)

        # 클라이언트 검색용 인덱스(제목 + 본문 텍스트)
        plain = re.sub(r"<[^>]+>", " ", body)
        plain = html_lib.unescape(plain)          # &quot; 등 엔티티 복원
        plain = re.sub(r"\s+", " ", plain)
        search_index.append({"u": slug + ".html", "t": title, "b": plain[:12000]})

    with open(os.path.join(OUT, "search-index.json"), "w", encoding="utf-8") as fh:
        import json
        json.dump(search_index, fh, ensure_ascii=False)

    # Jekyll이 docs/를 다시 처리하지 않도록
    open(os.path.join(OUT, ".nojekyll"), "w").close()

    assets_src = os.path.join(ROOT, "assets")
    assets_dst = os.path.join(OUT, "assets")
    if os.path.isdir(assets_src):
        if os.path.isdir(assets_dst):
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)

    print("built %d pages -> docs/" % len(PAGES))


if __name__ == "__main__":
    main()
