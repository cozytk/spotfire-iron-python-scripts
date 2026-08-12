# -*- coding: utf-8 -*-
# 테스트 9 — 예제 9·10을 확정하기 위한 마지막 확인
#
# 5차에서 알아낸 것:
#   - CreateDataWriter 시그니처는 정상: (typeId: TypeIdentifier) -] DataWriter
#     그런데 어떤 식별자를 넣어도 None 이 온다 -> 환경/라이선스 문제일 가능성
#   - Spotfire.Dxp.Data.Export 에 DataWriterFactory 가 있다
#   - TablePlot 에 ExportText / ExportData / ExportDataEnabled 가 있다
#   - DataTableDataSource 에 세 번째 오버로드가 있다:
#         DataTableDataSource(dataTable, dataSelection: DataSelection)
#     -> 예제 10(마킹 스냅샷)은 writer 없이 이것만으로 될 가능성이 높다
#
# 위험도: 낮음
#   - 1~4단계는 조회만 합니다
#   - 5단계만 임시 테이블을 만들었다 지웁니다. RUN_ROUNDTRIP 로 끌 수 있습니다
#   - 파일은 쓰지 않습니다
#   - 사본에서 실행하시길 권합니다

RUN_ROUNDTRIP = True
TEMP_TABLE = "__SNAPSHOT_TEST__"

from Spotfire.Dxp.Data import IndexSet, RowSelection
import Spotfire.Dxp.Data as data
import Spotfire.Dxp.Data.Import as imp

DOTNET_BASE = ["Equals", "GetHashCode", "GetType", "MemberwiseClone",
               "ReferenceEquals", "ToString"]


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


def members(obj, keyword=None):
    result = []
    for name in dir(obj):
        if name.startswith("_") or name in DOTNET_BASE:
            continue
        if keyword and keyword.lower() not in name.lower():
            continue
        result.append(name)
    return result


def doc_of(obj, label):
    try:
        print "  %s 시그니처:" % label
        print "   ", clean(obj.__doc__)
    except Exception, e:
        print "  %s 시그니처 확인 실패: %s" % (label, clean(str(e)))


table = Document.ActiveDataTableReference
print "기준 테이블:", clean(table.Name), "| 행", table.RowCount


# ---------------------------------------------------------------
print ""
print "=== 1. DataSelection — 예제 10의 열쇠 ==="
try:
    print "[OK] DataSelection 존재:", hasattr(data, "DataSelection")
    doc_of(data.DataSelection, "DataSelection 생성자")
    print "  멤버:", clean(", ".join(members(data.DataSelection)))
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "  --- RowSelection 도 함께 확인 ---"
try:
    doc_of(RowSelection, "RowSelection 생성자")
except Exception, e:
    print "  [NO]", clean(str(e))

print ""
print "  --- ColumnSelection 이 있는가 ---"
print "  ColumnSelection 존재:", hasattr(data, "ColumnSelection")
if hasattr(data, "ColumnSelection"):
    doc_of(data.ColumnSelection, "ColumnSelection 생성자")


# ---------------------------------------------------------------
print ""
print "=== 2. DataSelection 을 실제로 만들어 본다 ==="

# 마킹된 행, 없으면 앞의 5행
rows = Document.ActiveMarkingSelectionReference.GetSelection(table).AsIndexSet()
if rows.Count == 0:
    rows = IndexSet(table.RowCount, False)
    added = 0
    for i in range(table.RowCount):
        if added >= 5:
            break
        rows[i] = True
        added += 1
    print "  마킹이 없어 앞의", rows.Count, "행으로 시험"
else:
    print "  마킹된", rows.Count, "행으로 시험"

selection = None
rowSelection = RowSelection(rows)
print "[OK] RowSelection 생성:", clean(rowSelection)

# 가능한 형태를 순서대로 시도한다
attempts = [
    ("DataSelection(rowSelection)", lambda: data.DataSelection(rowSelection)),
    ("DataSelection(table, rowSelection)", lambda: data.DataSelection(table, rowSelection)),
    ("DataSelection(rows)", lambda: data.DataSelection(rows)),
]
for label, fn in attempts:
    try:
        selection = fn()
        print "[OK]", label, "->", clean(selection)
        break
    except Exception, e:
        print "[NO]", label, "->", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 3. DataTableDataSource(table, selection) 생성 ==="
dataSource = None
if selection is None:
    print "[SKIP] DataSelection 을 만들지 못해 건너뜁니다"
else:
    try:
        dataSource = imp.DataTableDataSource(table, selection)
        print "[OK] DataTableDataSource(table, selection) 생성 성공"
    except Exception, e:
        print "[NO]", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 4. 내보내기 대안 경로 확인 (예제 9) ==="

print "  --- DataWriterFactory ---"
try:
    import Spotfire.Dxp.Data.Export as exp
    print "  멤버:", clean(", ".join(members(exp.DataWriterFactory)))
    doc_of(exp.DataWriterFactory, "DataWriterFactory")
except Exception, e:
    print "  [NO]", clean(str(e))

print ""
print "  --- TablePlot.ExportText / ExportData ---"
from Spotfire.Dxp.Application.Visuals import TablePlot
found = False
for visual in Document.ActivePageReference.Visuals:
    try:
        plot = visual.As[TablePlot]()
        if plot is None:
            continue
        found = True
        print "  대상:", clean(visual.Title)
        print "  ExportDataEnabled 값:", plot.ExportDataEnabled
        doc_of(plot.ExportText, "ExportText")
        doc_of(plot.ExportData, "ExportData")
        break
    except:
        pass
if not found:
    print "  [SKIP] 이 페이지에 표(Table) 시각화가 없습니다"

print ""
print "  --- DataTable.ExportDataToLibrary ---"
doc_of(table.ExportDataToLibrary, "ExportDataToLibrary")

print ""
print "  --- CreateDataWriter 가 None 인 이유 단서 ---"
# 라이선스로 막혀 있으면 관련 기능도 함께 막혀 있을 가능성이 높다
try:
    from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
    identifier = DataWriterTypeIdentifiers.SbdfDataWriter
    print "  식별자 타입:", clean(type(identifier))
    print "  식별자 값:", clean(identifier)
    writer = Document.Data.CreateDataWriter(identifier)
    print "  반환:", clean(type(writer))
except Exception, e:
    print "  [NO]", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 5. 실제 왕복 — 마킹 행만 새 테이블로 (예제 10 최종 확인) ==="

if not RUN_ROUNDTRIP:
    print "[SKIP] RUN_ROUNDTRIP = False"
elif dataSource is None:
    print "[SKIP] 데이터 원본을 만들지 못해 건너뜁니다"
else:
    try:
        if Document.Data.Tables.Contains(TEMP_TABLE):
            Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])

        newTable = Document.Data.Tables.Add(TEMP_TABLE, dataSource)
        print "[OK] Tables.Add 성공"
        print "     새 테이블 행 수:", newTable.RowCount
        print "     넘긴 행 수:", rows.Count
        print "     일치 여부:", (newTable.RowCount == rows.Count)
        if newTable.RowCount != rows.Count:
            print "     -> 행 부분집합이 적용되지 않았습니다 (전체 복사됨)"
    except Exception, e:
        print "[NO] 왕복 실패 ->", clean(str(e))
    finally:
        try:
            if Document.Data.Tables.Contains(TEMP_TABLE):
                Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])
                print "[OK] 임시 테이블 삭제 완료"
        except Exception, e:
            print "[NO] 삭제 실패 - '" + TEMP_TABLE + "' 을 직접 지워 주세요:", clean(str(e))
