# 11. 예제 D · 심화 자동화

앞 장까지는 "있는 것을 고치는" 스크립트였습니다.
이 장은 **문서에 없던 것을 만들어 내는** 스크립트 세 편입니다.
분량이 길지만, 앞 장의 패턴이 조합되어 있을 뿐입니다.

---

## 예제 19. 마킹한 값별로 시각화 자동 생성

<ul class="meta">
<li class="badge hard">기본 기능으로 어려움</li>
</ul>

**문제 상황**  
지역 목록에서 관심 있는 5곳을 마킹하면, **그 5개 지역 각각에 대한 차트**가
새 페이지에 자동으로 만들어졌으면 합니다. 다음에는 3곳만 고를 수도 있습니다.

**기본 기능으로 어려운 이유**  
트렐리스(Trellis)로 비슷한 효과를 낼 수 있지만, 트렐리스는 **모든 값에 대해 같은 차트**를
같은 크기로 그립니다. 값마다 다른 축·다른 유형·다른 데이터 제한을 주거나,
선택한 개수만큼만 그리도록 하는 것은 불가능합니다.
"선택한 항목 수에 따라 시각화 개수가 달라지는 페이지"는 스크립트로만 만들 수 있습니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `sourceTable` | DataTable | 데이터 테이블 |
| `splitColumn` | String | 분할 기준 컬럼 (예: `Region`) |
| `measureExpr` | String | Y축 표현식 (예: `Sum([Revenue])`) |
| `categoryExpr` | String | X축 표현식 (예: `[Month]`) |

```python
# -*- coding: utf-8 -*-
# 마킹된 값마다 차트를 하나씩 만들어 새 페이지에 배치한다.
#
# 매개변수:
#   sourceTable  (DataTable) 데이터 테이블
#   splitColumn  (String)    분할 기준 컬럼명       예: "Region"
#   measureExpr  (String)    Y축 표현식             예: "Sum([Revenue])"
#   categoryExpr (String)    X축 표현식             예: "[Month]"

from Spotfire.Dxp.Application.Visuals import BarChart
from Spotfire.Dxp.Data import DataValueCursor

PAGE_TITLE = u"자동 생성 비교"
MARKING_NAME = "Marking"
MAX_CHARTS = 12          # 너무 많이 만들지 않도록 상한

# 1) 마킹된 행에서 분할 기준 값의 고유 목록을 얻는다
marking = Document.Data.Markings[MARKING_NAME]
markedRows = marking.GetSelection(sourceTable).AsIndexSet()
cursor = DataValueCursor.CreateFormatted(sourceTable.Columns[splitColumn])

values = set()
for row in sourceTable.GetRows(markedRows, cursor):
    if cursor.CurrentValue is not None:
        values.add(cursor.CurrentValue)

values = sorted(values)[:MAX_CHARTS]

if not values:
    Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 값을 선택하세요."
else:
    # 2) 기존 자동 생성 페이지가 있으면 지우고 새로 만든다 (재실행 대비)
    for page in [p for p in Document.Pages]:
        if page.Title == PAGE_TITLE:
            Document.Pages.Remove(page)

    newPage = Document.Pages.AddNew(PAGE_TITLE)

    # 3) 값마다 차트 하나씩 생성
    for value in values:
        chart = newPage.Visuals.AddNew[BarChart]()
        chart.Data.DataTableReference = sourceTable
        chart.XAxis.Expression = categoryExpr
        chart.YAxis.Expression = measureExpr

        # 이 차트만 해당 값으로 한정한다
        escaped = value.replace("'", "''")      # 작은따옴표 이스케이프
        chart.Data.WhereClauseExpression = "[%s] = '%s'" % (splitColumn, escaped)

        chart.Title = u"%s" % value
        chart.Legend.Visible = False

    Document.ActivePageReference = newPage
    Document.Properties["ScriptLog"] = u"%d개 차트를 '%s' 페이지에 생성했습니다." % (
        len(values), PAGE_TITLE)
```

### 변형: 값마다 다른 유형 섞기

```python
from Spotfire.Dxp.Application.Visuals import BarChart, LineChart

for index, value in enumerate(values):
    # 짝수는 막대, 홀수는 선
    chart = (newPage.Visuals.AddNew[BarChart]() if index % 2 == 0
             else newPage.Visuals.AddNew[LineChart]())
    ...
```

!!! note "검증 포인트"
    - **재실행 시 같은 페이지를 지우고 다시 만듭니다.** 사용자가 그 페이지를 손으로
      편집했다면 사라지므로, 페이지 제목을 명확히(`자동 생성`) 두었습니다.
    - 시각화 배치는 Spotfire가 자동으로 격자에 채웁니다. 개수가 12개 이하면 이것으로 충분합니다.
      **행/열을 정확히 지정하고 싶다면** `LayoutDefinition`을 쓰세요 →
      [예제 21](11-examples-advanced.html)에 사용법을 정리해 두었습니다.
    - 문자열 값에 작은따옴표가 들어 있으면 표현식이 깨지므로 이스케이프했습니다.
      **숫자 컬럼이라면 따옴표를 빼야 합니다.**
      ```python
      chart.Data.WhereClauseExpression = "[%s] = %s" % (splitColumn, value)
      ```
    - 페이지 삭제는 되돌리기가 안 될 수 있습니다. 사본에서 먼저 시험하세요.

---

## 예제 20. 표현식 전수 검사 (문서 감사 리포트)

<ul class="meta">
<li class="badge hard">기본 기능으로 어려움</li>
<li class="badge bulk">일괄 적용</li>
</ul>

**문제 상황**  
컬럼 이름을 `Amount`에서 `Revenue`로 바꿔야 합니다.
이 컬럼을 참조하는 곳이 **축 표현식, 데이터 제한, 트렐리스, 색 기준** 등 어디에 몇 개나
있는지 알아야 하는데, 전부 열어 볼 수는 없습니다.

**기본 기능으로 어려운 이유**  
Spotfire에는 **표현식 전체 검색** 기능이 없습니다.
문서 전체에서 특정 컬럼을 쓰는 곳을 찾는 UI가 아예 없습니다.

이 스크립트는 결과를 **새 데이터 테이블로 만들어** Spotfire 안에서 필터·검색할 수 있게 합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `searchTerm` | String | 문서 속성 `AuditSearch` (비우면 전체 목록) |

```python
# -*- coding: utf-8 -*-
# 문서 내 모든 시각화의 표현식을 수집해 "표현식 감사" 데이터 테이블로 만든다.
# searchTerm 이 주어지면 그 문자열을 포함한 표현식만 남긴다.
#
# 매개변수:
#   searchTerm (String) 찾을 문자열. 예: "Amount". 빈 문자열이면 전체

from Spotfire.Dxp.Application.Visuals import VisualContent
from Spotfire.Dxp.Data import DataType
from Spotfire.Dxp.Data.Import import TextFileDataSource, TextDataReaderSettings
from System.IO import MemoryStream, StreamWriter, SeekOrigin
from System.Text import Encoding

TABLE_NAME = u"표현식 감사"

# 조사할 축 이름들 — 시각화 유형에 따라 없는 것도 있으므로 전부 시도한다
AXIS_NAMES = ["XAxis", "YAxis", "ColorAxis", "SizeAxis", "ShapeAxis", "LabelAxis",
              "MeasureAxis", "HorizontalAxis", "VerticalAxis", "SectorSizeAxis",
              "CellValueAxis", "ValueAxis"]

term = (searchTerm or "").strip()

records = []      # (페이지, 시각화, 유형, 위치, 표현식)

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        typeName = visual.TypeId.Name

        # 1) 각 축의 표현식
        for axisName in AXIS_NAMES:
            try:
                expression = getattr(vc, axisName).Expression
            except:
                continue
            if expression:
                records.append((page.Title, visual.Title, typeName, axisName, expression))

        # 2) 데이터 제한 표현식
        try:
            where = vc.Data.WhereClauseExpression
            if where:
                records.append((page.Title, visual.Title, typeName,
                                "WhereClause", where))
        except:
            pass

        # 3) 트렐리스 분할 표현식
        try:
            panel = vc.Trellis.PanelAxis.Expression
            if panel:
                records.append((page.Title, visual.Title, typeName,
                                "Trellis", panel))
        except:
            pass

# 검색어 필터
if term:
    records = [r for r in records if term.lower() in r[4].lower()]

if not records:
    Document.Properties["ScriptLog"] = u"'%s' 를 포함한 표현식을 찾지 못했습니다." % term
else:
    # 탭 구분 텍스트로 만들어 데이터 테이블로 읽어들인다
    HEADERS = [u"페이지", u"시각화", u"유형", u"위치", u"표현식"]

    def clean(text):
        # 탭·줄바꿈은 구분자를 깨뜨리므로 공백으로 치환
        return (text or u"").replace(u"\t", u" ").replace(u"\r", u" ").replace(u"\n", u" ")

    stream = MemoryStream()
    writer = StreamWriter(stream, Encoding.UTF8)
    writer.WriteLine(u"\t".join(HEADERS))
    for record in records:
        writer.WriteLine(u"\t".join(clean(field) for field in record))
    writer.Flush()
    stream.Seek(0, SeekOrigin.Begin)

    settings = TextDataReaderSettings()
    settings.Separator = "\t"
    settings.AddColumnNameRow(0)
    for index in range(len(HEADERS)):
        settings.SetDataType(index, DataType.String)

    dataSource = TextFileDataSource(stream, settings)

    if Document.Data.Tables.Contains(TABLE_NAME):
        Document.Data.Tables[TABLE_NAME].ReplaceData(dataSource)
    else:
        Document.Data.Tables.Add(TABLE_NAME, dataSource)

    Document.Properties["ScriptLog"] = u"표현식 %d건을 '%s' 테이블로 정리했습니다." % (
        len(records), TABLE_NAME)
```

**사용법**  

1. 스크립트 실행 → `표현식 감사` 데이터 테이블 생성
2. 그 테이블로 **표(Table) 시각화**를 하나 만들면 문서 전체 표현식이 한눈에 보입니다
3. 문서 속성 `AuditSearch`에 `Amount`를 넣고 다시 실행하면 해당 컬럼 사용처만 남습니다

!!! note "검증 포인트"
    - `TextDataReaderSettings`의 메서드 이름(`AddColumnNameRow`, `SetDataType`, `Separator`)은
      오래 유지된 API지만, 실패하면 `dir(settings)`로 확인하세요.
    - 인코딩을 `Encoding.UTF8`로 지정했습니다. 한글 페이지 제목이 깨지면 이 부분을 의심하세요.
    - 표현식 안의 탭·줄바꿈을 공백으로 바꿉니다. 그러지 않으면 컬럼이 밀립니다.
    - 만들어진 테이블은 문서에 **저장**됩니다. 배포 전에 지우고 싶다면
      `Document.Data.Tables.Remove(Document.Data.Tables[TABLE_NAME])`.
    - 계산된 컬럼(Calculated Column)의 표현식은 이 스크립트에 포함되지 않습니다.
      필요하면 다음을 추가하세요.

      ```python
      from Spotfire.Dxp.Data import CalculatedColumn
      for table in Document.Data.Tables:
          for column in table.Columns:
              try:
                  expression = column.As[CalculatedColumn]().Expression
                  records.append((table.Name, column.Name, u"CalculatedColumn",
                                  u"Column", expression))
              except:
                  pass
      ```

---

## 예제 21. 산점도 매트릭스 자동 생성 (NxN 상관 분석)

<ul class="meta">
<li class="badge hard">기본 기능으로 어려움</li>
<li class="badge bulk">일괄 적용</li>
</ul>

**문제 상황**  
연속형 컬럼 5개의 상관관계를 보려면 산점도가 **25개** 필요합니다.
손으로 만들면 25번 생성 + 50번 축 설정 + 배치까지 반나절입니다.
게다가 분석할 컬럼이 바뀌면 처음부터 다시 해야 합니다.

**기본 기능으로 어려운 이유**  
Spotfire에는 산점도 매트릭스(SPLOM) 시각화가 없습니다.
트렐리스는 **하나의 X-Y 조합**을 범주별로 나눌 뿐, 축 조합 자체를 바꾸지 못합니다.
"드롭다운에서 고른 컬럼만큼 NxN 격자를 만들어라"는 스크립트로만 가능합니다.

**사전 준비**

- 데이터 테이블 (예: `iris`)
- 문자열 목록 타입 문서 속성 (예: `columns`) — 텍스트 영역의 다중 선택 목록 상자에 연결
- 결과를 놓을 페이지 이름 (없으면 자동 생성)

**스크립트 매개변수**  
없음 (아래 설정 상수를 직접 수정합니다).

```python
# -*- coding: utf-8 -*-
# 문서 속성에 선택된 연속형 컬럼들로 NxN 산점도 매트릭스를 만들고 격자로 배치한다.

from Spotfire.Dxp.Application.Visuals import ScatterPlot
from Spotfire.Dxp.Application.Layout import LayoutDefinition
from Spotfire.Dxp.Data import DataPropertyClass
from System import String

# ---------- 설정 ----------
DATA_TABLE_NAME = "iris"          # 데이터 테이블 이름
PAGE_NAME = u"상관성 분석"          # 결과 페이지 (없으면 생성)
PROPERTY_NAME = "columns"         # 컬럼 목록이 담긴 문서 속성
TEXT_AREA_TITLE = u"텍스트 영역"    # 왼쪽에 유지할 텍스트 영역 제목 (없으면 무시)
TEXT_AREA_WIDTH = 10.0            # 왼쪽 텍스트 영역 폭 비율
GRID_WIDTH = 90.0                 # 오른쪽 격자 폭 비율
INCLUDE_DIAGONAL = True           # 대각선(자기 자신과의 산점도) 포함 여부


# ---------- 문서 속성에서 컬럼 목록 읽기 ----------
def get_selected_columns(propertyName):
    raw = Document.Properties[propertyName]
    if raw is None:
        raise Exception(u"문서 속성 '%s' 값이 비어 있습니다." % propertyName)

    columns = []
    if isinstance(raw, String):
        # 단일 문자열이면 쉼표로 분리
        for name in str(raw).split(","):
            if name.strip():
                columns.append(name.strip())
    else:
        # 문자열 목록이면 그대로 순회
        for name in raw:
            if name is not None and str(name).strip():
                columns.append(str(name).strip())

    if not columns:
        raise Exception(u"문서 속성 '%s'에 선택된 컬럼이 없습니다." % propertyName)
    return columns


# ---------- 보조 함수 ----------
def get_page_by_title(title):
    for page in Document.Pages:
        if page.Title == title:
            return page
    return None


def get_visual_by_title(page, title):
    for visual in page.Visuals:
        if visual.Title == title:
            return visual
    return None


def remove_existing_scatter_plots(page):
    """재실행 대비: 기존 산점도만 지운다. 텍스트 영역은 남긴다."""
    targets = []
    for visual in page.Visuals:
        try:
            if visual.As[ScatterPlot]() is not None:
                targets.append(visual)
        except:
            pass
    for visual in targets:
        try:
            page.Visuals.Remove(visual)
        except:
            pass


def column_expression(columnName):
    # 컬럼 이름에 ] 가 있으면 이스케이프
    return "<[" + columnName.replace("]", "]]") + "]>"


def add_scatter(page, dataTable, xCol, yCol):
    """산점도를 만들고, 레이아웃에 넣을 Visual 컨테이너를 반환한다."""
    scatter = page.Visuals.AddNew[ScatterPlot]()
    scatter.Data.DataTableReference = dataTable
    scatter.XAxis.Expression = column_expression(xCol)
    scatter.YAxis.Expression = column_expression(yCol)

    title = u"%s vs %s" % (yCol, xCol)
    scatter.Title = title

    # 격자에서는 축 선택기와 범례가 공간만 차지한다
    for setter in ["XAxis", "YAxis"]:
        try:
            getattr(scatter, setter).ShowAxisSelector = False
        except:
            pass
    try:
        scatter.Legend.Visible = False
    except:
        pass
    try:
        scatter.MarkerSize = 2
    except:
        pass

    # AddNew는 콘텐츠를 반환하므로, 배치에 쓸 Visual 컨테이너는 제목으로 찾는다
    visual = get_visual_by_title(page, title)
    if visual is None:
        raise Exception(u"생성한 시각화를 찾을 수 없습니다: " + title)
    return visual


def apply_grid_layout(page, textAreaVisual, grid):
    """왼쪽 텍스트 영역 + 오른쪽 NxN 격자로 배치한다."""
    layout = LayoutDefinition()

    def build_grid():
        rowCount = len(grid)
        for row in grid:
            if not row:
                continue
            layout.BeginSideBySideSection(100.0 / rowCount)
            for visual in row:
                layout.Add(visual, 100.0 / len(row))
            layout.EndSection()

    if textAreaVisual is not None:
        layout.BeginSideBySideSection()
        layout.Add(textAreaVisual, TEXT_AREA_WIDTH)
        try:
            layout.BeginStackedSection(GRID_WIDTH)
        except:
            layout.BeginStackedSection()
        build_grid()
        layout.EndSection()
        layout.EndSection()
    else:
        layout.BeginStackedSection()
        build_grid()
        layout.EndSection()

    page.ApplyLayout(layout)


# ---------- 실행 ----------
columns = get_selected_columns(PROPERTY_NAME)

if not Document.Data.Tables.Contains(DATA_TABLE_NAME):
    raise Exception(u"데이터 테이블을 찾을 수 없습니다: " + DATA_TABLE_NAME)
dataTable = Document.Data.Tables[DATA_TABLE_NAME]

missing = [c for c in columns if not dataTable.Columns.Contains(c)]
if missing:
    raise Exception(u"다음 컬럼을 찾을 수 없습니다: " + u", ".join(missing))

# 페이지 확보 (있으면 재사용)
page = get_page_by_title(PAGE_NAME)
if page is None:
    page = Document.Pages.AddNew(PAGE_NAME)
Document.ActivePageReference = page

textAreaVisual = get_visual_by_title(page, TEXT_AREA_TITLE)
remove_existing_scatter_plots(page)

# NxN 격자 생성
grid = []
for yCol in columns:
    rowVisuals = []
    for xCol in columns:
        if (not INCLUDE_DIAGONAL) and xCol == yCol:
            continue
        rowVisuals.append(add_scatter(page, dataTable, xCol, yCol))
    grid.append(rowVisuals)

apply_grid_layout(page, textAreaVisual, grid)

Document.Properties["ScriptLog"] = u"컬럼 %d개로 산점도 %d개를 '%s' 페이지에 생성했습니다." % (
    len(columns), sum(len(r) for r in grid), PAGE_NAME)
```

### 레이아웃 API 정리

이 예제에서 처음 나온 `LayoutDefinition`이 **시각화 배치의 핵심**입니다.

| 호출 | 의미 |
|------|------|
| `LayoutDefinition()` | 빈 배치 정의 생성 |
| `BeginSideBySideSection(weight)` | **가로로** 나란히 놓는 구역 시작 |
| `BeginStackedSection(weight)` | **세로로** 쌓는 구역 시작 |
| `Add(visual, weight)` | 그 구역에 시각화 배치. `weight`는 비율 |
| `EndSection()` | 구역 종료 (Begin과 짝을 맞춰야 함) |
| `page.ApplyLayout(layout)` | 페이지에 적용 |

구역을 중첩해서 원하는 격자를 만듭니다.

```text
BeginSideBySideSection()          가로 분할
├─ Add(텍스트영역, 10)             왼쪽 10%
└─ BeginStackedSection(90)        오른쪽 90%를 세로로 분할
   ├─ BeginSideBySideSection()      1행 (가로)
   │  ├─ Add(산점도1) Add(산점도2)
   │  └─ EndSection()
   └─ BeginSideBySideSection()      2행
      └─ ...
```

!!! note "검증 포인트"
    - **`AddNew[ScatterPlot]()`은 시각화 콘텐츠를 반환하지, 레이아웃에 넣을
      `Visual` 컨테이너를 반환하지 않습니다.** 그래서 위 코드는 생성 직후
      제목으로 컨테이너를 다시 찾습니다. 이 점을 놓치면 `ApplyLayout`에서 실패합니다.
    - 그래서 **제목이 겹치면 안 됩니다.** 컬럼 이름이 유일하므로 `"Y vs X"` 제목은 안전합니다.
    - `BeginStackedSection(weight)`는 버전에 따라 인자를 받지 않을 수 있어 `try`로 감쌌습니다.
    - 축 표현식에 `<[컬럼]>` 형식(꺾쇠 포함)을 썼습니다. 이건 **축 선택기가 붙는 형태**로,
      일반 표현식 `[컬럼]`과 달리 사용자가 축을 바꿀 수 있게 합니다.
    - 컬럼을 6개 이상 고르면 36개 이상의 산점도가 생겨 **매우 느려집니다.**
      실무에서는 5개 정도로 제한하세요.
    - 재실행하면 기존 산점도를 지우고 다시 만듭니다. **그 페이지를 손으로 편집했다면 사라집니다.**

---

## 예제들을 조합하기

예제 20로 **어디를 고쳐야 하는지 찾고**, 예제 5로 **일괄 교체**하고, 다시 예제 20로
**남은 곳이 없는지 확인**하는 것이 실무에서 컬럼명 변경을 처리하는 순서입니다.

```text
① 예제 20 (검색어: "Amount")   → 사용처 목록 확보
② 예제 5  또는 개별 수정        → 일괄 교체
③ 예제 20 (검색어: "Amount")   → 0건이면 완료
```

---

예제 21개는 여기까지입니다. 다음 장에서 **실무에서 걸리는 함정들**을 정리합니다.
