# -*- coding: utf-8 -*-
# 예제 7. 모든 시각화의 데이터 테이블 일괄 교체
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-visuals.html
# 이 파일은 content/09-examples-visuals.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 특정 데이터 테이블을 참조하는 모든 시각화를 다른 테이블로 교체한다.
# 축 표현식은 최대한 보존한다 (컬럼 이름이 같다는 전제).
#
# 매개변수:
#   oldTable (DataTable) 교체 전
#   newTable (DataTable) 교체 후

from Spotfire.Dxp.Application.Visuals import VisualContent

# 보존을 시도할 축 이름들
AXIS_NAMES = ["XAxis", "YAxis", "ColorAxis", "SizeAxis", "ShapeAxis",
              "MeasureAxis", "HorizontalAxis", "VerticalAxis", "SectorSizeAxis"]

switched = 0
report = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        try:
            if vc.Data.DataTableReference != oldTable:
                continue
        except:
            continue

        # 1) 현재 축 표현식을 기억
        saved = {}
        for axisName in AXIS_NAMES:
            try:
                saved[axisName] = getattr(vc, axisName).Expression
            except:
                pass

        # 2) 데이터 테이블 교체
        vc.Data.DataTableReference = newTable

        # 3) 축 표현식 복원 — 컬럼이 없으면 그 축만 실패하고 넘어간다
        restored, lost = [], []
        for axisName, expression in saved.items():
            try:
                getattr(vc, axisName).Expression = expression
                restored.append(axisName)
            except:
                lost.append(axisName)

        switched += 1
        if lost:
            report.append(u"%s / %s → 복원 실패: %s" % (
                page.Title, visual.Title, u", ".join(lost)))

msg = u"%d개 시각화를 '%s' 로 교체했습니다." % (switched, newTable.Name)
if report:
    msg += u"<br><b>확인 필요:</b><br>" + u"<br>".join(report)

Document.Properties["ScriptLog"] = msg
