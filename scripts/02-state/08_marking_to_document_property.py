# -*- coding: utf-8 -*-
# 예제 8. 마킹 결과를 문서 속성으로 넘기기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-state.html
# 이 파일은 content/10-examples-state.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 마킹된 행에서 특정 컬럼의 고유값을 모아 문서 속성에 저장한다.
#
# 매개변수:
#   sourceTable (DataTable) 대상 테이블
#   keyColumn   (String)    값을 모을 컬럼 이름

from Spotfire.Dxp.Data import DataValueCursor

# 마킹 이름을 하드코딩하지 않고 "현재 활성 마킹"을 쓴다.
# 마킹 이름이 "Marking"이 아니어도, 나중에 바뀌어도 동작한다.
markedRows = Document.ActiveMarkingSelectionReference.GetSelection(sourceTable).AsIndexSet()

cursor = DataValueCursor.CreateFormatted(sourceTable.Columns[keyColumn])

# set을 쓰면 중복 제거가 빠르다 (행이 많을 때 특히)
seen = set()
for row in sourceTable.GetRows(markedRows, cursor):
    value = cursor.CurrentValue
    if value is not None and value != "":
        seen.add(value)

values = sorted(seen)

# 1) 사람이 읽는 문자열
Document.Properties["MarkedLabel"] = (
    u"선택: %s (%d개)" % (u", ".join(values), len(values)) if values
    else u"선택 없음")

# 2) 표현식에 넣을 형태 — "'East','West'"
Document.Properties["MarkedInList"] = u",".join(u"'%s'" % v for v in values)

# 3) 개수만
Document.Properties["MarkedCount"] = len(values)
