# -*- coding: utf-8 -*-
# 테스트 10 — 예제 9·10 최종 확정
#
# 6차에서 알아낸 것:
#   - DataSelection 은 추상 클래스라 직접 만들 수 없다
#     -> 하지만 마킹(DataMarkingSelection)과 필터링(DataFilteringSelection)이
#        DataSelection 의 구체 클래스일 가능성이 높다.
#        그렇다면 DataTableDataSource(table, 마킹) 이 바로 답이다.
#   - ExportData(self: TablePlot, typeIdentifier: TypeIdentifier, stream: Stream)
#     -> CreateDataWriter 없이 바로 내보낼 수 있다. 예제 9의 답.
#   - DataWriterFactory 에 IsLicensed 와 requiredLicenses 가 있다
#     -> CreateDataWriter 가 None 인 이유를 여기서 확인할 수 있다.
#
# 위험도: 낮음
#   - 1~3단계는 조회 + 메모리 내보내기 (파일 안 씀, 문서 안 바꿈)
#   - 4단계만 임시 테이블을 만들었다 지웁니다. RUN_ROUNDTRIP 로 끌 수 있습니다.

RUN_ROUNDTRIP = True
TEMP_TABLE = "__SNAPSHOT_TEST__"

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from System.IO import MemoryStream
import Spotfire.Dxp.Data as data
import Spotfire.Dxp.Data.Import as imp


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


table = Document.ActiveDataTableReference
marking = Document.ActiveMarkingSelectionReference
filtering = Document.ActiveFilteringSelectionReference

print "기준 테이블:", clean(table.Name), "| 행", table.RowCount


# ---------------------------------------------------------------
print ""
print "=== 1. 마킹/필터링이 DataSelection 인가 (예제 10의 답) ==="
print "  마킹 타입     :", clean(type(marking))
print "  필터링 타입   :", clean(type(filtering))
try:
    print "  마킹이 DataSelection 인가  :", isinstance(marking, data.DataSelection)
    print "  필터링이 DataSelection 인가:", isinstance(filtering, data.DataSelection)
except Exception, e:
    print "  isinstance 확인 실패:", clean(str(e))

print ""
print "  --- DataTableDataSource 에 넘겨 본다 ---"
candidates = [
    ("마킹", marking),
    ("필터링", filtering),
]
workingSource = None
workingLabel = None
for label, selection in candidates:
    try:
        source = imp.DataTableDataSource(table, selection)
        print "[OK] DataTableDataSource(table,", label + ") 생성 성공"
        if workingSource is None:
            workingSource = source
            workingLabel = label
    except Exception, e:
        print "[NO] DataTableDataSource(table,", label + ") ->", clean(str(e))

print ""
print "  --- UpdateBehavior 선택지 (스냅샷이냐 실시간 연동이냐) ---"
try:
    behavior = imp.DataTableDataSourceUpdateBehavior
    names = []
    for name in dir(behavior):
        if not name.startswith("_") and name not in [
                "Equals", "GetHashCode", "GetType", "MemberwiseClone",
                "ReferenceEquals", "ToString"]:
            names.append(name)
    print "  값 목록:", clean(", ".join(names))
except Exception, e:
    print "  [NO]", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 2. CreateDataWriter 가 None 인 이유 — 라이선스 확인 ==="
try:
    from Spotfire.Dxp.Data.Export import DataWriterFactory
    print "  DataWriterFactory 를 어떻게 얻는지 확인 중..."
    # 서비스로 등록되어 있는지 먼저 시도
    try:
        factories = Application.GetService[DataWriterFactory]()
        print "  GetService 결과:", clean(factories)
    except Exception, e:
        print "  GetService 불가:", clean(str(e))[:80]

    # 팩토리 목록을 얻는 다른 경로
    try:
        import Spotfire.Dxp.Framework.ApplicationModel as appmodel
        print "  ApplicationModel 에서 팩토리 관련:",
        found = []
        for name in dir(appmodel):
            if "Factory" in name or "Registry" in name:
                found.append(name)
        print clean(", ".join(found)) if found else "(없음)"
    except Exception, e:
        print "  [NO]", clean(str(e))[:80]
except Exception, e:
    print "[NO]", clean(str(e))


# ---------------------------------------------------------------
print ""
print "=== 3. TablePlot.ExportData 로 메모리에 내보내기 (예제 9의 답) ==="
from Spotfire.Dxp.Application.Visuals import TablePlot

plot = None
for visual in Document.ActivePageReference.Visuals:
    try:
        candidate = visual.As[TablePlot]()
        if candidate is not None:
            plot = candidate
            print "  대상 표:", clean(visual.Title)
            break
    except:
        pass

if plot is None:
    print "  [SKIP] 이 페이지에 표(Table) 시각화가 없습니다"
    print "         표가 있는 페이지에서 다시 실행하면 확인됩니다"
else:
    print "  ExportDataEnabled:", plot.ExportDataEnabled

    for name in ["SpreadsheetDataCsvUtf8Writer", "ExcelXlsxDataWriter", "SbdfDataWriter"]:
        try:
            stream = MemoryStream()
            plot.ExportData(getattr(DataWriterTypeIdentifiers, name), stream)
            print "[OK] ExportData(%s) -> %d 바이트" % (name, stream.Length)
            stream.Close()
        except Exception, e:
            print "[NO] ExportData(%s) -> %s" % (name, clean(str(e))[:90])

    # ExportText 도 메모리로
    try:
        from System.IO import StringWriter
        writer = StringWriter()
        plot.ExportText(writer)
        text = writer.ToString()
        writer.Close()
        print "[OK] ExportText -> %d 글자, 첫 줄: %s" % (
            len(text), clean(text.split("\n")[0][:70]))
    except Exception, e:
        print "[NO] ExportText ->", clean(str(e))[:90]


# ---------------------------------------------------------------
print ""
print "=== 4. 예제 10 최종 확인 — 마킹 행만 새 테이블로 ==="

markedCount = marking.GetSelection(table).AsIndexSet().Count
print "  현재 마킹된 행 수:", markedCount

if not RUN_ROUNDTRIP:
    print "[SKIP] RUN_ROUNDTRIP = False"
elif workingSource is None:
    print "[SKIP] 데이터 원본을 만들지 못했습니다"
elif markedCount == 0:
    print "[SKIP] 마킹된 행이 없습니다. 차트에서 몇 개 선택한 뒤 다시 실행하세요"
else:
    try:
        if Document.Data.Tables.Contains(TEMP_TABLE):
            Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])

        newTable = Document.Data.Tables.Add(TEMP_TABLE, workingSource)
        print "[OK] Tables.Add 성공 (사용:", workingLabel + ")"
        print "     새 테이블 행 수:", newTable.RowCount
        print "     마킹된 행 수  :", markedCount
        print "     일치 여부     :", (newTable.RowCount == markedCount)
        if newTable.RowCount != markedCount:
            print "     -> 부분집합이 적용되지 않고 전체가 복사된 것으로 보입니다"
    except Exception, e:
        print "[NO] 실패 ->", clean(str(e))
    finally:
        try:
            if Document.Data.Tables.Contains(TEMP_TABLE):
                Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])
                print "[OK] 임시 테이블 삭제 완료"
        except Exception, e:
            print "[NO] 삭제 실패 - '" + TEMP_TABLE + "' 을 직접 지워 주세요:", clean(str(e))
