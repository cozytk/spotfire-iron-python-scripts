# -*- coding: utf-8 -*-
# 예제 19. 마킹한 값별로 시각화 자동 생성
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/11-examples-advanced.html
# 이 파일은 content/11-examples-advanced.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 마킹된 값마다 차트를 하나씩 만들어 새 페이지에 배치한다.
#
# 매개변수:
#   sourceTable  (DataTable) 데이터 테이블
#   splitColumn  (String)    분할 기준 컬럼명       예: "Region"
#   measureExpr  (String)    Y축 표현식             예: "Sum([Revenue])"
#   categoryExpr (String)    X축 표현식             예: "[Month]"

from Spotfire.Dxp.Application.Visuals import BarChart
from Spotfire.Dxp.Data import DataValueCursor

PAGE_TITLE = u"자동 생성 비교"
MARKING_NAME = "Marking"
MAX_CHARTS = 12          # 너무 많이 만들지 않도록 상한

# 1) 마킹된 행에서 분할 기준 값의 고유 목록을 얻는다
marking = Document.Data.Markings[MARKING_NAME]
markedRows = marking.GetSelection(sourceTable).AsIndexSet()
cursor = DataValueCursor.CreateFormatted(sourceTable.Columns[splitColumn])

values = set()
for row in sourceTable.GetRows(markedRows, cursor):
    if cursor.CurrentValue is not None:
        values.add(cursor.CurrentValue)

values = sorted(values)[:MAX_CHARTS]

if not values:
    Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 값을 선택하세요."
else:
    # 2) 기존 자동 생성 페이지가 있으면 지우고 새로 만든다 (재실행 대비)
    for page in [p for p in Document.Pages]:
        if page.Title == PAGE_TITLE:
            Document.Pages.Remove(page)

    newPage = Document.Pages.AddNew(PAGE_TITLE)

    # 3) 값마다 차트 하나씩 생성
    for value in values:
        chart = newPage.Visuals.AddNew[BarChart]()
        chart.Data.DataTableReference = sourceTable
        chart.XAxis.Expression = categoryExpr
        chart.YAxis.Expression = measureExpr

        # 이 차트만 해당 값으로 한정한다
        escaped = value.replace("'", "''")      # 작은따옴표 이스케이프
        chart.Data.WhereClauseExpression = "[%s] = '%s'" % (splitColumn, escaped)

        chart.Title = u"%s" % value
        chart.Legend.Visible = False

    Document.ActivePageReference = newPage
    Document.Properties["ScriptLog"] = u"%d개 차트를 '%s' 페이지에 생성했습니다." % (
        len(values), PAGE_TITLE)
