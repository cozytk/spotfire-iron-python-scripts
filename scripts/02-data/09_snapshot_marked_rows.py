# -*- coding: utf-8 -*-
# 예제 9. 마킹한 행을 새 데이터 테이블로 스냅샷
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/06-examples-data.html
# 이 파일은 content/06-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 현재 마킹된 행을 새 데이터 테이블로 복사한다.
# 메모리 스트림에 STDF로 쓴 뒤 다시 읽어 들이는 방식.
#
# 매개변수:
#   sourceTable  (DataTable) 원본 테이블
#   snapshotName (String)    만들 테이블 이름

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from Spotfire.Dxp.Data.Import import StdfDataSource
from System.IO import MemoryStream, SeekOrigin

MARKING_NAME = "Marking"

marking = Document.Data.Markings[MARKING_NAME]
markedRows = marking.GetSelection(sourceTable).AsIndexSet()

if markedRows.Count == 0:
    Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 차트에서 선택하세요."
else:
    columnNames = [c.Name for c in sourceTable.Columns]

    # 1) 마킹된 행만 메모리에 STDF로 기록
    stream = MemoryStream()
    writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.StdfDataWriter)
    writer.Write(stream, sourceTable, markedRows, columnNames)

    # 2) 스트림을 처음으로 되감아 데이터 원본으로 사용
    stream.Seek(0, SeekOrigin.Begin)
    dataSource = StdfDataSource(stream)

    # 3) 같은 이름이 있으면 내용만 교체, 없으면 새로 추가
    if Document.Data.Tables.Contains(snapshotName):
        Document.Data.Tables[snapshotName].ReplaceData(dataSource)
        action = u"갱신"
    else:
        Document.Data.Tables.Add(snapshotName, dataSource)
        action = u"생성"

    Document.Properties["ScriptLog"] = u"'%s' 테이블을 %s했습니다. (%d행)" % (
        snapshotName, action, markedRows.Count)
