# -*- coding: utf-8 -*-
# 예제 2. 모든 시각화에 데이터 제한 표현식 일괄 적용
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/05-examples-bulk.html
# 이 파일은 content/05-examples-bulk.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 지정한 데이터 테이블을 참조하는 모든 시각화에 데이터 제한 표현식을 적용한다.
#
# 매개변수:
#   expr        (String)    적용할 표현식. 빈 문자열이면 제한 해제
#   targetTable (DataTable) 이 테이블을 쓰는 시각화만 대상으로 함

from Spotfire.Dxp.Application.Visuals import VisualContent

applied = 0
skipped = 0

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            # 대상 테이블을 쓰는 시각화만
            if vc.Data.DataTableReference == targetTable:
                vc.Data.WhereClauseExpression = expr
                applied += 1
            else:
                skipped += 1
        except:
            # 텍스트 영역 등 데이터가 없는 시각화
            skipped += 1

Document.Properties["ScriptLog"] = u"%d개 시각화에 적용, %d개 건너뜀" % (applied, skipped)
