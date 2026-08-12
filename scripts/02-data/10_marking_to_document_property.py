# -*- coding: utf-8 -*-
# 예제 10. 마킹 결과를 문서 속성으로 넘기기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/06-examples-data.html
# 이 파일은 content/06-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 마킹된 행에서 특정 컬럼의 고유값을 모아 문서 속성에 저장한다.
#
# 매개변수:
#   sourceTable (DataTable) 대상 테이블
#   keyColumn   (String)    값을 모을 컬럼 이름

from Spotfire.Dxp.Data import DataValueCursor

MARKING_NAME = "Marking"

marking = Document.Data.Markings[MARKING_NAME]
markedRows = marking.GetSelection(sourceTable).AsIndexSet()

cursor = DataValueCursor.CreateFormatted(sourceTable.Columns[keyColumn])

values = []
for row in sourceTable.GetRows(markedRows, cursor):
    value = cursor.CurrentValue
    if value is not None and value not in values:
        values.append(value)

values.sort()

# 1) 사람이 읽는 문자열
Document.Properties["MarkedLabel"] = (
    u"선택: %s (%d개)" % (u", ".join(values), len(values)) if values
    else u"선택 없음")

# 2) 표현식에 넣을 형태 — "'East','West'"
Document.Properties["MarkedInList"] = u",".join(u"'%s'" % v for v in values)

# 3) 개수만
Document.Properties["MarkedCount"] = len(values)
