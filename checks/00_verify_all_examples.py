# -*- coding: utf-8 -*-
# 예제 21종 사전 검증 하네스
#
# 목적:
#   예제를 하나씩 실제로 돌리지 않고도, 각 예제가 쓰는 API가 이 환경에 존재하고
#   동작하는지를 한 번에 확인한다.
#
# 위험도: 낮음. 다음 원칙으로 만들었습니다.
#   - 읽기: 그대로 수행
#   - 쓰기: "현재 값을 읽어서 같은 값을 다시 쓰는" 방식으로 setter 만 확인
#           (값이 실제로 바뀌지 않음)
#   - 파괴적 동작(삭제, 테이블 교체, 페이지 생성, 파일 쓰기): 호출하지 않고
#           메서드 존재 여부만 확인 -> 결과에 [SKIP] 으로 표시
#
#   그래도 만약을 위해 사본에서 실행하시길 권합니다.
#
# 실행:
#   여러 종류의 시각화(막대/선/산점도/표/교차표/텍스트영역)가 섞인 페이지를
#   활성 페이지로 두고 실행하면 확인 범위가 넓어집니다.
#   출력 전체를 복사해 주시면 됩니다.

OK, NO, SKIP = "[OK]", "[NO]", "[SKIP]"

results = []          # (예제번호, 제목, [(수준, 메시지), ...])
current = None


# 모든 .NET 객체가 갖는 기본 메서드 — 목록에서 제외한다
DOTNET_BASE = ["Equals", "GetHashCode", "GetType", "MemberwiseClone",
               "ReferenceEquals", "ToString"]


def real_members(obj):
    """.NET 기본 메서드를 뺀 실제 멤버 목록"""
    result = []
    for name in dir(obj):
        if name.startswith("_") or name in DOTNET_BASE:
            continue
        result.append(name)
    return result


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


def note(level, message):
    current.append((level, message))


def attempt(label, fn):
    """읽기 동작을 시도하고 결과를 기록한다."""
    try:
        value = fn()
        note(OK, "%s = %s" % (label, clean(value)))
        return value
    except Exception, e:
        note(NO, "%s -> %s" % (label, clean(str(e))))
        return None


def imported(label, ok, error=None):
    if ok:
        note(OK, "import %s" % label)
    else:
        note(NO, "import %s -> %s" % (label, clean(str(error))))
    return ok


def has(label, obj, name):
    if obj is None:
        note(SKIP, "%s (대상 없음)" % label)
        return False
    if hasattr(obj, name):
        note(OK, "%s.%s 존재" % (label, name))
        return True
    note(NO, "%s.%s 없음" % (label, name))
    return False


def writable(label, obj, name):
    """현재 값을 다시 써서 setter 만 확인한다. 값은 바뀌지 않는다."""
    if obj is None:
        note(SKIP, "%s (대상 없음)" % label)
        return False
    try:
        value = getattr(obj, name)
    except Exception, e:
        note(NO, "%s 읽기 실패 -> %s" % (label, clean(str(e))))
        return False
    try:
        setattr(obj, name, value)
        note(OK, "%s 읽기/쓰기 가능 (현재값 유지)" % label)
        return True
    except Exception, e:
        note(NO, "%s 쓰기 실패 -> %s" % (label, clean(str(e))))
        return False


# ---------------------------------------------------------------
# 공통 대상 수집
# ---------------------------------------------------------------
from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

page = Document.ActivePageReference
allVisuals = []
contents = []          # (visual, vc)

for visual in page.Visuals:
    allVisuals.append(visual)
    try:
        contents.append((visual, visual.As[VisualContent]()))
    except:
        pass


def first_with(pathName):
    """지정한 속성을 가진 첫 시각화의 VisualContent 를 돌려준다."""
    for visual, vc in contents:
        try:
            getattr(vc, pathName)
            return vc
        except:
            continue
    return None


table = None
if Document.Data.Tables.Count > 0:
    table = Document.ActiveDataTableReference


def start(number, title):
    global current
    current = []
    results.append((number, title, current))


# ===============================================================
# 예제별 검증
# ===============================================================

start(1, u"문서 전체 시각화 인벤토리")
note(OK, "VisualContent 캐스팅 성공 %d / 전체 시각화 %d" % (len(contents), len(allVisuals)))
if contents:
    attempt("TypeId.Name", lambda: contents[0][0].TypeId.Name)
    attempt("Data.DataTableReference.Name", lambda: contents[0][1].Data.DataTableReference.Name)
attempt("Document.Pages.Count", lambda: Document.Pages.Count)
try:
    Document.Properties["ScriptLog"] = Document.Properties["ScriptLog"]
    note(OK, "Document.Properties['ScriptLog'] 읽기/쓰기 가능")
except Exception, e:
    note(NO, "Document.Properties['ScriptLog'] -> %s (문서 속성을 만들어야 함)" % clean(str(e)))

start(2, u"데이터 제한 표현식 일괄 적용")
vc = first_with("Data")
writable("Data.WhereClauseExpression", (vc.Data if vc else None), "WhereClauseExpression")

start(3, u"축 표현식 동시 전환")
for axisName in ["YAxis", "MeasureAxis", "SectorSizeAxis", "SizeAxis"]:
    target = first_with(axisName)
    if target is None:
        note(SKIP, "%s 를 가진 시각화가 이 페이지에 없음" % axisName)
    else:
        writable("%s.Expression" % axisName, getattr(target, axisName), "Expression")

start(4, u"범례·제목·서식 일괄 통일")
legendVc = first_with("Legend")
writable("Legend.Visible", (legendVc.Legend if legendVc else None), "Visible")
if allVisuals:
    writable("visual.Title", allVisuals[0], "Title")
markerVc = first_with("MarkerSize")
if markerVc is None:
    note(SKIP, "MarkerSize 를 가진 시각화(산점도) 없음")
else:
    writable("MarkerSize", markerVc, "MarkerSize")

start(5, u"데이터 테이블 일괄 교체")
if vc is None:
    note(SKIP, "대상 시각화 없음")
else:
    writable("Data.DataTableReference", vc.Data, "DataTableReference")
note(SKIP, "실제 교체는 파괴적이라 수행하지 않음")

start(6, u"줌·축 범위 초기화")
try:
    from Spotfire.Dxp.Application.Visuals import AxisRange
    imported("AxisRange", True)
    attempt("AxisRange.DefaultRange", lambda: AxisRange.DefaultRange)
except Exception, e:
    imported("AxisRange", False, e)
zoomVc = first_with("XAxis")
if zoomVc is None:
    note(SKIP, "XAxis 를 가진 시각화 없음")
else:
    writable("XAxis.ZoomRange", zoomVc.XAxis, "ZoomRange")

start(7, u"축 범위 동시 고정")
rangeVc = first_with("YAxis")
if rangeVc is None:
    note(SKIP, "YAxis 를 가진 시각화 없음")
else:
    writable("YAxis.Range", rangeVc.YAxis, "Range")
try:
    from Spotfire.Dxp.Application.Visuals import AxisRange
    attempt("AxisRange(0, 100) 생성", lambda: AxisRange(0, 100))
except Exception, e:
    note(NO, "AxisRange(0,100) -> %s" % clean(str(e)))
if allVisuals:
    attempt("str(TypeId) 문자열 비교용", lambda: str(allVisuals[0].TypeId))

start(8, u"시각화 PNG 일괄 내보내기")
drawing = False
try:
    import clr
    clr.AddReference("System.Drawing")
    from System.Drawing import Bitmap, Graphics, Rectangle
    drawing = True
    note(OK, "System.Drawing 사용 가능")
except Exception, e:
    note(NO, "System.Drawing -> %s" % clean(str(e)))
if drawing:
    rendered, failed = [], []
    for visual, content in contents:
        try:
            bitmap = Bitmap(320, 240)
            graphics = Graphics.FromImage(bitmap)
            content.Render(graphics, Rectangle(0, 0, 320, 240))
            graphics.Dispose()
            bitmap.Dispose()
            rendered.append(visual.Title)
        except Exception, e:
            failed.append("%s (%s)" % (visual.Title, clean(str(e))[:40]))
    note(OK, "Render 성공 %d개: %s" % (len(rendered), clean(", ".join(rendered))))
    if failed:
        note(NO, "Render 실패 %d개: %s" % (len(failed), clean(", ".join(failed))))
    if allVisuals:
        note(OK, "RenderSync 존재: %s / RenderAsync 존재: %s" % (
            hasattr(allVisuals[0], "RenderSync"), hasattr(allVisuals[0], "RenderAsync")))
note(SKIP, "실제 파일 저장은 수행하지 않음")

start(9, u"데이터 테이블 파일 내보내기")
try:
    from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
    names = real_members(DataWriterTypeIdentifiers)
    note(OK, "DataWriterTypeIdentifiers: %s" % clean(", ".join(names)))
    for name in names:
        try:
            writer = Document.Data.CreateDataWriter(getattr(DataWriterTypeIdentifiers, name))
            # 반환값을 반드시 확인한다. 예외 없이 None 이 오는 경우가 있다
            if writer is None:
                note(NO, "CreateDataWriter(%s) -> None 반환 (Write 호출 불가)" % name)
            elif not hasattr(writer, "Write"):
                note(NO, "CreateDataWriter(%s) -> Write 메서드 없음" % name)
            else:
                note(OK, "CreateDataWriter(%s) -> 사용 가능" % name)
        except Exception, e:
            note(NO, "CreateDataWriter(%s) -> %s" % (name, clean(str(e))[:50]))
except Exception, e:
    note(NO, "DataWriterTypeIdentifiers -> %s" % clean(str(e)))
if table is not None:
    attempt("필터 통과 행 수", lambda:
            Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet().Count)
note(SKIP, "실제 파일 쓰기는 수행하지 않음")

start(10, u"마킹 행 스냅샷 (StdfDataSource)")
try:
    from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
    note(OK, "StdfDataWriter 존재: %s" % hasattr(DataWriterTypeIdentifiers, "StdfDataWriter"))
except Exception, e:
    note(NO, clean(str(e)))
try:
    import Spotfire.Dxp.Data.Import as imp
    sources = [n for n in dir(imp) if "DataSource" in n]
    note(OK, "Data.Import 의 DataSource 목록: %s" % clean(", ".join(sources)))
    note(OK if "StdfDataSource" in sources else NO,
         "StdfDataSource 존재 여부: %s" % ("StdfDataSource" in sources))
except Exception, e:
    note(NO, "Data.Import -> %s" % clean(str(e)))
try:
    from System.IO import MemoryStream, SeekOrigin
    imported("System.IO.MemoryStream / SeekOrigin", True)
except Exception, e:
    imported("System.IO.MemoryStream", False, e)
has("Document.Data.Tables", Document.Data.Tables, "Contains")
has("Document.Data.Tables", Document.Data.Tables, "Add")
if table is not None:
    has("DataTable", table, "ReplaceData")
note(SKIP, "실제 테이블 생성은 수행하지 않음")

start(11, u"마킹 결과를 문서 속성으로")
attempt("ActiveMarkingSelectionReference.Name",
        lambda: Document.ActiveMarkingSelectionReference.Name)
if table is not None:
    attempt("마킹된 행 수", lambda:
            Document.ActiveMarkingSelectionReference.GetSelection(table).AsIndexSet().Count)
    try:
        from Spotfire.Dxp.Data import DataValueCursor
        cursor = DataValueCursor.CreateFormatted(table.Columns[0])
        note(OK, "DataValueCursor.CreateFormatted 생성 성공")
    except Exception, e:
        note(NO, "DataValueCursor -> %s" % clean(str(e)))
try:
    from System.Collections.Generic import List
    items = List[str]()
    items.Add("a")
    note(OK, "List[str] 사용 가능 (변형 코드용)")
except Exception, e:
    note(NO, "List[str] -> %s" % clean(str(e)))

start(12, u"키 컬럼으로 마킹 전파")
try:
    from Spotfire.Dxp.Data import IndexSet, RowSelection
    if table is not None:
        indexSet = IndexSet(table.RowCount, False)
        selection = RowSelection(indexSet)
        note(OK, "IndexSet / RowSelection 생성 성공")
        note(OK, "IndexSet.Add 존재: %s (없는 것이 정상)" % hasattr(indexSet, "Add"))
        try:
            indexSet[0] = True
            indexSet[0] = False
            note(OK, "IndexSet[i] = True 인덱서로 설정 가능")
        except Exception, e:
            note(NO, "IndexSet[i] = True -> %s" % clean(str(e)))
        note(OK, "IndexSet 실제 멤버: %s" % clean(", ".join(real_members(indexSet))))
    marking = Document.ActiveMarkingSelectionReference
    note(OK, "marking.SetSelection 존재: %s" % hasattr(marking, "SetSelection"))
    note(SKIP, "실제 마킹 변경은 수행하지 않음")
except Exception, e:
    note(NO, clean(str(e)))

start(13, u"데이터 테이블 일괄 새로고침")
for dataTable in Document.Data.Tables:
    try:
        note(OK, "%s | IsRefreshable=%s NeedsRefresh=%s Refresh존재=%s" % (
            clean(dataTable.Name), dataTable.IsRefreshable,
            dataTable.NeedsRefresh, hasattr(dataTable, "Refresh")))
    except Exception, e:
        note(NO, "%s -> %s" % (clean(dataTable.Name), clean(str(e))))
try:
    from Spotfire.Dxp.Framework.ApplicationModel import NotificationService
    ns = Application.GetService[NotificationService]()
    methods = [n for n in dir(ns) if "Notification" in n]
    note(OK, "NotificationService 메서드: %s" % clean(", ".join(methods)))
except Exception, e:
    note(NO, "NotificationService -> %s" % clean(str(e)))
note(SKIP, "실제 Refresh 는 수행하지 않음")

start(14, u"대시보드 전체 상태 초기화")
count = 0
for scheme in Document.FilteringSchemes:
    count += 1
    if count == 1:
        note(OK, "FilteringScheme.ResetAllFilters 존재: %s" % hasattr(scheme, "ResetAllFilters"))
note(OK, "필터링 스킴 개수: %d" % count)
markingCount = 0
for marking in Document.Data.Markings:
    markingCount += 1
note(OK, "마킹 개수: %d" % markingCount)
note(SKIP, "실제 초기화는 수행하지 않음")

start(15, u"문서 속성으로 페이지 표시/숨김")
writable("Page.Visible", Document.Pages[0], "Visible")
try:
    from System.Threading import Thread
    note(OK, "현재 사용자: %s" % clean(Thread.CurrentPrincipal.Identity.Name))
except Exception, e:
    note(NO, "Thread.CurrentPrincipal -> %s" % clean(str(e)))

start(16, u"역할별 필터 패널 구성")
try:
    panel = page.FilterPanel
    note(OK, "FilterPanel.Visible = %s" % panel.Visible)
    groups = 0
    handles = 0
    firstHandle = None
    for group in panel.TableGroups:
        groups += 1
        note(OK, "TableGroup: %s | Expanded 존재=%s | SubGroups 존재=%s" % (
            clean(group.FilterCollectionReference.DataTableReference.Name),
            hasattr(group, "Expanded"), hasattr(group, "SubGroups")))
        for handle in group.FilterHandles:
            handles += 1
            if firstHandle is None:
                firstHandle = handle
    note(OK, "테이블 그룹 %d개 / 필터 핸들 %d개" % (groups, handles))
    if firstHandle is not None:
        note(OK, "필터 이름 예: %s | TypeId: %s | Modified 존재: %s" % (
            clean(firstHandle.FilterReference.Name),
            clean(firstHandle.FilterReference.TypeId),
            hasattr(firstHandle.FilterReference, "Modified")))
        writable("FilterHandle.Visible", firstHandle, "Visible")
    note(OK, "InteractiveSearchPattern 존재: %s" % hasattr(panel, "InteractiveSearchPattern"))
except Exception, e:
    note(NO, clean(str(e)))

start(17, u"시각화 유형 일괄 토글")
if allVisuals:
    writable("visual.TypeId (같은 값 재지정)", allVisuals[0], "TypeId")
    typeNames = real_members(VisualTypeIdentifiers)
    note(OK, "VisualTypeIdentifiers %d종: %s" % (len(typeNames), clean(", ".join(typeNames))))
else:
    note(SKIP, "시각화 없음")

start(18, u"원하는 컬럼 필터만 초기화")
try:
    scheme = None
    for s in Document.FilteringSchemes:
        scheme = s
        break
    dataTable = None
    for dt in Document.Data.Tables:
        dataTable = dt
        break
    column = dataTable.Columns[0]
    columnFilter = scheme[dataTable][column]
    note(OK, "scheme[table][column] 인덱싱 성공: %s" % clean(columnFilter))
    note(OK, "Reset 존재: %s" % hasattr(columnFilter, "Reset"))
    note(SKIP, "실제 Reset 은 수행하지 않음")
except Exception, e:
    note(NO, "scheme[table][column] -> %s" % clean(str(e)))

start(19, u"마킹 값별 시각화 자동 생성")
has("Document.Pages", Document.Pages, "AddNew")
has("Document.Pages", Document.Pages, "Remove")
has("page.Visuals", page.Visuals, "AddNew")
has("page.Visuals", page.Visuals, "Remove")
try:
    from Spotfire.Dxp.Application.Visuals import BarChart, LineChart
    imported("BarChart / LineChart", True)
except Exception, e:
    imported("BarChart", False, e)
note(SKIP, "실제 페이지/시각화 생성은 06_page_and_layout.py 에서 확인")

start(20, u"표현식 전수 검사")
try:
    from Spotfire.Dxp.Data.Import import TextFileDataSource, TextDataReaderSettings
    settings = TextDataReaderSettings()
    note(OK, "TextDataReaderSettings 생성 성공")
    for name in ["Separator", "AddColumnNameRow", "SetDataType"]:
        note(OK if hasattr(settings, name) else NO, "settings.%s 존재: %s" % (
            name, hasattr(settings, name)))
except Exception, e:
    note(NO, "TextDataReaderSettings -> %s" % clean(str(e)))
try:
    from System.IO import StreamWriter
    imported("System.IO.StreamWriter", True)
except Exception, e:
    imported("System.IO.StreamWriter", False, e)
try:
    from System.Text import Encoding
    imported("System.Text.Encoding", True)
except Exception, e:
    imported("System.Text.Encoding", False, e)
trellisVc = first_with("Trellis")
if trellisVc is None:
    note(SKIP, "Trellis 를 가진 시각화 없음")
else:
    attempt("Trellis.PanelAxis.Expression", lambda: trellisVc.Trellis.PanelAxis.Expression)
try:
    from Spotfire.Dxp.Data import CalculatedColumn
    note(OK, "CalculatedColumn import 성공 (계산된 컬럼 감사용)")
except Exception, e:
    note(NO, "CalculatedColumn -> %s" % clean(str(e)))

start(21, u"산점도 매트릭스 자동 생성")
try:
    from Spotfire.Dxp.Application.Layout import LayoutDefinition
    layout = LayoutDefinition()
    note(OK, "LayoutDefinition 생성 성공")
    for name in ["BeginSideBySideSection", "BeginStackedSection", "Add", "EndSection"]:
        note(OK if hasattr(layout, name) else NO, "layout.%s 존재: %s" % (
            name, hasattr(layout, name)))
    note(OK if hasattr(page, "ApplyLayout") else NO,
         "page.ApplyLayout 존재: %s" % hasattr(page, "ApplyLayout"))
except Exception, e:
    note(NO, "LayoutDefinition -> %s" % clean(str(e)))
try:
    from Spotfire.Dxp.Application.Visuals import ScatterPlot
    imported("ScatterPlot", True)
except Exception, e:
    imported("ScatterPlot", False, e)
try:
    from Spotfire.Dxp.Data import DataPropertyClass
    props = Document.Data.Properties.GetProperties(DataPropertyClass.Document)
    names = []
    for prop in props:
        names.append(prop.Name)
    note(OK, "문서 속성 %d개: %s" % (len(names), clean(", ".join(names[:15]))))
except Exception, e:
    note(NO, "GetProperties -> %s" % clean(str(e)))


# ===============================================================
# 결과 출력
# ===============================================================
print "==============================================="
print " 예제 21종 API 사전 검증 결과"
print "==============================================="
print "활성 페이지:", clean(page.Title)
print "시각화:", len(allVisuals), "개 (VisualContent 캐스팅 가능", len(contents), "개)"
print "데이터 테이블:", Document.Data.Tables.Count, "개"
print ""

summary = []
for number, title, items in results:
    failures = 0
    skips = 0
    for level, message in items:
        if level == NO:
            failures += 1
        elif level == SKIP:
            skips += 1

    if failures == 0:
        verdict = "통과"
    elif failures == len(items):
        verdict = "실패"
    else:
        verdict = "일부실패"

    summary.append((number, title, verdict, failures, skips))

    print "-----------------------------------------------"
    print u"예제 %d. %s  ->  %s" % (number, title, verdict)
    for level, message in items:
        print "   ", level, message

print ""
print "==============================================="
print " 요약"
print "==============================================="
for number, title, verdict, failures, skips in summary:
    mark = "OK " if verdict == u"통과" else ("!! " if verdict == u"일부실패" else "XX ")
    print u"%s예제 %2d  %-28s %s (실패 %d, 미수행 %d)" % (
        mark, number, title, verdict, failures, skips)

failed = 0
for number, title, verdict, failures, skips in summary:
    if verdict != u"통과":
        failed += 1
print ""
print u"통과 %d / 전체 %d" % (len(summary) - failed, len(summary))
print u"(미수행 = 파괴적이라 일부러 호출하지 않은 항목. 실패가 아닙니다)"
