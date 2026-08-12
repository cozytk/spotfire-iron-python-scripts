# -*- coding: utf-8 -*-
# 예제 16. 마킹한 행을 새 데이터 테이블로 스냅샷
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/11-examples-data.html
# 이 파일은 content/11-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 현재 마킹된 행만 새 데이터 테이블로 복사한다.
#
# 매개변수:
#   sourceTable  (DataTable) 원본 테이블
#   snapshotName (String)    만들 테이블 이름

from Spotfire.Dxp.Data.Import import DataTableDataSource

# 마킹 이름은 하드코딩하지 않는다 (한국어 UI에서는 "마킹")
marking = Document.ActiveMarkingSelectionReference
markedRows = marking.GetSelection(sourceTable).AsIndexSet()

if markedRows.Count == 0:
    Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 차트에서 선택하세요."
else:
    # 마킹을 그대로 데이터 원본에 넘긴다.
    # 마킹(DataMarkingSelection)이 곧 DataSelection 이므로 별도 변환이 필요 없다.
    source = DataTableDataSource(sourceTable, marking)

    if Document.Data.Tables.Contains(snapshotName):
        Document.Data.Tables[snapshotName].ReplaceData(source)
        action = u"갱신"
    else:
        Document.Data.Tables.Add(snapshotName, source)
        action = u"생성"

    Document.Properties["ScriptLog"] = u"'%s' 테이블을 %s했습니다. (%d행)" % (
        snapshotName, action, markedRows.Count)
