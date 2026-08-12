# -*- coding: utf-8 -*-
# 예제 24. 모든 시각화의 툴팁 일괄 통일
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-visuals.html
# 이 파일은 content/09-examples-visuals.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 지정한 테이블을 쓰는 모든 시각화의 툴팁(Details) 항목을 동일하게 맞춘다.
#
# 매개변수:
#   targetTable (DataTable) 대상 테이블
#   tooltipList (String)    ";" 로 구분한 표현식 목록. 빈 문자열이면 기본 항목만 끄긴다

from Spotfire.Dxp.Application.Visuals import VisualContent

expressions = [e.strip() for e in tooltipList.split(";") if e.strip()]

applied, skipped = 0, 0
report = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        # 대상 테이블을 쓰는 시각화만. 텍스트 영역은 Data 자체가 없다
        try:
            if vc.Data.DataTableReference != targetTable:
                continue
        except:
            continue

        # Details 가 없는 유형도 있다 (텍스트 영역, 일부 미니어처)
        try:
            details = vc.Details
        except:
            skipped += 1
            continue

        # 1) 기존 항목을 전부 숨긴다 (삭제가 아니므로 되돌리기 쉽다)
        hidden = 0
        for item in details.Items:
            try:
                item.Visible = False
                hidden += 1
            except:
                pass

        # 2) 지정한 표현식을 추가한다
        added = 0
        for expression in expressions:
            try:
                details.Items.AddExpression(expression)
                added += 1
            except Exception, err:
                report.append(u"  ! %s / %s : %s" % (visual.Title, expression, err))

        applied += 1
        report.append(u"%s — 숨김 %d, 추가 %d" % (visual.Title, hidden, added))

summary = u"툴팁 통일: 시각화 %d개 적용, %d개 건너뜀\n%s" % (
    applied, skipped, u"\n".join(report))
Document.Properties["ScriptLog"] = summary
print summary
