# 실측으로 확인된 API

Spotfire 14.x / IronPython 2.7.12에서 **여덟 차례 실행해 확인**한 결과입니다.
버전이나 라이선스에 따라 다를 수 있으니, 다르면 `dir()` 로 확인하세요.

## 존재하지 않는 이름 — 쓰지 말 것

| 틀린 이름 | 실제 | 왜 그럴듯한가 |
|-----------|------|---------------|
| `VisualTypeIdentifiers.TreemapChart` | `Treemap` | `BarChart`·`LineChart`와 대칭 |
| `IndexSet.Add(i)` | `AddIndex(i)` / `indexSet[i] = True` | 파이썬 `set`을 알면 당연한 이름 |
| `StdfDataSource(stream)` | 없음. `DataTableDataSource` 사용 | `StdfDataWriter`가 있으니 짝이 있을 듯 |
| `Visual.RenderSync` | `RenderAsync` 만 존재 | Async가 있으면 Sync도 있을 듯 |
| `ColumnSelection` | 없음 (`RowSelection` 만) | `RowSelection`이 있으니 |
| `DataSelection(...)` 직접 생성 | 추상 클래스. 마킹/필터링이 구체 클래스 | — |

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
