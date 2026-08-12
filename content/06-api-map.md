# 6. Spotfire API 객체 모델

문법을 알아도 **"이 기능이 어느 객체에 매달려 있는지"** 를 모르면 코드를 못 씁니다.
이 장은 `Document`에서 출발해 아래로 내려가는 지도입니다. 8장 이후 예제는 전부 이 지도 위에서 움직입니다.

## 6.1 전체 구조

```text
Application  (AnalysisApplication)
└── Document  (Spotfire.Dxp.Application.Document)
    │
    ├── Pages ─────────────── 페이지 컬렉션
    │   └── Page
    │       ├── Title / Visible
    │       ├── Visuals ───── 시각화 컬렉션
    │       │   └── Visual
    │       │       ├── Title / TypeId
    │       │       └── As[VisualContent]()
    │       │           ├── Data ──── DataTableReference / MarkingReference
    │       │           │             WhereClauseExpression
    │       │           ├── XAxis / YAxis / ColorAxis ── Expression
    │       │           ├── Legend ── Visible / Items
    │       │           └── Trellis
    │       ├── FilterPanel ─ TableGroups → FilterHandles → FilterReference
    │       └── Panels ────── 세부 정보 패널, 협업 패널 등
    │
    ├── Data  (DataManager)
    │   ├── Tables ────────── DataTable
    │   │   ├── Columns ──── DataColumn (Name / DataType / Properties)
    │   │   ├── RowCount
    │   │   ├── Select() / GetRows() / GetDistinctRows()
    │   │   └── Refresh() / ReplaceData() / AddRows()
    │   ├── Markings ──────── DataMarkingSelection
    │   ├── Filterings
    │   └── Properties ───── 데이터/컬럼/문서 속성 정의
    │
    ├── Properties ────────── 문서 속성 값 (읽기/쓰기)
    ├── FilteringSchemes ──── 필터링 스킴 (필터 초기화의 열쇠)
    ├── ActivePageReference
    ├── ActiveDataTableReference
    ├── ActiveMarkingSelectionReference
    └── ActiveFilteringSelectionReference
```

## 6.2 문서와 페이지

```python
# 현재 활성 페이지
page = Document.ActivePageReference
print page.Title

# 페이지 이동
Document.ActivePageReference = Document.Pages[2]        # 인덱스는 0부터

# 이름으로 페이지 찾기
for p in Document.Pages:
    if p.Title == u"요약":
        Document.ActivePageReference = p
        break

# 페이지 숨기기 / 보이기
Document.Pages[3].Visible = False

# 페이지 추가 / 삭제
newPage = Document.Pages.AddNew(u"새 페이지")
Document.Pages.Remove(newPage)
```

## 6.3 시각화

`Visual`(껍데기)과 `VisualContent`(알맹이)의 구분이 핵심입니다 → [3.2 참조](05-dotnet-interop.html#52-ast)

```python
from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

for visual in Document.ActivePageReference.Visuals:
    # Visual 수준
    print visual.Title, visual.TypeId

    # VisualContent 수준
    vc = visual.As[VisualContent]()
    print vc.Data.DataTableReference.Name
```

### 주요 시각화 유형 식별자

아래는 Spotfire 14.x에서 `dir(VisualTypeIdentifiers)` 로 실제 확인한 전체 목록입니다.

```python
VisualTypeIdentifiers.BarChart
VisualTypeIdentifiers.LineChart
VisualTypeIdentifiers.ScatterPlot
VisualTypeIdentifiers.ScatterPlot3D
VisualTypeIdentifiers.PieChart
VisualTypeIdentifiers.CombinationChart
VisualTypeIdentifiers.WaterfallChart
VisualTypeIdentifiers.BoxPlot
VisualTypeIdentifiers.HeatMap
VisualTypeIdentifiers.Treemap             # TreemapChart 가 아님에 주의
VisualTypeIdentifiers.ParallelCoordinatePlot
VisualTypeIdentifiers.MapChart
VisualTypeIdentifiers.MapChart2
VisualTypeIdentifiers.Table
VisualTypeIdentifiers.CrossTable
VisualTypeIdentifiers.SummaryTable
VisualTypeIdentifiers.GraphicalTable
VisualTypeIdentifiers.KpiChart
VisualTypeIdentifiers.KpiVisualization
VisualTypeIdentifiers.HtmlTextArea        # 텍스트 영역
VisualTypeIdentifiers.TextArea

# 그래픽 테이블 안의 미니 시각화들
VisualTypeIdentifiers.SparklineMiniatureVisualization
VisualTypeIdentifiers.BulletGraphMiniatureVisualization
VisualTypeIdentifiers.CalculatedValueMiniatureVisualization
VisualTypeIdentifiers.IconMiniatureVisualization
```

!!! warning "이름을 추측하지 마세요"
    `Treemap` 을 `TreemapChart` 로 쓰면 `AttributeError` 가 납니다.
    확실하지 않으면 아래로 직접 확인하세요.

    ```python
    from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
    for name in dir(VisualTypeIdentifiers):
        if not name.startswith("_"):
            print name
    ```

### 시각화의 데이터 설정

```python
vc = visual.As[VisualContent]()

vc.Data.DataTableReference = Document.Data.Tables["Sales"]   # 데이터 테이블 지정
vc.Data.WhereClauseExpression = "[Year] > 2020"              # 데이터 제한 표현식
vc.Data.MarkingReference = Document.Data.Markings["Marking"] # 마킹 연결
vc.Data.LimitingMarkingsEmptyMessage = u"항목을 선택하세요"     # 마킹 대기 문구
```

### 축

```python
vc.XAxis.Expression = "[Region]"
vc.YAxis.Expression = "Sum([Revenue])"
vc.ColorAxis.Expression = "[Category]"

# 축 서식
vc.XAxis.ShowAxisSelector = False
vc.YAxis.Scale.ShowGridlines = True
```

시각화 유형마다 축 이름이 다릅니다.

| 유형 | 축 |
|------|-----|
| 막대/선/산점도 | `XAxis`, `YAxis`, `ColorAxis`, `SizeAxis`, `ShapeAxis` |
| 원형 차트 | `SectorSizeAxis`, `ColorAxis` |
| 교차 표 | `HorizontalAxis`, `VerticalAxis`, `MeasureAxis` |
| 히트 맵 | `XAxis`, `YAxis`, `CellValueAxis` |
| KPI 차트 | KPI 항목별 `ValueAxis` |

!!! tip "축이 없는 시각화를 만나면"
    표(`Table`)나 텍스트 영역에는 `XAxis`가 없습니다. 일괄 처리 루프에서는 반드시
    `try/except`로 감싸거나 `TypeId`로 걸러 내세요.

## 6.4 데이터 테이블과 컬럼

```python
tables = Document.Data.Tables

table = tables["Sales"]                       # 이름으로
table = Document.ActiveDataTableReference     # 현재 활성 테이블
print table.RowCount

for col in table.Columns:
    print col.Name, col.DataType

col = table.Columns["Revenue"]
print col.DataType.IsNumeric
```

### 값 읽기 — DataValueCursor

행 값을 읽는 표준 방법입니다. **커서를 만들고 → 행을 순회하며 → 현재 값을 읽습니다.**

```python
from Spotfire.Dxp.Data import DataValueCursor, IndexSet

table = Document.Data.Tables["Sales"]
cursor = DataValueCursor.CreateFormatted(table.Columns["Region"])

rows = IndexSet(table.RowCount, True)          # 전체 행
for row in table.GetRows(rows, cursor):
    print cursor.CurrentValue
```

커서를 여러 개 넘기면 여러 컬럼을 동시에 읽습니다.

```python
c1 = DataValueCursor.CreateFormatted(table.Columns["Region"])
c2 = DataValueCursor.Create[float](table.Columns["Revenue"])

for row in table.GetRows(rows, c1, c2):
    print c1.CurrentValue, c2.CurrentValue
```

### 고유값 읽기

```python
from Spotfire.Dxp.Data import DataValueCursor

cursor = DataValueCursor.CreateFormatted(table.Columns["Region"])
values = []
distinct = table.GetDistinctRows(None, cursor)     # None = 전체 행
distinct.Reset()
while distinct.MoveNext():
    values.append(cursor.CurrentValue)
print values
```

### IndexSet과 RowSelection

Spotfire에서 "어떤 행들"을 표현하는 두 타입입니다.

```python
from Spotfire.Dxp.Data import IndexSet, RowSelection

allRows = IndexSet(table.RowCount, True)      # 전부 선택된 상태
noRows = IndexSet(table.RowCount, False)      # 전부 해제된 상태
noRows.Add(5)                                 # 6번째 행만 추가

selection = RowSelection(noRows)              # 마킹 API에 넘길 형태
```

- **`IndexSet`**: 행 인덱스의 비트 집합. `And`, `Or`, `Not` 연산 가능
- **`RowSelection`**: 마킹/필터 API가 요구하는 래퍼

```python
combined = IndexSet.And(setA, setB)     # 교집합
```

### 표현식으로 행 선택

```python
selection = table.Select("[Region] = 'East' and [Revenue] > 1000")
```

## 6.5 마킹

```python
marking = Document.Data.Markings["Marking"]

# 마킹된 행 읽기
marked = marking.GetSelection(table).AsIndexSet()
print marked.Count

# 마킹 설정 (표현식으로)
selection = table.Select("[Region] = 'East'")
marking.SetSelection(selection, table)

# 마킹 해제
from Spotfire.Dxp.Data import IndexSet, RowSelection
marking.SetSelection(RowSelection(IndexSet(table.RowCount, False)), table)

# 현재 활성 마킹
activeMarking = Document.ActiveMarkingSelectionReference
```

## 6.6 필터와 필터링 스킴

**필터링 스킴(FilteringScheme)** 은 필터 설정 묶음입니다. 페이지마다 다른 스킴을 쓸 수 있고,
"모든 필터 초기화" 버튼은 **현재 스킴 하나만** 초기화합니다. 이것이 [예제 14](10-examples-ui.html)의 출발점입니다.

```python
# 모든 필터링 스킴 초기화
for scheme in Document.FilteringSchemes:
    scheme.ResetAllFilters()

# 현재 페이지의 필터 패널
filterPanel = Document.ActivePageReference.FilterPanel

for tableGroup in filterPanel.TableGroups:
    print tableGroup.FilterCollectionReference.DataTableReference.Name
    for fh in tableGroup.FilterHandles:
        print fh.FilterReference.Name, fh.Visible
        fh.Visible = True                 # 필터 표시/숨김
```

### 특정 필터 조작

```python
import Spotfire.Dxp.Application.Filters as filters
from Spotfire.Dxp.Application.Filters import FilterTypeIdentifiers

filterPanel = Document.ActivePageReference.FilterPanel
handle = filterPanel.TableGroups[0].GetFilter("Region")

if handle.FilterReference.TypeId == FilterTypeIdentifiers.CheckBoxFilter:
    cb = handle.FilterReference.As[filters.CheckBoxFilter]()
    cb.Reset()                    # 전체 선택
    cb.Uncheck("East")            # 특정 값 해제
    cb.Check("West")
    cb.IncludeEmpty = False

if handle.FilterReference.TypeId == FilterTypeIdentifiers.RangeFilter:
    rf = handle.FilterReference.As[filters.RangeFilter]()
    rf.Reset()
```

주요 필터 유형: `CheckBoxFilter`, `ListBoxFilter`, `RangeFilter`, `ItemFilter`,
`RadioButtonFilter`, `TextFilter`, `CheckBoxHierarchyFilter`

## 6.7 문서 속성

스크립트와 UI 사이의 **다리**입니다. 텍스트 영역의 속성 컨트롤(드롭다운, 입력 상자)이
문서 속성에 묶이고, 스크립트가 그 값을 읽거나 씁니다.

```python
# 읽기 / 쓰기
value = Document.Properties["SelectedRegion"]
Document.Properties["SelectedRegion"] = "East"
Document.Properties["ScriptLog"] = u"완료"
```

### 새 문서 속성 만들기

```python
from Spotfire.Dxp.Data import DataProperty, DataType, DataPropertyClass

name = "MyProperty"
if not Document.Data.Properties.Contains(DataPropertyClass.Document, name):
    attr = DataProperty.DefaultAttributes
    prop = DataProperty.CreateCustomPrototype(name, DataType.String, attr)
    Document.Data.Properties.AddProperty(DataPropertyClass.Document, prop)

Document.Properties[name] = "초기값"
```

`DataPropertyClass`는 `Document`, `Table`, `Column` 세 가지입니다.

## 6.8 자주 쓰는 진입점 요약

| 하고 싶은 것 | 시작 지점 |
|--------------|-----------|
| 모든 시각화 순회 | `Document.Pages` → `page.Visuals` |
| 시각화의 축·데이터 바꾸기 | `visual.As[VisualContent]()` |
| 데이터 값 읽기 | `Document.Data.Tables[...]` + `DataValueCursor` |
| 마킹 읽기/설정 | `Document.Data.Markings["Marking"]` |
| 필터 초기화 | `Document.FilteringSchemes` |
| 필터 표시/숨김 | `page.FilterPanel.TableGroups` |
| UI와 값 주고받기 | `Document.Properties[...]` |
| 알림 띄우기 | `Application.GetService[NotificationService]()` |
| 파일 내보내기 | `Document.Data.CreateDataWriter(...)` |

---

지도는 여기까지입니다. 다음 [7장](07-ai-workflow.html)에서 이 지도를 생성형 AI에게 넘겨
원하는 스크립트를 얻어내는 방법을 익힙니다.
