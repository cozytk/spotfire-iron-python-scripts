# -*- coding: utf-8 -*-
# 예제 22. 문서 안의 스크립트 전수 조사
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/12-examples-create.html
# 이 파일은 content/12-examples-create.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 문서에 저장된 모든 스크립트(IronPython/JavaScript)의 목록과 요약을 만든다.
# 결과를 보려면 텍스트 영역에 문서 속성 "InventoryReport" 를 삽입하세요.
#
# 필요 버전: Spotfire 12.0 이상 (Document.ScriptManager)

# 스크립트 안에서 눈여겨봐야 할 흔적들
SUSPICIOUS = [
    ("C:/",           u"로컬 경로 (Web Player에서 실패)"),
    ("C:\\",          u"로컬 경로 (Web Player에서 실패)"),
    ("MessageBox",    u"Analyst 전용 UI"),
    ("Windows.Forms", u"Analyst 전용 UI"),
    ('["Marking"]',   u"마킹 이름 하드코딩 (한국어 UI에서 실패)"),
    ("CreateDataWriter", u"라이선스에 막힐 수 있음"),
]

rows = []
total = 0
byLanguage = {}

try:
    scripts = list(Document.ScriptManager.GetScripts())
except:
    scripts = None


def report(html, summary):
    # 문서 속성이 아직 없으면 편집 창 출력으로 떨어뜨린다
    try:
        Document.Properties["InventoryReport"] = html
        Document.Properties["ScriptLog"] = summary
    except:
        print summary
        print html


if scripts is None:
    report(u"<p>이 Spotfire 버전에는 ScriptManager API가 없습니다. (12.0 이상 필요)</p>",
           u"ScriptManager를 사용할 수 없습니다.")
else:
    for script in scripts:
        total += 1

        try:
            language = script.Language.Language
        except:
            language = u"(알 수 없음)"
        byLanguage[language] = byLanguage.get(language, 0) + 1

        code = script.ScriptCode or u""
        lineCount = len(code.splitlines())

        try:
            paramNames = [p.Name for p in script.Parameters]
        except:
            paramNames = []

        flags = []
        for needle, why in SUSPICIOUS:
            if needle in code and why not in flags:
                flags.append(why)

        rows.append(u"<tr><td>%s</td><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>" % (
            script.Name,
            language,
            lineCount,
            u", ".join(paramNames) or u"—",
            u"<br>".join(flags) or u"—",
        ))

    # 이름이 겹치는 스크립트 찾기 — 실수로 복제된 것을 잡아낸다
    names = [s.Name for s in scripts]
    duplicated = sorted(set([n for n in names if names.count(n) > 1]))

    summary = u", ".join(u"%s %d개" % (lang, n) for lang, n in byLanguage.items())

    html = u"""
<table border="1" cellpadding="4" cellspacing="0">
<tr><th>스크립트</th><th>언어</th><th>줄 수</th><th>매개변수</th><th>확인 필요</th></tr>
%s
</table>
<p>총 %d개 (%s)</p>
""" % (u"".join(rows), total, summary)

    if duplicated:
        html += u"<p><b>이름이 겹치는 스크립트:</b> %s</p>" % u", ".join(duplicated)

    report(html, u"스크립트 %d개를 조사했습니다." % total)
