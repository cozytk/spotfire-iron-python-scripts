# -*- coding: utf-8 -*-
# 예제 3. 범례·제목·서식 일괄 통일
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-visuals.html
# 이 파일은 content/09-examples-visuals.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 모든 페이지의 모든 시각화에 대해 범례와 제목 표시 여부를 통일한다.
#
# 매개변수:
#   showLegend (String) "True" 또는 "False"

from Spotfire.Dxp.Application.Visuals import VisualContent

visible = (str(showLegend).lower() == "true")

SHOW_TITLE = True        # 제목 표시 여부도 함께 통일한다

changed = 0
noLegend = 0

for page in Document.Pages:
    for visual in page.Visuals:
        # 제목 표시 여부는 Visual(껍데기)의 속성이라 캐스팅 없이 바로 된다.
        # 텍스트 영역에도 있으므로 모든 시각화에 적용된다.
        try:
            visual.ShowTitle = SHOW_TITLE
        except:
            pass

        # 범례는 VisualContent(알맹이) 쪽이고, 없는 유형도 있다
        try:
            vc = visual.As[VisualContent]()
            vc.Legend.Visible = visible
            changed += 1
        except:
            # 범례 개념이 없는 시각화 (텍스트 영역, 표 등)
            noLegend += 1

Document.Properties["ScriptLog"] = u"범례 %s: %d개 적용, %d개 해당 없음" % (
    u"표시" if visible else u"숨김", changed, noLegend)
