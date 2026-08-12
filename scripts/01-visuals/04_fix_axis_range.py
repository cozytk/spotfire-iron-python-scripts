# -*- coding: utf-8 -*-
# 예제 4. 여러 차트의 축 범위 동시 고정
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-visuals.html
# 이 파일은 content/09-examples-visuals.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 지정한 페이지의 막대/선 차트 Y축 범위를 문서 속성 값으로 한 번에 고정한다.
#
# 사전 준비: 문서 속성 "최소", "최대" (실수 또는 정수)

from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

TARGET_PAGE = u"매출분석"        # 빈 문자열이면 모든 페이지

AxisMin = Document.Properties["최소"]
AxisMax = Document.Properties["최대"]

# TypeId를 문자열로 비교하는 방식 — 열거형 import 없이도 동작한다
TARGET_TYPES = [
    "TypeIdentifier:Spotfire.BarChart",
    "TypeIdentifier:Spotfire.LineChart",
    "TypeIdentifier:Spotfire.CombinationChart",
]

applied = 0

for page in Document.Pages:
    if TARGET_PAGE and page.Title != TARGET_PAGE:
        continue

    for visual in page.Visuals:
        if str(visual.TypeId) not in TARGET_TYPES:
            continue
        try:
            vc = visual.As[VisualContent]()
            vc.YAxis.Range = AxisRange(AxisMin, AxisMax)
            applied += 1
        except:
            pass

Document.Properties["ScriptLog"] = u"%d개 차트의 Y축을 %s ~ %s 로 고정했습니다." % (
    applied, AxisMin, AxisMax)
