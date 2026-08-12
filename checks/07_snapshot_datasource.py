# -*- coding: utf-8 -*-
# 테스트 7 — 예제 10(마킹 행 스냅샷)을 고치기 위한 확인
#
# 배경:
#   교안 예제 10 은 StdfDataSource(stream) 을 썼는데, 실측 결과 그 이름은
#   존재하지 않습니다. Spotfire.Dxp.Data.Import 에 실제로 있는 것은 다음입니다.
#
#     StdfFileDataSource   SbdfFileDataSource   SbdfLibraryDataSource
#     TextFileDataSource   DataTableDataSource  DatabaseDataSource
#     FileDataSource       InformationLinkDataSource
#     DataSourceFactory    FileDataSourceFactory
#
#   이 중 무엇이 "메모리 스트림"을 받아 주는지 확인해야 예제를 고칠 수 있습니다.
#
# 위험도: 낮음~중간
#   - 1~3단계는 데이터 원본 객체를 만들기만 합니다 (문서 변경 없음)
#   - 4단계는 실제로 임시 테이블을 만들었다 지웁니다. 아래 RUN_ROUNDTRIP 로 끕니다.
#   - 사본에서 실행하시길 권합니다.

RUN_ROUNDTRIP = True        # False 로 두면 4단계를 건너뜁니다

TEMP_TABLE = "__SNAPSHOT_TEST__"

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from Spotfire.Dxp.Data import IndexSet
from System.IO import MemoryStream, SeekOrigin
import Spotfire.Dxp.Data.Import as imp


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


# ---------------------------------------------------------------
print "=== 1. 컬렉션 인덱싱 방식 확인 ==="
# 04 테스트에서 'expected str, got int' 가 났던 원인을 특정한다
try:
    t = Document.Data.Tables[0]
    print "[OK] Document.Data.Tables[0]  (숫자 인덱스 가능):", clean(t.Name)
except Exception, e:
    print "[NO] Document.Data.Tables[0] ->", clean(str(e))

try:
    s = Document.FilteringSchemes[0]
    print "[OK] Document.FilteringSchemes[0] (숫자 인덱스 가능)"
except Exception, e:
    print "[NO] Document.FilteringSchemes[0] ->", clean(str(e))

table = Document.ActiveDataTableReference
try:
    c = table.Columns[0]
    print "[OK] table.Columns[0] (숫자 인덱스 가능):", clean(c.Name)
except Exception, e:
    print "[NO] table.Columns[0] ->", clean(str(e))

try:
    p = Document.Pages[0]
    print "[OK] Document.Pages[0] (숫자 인덱스 가능):", clean(p.Title)
except Exception, e:
    print "[NO] Document.Pages[0] ->", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 2. 스냅샷용 데이터를 메모리에 기록 ==="

# 마킹된 행이 있으면 그걸, 없으면 앞의 10행만 쓴다
rows = Document.ActiveMarkingSelectionReference.GetSelection(table).AsIndexSet()
if rows.Count == 0:
    rows = IndexSet(table.RowCount, False)
    added = 0
    for i in range(table.RowCount):
        if added >= 10:
            break
        rows.Add(i)
        added += 1
    print "  마킹이 없어 앞의", rows.Count, "행으로 시험합니다"
else:
    print "  마킹된", rows.Count, "행으로 시험합니다"

columnNames = []
for column in table.Columns:
    columnNames.append(column.Name)

streams = {}
for writerName in ["SbdfDataWriter", "StdfDataWriter"]:
    try:
        stream = MemoryStream()
        writer = Document.Data.CreateDataWriter(getattr(DataWriterTypeIdentifiers, writerName))
        writer.Write(stream, table, rows, columnNames)
        stream.Seek(0, SeekOrigin.Begin)
        streams[writerName] = stream
        print "[OK]", writerName, "-> 메모리에 기록 성공, 길이:", stream.Length
    except Exception, e:
        print "[NO]", writerName, "->", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 3. 어떤 DataSource 가 메모리 스트림을 받는가 ==="

CANDIDATES = [
    ("SbdfFileDataSource", "SbdfDataWriter"),
    ("StdfFileDataSource", "StdfDataWriter"),
    ("FileDataSource", "SbdfDataWriter"),
]

working = []

for sourceName, writerName in CANDIDATES:
    if not hasattr(imp, sourceName):
        print "[NO]", sourceName, "- 이 버전에 없음"
        continue
    if writerName not in streams:
        print "[SKIP]", sourceName, "-", writerName, "기록이 실패해서 시험 못 함"
        continue

    sourceType = getattr(imp, sourceName)
    stream = streams[writerName]
    try:
        stream.Seek(0, SeekOrigin.Begin)
        dataSource = sourceType(stream)
        print "[OK]", sourceName + "(stream) 생성 성공 ->", clean(dataSource)
        working.append((sourceName, writerName))
    except Exception, e:
        print "[NO]", sourceName + "(stream) ->", clean(str(e))

print ""
print "  --- DataTableDataSource (다른 접근) ---"
try:
    dts = imp.DataTableDataSource(table)
    print "[OK] DataTableDataSource(table) 생성 성공 ->", clean(dts)
    print "     (행 부분집합을 지정할 수 있는지는 별도 확인 필요)"
except Exception, e:
    print "[NO] DataTableDataSource(table) ->", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 4. 실제 왕복 시험 (임시 테이블 생성 후 삭제) ==="

if not RUN_ROUNDTRIP:
    print "[SKIP] RUN_ROUNDTRIP = False 라서 건너뜁니다"
elif not working:
    print "[SKIP] 3단계에서 성공한 DataSource 가 없어 건너뜁니다"
else:
    sourceName, writerName = working[0]
    print "  사용:", sourceName, "+", writerName
    try:
        # 이전 실행이 남긴 것 정리
        if Document.Data.Tables.Contains(TEMP_TABLE):
            Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])

        stream = streams[writerName]
        stream.Seek(0, SeekOrigin.Begin)
        dataSource = getattr(imp, sourceName)(stream)

        newTable = Document.Data.Tables.Add(TEMP_TABLE, dataSource)
        print "[OK] Tables.Add 성공 - 행:", newTable.RowCount, "컬럼:", newTable.Columns.Count
        print "     원본에서 넘긴 행 수:", rows.Count, "-> 일치 여부:", (newTable.RowCount == rows.Count)
    except Exception, e:
        print "[NO] 왕복 실패 ->", clean(str(e))
    finally:
        try:
            if Document.Data.Tables.Contains(TEMP_TABLE):
                Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])
                print "[OK] 임시 테이블 삭제 완료"
        except Exception, e:
            print "[NO] 임시 테이블 삭제 실패 - '" + TEMP_TABLE + "' 을 직접 지워 주세요:", clean(str(e))

print ""
print "=== 요약 ==="
if working:
    print "예제 10 에 쓸 수 있는 조합:"
    for sourceName, writerName in working:
        print "   ", writerName, "+", sourceName + "(stream)"
else:
    print "메모리 스트림을 받는 DataSource 를 찾지 못했습니다."
    print "이 경우 임시 파일을 거치는 방식으로 예제 10 을 다시 작성하겠습니다."
