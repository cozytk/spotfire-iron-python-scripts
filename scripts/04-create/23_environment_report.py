# -*- coding: utf-8 -*-
# 예제 23. 실행 환경 진단 리포트
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/12-examples-create.html
# 이 파일은 content/12-examples-create.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 이 환경에서 무엇이 되고 무엇이 안 되는지 한 번에 진단한다.
# 문서를 전혀 변경하지 않는다.
#
# 결과를 보려면 텍스트 영역에 문서 속성 "InventoryReport" 를 삽입하세요.

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers

lines = []


def add(label, value):
    lines.append(u"<tr><td>%s</td><td>%s</td></tr>" % (label, value))


# 1) 클라이언트 종류 — 파일 쓰기·MessageBox 가능 여부를 가른다
appType = Application.GetType().ToString()
isAnalyst = "RichAnalysisApplication" in appType
add(u"클라이언트", u"%s<br><code>%s</code>" % (
    u"Analyst (데스크톱)" if isAnalyst else u"Web Player (브라우저)", appType))
add(u"로컬 파일 쓰기", u"가능" if isAnalyst else u"<b>불가</b>")
add(u"MessageBox / 파일 대화상자", u"가능" if isAnalyst else u"<b>불가</b>")

# 2) 마킹 이름 — 하드코딩된 "Marking" 이 통하는지
markingNames = [m.Name for m in Document.Data.Markings]
add(u"마킹 이름", u", ".join(markingNames) or u"(없음)")
add(u'`Markings["Marking"]` 사용 가능', u"예" if "Marking" in markingNames else u"<b>아니오</b>")

# 3) 필터링 스킴 이름
schemeNames = []
for scheme in Document.FilteringSchemes:
    try:
        schemeNames.append(scheme.FilteringSelectionReference.Name)
    except:
        schemeNames.append(u"(이름 없음)")
add(u"필터링 스킴", u"%d개 — %s" % (len(schemeNames), u", ".join(schemeNames)))

# 4) 내보내기 라이선스 — CreateDataWriter 가 None 을 돌려주는지 확인만 한다
#    writer 객체를 만들 뿐 파일을 쓰지 않으므로 안전하다.
DOTNET_BASE = ["Equals", "GetHashCode", "GetType", "MemberwiseClone",
               "ReferenceEquals", "ToString"]

writable, blocked = [], []
for name in dir(DataWriterTypeIdentifiers):
    if name.startswith("_") or name in DOTNET_BASE:
        continue
    try:
        identifier = getattr(DataWriterTypeIdentifiers, name)
        writer = Document.Data.CreateDataWriter(identifier)
        (writable if writer is not None else blocked).append(name)
    except:
        blocked.append(name)
add(u"내보내기 가능한 형식", u", ".join(writable) or u"<b>없음 (라이선스 확인 필요)</b>")

# 5) 문서 규모와 구성
typeCounts = {}
for page in Document.Pages:
    for visual in page.Visuals:
        key = visual.TypeId.Name
        typeCounts[key] = typeCounts.get(key, 0) + 1
add(u"페이지 / 시각화", u"%d개 / %d개" % (
    Document.Pages.Count, sum(typeCounts.values())))
add(u"시각화 구성", u", ".join(
    u"%s %d" % (k, v) for k, v in sorted(typeCounts.items())) or u"(없음)")

# 6) 데이터 테이블과 새로고침 가능 여부
tableRows = []
for table in Document.Data.Tables:
    tableRows.append(u"%s (%d행, 새로고침 %s)" % (
        table.Name, table.RowCount, u"가능" if table.IsRefreshable else u"불가"))
add(u"데이터 테이블", u"<br>".join(tableRows) or u"(없음)")

# 7) 교안 예제가 쓰는 문서 속성이 준비되어 있는지
NEEDED = ["ScriptLog", "InventoryReport", "LimitExpression", "SelectedMeasure"]
existing = []
for name in NEEDED:
    try:
        Document.Properties[name]
        existing.append(name)
    except:
        pass
missing = [n for n in NEEDED if n not in existing]
add(u"예제용 문서 속성",
    (u"없음: %s" % u", ".join(missing)) if missing else u"모두 준비됨")

report = (u'<table border="1" cellpadding="4" cellspacing="0">'
          u"<tr><th>항목</th><th>결과</th></tr>%s</table>" % u"".join(lines))
summary = u"환경 진단 완료 — %s" % (u"Analyst" if isAnalyst else u"Web Player")

# 결과를 담을 문서 속성 자체가 없을 수도 있다. 그게 진단 대상 중 하나이므로
# 여기서 실패하면 안 된다. 없으면 편집 창 출력으로 떨어뜨린다.
try:
    Document.Properties["InventoryReport"] = report
    Document.Properties["ScriptLog"] = summary
except:
    print summary
    print report
