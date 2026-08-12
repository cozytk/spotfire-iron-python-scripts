# -*- coding: utf-8 -*-
# 예제 6. 모든 차트의 줌·축 범위 초기화
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/08-examples-bulk.html
# 이 파일은 content/08-examples-bulk.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 모든 페이지의 모든 차트에서 축 줌 범위를 기본값으로 되돌린다.

from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

AXIS_NAMES = ["XAxis", "YAxis"]

reset = 0

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        for axisName in AXIS_NAMES:
            try:
                getattr(vc, axisName).ZoomRange = AxisRange.DefaultRange
                reset += 1
            except:
                pass

Document.Properties["ScriptLog"] = u"%d개 축의 줌을 초기화했습니다." % reset
