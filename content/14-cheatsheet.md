# 14. 치트시트 & FAQ

필요할 때 바로 복사해 쓰는 한 장 요약입니다.

## 14.1 import 모음

```python
# 시각화
from Spotfire.Dxp.Application.Visuals import (
    VisualContent, VisualTypeIdentifiers, AxisRange,
    BarChart, LineChart, ScatterPlot, PieChart,
    TablePlot, CrossTablePlot, HtmlTextArea)

# 데이터
from Spotfire.Dxp.Data import (
    DataValueCursor, IndexSet, RowSelection, DataType,
    DataProperty, DataPropertyClass, CalculatedColumn, TagsColumn)

# 데이터 입출력
from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from Spotfire.Dxp.Data.Import import (
    TextFileDataSource, TextDataReaderSettings, InformationLinkDataSource)

# 레이아웃(배치)
from Spotfire.Dxp.Application.Layout import LayoutDefinition

# 필터
import Spotfire.Dxp.Application.Filters as filters
from Spotfire.Dxp.Application.Filters import FilterTypeIdentifiers

# 서비스
from Spotfire.Dxp.Framework.ApplicationModel import (
    NotificationService, ProgressService, ApplicationThread)

# 스크립트 관리 (12.0+)
from Spotfire.Dxp.Application.Scripting import (
    ScriptDefinition, ScriptLanguage, ScriptParameter, ScriptParameterCollection)

# .NET
from System import Array, String, Guid, DateTime
from System.IO import File, Path, Directory, MemoryStream, StreamWriter, SeekOrigin
from System.Threading import Thread, CancellationToken

import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
```

## 14.2 페이지와 시각화

```python
# 현재 페이지 / 이동
page = Document.ActivePageReference
Document.ActivePageReference = Document.Pages[0]

# 모든 시각화 순회
for page in Document.Pages:
    for visual in page.Visuals:
        vc = visual.As[VisualContent]()

# 페이지 추가 / 삭제 / 숨김
newPage = Document.Pages.AddNew(u"제목")
Document.Pages.Remove(newPage)
page.Visible = False

# 시각화 생성
chart = page.Visuals.AddNew[BarChart]()

# 유형 확인 / 변경
if visual.TypeId == VisualTypeIdentifiers.BarChart:
    visual.TypeId = VisualTypeIdentifiers.LineChart

# Visual(껍데기) 수준 속성 — 캐스팅 없이 바로 된다
visual.Title = u"제목"
visual.ShowTitle = False        # 제목 문자열과 별개. 자리까지 없앤다
print visual.Id                 # 이름이 바뀌어도 변하지 않는 고유 ID

# 새로 만든 시각화 기본 설정
visual.AutoConfigure()
visual.ApplyUserPreferences()

# 배치 — 격자만 필요하면 한 줄
from Spotfire.Dxp.Application.Layout import TileMode
page.ApplyLayout(TileMode.Evenly)   # Horizontally / Vertically / Evenly / Maximize
```

## 14.3 시각화 속성

```python
vc = visual.As[VisualContent]()

vc.Data.DataTableReference = Document.Data.Tables["Sales"]
vc.Data.WhereClauseExpression = "[Year] > 2020"
vc.Data.MarkingReference = Document.Data.Markings["Marking"]

vc.XAxis.Expression = "[Region]"
vc.YAxis.Expression = "Sum([Revenue])"
vc.ColorAxis.Expression = "[Category]"
vc.XAxis.ZoomRange = AxisRange.DefaultRange

vc.Legend.Visible = False
visual.Title = u"제목"

# 축 범위 고정 / 해제
from Spotfire.Dxp.Application.Visuals import AxisRange
vc.YAxis.Range = AxisRange(0, 100)          # 고정
vc.YAxis.Range = AxisRange.DefaultRange     # 자동으로 되돌리기
vc.XAxis.ZoomRange = AxisRange.DefaultRange # 줌 슬라이더 초기화 (Range와 다름)

# 유형 고유 속성은 그 타입으로 캐스팅
from Spotfire.Dxp.Application.Visuals import ScatterPlot
scatter = visual.As[ScatterPlot]()
scatter.MarkerSize = scatter.MarkerSize + 1
```

### 유형 판별 두 가지 방식

```python
# 방식 1: 열거형 비교 — 오타에 안전
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
if visual.TypeId == VisualTypeIdentifiers.BarChart:
    pass

# 방식 2: 문자열 비교 — import 없이 가능
if str(visual.TypeId) == "TypeIdentifier:Spotfire.BarChart":
    pass
```

## 14.4 데이터

```python
table = Document.Data.Tables["Sales"]
table = Document.ActiveDataTableReference
print table.RowCount

# 컬럼 목록
names = [c.Name for c in table.Columns]

# 존재 확인
if Document.Data.Tables.Contains("Sales"):
    pass

# 값 읽기
cursor = DataValueCursor.CreateFormatted(table.Columns["Region"])
rows = IndexSet(table.RowCount, True)
for row in table.GetRows(rows, cursor):
    print row.Index, cursor.CurrentValue

# 고유값
values = set()
distinct = table.GetDistinctRows(None, cursor)
distinct.Reset()
while distinct.MoveNext():
    values.add(cursor.CurrentValue)

# 표현식으로 행 선택
selection = table.Select("[Region] = 'East'")

# 새로고침
if table.IsRefreshable:
    table.Refresh()
```

## 14.5 마킹

```python
marking = Document.Data.Markings["Marking"]

# 읽기
marked = marking.GetSelection(table).AsIndexSet()
print marked.Count

# 설정
marking.SetSelection(table.Select("[Region] = 'East'"), table)

# 해제
marking.SetSelection(RowSelection(IndexSet(table.RowCount, False)), table)

# 활성 마킹 / 필터링
Document.ActiveMarkingSelectionReference
Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()
```

## 14.6 필터

```python
# 모든 필터 초기화 (모든 스킴)
for scheme in Document.FilteringSchemes:
    scheme.ResetAllFilters()

# 필터 패널 순회
filterPanel = Document.ActivePageReference.FilterPanel
for tableGroup in filterPanel.TableGroups:
    for handle in tableGroup.FilterHandles:
        print handle.FilterReference.Name, handle.Visible
        handle.Visible = True

# 특정 필터 조작
handle = filterPanel.TableGroups[0].GetFilter("Region")
cb = handle.FilterReference.As[filters.CheckBoxFilter]()
cb.Reset()
cb.Check("East")
cb.Uncheck("West")

# 특정 컬럼의 필터만 초기화 (모든 스킴에서)
for scheme in Document.FilteringSchemes:
    for table in Document.Data.Tables:
        for column in table.Columns:
            if column.Name in ["Region", "Product"]:
                try:
                    scheme[table][column].Reset()
                except:
                    pass

# 특정 스킴 하나만 전체 초기화
Document.FilteringSchemes[0].ResetAllFilters()

# 필터 패널 표시/숨김
Document.ActivePageReference.FilterPanel.Visible = False
```

## 14.7 문서 속성

```python
value = Document.Properties["Name"]
Document.Properties["Name"] = u"값"

# 새로 만들기
from Spotfire.Dxp.Data import DataProperty, DataType, DataPropertyClass
if not Document.Data.Properties.Contains(DataPropertyClass.Document, "New"):
    prop = DataProperty.CreateCustomPrototype(
        "New", DataType.String, DataProperty.DefaultAttributes)
    Document.Data.Properties.AddProperty(DataPropertyClass.Document, prop)
```

## 14.8 레이아웃(배치)

```python
from Spotfire.Dxp.Application.Layout import LayoutDefinition

layout = LayoutDefinition()
layout.BeginSideBySideSection()       # 가로 분할 시작
layout.Add(visualA, 30.0)             # 왼쪽 30%
layout.BeginStackedSection(70.0)      # 오른쪽 70%를 세로 분할
layout.Add(visualB, 50.0)
layout.Add(visualC, 50.0)
layout.EndSection()
layout.EndSection()
page.ApplyLayout(layout)
```

주의: `page.Visuals.AddNew[BarChart]()`는 **콘텐츠**를 반환합니다.
`layout.Add()`에 넣을 `Visual` 컨테이너는 생성 후 제목으로 다시 찾아야 합니다.

```python
def get_visual_by_title(page, title):
    for visual in page.Visuals:
        if visual.Title == title:
            return visual
    return None
```

## 14.9 내보내기

```python
# 데이터 — 표 시각화 경유. 이 교안 검증 환경에서 확인된 방법
from Spotfire.Dxp.Application.Visuals import TablePlot
from System.IO import StreamWriter
from System.Text import Encoding

plot = vTable.As[TablePlot]()           # 매개변수로 받은 표 시각화
if plot.ExportDataEnabled:
    writer = StreamWriter("C:/out/data.txt", False, Encoding.UTF8)
    try:
        plot.ExportText(writer)         # 탭 구분 텍스트
    finally:
        writer.Close()
```

```python
# 데이터 — CreateDataWriter 방식. 라이선스에 막히면 None 을 반환한다
from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from System.IO import File

writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.ExcelXlsDataWriter)
if writer is not None:                  # 반드시 확인할 것 (7.5)
    filtered = Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()
    names = [c.Name for c in table.Columns]

    stream = File.OpenWrite("C:/out/data.xls")
    try:
        writer.Write(stream, table, filtered, names)
    finally:
        stream.Close()
```

```python
# 이미지 — Render 방식 (검증 환경에서 동작 확인. 단 API 문서상 폐기 예정)
import clr
clr.AddReference("System.Drawing")
from System.Drawing import Bitmap, Graphics, Rectangle

bitmap = Bitmap(1200, 800)
graphics = Graphics.FromImage(bitmap)
visual.As[VisualContent]().Render(graphics, Rectangle(0, 0, 1200, 800))
bitmap.Save("C:/out/chart.png")
graphics.Dispose()
bitmap.Dispose()
```

```python
# 이미지 — RenderAsync 방식 (15.x 정식 경로. 이 교안에서는 미검증)
from Spotfire.Dxp.Application.Visuals import RenderResultSettings, VisualRenderSettings
from System.Drawing import Size
from System.Threading import CancellationToken
from System.IO import FileStream, FileMode

task = visual.RenderAsync(RenderResultSettings(Size(1200, 800)),
                          VisualRenderSettings(),
                          CancellationToken())     # .None 은 파이썬 문법 오류
result = task.Result
if result.IsValid:
    stream = FileStream("C:/out/chart.png", FileMode.Create)
    try:
        result.WriteTo(stream)
    finally:
        stream.Close()
```

## 14.10 사용자 알림과 진행 표시

```python
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService
ns = Application.GetService[NotificationService]()
ns.AddInformationNotification(u"제목", u"설명", u"상세")
ns.AddWarningNotification(u"제목", u"설명", u"상세")
ns.AddErrorNotification(u"제목", u"설명", u"상세")
```

```python
# 진행 표시 + 취소 — 스크립트의 "트랜잭션으로 감싸기"를 꺼야 동작한다 (7.4)
from Spotfire.Dxp.Framework.ApplicationModel import ProgressService
ps = Application.GetService[ProgressService]()

def work():
    try:
        with ps.CurrentProgress.BeginSubtask(u"처리", 10, u"{0} / {1}"):
            for i in range(10):
                ps.CurrentProgress.CheckCancel()
                ps.CurrentProgress.TryReportProgress()
    except:
        pass

ps.ExecuteWithProgress(u"제목", u"설명", work)
```

## 14.11 환경 판별과 스크립트 관리

```python
# 지금 Analyst인가 Web Player인가 (직접 알려 주는 API는 없다)
isAnalyst = "RichAnalysisApplication" in Application.GetType().ToString()

# 로그인 사용자 이름
from System.Threading import Thread
print Thread.CurrentPrincipal.Identity.Name
```

```python
# 문서에 저장된 스크립트 목록 (Spotfire 12.0+)
for script in Document.ScriptManager.GetScripts():
    print script.Name, "|", script.Language.Language

# 이름으로 찾기 — out 매개변수는 튜플로 돌아온다
found, definition = Document.ScriptManager.TryGetScript(u"대시보드 초기화")

# 고치기 — ScriptDefinition 은 불변이라 복사본을 만들어 교체한다
if found:
    updated = definition.WithScriptCode(definition.ScriptCode.replace("0.5", "0.9"))
    Document.ScriptManager.Replace(definition, updated)
```

```python
# 북마크 — 이름 속성이 Name 이 아니라 DisplayName
for bookmark in Document.Bookmarks:
    print bookmark.DisplayName, bookmark.IsBroken
Document.Bookmarks[0].Apply()
```

```python
# 그래픽 표·KPI 차트의 클릭 액션 스크립트에서만 쓸 수 있는 객체
Context.Value                   # 클릭한 셀 값
Context.HierarchyPathValues[0]  # 같은 행의 기준 값
Context.Visualization           # 클릭된 미니어처 시각화
```

## 14.12 탐색용 스니펫

```python
# 객체의 멤버 보기
for m in dir(someObject):
    if not m.startswith("_"):
        print m

# 시각화 유형 식별자 전부 보기
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
for m in dir(VisualTypeIdentifiers):
    if not m.startswith("_"):
        print m

# 문서 구조 훑기
for page in Document.Pages:
    print u"[%s]" % page.Title
    for visual in page.Visuals:
        print u"   - %s (%s)" % (visual.Title, visual.TypeId.Name)

# 데이터 테이블/컬럼 훑기
for table in Document.Data.Tables:
    print u"%s (%d행)" % (table.Name, table.RowCount)
    for column in table.Columns:
        print u"   - %s : %s" % (column.Name, column.DataType)

# 마킹 이름 확인
for m in Document.Data.Markings:
    print m.Name
```

---

## FAQ

### Q. `pandas`나 `numpy`를 쓸 수 있나요?

**아니요.** IronPython은 C 확장 모듈을 로드하지 못합니다.
데이터 계산이 필요하면 **Python 데이터 함수(CPython)** 를 쓰세요. IronPython은 UI 제어용입니다.

### Q. Python 3 문법을 쓰면 안 되나요?

대부분 안 됩니다. f-string·타입 힌트·`async` 등은 문법 오류가 납니다.

다만 두 가지는 예외입니다.

- `print("hello")` 는 **정상 동작합니다.** `print` 가 문이고 괄호는 값을 감싼 것뿐이기 때문입니다.
  단 `print("a", "b")` 는 오류 없이 튜플 `('a', 'b')` 를 출력하므로 주의하세요.
- `from __future__ import print_function` / `division` 을 첫 줄에 넣으면
  해당 기능만 Python 3 방식으로 바뀝니다. (2.7.12에서 `print_function` 동작 확인)

자세한 내용은 [4.1 참조](04-python-syntax.html)

### Q. 스크립트끼리 변수를 공유할 수 있나요?

직접은 안 됩니다. **문서 속성**(`Document.Properties[...]`)을 전역 저장소로 쓰세요.

### Q. 마킹이 바뀔 때 스크립트를 자동 실행할 수 있나요?

마킹 변경에 직접 걸리는 훅은 없습니다. 실무에서는 **문서 속성 변경 트리거**를 쓰거나,
사용자가 누르는 버튼으로 실행합니다.

### Q. `Document`와 `Application.Document`는 다른가요?

같습니다. 짧은 `Document`를 쓰세요.

### Q. 시각화를 이름으로 찾는 게 왜 나쁜가요?

사용자가 제목을 바꾸면 스크립트가 조용히 실패합니다.
**스크립트 매개변수**로 시각화 객체를 직접 넘기세요 → [2.4 참조](02-getting-started.html)

### Q. `As[VisualContent]()`가 자꾸 실패합니다

텍스트 영역·필터 패널·Mod 시각화는 캐스팅되지 않거나 다른 속성 구조를 가집니다.
`try/except`로 감싸고 `TypeId`로 걸러 내세요 → [5.2 참조](05-dotnet-interop.html#52-ast)

### Q. `print` 출력이 안 보입니다

액션 컨트롤 버튼으로 실행하면 어디에도 표시되지 않습니다.
**스크립트 편집 창의 실행(Execute)** 버튼으로만 보입니다.
사용자에게 보여 주려면 문서 속성이나 `NotificationService`를 쓰세요.

### Q. 스크립트를 되돌릴 수 있나요?

**믿지 마세요.** 데이터 테이블 교체, 페이지·시각화 삭제, 축 일괄 변경은 복구가 어렵습니다.
반드시 사본에서 먼저 시험하세요 → [13.3 참조](13-tips.html)

### Q. Web Player에서 스크립트가 실패합니다

`MessageBox`, 파일 대화상자, 로컬 파일 쓰기는 브라우저에서 동작하지 않습니다.
→ [13.1 참조](13-tips.html)

### Q. 한글이 깨집니다

문자열에 `u` 접두사를 붙이고(`u"한글"`), 스크립트 첫 줄에 `# -*- coding: utf-8 -*-` 를 넣으세요.

### Q. API 문서는 어디서 보나요?

세 군데를 순서대로 쓰면 됩니다.

1. **[공식 API 레퍼런스](https://docs.tibco.com/pub/doc_remote/sfire_dev/area/doc/api/tib_sfire-analyst_api/index.aspx)**
   — 이름·시그니처·폐기 여부의 최종 근거. URL 규칙이 단순해서 주소창에 직접 치는 편이 빠릅니다
   → [6.10 참조](06-api-map.html)

   ```text
   .../html/T_Spotfire_Dxp_Application_Visuals_BarChart.htm
   ```

2. **[IronPython 예제 색인 (Spotfire Community)](https://community.spotfire.com/articles/spotfire/ironpython-scripting-in-spotfire/)**
   — "이런 걸 하고 싶다"에서 출발할 때. 데이터·시각화·필터/마킹·레이아웃·지도·문서·연동으로
   분류된 수백 개의 예제 링크가 있습니다
3. **[sf-ref.com](https://www.sf-ref.com/ironpython/)** — 시각화 유형별로 어떤 속성이
   있는지 훑을 때

셋 다 못 찾겠으면 `dir()`로 직접 탐색하는 편이 빠릅니다 → [7.6 참조](07-pitfalls.html)

### Q. 진행 표시줄을 띄우고 싶습니다

`ProgressService.ExecuteWithProgress(...)` 를 쓰고, 스크립트 편집 대화상자에서
**"트랜잭션으로 감싸기" 체크를 해제**하세요. 체크가 켜져 있으면 진행 표시가 뜨지 않습니다
→ [13.2 참조](13-tips.html)

### Q. 스크립트 중간에 문서 속성을 써도 화면에 안 나옵니다

정상입니다. 스크립트 전체가 하나의 트랜잭션이라 **끝날 때 한꺼번에** 반영됩니다.
로그를 리스트에 모았다가 마지막에 한 번 쓰세요 → [7.4 참조](07-pitfalls.html)

### Q. 그래픽 표에서 클릭한 값을 어떻게 받나요?

그래픽 표·KPI 차트의 **클릭 시 액션**으로 등록한 스크립트에서만 `Context` 객체를 쓸 수
있습니다. `Context.Value`, `Context.HierarchyPathValues[0]`, `Context.Visualization`
→ [2.3 참조](02-getting-started.html)

---

## 참고한 자료

### 시작점

- [IronPython Scripting in Spotfire® – Overview (Spotfire Community)](https://community.spotfire.com/articles/spotfire/ironpython-scripting-in-spotfire/)
  — 수백 개 예제의 분류 색인. 하고 싶은 일이 있으면 여기부터
- [Spotfire Analyst API Reference](https://docs.tibco.com/pub/doc_remote/sfire_dev/area/doc/api/tib_sfire-analyst_api/index.aspx)
  — 이름·시그니처·폐기 여부의 최종 근거 → [6.10](06-api-map.html)
- [The Spotfire IronPython Quick Reference (sf-ref.com)](https://www.sf-ref.com/ironpython/)
  — 시각화 유형별 속성 훑어보기
- [IronPython Example Scripts (Spotfire 제품 문서)](https://docs.tibco.com/pub/sfire-analyst/12.0.6/doc/html/en-US/TIB_sfire-analyst_UsersGuide/text/text_ironpython_example_scripts.htm)

### 이 교안이 근거로 삼은 공식 문서

| 교안의 내용 | 출처 |
|-------------|------|
| 7.4 트랜잭션·격리 실행·라이브러리 제약 | [How to develop IronPython scripts and their limitations](https://community.spotfire.com/s/article/How-to-develop-IronPython-scripts-in-TIBCO-Spotfire-and-their-limitations) |
| 7.4 ③ 스냅샷 오류 우회 | [Attempt take snapshot … 오류 해결](https://community.spotfire.com/s/article/how-troubleshoot-exception-thrown-when-executing-ironpython-script-error-attempt-take-snapshot) |
| 7.7 클라이언트 종류 판별 | [How to determine the client type](https://community.spotfire.com/s/article/how-determine-client-type-analyst-or-web-player-user-running-tibco-spotfire-using-ironpython) |
| 2.3 `Context` 객체 | [Miniature Visualization Action Scripts](https://community.spotfire.com/s/article/How-to-use-Miniature-Visualization-Action-Scripts-using-IronPython-in-TIBCO-Spotfire) |
| 2.5 TRACE 로깅·알림 | [Debugging IronPython Scripts in Spotfire®](https://community.spotfire.com/s/article/Debugging-IronPython-Scripts-TIBCO-Spotfire) |
| 6.8 · 예제 22 ScriptManager | [Introducing the Spotfire Script Management APIs](https://community.spotfire.com/articles/spotfire/introducing-the-spotfire-script-management-apis/) |
| 13.2 진행 표시·취소 | [Progress bar and cancellation option](https://community.spotfire.com/s/article/How-to-Add-Progress-Bar-and-Cancellation-Option-when-Executing-IronPython-Scripts-in-TIBCO-Spotfire) |

### 커뮤니티 예제 모음

- [essejhsif/spotfire — IronPython scripts for Spotfire](https://github.com/essejhsif/spotfire)
- [Gurudutt-Goswami/Spotfire-Ironpython](https://github.com/Gurudutt-Goswami/Spotfire-Ironpython)
- [How to Reset All Filters For All Filtering Schemes (Spotfire Community)](https://community.spotfire.com/articles/spotfire/how-to-reset-all-filters-for-all-filtering-schemes-in-spotfire-using-ironpython-scripting/)
- [How to export a visualization as an image using IronPython (Spotfire Community)](https://community.spotfire.com/articles/spotfire/how-to-export-a-visualization-as-an-image-in-spotfire-using-ironpython-scripting/)
- [Loop Through Pages and Visualization Using IronPython (Spotfire Community)](https://community.spotfire.com/articles/spotfire/loop-through-pages-and-visualization-spotfirer-using-ironpython-scripting/)

!!! warning "커뮤니티 코드를 그대로 쓰기 전에"
    위 저장소들의 스크립트는 대부분 2012~2021년에 작성된 것이라
    **마킹 이름을 하드코딩하고**(`Markings["Marking"]`), **로컬 경로를 박아 두고**,
    **`CreateDataWriter` 반환값을 확인하지 않습니다.**
    7장의 체크리스트로 한 번 걸러서 쓰세요.
