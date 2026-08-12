# 실측으로 확인된 API

Spotfire 14.x / IronPython 2.7.12에서 **여덟 차례 실행해 확인**한 결과입니다.
버전이나 라이선스에 따라 다를 수 있으니, 다르면 `dir()` 로 확인하세요.

맨 아래 "**문서로만 확인된 것**" 절은 실행해 보지 않았습니다. 구분해서 쓰세요.

## 존재하지 않는 이름 — 쓰지 말 것

| 틀린 이름 | 실제 | 왜 그럴듯한가 |
|-----------|------|---------------|
| `VisualTypeIdentifiers.TreemapChart` | `Treemap` | `BarChart`·`LineChart`와 대칭 |
| `IndexSet.Add(i)` | `AddIndex(i)` / `indexSet[i] = True` | 파이썬 `set`을 알면 당연한 이름 |
| `StdfDataSource(stream)` | 없음. `DataTableDataSource` 사용 | `StdfDataWriter`가 있으니 짝이 있을 듯 |
| `Visual.RenderSync` | `RenderAsync` 만 존재 | Async가 있으면 Sync도 있을 듯 |
| `ColumnSelection` | 없음 (`RowSelection` 만) | `RowSelection`이 있으니 |
| `DataSelection(...)` 직접 생성 | 추상 클래스. 마킹/필터링이 구체 클래스 | — |
| `TileMode.Grid` | `Horizontally`/`Vertically`/`Evenly`/`Maximize` | 격자니까 Grid일 듯 (API 문서 확인) |
| `Bookmark.Name` | `DisplayName` | 다른 객체는 `Name` 을 쓰니까 |
| `CancellationToken.None` | 파이썬 문법 오류. `CancellationToken()` | C# 코드를 그대로 옮기면 |

## 동작이 확인된 것

| API | 결과 |
|-----|------|
| `Page.Visible` | 읽기·쓰기 모두 동작 |
| `AxisRange(min, max)` / `AxisRange.DefaultRange` | 동작 |
| `vc.YAxis.Range` / `vc.XAxis.ZoomRange` | 쓰기 가능. 서로 다른 속성 |
| `vc.Data.WhereClauseExpression` | 쓰기 가능 |
| `vc.Data.DataTableReference` | 쓰기 가능 |
| `visual.TypeId` | 쓰기 가능 (유형 변경) |
| `vc.Legend.Visible`, `visual.Title` | 쓰기 가능 |
| `scatter.MarkerSize` | 쓰기 가능 (ScatterPlot 캐스팅 필요) |
| `scheme[table][column].Reset()` | 동작. 컬럼 단위 필터 초기화 |
| `scheme.ResetAllFilters()` | 동작 |
| `handle.Visible`, `panel.InteractiveSearchPattern` | 동작 |
| `VisualContent.Render(Graphics, Rectangle)` | 동작 (텍스트 영역은 실패) |
| `LayoutDefinition` + `page.ApplyLayout(layout)` | 동작. `BeginStackedSection(weight)` 인자 받음 |
| `TextDataReaderSettings` (`Separator`, `AddColumnNameRow`, `SetDataType`) | 동작 |
| `NotificationService.Add{Information,Warning,Error}Notification` | 동작 |
| `ProgressService` (`CurrentProgress`, `ExecuteWithProgress`) | 존재 |
| `DataTableDataSource(table, 마킹)` | **동작. 마킹된 행만 들어오고 생성 시점에 고정된다** |
| `TablePlot.ExportText(writer)` | 동작. 탭 구분 텍스트 |

## 조건부·환경 의존

| API | 주의 |
|-----|------|
| `Document.Data.CreateDataWriter(...)` | **라이선스가 없으면 예외 없이 `None` 반환** |
| `TablePlot.ExportData(식별자, 스트림)` | 시그니처는 맞지만 `cannot write from reader` 로 실패할 수 있음 |
| `TablePlot.ExportDataEnabled` | 내보내기 가능 여부를 코드에서 판별 |
| `DataTable.IsRefreshable` | 임베디드 데이터는 `False` |
| `Render` | 텍스트 영역에서 실패: `Attempt take snapshot on application thread` |

## 컬렉션 인덱싱

| 컬렉션 | `[0]` | `["이름"]` |
|--------|:-----:|:----------:|
| `Document.Data.Tables` | **불가** | 가능 |
| `table.Columns` | 가능 | 가능 |
| `Document.Pages` | 가능 | — |
| `Document.FilteringSchemes` | 가능 | — |

## 시각화 유형별 속성

| 시각화 | 캐스팅 | 가진 것 |
|--------|:------:|---------|
| 막대·선·산점도 | 성공 | 축·범례·데이터 전부 |
| `Table` | 성공 | `Data.*`, `Legend`, `TableColumns`, `SortInfos`. **축 없음** |
| `HtmlTextArea` | 성공 | **아무것도 없음** |

## 언어

| 항목 | 결과 |
|------|------|
| `print("hello")` | 동작 (괄호는 값을 감싼 것) |
| `print("a", "b")` | `('a', 'b')` 튜플 출력 — 함정 |
| `print("a", end="")` | `SyntaxError: unexpected token '='` |
| `from __future__ import print_function` | **지원됨** |
| `from __future__ import division` | **지원됨** |
| `3 / 4` | `0` |
| `type(u"한글")` / `type("한글")` | 둘 다 `str` — 같은 타입 |
| `len("한글")` | `2` — 바이트가 아니라 글자 수 |
| 표준 라이브러리 | `re math datetime json csv collections itertools os codecs random time string` 전부 가능 |

## `DataWriterTypeIdentifiers` 전체 (14.x)

```text
ExcelXlsDataWriter                 SpreadsheetDataSemicolonWriter
ExcelXlsxDataWriter                SpreadsheetDataWriter
SbdfDataWriter                     SpreadsheetUtf8DataWriter
SpreadsheetDataCsvUtf8Writer       StdfDataWriter
SpreadsheetDataCsvWriter           StdfOneDataWriter
SpreadsheetDataSemicolonUtf8Writer
```

## `Spotfire.Dxp.Data.Import` 의 DataSource 전체 (14.x)

```text
StdfFileDataSource    SbdfFileDataSource    SbdfLibraryDataSource
TextFileDataSource    DataTableDataSource   DatabaseDataSource
FileDataSource        InformationLinkDataSource
DataSourceFactory     FileDataSourceFactory
```

## 문서로만 확인된 것 (실행 안 해 봄)

Spotfire 15.0 API 레퍼런스와 공식 커뮤니티 문서에서 확인한 것입니다.
**실행 검증은 하지 않았습니다.** 쓰기 전에 `dir()` 로 한 번 걸러 보세요.

| API | 내용 |
|-----|------|
| `Document.ScriptManager` | `GetScripts()` · `TryGetScript(name)` → **튜플** · `GetAllScriptsWithName` · `AddScriptDefinition` · `Replace` · `Remove` · `ExecuteScript`. **Spotfire 12.0+** |
| `ScriptDefinition` | **불변**. `WithScriptCode` · `WithName` · `WithDescription` 로 복사본 생성. `IsEquivalentTo` 로 비교 |
| `Document.Bookmarks` | `Bookmark.DisplayName` · `IsBroken` · `Apply()` · `Update()`. `AddNew` 는 **폐기 예정** |
| `Visual.ShowTitle` / `Visual.Id` | 제목 표시 여부 / 이름이 바뀌어도 안 변하는 고유 ID |
| `Visual.AutoConfigure()` / `ApplyUserPreferences()` | 새로 만든 시각화 기본 설정 |
| `Visual.Render(gfx, rect)` | **폐기 예정(Obsolete)**. 14.x에서 동작은 확인됨 |
| `Visual.RenderAsync(RenderResultSettings, VisualRenderSettings, CancellationToken)` | `Task<RenderResult>` 반환. `.Result` 로 대기 |
| `RenderResultSettings(Size)` / `VisualRenderSettings()` | 후자는 `ShowTitle`·`ShowLegend`·`ShowAxisLabels`·`ShowAnnotations` |
| `RenderResult` | `IsValid` · `WriteTo(stream)`. `AsImage()` 는 **폐기 예정** |
| `Page.RenderAsync(...)` | 페이지 전체를 PNG로 |
| `Page.GetVisualBounds(visual, rect)` | 배치 비율에 맞는 사각형 |
| `Page.ApplyLayout(TileMode)` | `Horizontally` · `Vertically` · `Evenly` · `Maximize` |
| `ApplicationThread.InvokeAsynchronously(fn)` | 트랜잭션 밖에서 실행. 스냅샷 오류 우회 |
| `ProgressService.ExecuteWithProgress(title, desc, fn)` | `CurrentProgress` 의 `ExecuteSubtask` · `BeginSubtask(name, n, fmt)` · `CheckCancel()` · `TryReportProgress()`. **트랜잭션 래핑을 꺼야 동작** |
| `Application.GetType().ToString()` | Analyst = `...RichAnalysisApplication`, Web Player = `...WebAnalysisApplication` |
| `Context` (그래픽 표·KPI 클릭 액션 전용) | `Value` · `HierarchyPathValues` · `Visualization` |

## 트랜잭션 (공식 문서 근거)

- 스크립트는 **전체가 하나의 트랜잭션**으로 실행된다. 개별 변경은 끝날 때 한꺼번에 적용된다
- 그래서 중간에 쓴 `Document.Properties` 값은 화면에 나타나지 않는다
- 바꾼 속성의 재계산 결과를 같은 스크립트에서 읽을 수 없다
- 스냅샷이 필요한 작업(렌더링)은 `Attempt take snapshot on application thread in state 'Executing'` 로 실패한다
- 스크립트 대화상자의 **"트랜잭션으로 감싸기"** 를 끄면 진행 표시가 가능해지지만 Undo 를 잃는다

## 확인하는 방법

```python
DOTNET_BASE = ["Equals", "GetHashCode", "GetType", "MemberwiseClone",
               "ReferenceEquals", "ToString"]

def members(obj):
    return [n for n in dir(obj)
            if not n.startswith("_") and n not in DOTNET_BASE]

print members(someObject)
print someObject.SomeMethod.__doc__      # 시그니처와 오버로드
```
