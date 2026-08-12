# 6. Spotfire API 객체 모델

문법을 알아도 **"이 기능이 어느 객체에 매달려 있는지"** 를 모르면 코드를 못 씁니다.
이 장은 `Document`에서 출발해 아래로 내려가는 지도입니다. 9장 이후 예제는 전부 이 지도 위에서 움직입니다.

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
    ├── Bookmarks ─────────── 북마크 (상태 저장/복원)
    ├── ScriptManager ─────── 이 문서에 저장된 스크립트들 (12.0+)
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

`Visual`(껍데기)과 `VisualContent`(알맹이)의 구분이 핵심입니다 → [5.2 참조](05-dotnet-interop.html#52-ast)

```python
from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

for visual in Document.ActivePageReference.Visuals:
    # Visual 수준
    print visual.Title, visual.TypeId

    # VisualContent 수준
    vc = visual.As[VisualContent]()
    print vc.Data.DataTableReference.Name
```

`Visual`(껍데기)이 가진 것은 이게 전부입니다. 짧으니 외워 두면 편합니다.

| 멤버 | 의미 |
|------|------|
| `Title` | 제목 문자열 |
| `ShowTitle` | 제목 표시 여부 (제목 문자열과 별개) |
| `TypeId` | 유형. **쓰면 그 유형으로 변환된다** |
| `Id` | 이 시각화의 **고유 ID**. 제목이 바뀌어도 그대로 |
| `As[T]()` | 알맹이로 캐스팅 |
| `AutoConfigure()` | 새로 만든 시각화를 현재 데이터에 맞게 기본 설정 |
| `ApplyUserPreferences()` | 사용자 기본 서식 적용 |
| `RenderAsync(...)` | 이미지로 렌더링 (`Render` 는 폐기 예정) |

!!! tip "제목 대신 Id를 키로 쓰세요"
    "이 시각화만 건드리지 마라" 같은 규칙을 제목 문자열로 만들면 사용자가 제목을 바꾸는 순간
    깨집니다 → [7.1 참조](07-pitfalls.html). `Visual.Id` 는 바뀌지 않습니다.

    ```python
    # 한 번 실행해서 Id를 알아낸다
    for page in Document.Pages:
        for visual in page.Visuals:
            print visual.Id, "|", visual.Title

    # 그 Id를 스크립트에 박아 둔다
    SKIP_IDS = ["...붙여 넣기..."]
    if str(visual.Id) in SKIP_IDS:
        continue
    ```

!!! note "공식 문서가 못 박아 둔 것"
    `Visual` 클래스 문서에는 이렇게 적혀 있습니다.

    - 사용자가 언제든 UI에서 유형을 바꿀 수 있으므로 **`As<T>()` 를 부르기 전에 반드시
      `TypeId` 를 먼저 확인**할 것
    - `TablePlotBase` · `TrellisVisualization` 같은 **추상 기반 클래스 말고
      `BarChart` 같은 구체 클래스**로 캐스팅할 것

    이 교안의 예제가 전부 `TypeId` 로 먼저 거르는 이유입니다.

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
noRows[5] = True                              # 6번째 행만 켠다

selection = RowSelection(noRows)              # 마킹 API에 넘길 형태
```

- **`IndexSet`**: 행 인덱스의 비트 집합. `And`, `Or`, `Not` 연산 가능
- **`RowSelection`**: 마킹/필터 API가 요구하는 래퍼

!!! warning "`IndexSet` 에는 `Add()` 가 없습니다"
    실측 확인 결과 `hasattr(indexSet, "Add")` 는 `False` 입니다.
    파이썬 `set` 처럼 `Add(5)` 를 부르면 실패합니다. **두 가지 방법이 있습니다.**

    ```python
    indexSet[5] = True        # 인덱서 — 켜고 끄기 모두 가능
    indexSet[5] = False

    indexSet.AddIndex(5)      # 전용 메서드 — 의도가 더 분명하다
    indexSet.RemoveIndex(5)
    ```

    Spotfire 14.x에서 확인한 `IndexSet` 의 실제 멤버입니다.

    ```text
    AddIndex  AddIndexes  RemoveIndex  RemoveIndexes  Item
    And  Or  Not  Xor  Subtract  Intersects
    Clear  Fill  Clone  Contains  HasIndex  Count  Capacity
    First  Last  IsEmpty  IsFull  GetNextIndex  GetPreviousIndex
    ```

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
"모든 필터 초기화" 버튼은 **현재 스킴 하나만** 초기화합니다. 이것이 [예제 14](11-examples-data.html)의 출발점입니다.

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

## 6.8 북마크와 스크립트 관리

두 가지는 잘 알려져 있지 않지만 알아 두면 쓸 데가 많습니다.

### 북마크 — 상태를 통째로 저장·복원

필터·마킹·페이지·시각화 설정을 **한 덩어리로** 저장했다 되돌립니다.

```python
# 목록 보기 / 적용
for bookmark in Document.Bookmarks:
    print bookmark.DisplayName, bookmark.IsBroken

Document.Bookmarks[0].Apply()
```

이름 속성이 `Name` 이 아니라 **`DisplayName`** 입니다. 여기서 자주 틀립니다.
`IsBroken` 이 `True` 면 북마크가 참조하던 대상이 사라진 것이고,
`Apply()` 는 **깨지지 않은 부분만** 적용합니다.

"보기 초기화"를 직접 짜는 대신([예제 10](10-examples-state.html)) 기준 상태를 북마크로
저장해 두고 적용하는 방법도 있습니다. 다만 북마크는 **저장한 것 전부**를 되돌리므로
"필터만 초기화" 같은 선택적 제어에는 맞지 않습니다.
`BookmarkCollection.AddNew(...)` 는 **폐기 예정(Obsolete)** 이므로 새 북마크는 UI에서
만들고, 스크립트는 적용만 하는 쪽이 안전합니다.

### ScriptManager — 문서 안의 스크립트 목록 (Spotfire 12.0+)

분석 파일에 스크립트가 20개씩 쌓이면 **뭐가 어디서 쓰이는지** 알 수 없게 됩니다.
`Document.ScriptManager` 가 그 목록을 코드로 보여 줍니다.

```python
for script in Document.ScriptManager.GetScripts():
    print script.Name, "|", script.Language.Language
    print script.ScriptCode
```

| 멤버 | 하는 일 |
|------|---------|
| `GetScripts()` | 문서의 모든 스크립트 정의 열거 |
| `TryGetScript(name)` | `(찾음여부, 정의)` 튜플 반환 → [5.8 참조](05-dotnet-interop.html#58-api) |
| `GetAllScriptsWithName(name)` | 같은 이름의 스크립트 전부 (중복 정리용) |
| `AddScriptDefinition(def)` / `Replace(old, new)` / `Remove(def)` | 추가·교체·삭제 |
| `ExecuteScript(...)` | 스크립트 안에서 다른 스크립트 실행 |

`ScriptDefinition` 은 **불변(immutable)** 입니다. 고치려면 `WithScriptCode(...)` ·
`WithName(...)` 로 복사본을 만들어 `Replace` 합니다.

```python
found, old = Document.ScriptManager.TryGetScript(u"대시보드 초기화")
if found:
    new = old.WithScriptCode(old.ScriptCode.replace("0.5", "0.9"))
    Document.ScriptManager.Replace(old, new)
```

읽기만 하는 사용법은 [예제 22](12-examples-create.html)에 있습니다.

!!! danger "쓰기는 조심하세요"
    `Remove` 로 지운 스크립트가 액션 컨트롤에 연결되어 있었다면 **그 버튼을 손으로 다시
    설정해야** 합니다. `Replace` 도 매개변수 구성이 달라지면 연결된 액션이 비활성화됩니다.
    (공식 API 문서의 경고입니다.)

## 6.9 자주 쓰는 진입점 요약

| 하고 싶은 것 | 시작 지점 |
|--------------|-----------|
| 모든 시각화 순회 | `Document.Pages` → `page.Visuals` |
| 시각화의 축·데이터 바꾸기 | `visual.As[VisualContent]()` |
| 데이터 값 읽기 | `Document.Data.Tables[...]` + `DataValueCursor` |
| 마킹 읽기/설정 | `Document.ActiveMarkingSelectionReference` |
| 필터 초기화 | `Document.FilteringSchemes` |
| 필터 표시/숨김 | `page.FilterPanel.TableGroups` |
| UI와 값 주고받기 | `Document.Properties[...]` |
| 알림 띄우기 | `Application.GetService[NotificationService]()` |
| 진행률 표시 | `Application.GetService[ProgressService]()` |
| 파일 내보내기 | `TablePlot.ExportText(...)` / `Document.Data.CreateDataWriter(...)` |
| 상태 저장·복원 | `Document.Bookmarks` |
| 스크립트 목록 | `Document.ScriptManager` |
| 클라이언트 종류 판별 | `Application.GetType().ToString()` |

## 6.10 시각화 속성 레시피 — UI 탭과 코드의 대응표

시각화 속성 대화상자의 탭 하나하나가 대체로 코드 한 줄에 대응합니다.
여기서는 그 대응관계를 모아 둡니다. 전부 `vc = visual.As[VisualContent]()` 로 내려온
다음을 전제로 합니다.

!!! warning "이 절은 문서 · 외부 레퍼런스 기반입니다"
    9~12장 예제와 달리, 이 절의 속성 이름은 공식 API 레퍼런스와
    [sf-ref.com](https://www.sf-ref.com/ironpython/)을 대조해 정리한 것이며,
    **이 교안의 검증 환경에서 전부 실행해 본 것은 아닙니다.**
    시각화 유형마다 있는 속성이 다르므로, 쓰기 전에 `dir(vc)` 로 한 번 확인하세요 → [7.6](07-pitfalls.html)

### 축 — 범위·줌·눈금·로그 스케일

```python
from Spotfire.Dxp.Application.Visuals import AxisRange, AxisTransformType

vc.XAxis.Expression = "[Month]"
vc.YAxis.Range = AxisRange(0, 100)          # 고정
vc.YAxis.Range = AxisRange(None, None)      # 자동으로 되돌리기
vc.YAxis.IncludeZeroInAutoZoom = True       # 원점 포함
vc.XAxis.ManualZoom = True                  # 줌 슬라이더 표시
vc.XAxis.Reversed = True                    # 축 반전
vc.YAxis.TransformType = AxisTransformType.Log10   # 로그 스케일
vc.XAxis.Scale.ShowGridlines = True
vc.XAxis.Scale.ShowLabels = True
```

줌 범위를 초기화할 때는 `Range` 가 아니라 `ZoomRange` 입니다 → [예제 5](09-examples-visuals.html)

```python
vc.XAxis.ZoomRange = AxisRange.DefaultRange
```

### 눈금 서식 — 데이터 타입별 포매터

서식은 **축의 데이터 타입에 따라 받는 포매터 이름이 다릅니다.** 이게 가장 흔한 실수입니다.

```python
from Spotfire.Dxp.Data import DataType
from Spotfire.Dxp.Data.Formatters import NumberFormatCategory

fmt = DataType.Real.CreateLocalizedFormatter()
fmt.Category = NumberFormatCategory.Currency
fmt.DecimalDigits = 0
fmt.GroupSeparatorEnabled = True      # 천 단위 구분
fmt.ShortFormattingEnabled = True     # 1200 -> 1.2K

vc.YAxis.Scale.Formatting.RealFormatter = fmt
```

| 컬럼 데이터 타입 | 대입할 속성 |
|-------------------|-------------|
| Real | `Formatting.RealFormatter` |
| SingleReal | `Formatting.SingleRealFormatter` |
| Integer | `Formatting.IntegerFormatter` |
| LongInteger | `Formatting.LongIntegerFormatter` |
| Currency | `Formatting.CurrencyFormatter` |
| DateTime / Date / Time | `Formatting.DateTimeFormatter` |

문자열·불리언·범주형·빈 컬럼은 서식을 받지 않습니다.
UI 서식 탭에 "텍스트"만 보이는 축이라면 코드로도 안 됩니다.

### 범례

```python
from Spotfire.Dxp.Application.Visuals import LegendDock

vc.Legend.Visible = True
vc.Legend.Dock = LegendDock.Right
vc.Legend.Width = 150

for item in vc.Legend.Items:          # 항목별로 켜고 끄기
    item.Visible = (item.Title == "Color by")
```

### 툴팁(Details)

```python
for t in vc.Details.Items:             # 기본 항목 전부 끄기
    t.Visible = False

vc.Details.Items.AddExpression("Sum([Revenue]) as [매출]")
vc.Details.Items.InsertExpression(0, "[Region] as [지역]")   # 맨 앞에
```

### 트렉스(분할 보기)

```python
from Spotfire.Dxp.Application.Visuals import TrellisMode

vc.Trellis.TrellisMode = TrellisMode.Panels
vc.Trellis.PanelAxis.Expression = "<[Region]>"    # 범주형은 <[ ]>
vc.Trellis.ManualLayout = True
vc.Trellis.ManualColumnCount = 3

# 행/열 모드
vc.Trellis.TrellisMode = TrellisMode.RowsColumns
vc.Trellis.RowAxis.Expression = "<[Category]>"
vc.Trellis.ColumnAxis.Expression = "<[Year]>"
```

트렉스·색상·마커 등 **범주형 축은 `<[컬럼]>` 처럼 꺠솠 괄호**를 씁니다.
그냥 `[컬럼]` 을 넣으면 오류가 나거나 집계로 해석됩니다.

### 시각화의 데이터 범위 설정

```python
from Spotfire.Dxp.Application.Visuals import LimitingMarkingsEmptyBehavior

vc.Data.DataTableReference = Document.Data.Tables["Sales"]
vc.Data.MarkingReference = Document.Data.Markings["Marking"]     # 이 시각화가 쓰는 마킹
vc.Data.WhereClauseExpression = "[Region] = 'East'"              # 데이터 제한 표현식
vc.Data.UseActiveFiltering = False                               # 페이지 필터링 무시

# 마킹으로 데이터 제한 ("이 마킹에 속한 행만 보기")
vc.Data.Filterings.Add(Document.Data.Markings["Marking"])
vc.Data.LimitingMarkingsEmptyBehavior = LimitingMarkingsEmptyBehavior.ShowAll
```

이 세 가지를 헷갈리지 마세요.

| 속성 | 의미 |
|------|------|
| `Data.MarkingReference` | 이 시각화에서 **드래그하면 칠해지는** 마킹 |
| `Data.Filterings` | 이 시각화가 **보여 줄 범위를 좁히는** 마킹/필터링 |
| `Data.WhereClauseExpression` | 표현식으로 직접 제한 (예제 1) |

### 표 시각화 정렬

```python
from Spotfire.Dxp.Application.Visuals import TablePlot, TablePlotColumnSortMode

tp = visual.As[TablePlot]()
col = tp.Data.DataTableReference.Columns["Revenue"]
tp.SortInfos.Clear()
tp.SortInfos.Add(col, TablePlotColumnSortMode.Descending)
```

### 필터 패널·페이지 단위 토글

```python
panel = Document.ActivePageReference.FilterPanel
panel.Visible = not panel.Visible
```

## 6.11 공식 API 레퍼런스에서 클래스 찾기

Spotfire의 API 레퍼런스는 검색이 불편하지만, **URL 규칙이 단순**해서 주소창에 직접
쳐 넣는 편이 빠릅니다.

```text
https://docs.tibco.com/pub/doc_remote/sfire_dev/area/doc/api/tib_sfire-analyst_api/html/T_<네임스페이스>_<클래스>.htm
```

- 점(`.`)을 **밑줄(`_`)** 로 바꾸고
- 타입은 `T_`, 네임스페이스는 `N_`, 메서드는 `M_`, 속성은 `P_` 를 앞에 붙입니다

```text
Spotfire.Dxp.Application.Visuals.BarChart
→ .../html/T_Spotfire_Dxp_Application_Visuals_BarChart.htm

Spotfire.Dxp.Application.Visual.RenderAsync (메서드)
→ .../html/M_Spotfire_Dxp_Application_Visual_RenderAsync.htm
```

문서에서 확인해야 할 것은 세 가지입니다.

1. **Obsolete 표시** — 폐기 예정인 멤버인지 (예: `Visual.Render`)
2. **생성자 시그니처** — `RenderResultSettings(Size)` 처럼 인자가 필요한지
3. **Remarks** — "이 순서로 불러야 한다" 같은 제약이 여기 적혀 있습니다

!!! warning "문서에 있다고 동작하는 것은 아닙니다"
    문서는 **이름과 시그니처**를 확인하는 용도입니다.
    "그 환경에서 실제로 되는가"는 [7.10의 확인 방법](07-pitfalls.html)으로 따로 봐야 합니다.

---

지도는 여기까지입니다. 다음 [7장](07-pitfalls.html)에서는 이 API들이 **실제로는 어떻게
말썽을 부리는지** 봅니다. 문서대로 되지 않는 경우가 생각보다 많습니다.
