# -*- coding: utf-8 -*-
# 예제 1. 문서 전체 시각화 인벤토리 만들기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/08-examples-bulk.html
# 이 파일은 content/08-examples-bulk.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 문서 전체의 페이지/시각화/데이터 테이블 목록을 문서 속성에 HTML로 기록한다.
# 결과를 보려면 텍스트 영역에 문서 속성 "InventoryReport" 를 삽입하세요.

from Spotfire.Dxp.Application.Visuals import VisualContent

rows = []
totalVisuals = 0

for page in Document.Pages:
    for visual in page.Visuals:
        totalVisuals += 1

        # 데이터 테이블 이름 — 텍스트 영역 등은 데이터가 없으므로 예외 처리
        try:
            tableName = visual.As[VisualContent]().Data.DataTableReference.Name
        except:
            tableName = u"(없음)"

        # 데이터 제한 표현식이 걸려 있는지도 함께 본다
        try:
            where = visual.As[VisualContent]().Data.WhereClauseExpression or u""
        except:
            where = u""

        rows.append(u"<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            page.Title,
            visual.Title,
            visual.TypeId.Name,
            tableName,
            where,
        ))

html = u"""
<table border="1" cellpadding="4" cellspacing="0">
<tr><th>페이지</th><th>시각화</th><th>유형</th><th>데이터 테이블</th><th>데이터 제한</th></tr>
%s
</table>
<p>페이지 %d개 / 시각화 %d개</p>
""" % (u"".join(rows), Document.Pages.Count, totalVisuals)

Document.Properties["InventoryReport"] = html
