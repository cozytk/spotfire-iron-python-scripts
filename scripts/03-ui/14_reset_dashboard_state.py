# -*- coding: utf-8 -*-
# 예제 14. 대시보드 전체 상태 초기화
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-ui.html
# 이 파일은 content/10-examples-ui.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 대시보드를 초기 상태로 되돌린다.
#   1) 모든 필터링 스킴의 필터 초기화
#   2) 모든 마킹 해제
#   3) 문서 속성을 기본값으로
#   4) 모든 차트 줌 초기화
#   5) 첫 페이지로 이동

from Spotfire.Dxp.Data import IndexSet, RowSelection
from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

log = []

# 1) 모든 필터링 스킴 초기화 — 기본 버튼은 현재 스킴 하나만 처리한다
schemeCount = 0
for scheme in Document.FilteringSchemes:
    scheme.ResetAllFilters()
    schemeCount += 1
log.append(u"필터링 스킴 %d개 초기화" % schemeCount)

# 2) 모든 마킹 해제 (모든 테이블에 대해)
markingCount = 0
for marking in Document.Data.Markings:
    for table in Document.Data.Tables:
        try:
            empty = RowSelection(IndexSet(table.RowCount, False))
            marking.SetSelection(empty, table)
        except:
            pass
    markingCount += 1
log.append(u"마킹 %d개 해제" % markingCount)

# 3) 문서 속성 기본값 — 대시보드에 맞게 수정하세요
DEFAULTS = {
    "SelectedRegion": "All",
    "SelectedMeasure": "Revenue",
    "LimitExpression": "",
    "ScriptLog": "",
}
for name, value in DEFAULTS.items():
    try:
        Document.Properties[name] = value
    except:
        pass       # 없는 속성은 건너뛴다
log.append(u"문서 속성 %d개 복원" % len(DEFAULTS))

# 4) 모든 차트 줌 초기화
zoomReset = 0
for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            for axisName in ["XAxis", "YAxis"]:
                try:
                    getattr(vc, axisName).ZoomRange = AxisRange.DefaultRange
                    zoomReset += 1
                except:
                    pass
        except:
            pass
log.append(u"축 %d개 줌 초기화" % zoomReset)

# 5) 첫 페이지로
if Document.Pages.Count > 0:
    Document.ActivePageReference = Document.Pages[0]

Document.Properties["ScriptLog"] = u" / ".join(log)
