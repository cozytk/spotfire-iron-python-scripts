# Spotfire API 지도와 코드 조각

필요한 부분만 찾아 쓰세요.

## 목차

- [객체 모델](#객체-모델)
- [페이지와 시각화](#페이지와-시각화)
- [시각화 속성](#시각화-속성)
- [데이터](#데이터)
- [마킹](#마킹)
- [필터](#필터)
- [문서 속성](#문서-속성)
- [레이아웃](#레이아웃)
- [내보내기](#내보내기)
- [알림](#알림)

## 객체 모델

```text
Document
├── Pages ─── Page ─── Visuals ─── Visual ─── As[VisualContent]()
│                                              ├── Data (DataTableReference, WhereClauseExpression, MarkingReference)
│                                              ├── XAxis / YAxis / ColorAxis (Expression, Range, ZoomRange)
│                                              ├── Legend (Visible)
│                                              └── Trellis (PanelAxis)
│             └── FilterPanel ─── TableGroups ─── FilterHandles ─── FilterReference
├── Data (DataManager)
│   ├── Tables ─── DataTable ─── Columns / RowCount / Select() / GetRows() / Refresh()
│   ├── Markings ─── DataMarkingSelection
│   └── Properties (문서·테이블·컬럼 속성 정의)
├── Properties (문서 속성 값)
├── FilteringSchemes
├── ActivePageReference
├── ActiveDataTableReference
├── ActiveMarkingSelectionReference
└── ActiveFilteringSelectionReference
```

## 페이지와 시각화

```python
from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

page = Document.ActivePageReference
Document.ActivePageReference = Document.Pages[0]

for page in Document.Pages:
    for visual in page.Visuals:
        vc = visual.As[VisualContent]()

newPage = Document.Pages.AddNew(u"제목")
Document.Pages.Remove(newPage)
page.Visible = False

# 유형 판별 — 두 방식 모두 가능
if visual.TypeId == VisualTypeIdentifiers.BarChart:
    pass
if str(visual.TypeId) == "TypeIdentifier:Spotfire.BarChart":
    pass
```

유형 식별자 전체(14.x 실측): `BarChart` `LineChart` `ScatterPlot` `ScatterPlot3D`
`PieChart` `CombinationChart` `WaterfallChart` `BoxPlot` `HeatMap` **`Treemap`**
`ParallelCoordinatePlot` `MapChart` `MapChart2` `Table` `CrossTable` `SummaryTable`
`GraphicalTable` `KpiChart` `KpiVisualization` `HtmlTextArea` `TextArea`
`SparklineMiniatureVisualization` `BulletGraphMiniatureVisualization`
`CalculatedValueMiniatureVisualization` `IconMiniatureVisualization`

## 시각화 속성

```python
vc = visual.As[VisualContent]()

vc.Data.DataTableReference = Document.Data.Tables[u"매출"]
vc.Data.WhereClauseExpression = "[Year] > 2020"       # 빈 문자열로 해제
vc.Data.MarkingReference = Document.ActiveMarkingSelectionReference

vc.XAxis.Expression = "[Region]"
vc.YAxis.Expression = "Sum([Revenue])"
vc.Legend.Visible = False
visual.Title = u"제목"

# 축 범위와 줌은 다른 속성이다
from Spotfire.Dxp.Application.Visuals import AxisRange
vc.YAxis.Range = AxisRange(0, 100)            # 눈금 고정
vc.YAxis.Range = AxisRange.DefaultRange       # 자동으로
vc.XAxis.ZoomRange = AxisRange.DefaultRange   # 줌 슬라이더 초기화

# 유형 고유 속성은 그 타입으로 캐스팅
from Spotfire.Dxp.Application.Visuals import ScatterPlot
scatter = visual.As[ScatterPlot]()
scatter.MarkerSize = scatter.MarkerSize + 1
```

## 데이터

```python
from Spotfire.Dxp.Data import DataValueCursor, IndexSet, RowSelection

table = Document.ActiveDataTableReference
table = Document.Data.Tables[u"매출"]          # 이름으로만. Tables[0] 은 실패
names = [c.Name for c in table.Columns]

# 값 읽기
cursor = DataValueCursor.CreateFormatted(table.Columns[u"지역"])
rows = IndexSet(table.RowCount, True)
for row in table.GetRows(rows, cursor):
    print row.Index, cursor.CurrentValue

# 고유값
values = set()
distinct = table.GetDistinctRows(None, cursor)
distinct.Reset()
while distinct.MoveNext():
    values.add(cursor.CurrentValue)

# 표현식으로 행 선택 (파이썬 순회보다 훨씬 빠름)
selection = table.Select("[Region] = 'East'")

# IndexSet — Add() 는 없다
picked = IndexSet(table.RowCount, False)
picked.AddIndex(5)
picked[7] = True
combined = IndexSet.And(setA, setB)

if table.IsRefreshable:
    table.Refresh()
```

## 마킹

```python
marking = Document.ActiveMarkingSelectionReference     # 이름 하드코딩 금지

marked = marking.GetSelection(table).AsIndexSet()
marking.SetSelection(table.Select("[Region] = 'East'"), table)
marking.SetSelection(RowSelection(IndexSet(table.RowCount, False)), table)   # 해제
```

## 필터

```python
import Spotfire.Dxp.Application.Filters as filters

# 모든 스킴 초기화 (기본 버튼은 현재 스킴만 처리한다)
for scheme in Document.FilteringSchemes:
    scheme.ResetAllFilters()

# 특정 컬럼의 필터만 초기화
for scheme in Document.FilteringSchemes:
    for dataTable in Document.Data.Tables:
        for column in dataTable.Columns:
            if column.Name in [u"지역", u"제품"]:
                try:
                    scheme[dataTable][column].Reset()
                except:
                    pass

# 필터 패널
panel = Document.ActivePageReference.FilterPanel
for group in panel.TableGroups:
    for handle in group.FilterHandles:
        print handle.FilterReference.Name, handle.Visible
        handle.Visible = True
```

필터 유형: `CheckBoxFilter` `ListBoxFilter` `RangeFilter` `ItemFilter`
`RadioButtonFilter` `TextFilter` `CheckBoxHierarchyFilter`

## 문서 속성

```python
value = Document.Properties["Name"]
Document.Properties["Name"] = u"값"

# 새로 만들기 (없으면 읽기/쓰기 모두 실패한다)
from Spotfire.Dxp.Data import DataProperty, DataType, DataPropertyClass

def exists(name):
    for prop in Document.Data.Properties.GetProperties(DataPropertyClass.Document):
        if prop.Name == name:
            return True
    return False

if not exists("ScriptLog"):
    prototype = DataProperty.CreateCustomPrototype(
        "ScriptLog", DataType.String, DataProperty.DefaultAttributes)
    Document.Data.Properties.AddProperty(DataPropertyClass.Document, prototype)
```

## 레이아웃

```python
from Spotfire.Dxp.Application.Layout import LayoutDefinition

layout = LayoutDefinition()
layout.BeginSideBySideSection()
layout.Add(visualA, 30.0)
layout.BeginStackedSection(70.0)
layout.Add(visualB, 50.0)
layout.Add(visualC, 50.0)
layout.EndSection()
layout.EndSection()
page.ApplyLayout(layout)
```

**함정**: `page.Visuals.AddNew[BarChart]()` 는 **콘텐츠**(`BarChart`)를 반환한다.
`layout.Add()` 에 넣을 `Visual` 컨테이너는 생성 후 제목으로 다시 찾아야 한다.

```python
def get_visual_by_title(page, title):
    for visual in page.Visuals:
        if visual.Title == title:
            return visual
    return None
```

## 내보내기

```python
# 표 시각화 → 탭 구분 텍스트 (가장 확실한 경로)
from Spotfire.Dxp.Application.Visuals import TablePlot
from System.IO import StreamWriter
from System.Text import Encoding

plot = vTable.As[TablePlot]()
if plot.ExportDataEnabled:
    writer = StreamWriter("C:/temp/out.txt", False, Encoding.UTF8)
    try:
        plot.ExportText(writer)
    finally:
        writer.Close()

# 마킹/필터 결과를 새 데이터 테이블로 (writer 불필요)
from Spotfire.Dxp.Data.Import import DataTableDataSource
source = DataTableDataSource(table, Document.ActiveMarkingSelectionReference)
Document.Data.Tables.Add(u"스냅샷", source)

# 시각화 → 이미지
import clr
clr.AddReference("System.Drawing")
from System.Drawing import Bitmap, Graphics, Rectangle

bitmap = Bitmap(1200, 800)
graphics = Graphics.FromImage(bitmap)
visual.As[VisualContent]().Render(graphics, Rectangle(0, 0, 1200, 800))
bitmap.Save("C:/temp/chart.png")
graphics.Dispose()
bitmap.Dispose()
```

## 알림

```python
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService

ns = Application.GetService[NotificationService]()
ns.AddInformationNotification(u"제목", u"설명", u"상세")
ns.AddWarningNotification(u"제목", u"설명", u"상세")
ns.AddErrorNotification(u"제목", u"설명", u"상세")
```
