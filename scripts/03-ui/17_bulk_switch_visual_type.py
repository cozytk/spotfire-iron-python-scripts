# -*- coding: utf-8 -*-
# 예제 17. 시각화 유형 일괄 토글
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-ui.html
# 이 파일은 content/10-examples-ui.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 모든 페이지의 차트를 지정한 유형으로 바꾼다.
# 축 표현식은 Spotfire가 대체로 유지해 준다.
#
# 매개변수:
#   chartType (String) "Bar", "Line", "Area", "Scatter" 중 하나

from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers

TYPE_MAP = {
    "Bar":     VisualTypeIdentifiers.BarChart,
    "Line":    VisualTypeIdentifiers.LineChart,
    "Area":    VisualTypeIdentifiers.CombinationChart,
    "Scatter": VisualTypeIdentifiers.ScatterPlot,
}

# 서로 바꿔도 되는 유형들만 대상으로 한다 (표·텍스트 영역은 제외)
SWITCHABLE = [
    VisualTypeIdentifiers.BarChart,
    VisualTypeIdentifiers.LineChart,
    VisualTypeIdentifiers.CombinationChart,
    VisualTypeIdentifiers.ScatterPlot,
]

target = TYPE_MAP.get(chartType)

if target is None:
    Document.Properties["ScriptLog"] = u"알 수 없는 유형: %s" % chartType
else:
    changed = 0
    for page in Document.Pages:
        for visual in page.Visuals:
            try:
                if visual.TypeId in SWITCHABLE and visual.TypeId != target:
                    visual.TypeId = target
                    changed += 1
            except:
                pass

    Document.Properties["ScriptLog"] = u"%d개 시각화를 %s 로 전환했습니다." % (changed, chartType)
