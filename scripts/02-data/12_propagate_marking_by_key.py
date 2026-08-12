# -*- coding: utf-8 -*-
# 예제 12. 키 컬럼으로 다른 테이블에 마킹 전파
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-data.html
# 이 파일은 content/09-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 원본 테이블의 마킹된 키 값을 읽어, 같은 키를 가진 대상 테이블 행을 마킹한다.
#
# 매개변수:
#   sourceTable (DataTable) 마킹을 읽을 테이블
#   targetTable (DataTable) 마킹을 적용할 테이블
#   sourceKey   (String)    원본 키 컬럼명
#   targetKey   (String)    대상 키 컬럼명

from Spotfire.Dxp.Data import DataValueCursor, IndexSet, RowSelection

# 마킹 이름은 하드코딩하지 않는다 (한국어 UI에서는 "마킹")
marking = Document.ActiveMarkingSelectionReference

# 1) 원본에서 마킹된 키 값을 집합으로 수집
markedRows = marking.GetSelection(sourceTable).AsIndexSet()
sourceCursor = DataValueCursor.CreateFormatted(sourceTable.Columns[sourceKey])

keys = set()
for row in sourceTable.GetRows(markedRows, sourceCursor):
    value = sourceCursor.CurrentValue
    if value is not None:
        keys.add(value.strip().upper())      # 대소문자·공백 차이 무시

# 2) 대상 테이블 전체를 훑으며 일치하는 행 인덱스를 모은다
targetCursor = DataValueCursor.CreateFormatted(targetTable.Columns[targetKey])
allTargetRows = IndexSet(targetTable.RowCount, True)

hits = IndexSet(targetTable.RowCount, False)
matched = 0

for row in targetTable.GetRows(allTargetRows, targetCursor):
    value = targetCursor.CurrentValue
    if value is not None and value.strip().upper() in keys:
        hits[row.Index] = True        # IndexSet 은 Add() 가 아니라 인덱서로 설정한다
        matched += 1

# 3) 대상 테이블에 마킹 적용
marking.SetSelection(RowSelection(hits), targetTable)

Document.Properties["ScriptLog"] = u"키 %d개 → '%s' 테이블 %d행 마킹" % (
    len(keys), targetTable.Name, matched)
