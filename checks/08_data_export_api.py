# -*- coding: utf-8 -*-
# 테스트 8 — 데이터 내보내기 API 정확한 사용법 찾기 (예제 9, 10)
#
# 배경:
#   4차 결과에서 다음이 나왔습니다.
#
#     writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.SbdfDataWriter)
#     writer.Write(...)   ->  'NoneType' object has no attribute 'Write'
#
#   호출 자체는 예외 없이 지나가는데 반환값이 None 입니다.
#   교안 예제 9(데이터 내보내기)와 예제 10(마킹 스냅샷)이 모두 이 API를 쓰므로
#   올바른 형태를 찾아야 합니다.
#
# 위험도: 없음 (전부 조회. 파일도 쓰지 않고 문서도 바꾸지 않음)
# 실행:   붙여넣고 [실행(Execute)] -> 출력 전체 복사

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from Spotfire.Dxp.Data import IndexSet
from System.IO import MemoryStream

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


table = Document.ActiveDataTableReference
columnNames = []
for column in table.Columns:
    columnNames.append(column.Name)

rows = IndexSet(table.RowCount, False)
added = 0
for i in range(table.RowCount):
    if added >= 5:
        break
    rows[i] = True
    added += 1

print "기준 테이블:", clean(table.Name), "| 컬럼", len(columnNames), "개 | 시험 행", rows.Count, "개"


# ---------------------------------------------------------------
print ""
print "=== 1. Document.Data 는 무엇인가 ==="
print "  타입:", clean(type(Document.Data))
print "  Create/Writer/Export 관련 멤버:"
for name in members(Document.Data):
    low = name.lower()
    if "create" in low or "writer" in low or "export" in low:
        print "     -", name


# ---------------------------------------------------------------
print ""
print "=== 2. CreateDataWriter 의 반환값 정밀 확인 ==="
try:
    method = Document.Data.CreateDataWriter
    print "[OK] 메서드 객체 존재:", clean(method)
    try:
        print "  오버로드:", clean(method.Overloads)
    except Exception, e:
        print "  오버로드 정보 없음:", clean(str(e))
except Exception, e:
    print "[NO] CreateDataWriter 접근 불가:", clean(str(e))

for name in ["SbdfDataWriter", "StdfDataWriter", "ExcelXlsDataWriter",
             "SpreadsheetDataCsvUtf8Writer"]:
    try:
        identifier = getattr(DataWriterTypeIdentifiers, name)
        writer = Document.Data.CreateDataWriter(identifier)
        print "  %-30s -> 반환: %s | None 인가: %s" % (
            name, clean(type(writer)), writer is None)
        if writer is not None:
            print "      Write 존재:", hasattr(writer, "Write"), \
                  "| 멤버:", clean(", ".join(members(writer)))
    except Exception, e:
        print "  %-30s -> 예외: %s" % (name, clean(str(e)))


# ---------------------------------------------------------------
print ""
print "=== 3. DataManager 서비스로 다시 시도 ==="
try:
    from Spotfire.Dxp.Data import DataManager
    manager = Application.GetService[DataManager]()
    print "[OK] DataManager 서비스 획득:", clean(type(manager))
    print "  Document.Data 와 같은 객체인가:", (manager is Document.Data)
    try:
        writer = manager.CreateDataWriter(DataWriterTypeIdentifiers.SbdfDataWriter)
        print "  CreateDataWriter 반환:", clean(type(writer)), "| None 인가:", (writer is None)
    except Exception, e:
        print "  CreateDataWriter 예외:", clean(str(e))
except Exception, e:
    print "[NO]", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 4. Spotfire.Dxp.Data.Export 에 무엇이 있나 ==="
try:
    import Spotfire.Dxp.Data.Export as exp
    for name in members(exp):
        print "   -", name
except Exception, e:
    print "[NO]", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 5. DataWriter 를 직접 만들 수 있는가 ==="
try:
    from Spotfire.Dxp.Data.Export import DataWriter
    print "[OK] DataWriter import 성공"
    print "  정적 멤버:", clean(", ".join(members(DataWriter)))
except Exception, e:
    print "[NO] DataWriter import:", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 6. 시각화를 통한 내보내기 (대안 경로) ==="
# TablePlot 은 자체 ExportText / ExportData 를 가지고 있다
from Spotfire.Dxp.Application.Visuals import VisualContent, TablePlot, CrossTablePlot

found = False
for visual in Document.ActivePageReference.Visuals:
    for typeName, typeClass in [("TablePlot", TablePlot), ("CrossTablePlot", CrossTablePlot)]:
        try:
            plot = visual.As[typeClass]()
            if plot is None:
                continue
            found = True
            print "  %s (%s):" % (clean(visual.Title), typeName)
            print "     ExportText 존재:", hasattr(plot, "ExportText")
            print "     ExportData 존재:", hasattr(plot, "ExportData")
            print "     내보내기 관련 멤버:", clean(", ".join(members(plot, "export")))
        except:
            pass
if not found:
    print "  [SKIP] 이 페이지에 표/교차 표 시각화가 없습니다"
    print "         표가 있는 페이지에서 다시 실행하면 확인됩니다"


# ---------------------------------------------------------------
print ""
print "=== 7. DataTableDataSource 로 부분집합을 만들 수 있는가 (예제 10 대안) ==="
try:
    import Spotfire.Dxp.Data.Import as imp
    source = imp.DataTableDataSource(table)
    print "[OK] DataTableDataSource(table) 생성"
    print "  멤버:", clean(", ".join(members(source)))
    try:
        print "  생성자 오버로드:", clean(imp.DataTableDataSource.__doc__)
    except Exception, e:
        print "  생성자 정보 없음:", clean(str(e))
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 8. 데이터 테이블에 내보내기/복제 메서드가 있는가 ==="
print "  table 의 export/save/copy 관련 멤버:"
for name in members(table):
    low = name.lower()
    if "export" in low or "save" in low or "copy" in low or "add" in low:
        print "     -", name
