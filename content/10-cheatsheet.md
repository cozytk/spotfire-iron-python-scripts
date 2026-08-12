# 10. 치트시트 & FAQ

필요할 때 바로 복사해 쓰는 한 장 요약입니다.

## 10.1 import 모음

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

# 필터
import Spotfire.Dxp.Application.Filters as filters
from Spotfire.Dxp.Application.Filters import FilterTypeIdentifiers

# 서비스
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService

# .NET
from System import Array, String, Guid, DateTime
from System.IO import File, Path, Directory, MemoryStream, StreamWriter, SeekOrigin
from System.Threading import Thread

import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
```

## 10.2 페이지와 시각화

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
```

## 10.3 시각화 속성

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
```

## 10.4 데이터

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

## 10.5 마킹

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

## 10.6 필터

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

# 필터 패널 표시/숨김
Document.ActivePageReference.FilterPanel.Visible = False
```

## 10.7 문서 속성

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

## 10.8 내보내기

```python
# 데이터
from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from System.IO import File

writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.ExcelXlsDataWriter)
filtered = Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()
names = [c.Name for c in table.Columns]

stream = File.OpenWrite("C:/out/data.xls")
writer.Write(stream, table, filtered, names)
stream.Close()
```

```python
# 이미지
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

## 10.9 사용자 알림

```python
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService
ns = Application.GetService[NotificationService]()
ns.AddInformationNotification(u"제목", u"설명", u"상세")
ns.AddWarningNotification(u"제목", u"설명", u"상세")
```

## 10.10 탐색용 스니펫

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

안 됩니다. `print(...)`는 우연히 동작하는 경우가 있지만, f-string·타입 힌트·`async` 등은
문법 오류가 납니다. **Python 2.7 문법**으로 쓰세요 → [2장](02-python-syntax.html)

### Q. 스크립트끼리 변수를 공유할 수 있나요?

직접은 안 됩니다. **문서 속성**(`Document.Properties[...]`)을 전역 저장소로 쓰세요.

### Q. 마킹이 바뀔 때 스크립트를 자동 실행할 수 있나요?

마킹 변경에 직접 걸리는 훅은 없습니다. 실무에서는 **문서 속성 변경 트리거**를 쓰거나,
사용자가 누르는 버튼으로 실행합니다.

### Q. `Document`와 `Application.Document`는 다른가요?

같습니다. 짧은 `Document`를 쓰세요.

### Q. 시각화를 이름으로 찾는 게 왜 나쁜가요?

사용자가 제목을 바꾸면 스크립트가 조용히 실패합니다.
**스크립트 매개변수**로 시각화 객체를 직접 넘기세요 → [1.4 참조](01-getting-started.html#14)

### Q. `As[VisualContent]()`가 자꾸 실패합니다

텍스트 영역·필터 패널·Mod 시각화는 캐스팅되지 않거나 다른 속성 구조를 가집니다.
`try/except`로 감싸고 `TypeId`로 걸러 내세요 → [3.2 참조](03-dotnet-interop.html#32-ast)

### Q. `print` 출력이 안 보입니다

액션 컨트롤 버튼으로 실행하면 어디에도 표시되지 않습니다.
**스크립트 편집 창의 실행(Execute)** 버튼으로만 보입니다.
사용자에게 보여 주려면 문서 속성이나 `NotificationService`를 쓰세요.

### Q. 스크립트를 되돌릴 수 있나요?

**믿지 마세요.** 데이터 테이블 교체, 페이지·시각화 삭제, 축 일괄 변경은 복구가 어렵습니다.
반드시 사본에서 먼저 시험하세요 → [9.3 참조](09-tips.html#93-undo)

### Q. Web Player에서 스크립트가 실패합니다

`MessageBox`, 파일 대화상자, 로컬 파일 쓰기는 브라우저에서 동작하지 않습니다.
→ [9.1 참조](09-tips.html#91-analyst-web-player)

### Q. 한글이 깨집니다

문자열에 `u` 접두사를 붙이고(`u"한글"`), 스크립트 첫 줄에 `# -*- coding: utf-8 -*-` 를 넣으세요.

### Q. API 문서는 어디서 보나요?

Spotfire 공식 API 레퍼런스(`Spotfire.Dxp.*`)를 보세요. C# 시그니처로 되어 있는데,
IronPython으로 옮기는 규칙은 [3.8](03-dotnet-interop.html#38-api)에 정리해 두었습니다.
문서를 못 찾겠으면 `dir()`로 직접 탐색하는 편이 빠릅니다.

---

## 참고한 자료

- [IronPython Scripting in Spotfire® – Overview (Spotfire Community)](https://community.spotfire.com/articles/spotfire/ironpython-scripting-in-spotfire/)
- [essejhsif/spotfire — IronPython scripts for Spotfire](https://github.com/essejhsif/spotfire)
- [Gurudutt-Goswami/Spotfire-Ironpython](https://github.com/Gurudutt-Goswami/Spotfire-Ironpython)
- [IronPython Example Scripts (Spotfire 제품 문서)](https://docs.tibco.com/pub/sfire-analyst/12.0.6/doc/html/en-US/TIB_sfire-analyst_UsersGuide/text/text_ironpython_example_scripts.htm)
- [The Spotfire IronPython Quick Reference](https://www.sf-ref.com/ironpython/visualizations/common-operations/referencing-visualizations/)
- [How to Reset All Filters For All Filtering Schemes (Spotfire Community)](https://community.spotfire.com/articles/spotfire/how-to-reset-all-filters-for-all-filtering-schemes-in-spotfire-using-ironpython-scripting/)
- [How to export a visualization as an image using IronPython (Spotfire Community)](https://community.spotfire.com/articles/spotfire/how-to-export-a-visualization-as-an-image-in-spotfire-using-ironpython-scripting/)
- [Loop Through Pages and Visualization Using IronPython (Spotfire Community)](https://community.spotfire.com/articles/spotfire/loop-through-pages-and-visualization-spotfirer-using-ironpython-scripting/)
