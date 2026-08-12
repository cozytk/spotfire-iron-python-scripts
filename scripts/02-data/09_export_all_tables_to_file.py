# -*- coding: utf-8 -*-
# 예제 9. 여러 데이터 테이블을 한 번에 파일로 내보내기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-data.html
# 이 파일은 content/09-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 문서의 모든 데이터 테이블을, 현재 필터가 적용된 행만, 파일로 내보낸다.
# (Analyst 데스크톱 전용)
#
# 매개변수:
#   outDir (String) 저장 폴더 경로

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from System.IO import File, Path, Directory
from System import DateTime

# 형식 선택:
#   DataWriterTypeIdentifiers.ExcelXlsDataWriter  → .xls
#   DataWriterTypeIdentifiers.StdfDataWriter      → .stdf (Spotfire 이진 형식)
WRITER = DataWriterTypeIdentifiers.ExcelXlsDataWriter
EXTENSION = ".xls"

stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss")
folder = Path.Combine(outDir, "export_" + stamp)
Directory.CreateDirectory(folder)

exported = []

for table in Document.Data.Tables:
    # 현재 활성 필터링에서 살아남은 행만
    filtered = Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()

    # 전체 행을 내보내려면 위 줄 대신:
    # from Spotfire.Dxp.Data import IndexSet
    # filtered = IndexSet(table.RowCount, True)

    columnNames = [c.Name for c in table.Columns]

    writer = Document.Data.CreateDataWriter(WRITER)
    path = Path.Combine(folder, table.Name + EXTENSION)

    stream = File.OpenWrite(path)
    try:
        writer.Write(stream, table, filtered, columnNames)
    finally:
        stream.Close()

    exported.append(u"%s (%d행)" % (table.Name, filtered.Count))

Document.Properties["ScriptLog"] = u"%s<br>저장 위치: %s" % (u"<br>".join(exported), folder)
