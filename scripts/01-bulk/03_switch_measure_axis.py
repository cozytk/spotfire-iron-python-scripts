# -*- coding: utf-8 -*-
# 예제 3. 축 표현식 동시 전환 (측정지표 스위처)
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/08-examples-bulk.html
# 이 파일은 content/08-examples-bulk.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 모든 페이지의 차트 Y축(교차 표는 측정 축)을 지정한 측정지표로 한 번에 바꾼다.
#
# 매개변수:
#   measure (String) 컬럼 이름   예: "Revenue"
#   agg     (String) 집계 함수   예: "Sum", "Avg", "Max"

from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

expression = "%s([%s])" % (agg, measure)

# Y축을 가진 유형
Y_AXIS_TYPES = [
    VisualTypeIdentifiers.BarChart,
    VisualTypeIdentifiers.LineChart,
    VisualTypeIdentifiers.ScatterPlot,
    VisualTypeIdentifiers.CombinationChart,
]

changed = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()

            if visual.TypeId in Y_AXIS_TYPES:
                vc.YAxis.Expression = expression
                changed.append(visual.Title)

            elif visual.TypeId == VisualTypeIdentifiers.CrossTable:
                vc.MeasureAxis.Expression = expression
                changed.append(visual.Title)

            elif visual.TypeId == VisualTypeIdentifiers.PieChart:
                vc.SectorSizeAxis.Expression = expression
                changed.append(visual.Title)

            elif visual.TypeId == VisualTypeIdentifiers.TreemapChart:
                vc.SizeAxis.Expression = expression
                changed.append(visual.Title)
        except:
            pass

Document.Properties["ScriptLog"] = u"%s 기준으로 %d개 차트를 전환했습니다." % (
    expression, len(changed))
