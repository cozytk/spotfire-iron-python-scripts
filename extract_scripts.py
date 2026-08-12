# -*- coding: utf-8 -*-
"""
교안(content/09~12)의 예제 코드 블록을 scripts/ 폴더의 .py 파일로 추출한다.

교안 본문과 스크립트 파일이 어긋나지 않도록, 스크립트는 항상 이 도구로 생성한다.
직접 scripts/*.py 를 수정하지 말고 content/*.md 를 고친 뒤 다시 실행할 것.

사용법:
    python extract_scripts.py
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
SCRIPTS = os.path.join(ROOT, "scripts")

DOC_BASE = "https://cozytk.github.io/spotfire-iron-python-scripts"

# 교안 파일 -> (출력 폴더, 교안 페이지 파일명)
CHAPTERS = [
    ("09-examples-visuals.md", "01-visuals", "09-examples-visuals.html"),
    ("10-examples-state.md", "02-state", "10-examples-state.html"),
    ("11-examples-data.md", "03-data", "11-examples-data.html"),
    ("12-examples-create.md", "04-create", "12-examples-create.html"),
]

# 예제 번호 -> 파일명 (한글 제목 대신 영문 슬러그 사용)
FILENAMES = {
    1: "bulk_limit_expression",
    2: "switch_measure_axis",
    3: "unify_legend_and_title",
    4: "fix_axis_range",
    5: "reset_zoom_all_charts",
    6: "bulk_switch_visual_type",
    7: "swap_data_table",
    8: "marking_to_document_property",
    9: "propagate_marking_by_key",
    10: "reset_dashboard_state",
    11: "reset_selected_column_filters",
    12: "configure_filter_panel",
    13: "toggle_pages_by_role",
    14: "export_all_visuals_to_png",
    15: "export_tables_to_file",
    16: "snapshot_marked_rows",
    17: "refresh_all_data_tables",
    18: "visual_inventory",
    19: "audit_expressions",
    20: "generate_visuals_from_marking",
    21: "scatter_plot_matrix",
    22: "script_inventory",
    23: "environment_report",
}

HEADING = re.compile(r"^## 예제 (\d+)\.\s*(.+?)\s*$", re.M)
CODE = re.compile(r"```python\n(.*?)```", re.S)

# 예제 번호를 갖지 않는 별도 스크립트 (교안 파일, 섹션 제목, 출력 경로)
EXTRAS = [
    ("09-examples-visuals.md", u"## 사전 준비 · 문서 속성 만들기",
     "00_setup_document_properties.py", u"사전 준비 · 문서 속성 만들기",
     "09-examples-visuals.html"),
]


def extract_extras():
    written = 0
    for mdName, heading, fileName, title, htmlName in EXTRAS:
        with open(os.path.join(CONTENT, mdName), encoding="utf-8") as fh:
            text = fh.read()
        start = text.find(heading)
        if start < 0:
            continue
        code = CODE.search(text, start)
        if not code:
            continue
        body = re.sub(r"^# -\*- coding: utf-8 -\*-\n", "", code.group(1).rstrip() + "\n")
        header = (
            u"# -*- coding: utf-8 -*-\n"
            u"# %s\n"
            u"#\n"
            u"# 예제를 실행하기 전에 이 스크립트를 한 번 실행하세요.\n"
            u"# 설명: %s/%s\n"
            u"# 이 파일은 content/%s 에서 자동 생성됩니다. 직접 수정하지 마세요.\n"
            u"\n" % (title, DOC_BASE, htmlName, mdName)
        )
        with open(os.path.join(SCRIPTS, fileName), "w", encoding="utf-8") as fh:
            fh.write(header + body)
        written += 1
    return written


def main():
    written = 0

    for mdName, folder, htmlName in CHAPTERS:
        with open(os.path.join(CONTENT, mdName), encoding="utf-8") as fh:
            text = fh.read()

        outDir = os.path.join(SCRIPTS, folder)
        if not os.path.isdir(outDir):
            os.makedirs(outDir)

        matches = list(HEADING.finditer(text))
        for i, match in enumerate(matches):
            number = int(match.group(1))
            title = match.group(2)
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            section = text[start:end]

            code = CODE.search(section)
            if not code:
                continue
            body = code.group(1).rstrip() + "\n"

            # 코드 첫 줄의 인코딩 선언은 헤더에서 다시 넣으므로 제거
            body = re.sub(r"^# -\*- coding: utf-8 -\*-\n", "", body)

            header = (
                u"# -*- coding: utf-8 -*-\n"
                u"# 예제 %d. %s\n"
                u"#\n"
                u"# 설명과 검증 포인트: %s/%s\n"
                u"# 이 파일은 content/%s 에서 자동 생성됩니다. 직접 수정하지 마세요.\n"
                u"\n" % (number, title, DOC_BASE, htmlName, mdName)
            )

            fileName = "%02d_%s.py" % (number, FILENAMES.get(number, "example"))
            path = os.path.join(outDir, fileName)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(header + body)
            written += 1

    if not os.path.isdir(SCRIPTS):
        os.makedirs(SCRIPTS)
    written += extract_extras()

    print("wrote %d scripts -> scripts/" % written)


if __name__ == "__main__":
    main()
