# API 검증 하네스와 실측 기록

교안의 예제가 **실제 Spotfire에서 동작하는지** 확인하는 스크립트와, 그 결과 기록입니다.
교안 예제가 아니므로 `scripts/` 와 분리해 두었습니다.

2026년 8월, 예제 21종을 **여덟 차례에 걸쳐 실제 환경에서 검증**했습니다.
그 과정에서 나온 교훈은 교안 [7장 · 스크립팅의 현실](https://cozytk.github.io/spotfire-iron-python-scripts/07-pitfalls.html)
로 정리했습니다. 아래는 원본 기록입니다.

> 차수별 실행 결과 원본은 GitHub 이슈 #2 ~ #9 에도 남아 있습니다.

---

## 먼저 이것부터 — 예제 27종 일괄 검증

예제를 하나씩 실제로 돌리는 것은 현실적이지 않으므로,
**예제 27개가 쓰는 API를 한 번에 확인하는 하네스**를 만들었습니다.

### [`00_verify_all_examples.py`](00_verify_all_examples.py)

이 파일 하나면 대부분이 확인됩니다. 예제별로 `통과 / 일부실패 / 실패` 를 판정하고
마지막에 요약표를 출력합니다.

**안전 설계**

| 동작 | 처리 방식 |
|------|-----------|
| 읽기 | 그대로 수행 |
| 쓰기 | **현재 값을 읽어 같은 값을 다시 쓰기** — setter 만 확인되고 값은 안 바뀜 |
| 파괴적 동작 (삭제·테이블 교체·페이지 생성·파일 쓰기) | **호출하지 않음.** 메서드 존재만 확인하고 `[SKIP]` 표시 |

`[SKIP]` 은 실패가 아니라 **일부러 안 한 것**입니다.

**실행 요령**

- 막대·선·산점도·표·교차표·텍스트 영역이 **여러 종류 섞인 페이지**를 활성 페이지로 두세요.
  없는 유형은 `[SKIP]` 으로 빠지므로, 섞여 있을수록 확인 범위가 넓어집니다.
- 문서 속성 `ScriptLog` 가 없으면 예제 1에서 `[NO]` 가 납니다. 정상입니다(속성을 안 만든 것뿐).
- 값을 바꾸지 않도록 설계했지만, 그래도 **사본에서 실행**하시길 권합니다.
- 출력이 100줄쯤 됩니다. 전체를 붙여 주셔도 되고, **마지막 "요약" 절만** 주셔도 큰 도움이 됩니다.

---

## 검증 완료

**예제 1~21은 전부 실제 Spotfire에서 확인했습니다.** (Spotfire 14.x / IronPython 2.7.12)

교안을 고친 뒤 회귀 확인이 필요하면 `00_verify_all_examples.py` 를 다시 돌리세요.
하네스에는 **아직 실측하지 않은 예제 22~27의 API 존재 확인**도 넣어 두었으므로,
한 번 돌리면 아래 표의 상당 부분이 채워집니다.

### 아직 확인하지 않은 것

나중에 추가한 항목들입니다. **Spotfire 15.0 API 레퍼런스와 공식 커뮤니티 문서를
근거로 작성했고, 실행해 보지는 않았습니다.** 교안에도 그렇게 표시해 두었습니다.

| 대상 | 확인할 것 |
|------|-----------|
| 예제 22 (스크립트 인벤토리) | `Document.ScriptManager.GetScripts()` 가 14.x에 있는지. `ScriptDefinition` 의 `Name`·`Language.Language`·`ScriptCode`·`Parameters` 접근 |
| 예제 23 (환경 진단) | `Application.GetType().ToString()` 의 실제 반환 문자열. `scheme.FilteringSelectionReference.Name` 접근 |
| 예제 24 (툴팁 통일) | `vc.Details.Items` 순회·`AddExpression`·`InsertExpression`·항목의 `Visible` |
| 예제 25 (축 서식) | `DataType.<T>.CreateLocalizedFormatter()` 와 `Scale.Formatting.<T>Formatter` 속성명, `ShortFormattingEnabled` 유무 |
| 예제 26 (마킹 행 태그) | `column.As[TagsColumn]()` 캐스팅과 `Tag(value, RowSelection)` 시그니처 |
| 예제 27 (포커스 모드) | `vc.Data.Filterings` 의 `Contains`·`Add`·`Remove`, `LimitingMarkingsEmptyBehavior` 쓰기 |
| 7.4 ③ 스냅샷 우회 | `Document.GetService(ApplicationThread)` 와 `InvokeAsynchronously` 로 텍스트 영역까지 렌더링되는지 |
| 예제 14 RenderAsync | `RenderResultSettings(Size)` · `VisualRenderSettings()` · `task.Result` · `result.WriteTo(stream)` |
| 13.2 진행 표시 | `ProgressService.ExecuteWithProgress` + 트랜잭션 래핑 해제 |
| `Visual.ShowTitle` / `Visual.Id` | 읽기·쓰기 동작 |
| `Document.Bookmarks` | `DisplayName` · `IsBroken` · `Apply()` |
| `page.ApplyLayout(TileMode.Evenly)` | 배치 동작 |

확인하기 가장 빠른 방법은 **예제 23을 먼저 돌려 보는 것**입니다.
그 뒤 개별 API는 `dir()` 과 `__doc__` 으로 봅니다.

```python
print hasattr(Document, "ScriptManager")
print hasattr(Document, "Bookmarks")
print Application.GetType().ToString()

for v in Document.ActivePageReference.Visuals:
    print v.Id, "|", v.ShowTitle, "|", v.Title
    break
```

교안 내용을 크게 바꿨다면 아래 순서를 권합니다.

1. `python build.py && python extract_scripts.py`
2. Spotfire 사본에서 `00_verify_all_examples.py` 실행
3. 요약표에서 `[NO]` 가 늘었는지 확인

---

## 확인 완료

### 1차 — print 동작 (2026-08-12)

**환경: IronPython 2.7.12 (2.7.12.1000), .NET Framework 4.8.9332.0 (64-bit)**

| 테스트 | 결과 | 결론 |
|--------|------|------|
| `print("hello")` | `hello` | 정상 동작. 괄호는 값을 감싼 것일 뿐 |
| `print("a", "b")` | `('a', 'b')` | **튜플 출력.** `print` 는 문(statement)이 맞음 |
| `3 / 4` | `0` | 정수 나눗셈 확인 |
| `__builtin__` 에 `print` | `True` | 함수 객체 자체는 존재 |
| `print("a", end="")` | `SyntaxError: unexpected token '='` | 예상대로 실패 |
| `from __future__ import print_function` + `sep="-"` | `a-b` | **지원됨** |

**결정적 증거** — `print("a", end="")` 의 오류 스택:

```text
IronPython.Compiler.Parser.ParsePrintStmt()
```

파서가 이 줄을 **print 문**으로 처리하다 `=` 에서 실패했다는 뜻입니다.
`print` 가 함수였다면 호출식(call expression) 파싱 경로가 찍혔을 것입니다.

**교안 반영 완료**

- 4.1 — `print("hello")` 가 동작하는 이유, `print(a, b)` 함정, `__future__` 사용법 추가
- 7.5 — AI 검증 체크리스트 1번을 "인자 2개 이상인 `print(a, b)`" 로 정정
- 13 FAQ — Python 3 문법 답변에 예외 두 가지 추가
- 버전 정보 — 확인 환경 명시

### 1차 추가 확인 — 문자열 타입

```text
type(u"한글") -> [type 'str']
type("한글")  -> [type 'str']
```

**IronPython에서는 `str` 과 `unicode` 가 같은 타입입니다.**
.NET의 `System.String` 이 이미 UTF-16이라 CPython 2처럼 바이트열/유니코드로
나뉘지 않습니다.

다만 이것이 "`u` 접두사가 불필요하다"는 뜻인지는 **`len` 값을 봐야 확정**됩니다.

- `len("한글") == 2` 이면 → 진짜 유니코드. `u` 접두사는 선택 사항
- `len("한글") == 6` 이면 → UTF-8 바이트열. `u` 접두사 필요

`01_environment.py` 의 3번 항목에 `len` 확인이 들어 있습니다.
결과가 나오면 교안 4장의 "한글에는 `u` 를 붙이세요" 서술을 정확하게 고치겠습니다.

`__future__ division` 확인도 `01_environment.py` 에 포함했습니다.

---

### 2차 — 환경·API 실측 (2026-08-12)

**환경: IronPython 2.7.12 / .NET Framework 4.8 (64-bit) / Spotfire 14.x**

#### 언어·환경

| 항목 | 결과 |
|------|------|
| `from __future__ import division` | **지원** (`3/4` → `0.75`, `3//4` → `0`) |
| `type(u"한글")` / `type("한글")` | 둘 다 `str` — **같은 타입** |
| `len(u"한글")` / `len("한글")` | 둘 다 `2` — **바이트가 아니라 글자 수** |
| 표준 라이브러리 | `re math datetime json csv collections itertools os codecs random time string` 전부 OK |
| `clr`, `System.IO`, `System.DateTime`, `List[str]` | 전부 OK |
| `Application` 실제 타입 | `RichAnalysisApplication` |

→ **`u` 접두사는 정확성을 위해 필요하지 않습니다.** 교안에서는 의도 표현과 이식성을
이유로 계속 쓰되, "필요하다"는 서술은 정정했습니다.

#### 교안 오류 발견

| 문제 | 실제 | 반영 |
|------|------|------|
| `VisualTypeIdentifiers.TreemapChart` | **`Treemap`** 이 맞음 | 예제 3, 6장 수정 |
| `StdfDataSource` | **존재하지 않음** | 예제 10 보류, 3차에서 확정 |
| `RenderSync` | **없음.** `RenderAsync` 만 존재 | 예제 8 수정 |
| 마킹 이름 `"Marking"` | 한국어 UI에서는 **`"마킹"`** | 예제 10·19, 12장 수정 |
| `Document.Data.Tables[0]` | `expected str, got int` 로 추정 실패 | 5장 수정, 3차에서 확정 |

#### 확정된 API (교안의 "버전 확인 필요" 표시 제거)

| 항목 | 결과 |
|------|------|
| `Page.Visible` | 읽기·쓰기 모두 동작 |
| `AxisRange.DefaultRange` / `AxisRange(0, 100)` | 동작 |
| `LayoutDefinition` | `Add` `BeginSideBySideSection` `BeginStackedSection` `EndSection` 존재 |
| `BeginStackedSection(weight)` | **인자 받는 형태로 동작.** `ApplyLayout` 성공 |
| `Visuals.AddNew[BarChart]()` 반환형 | `BarChart`(콘텐츠). 컨테이너는 `Visual` — 예제 21의 경고가 맞았음 |
| `VisualContent.Render(Graphics, Rectangle)` | 동작 |
| `NotificationService` | `Add{Information,Warning,Error}Notification` + `...WithActions` |
| `ProgressService` | `CurrentProgress`, `ExecuteWithProgress`, `BackgroundProgresses` |
| `TextDataReaderSettings` | `Separator`, `AddColumnNameRow`, `SetDataType` 존재 |
| `scheme.ResetAllFilters()` | 스킴 3개 모두 존재 |

#### 시각화 유형별 속성 (일괄 처리 루프 설계 근거)

| 시각화 | 확인된 것 |
|--------|-----------|
| `Table` | `Data.*`, `Legend.Visible`, `TableColumns`, `SortInfos` — **축(`XAxis`/`YAxis`) 없음** |
| `HtmlTextArea` | `As[VisualContent]()` **캐스팅은 성공하지만 속성이 하나도 없음** |

→ **캐스팅 성공만으로는 대상을 걸러낼 수 없습니다.** 속성별 `try/except` 가 필요하다는
교안의 설계가 실측으로 뒷받침되었습니다.

#### `DataWriterTypeIdentifiers` 전체 (14.x)

```text
ExcelXlsDataWriter                 SpreadsheetDataSemicolonWriter
ExcelXlsxDataWriter                SpreadsheetDataWriter
SbdfDataWriter                     SpreadsheetUtf8DataWriter
SpreadsheetDataCsvUtf8Writer       StdfDataWriter
SpreadsheetDataCsvWriter           StdfOneDataWriter
SpreadsheetDataSemicolonUtf8Writer
```

→ **CSV writer 가 있습니다.** 한글이 있으면 `SpreadsheetDataCsvUtf8Writer`.
예제 9를 이걸로 바꿨습니다.

#### `Spotfire.Dxp.Data.Import` 의 DataSource 전체 (14.x)

```text
StdfFileDataSource    SbdfFileDataSource    SbdfLibraryDataSource
TextFileDataSource    DataTableDataSource   DatabaseDataSource
FileDataSource        InformationLinkDataSource
DataSourceFactory     FileDataSourceFactory
```

#### 렌더링 실패 사례

텍스트 영역에서 `Render` 실패:

```text
Attempt take snapshot on application thread in state 'Executing'.
```

→ 예제 8의 `try/except` + 실패 목록 보고 구조가 필요한 이유입니다.


---

### 3차 — 예제 21종 일괄 검증 (2026-08-12)

**결과: 통과 16 / 21**

활성 페이지에 `Table` 과 `HtmlTextArea` 만 있어서 축 관련 항목은 `[SKIP]` 되었습니다.

#### 새로 발견한 교안 오류

| 문제 | 실제 | 반영 |
|------|------|------|
| `IndexSet.Add(i)` | **`Add` 메서드가 없음** (`hasattr` → `False`) | 예제 12, 6장 수정 → `indexSet[i] = True` |
| 예제들이 `Document.Properties["ScriptLog"]` 에 쓰는데 속성이 없으면 실패 | `The property named 'ScriptLog' could not be found.` | 8장에 **사전 준비 절** 신설 + `scripts/00_setup_document_properties.py` 추가 |
| 예제 12가 여전히 `MARKING_NAME = "Marking"` 사용 | 한국어 UI는 `"마킹"` | 예제 12도 `ActiveMarkingSelectionReference` 로 교체 |

#### 하네스(제 검증 스크립트) 버그 — 교안 문제 아님

| 증상 | 원인 |
|------|------|
| `[NO] CreateDataWriter(Equals)` 등 6건 | `dir()` 결과에서 .NET 기본 메서드를 안 걸렀음 |
| `VisualTypeIdentifiers 31종` | 같은 이유. 실제 시각화 유형은 25종 |
| 예제 18 `scheme[table][column]` 실패 | 검사 코드가 `Tables[0]` 을 씀. 예제 18 본문은 순회하므로 무관할 가능성이 높음 → 3차 확인 대상 |

#### 확정된 것

| 항목 | 결과 |
|------|------|
| `Data.WhereClauseExpression` 쓰기 | 가능 (예제 2) |
| `Legend.Visible`, `visual.Title` 쓰기 | 가능 (예제 4) |
| `Data.DataTableReference` 쓰기 | 가능 (예제 5) |
| `visual.TypeId` 쓰기 | 가능 (예제 17) |
| `Page.Visible` 쓰기 | 가능 (예제 15) |
| `FilterHandle.Visible` 쓰기 | 가능 (예제 16) |
| `FilterPanel` 구조 | 테이블 그룹 5개 / 필터 핸들 59개, `Expanded`·`SubGroups`·`Modified`·`InteractiveSearchPattern` 전부 존재 |
| `ActiveMarkingSelectionReference.Name` | `"마킹"` — 한국어 UI 확인 |
| `CalculatedColumn` import | 성공 (예제 20의 계산된 컬럼 감사) |
| `DataTable.Refresh` | 5개 테이블 모두 존재 |

#### 참고 — 확인된 문서 속성 목록

```text
Description, Keywords, AllowWebPlayerResume, PublicBookmarkCreation,
PrivateBookmarkCreation, spotfire.Comments, MaxMissingTimeParts,
FiscalYearOffset, Preview.Thumb, Preview.Mode, 최대, 최소, token
```

앞의 10개는 Spotfire 내장 속성이고, `최대`·`최소`·`token` 이 사용자가 만든 것입니다.

---

### 4차 — 스냅샷/인덱싱 확인 (2026-08-12)

#### 확정

| 항목 | 결과 |
|------|------|
| `Document.Data.Tables[0]` | **`expected str, got int`** — 숫자 인덱스 불가 확정 |
| `Document.FilteringSchemes[0]` | 가능 |
| `table.Columns[0]` | 가능 |
| `Document.Pages[0]` | 가능 |

→ **예제 18의 실패는 제 검증 하네스 버그였습니다.** 하네스가 `Tables[0]` 을 썼기 때문이고,
예제 18 본문은 `for dataTable in Document.Data.Tables:` 로 순회하므로 영향이 없습니다.
5장에 컬렉션별 인덱싱 표를 넣었습니다.

#### 새로 드러난 문제 — 데이터 내보내기 API

```python
writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.SbdfDataWriter)
writer.Write(stream, table, rows, columnNames)
# -> 'NoneType' object has no attribute 'Write'
```

**호출은 예외 없이 지나가는데 반환값이 `None`** 입니다. `SbdfDataWriter` 와
`StdfDataWriter` 둘 다 같습니다.

이 때문에 **예제 9(데이터 내보내기)와 예제 10(마킹 스냅샷)이 모두 막혔습니다.**
두 예제에 경고를 달고 5차 확인(`08_data_export_api.py`)으로 넘겼습니다.

#### 또 하나의 하네스 버그

3차에서 `CreateDataWriter(SbdfDataWriter) 성공` 으로 보고했던 것은 **오보고**였습니다.
반환값을 확인하지 않고 호출만 해 봤기 때문입니다. `None` 체크를 추가했습니다.

> 교훈: "예외가 안 났다"와 "동작한다"는 다릅니다.
> 검증 코드는 **반환값까지 확인**해야 합니다.

#### 대안 후보

| 후보 | 상태 |
|------|------|
| `DataTableDataSource(table)` | **생성 성공.** 단 테이블 전체를 복사함 |
| `TablePlot.ExportText(writer)` | 5차에서 확인 예정 |
| `TablePlot.ExportData(...)` | 5차에서 확인 예정 |


---

### 5차 — 내보내기 API 정밀 조사 (2026-08-12)

#### `CreateDataWriter` 는 코드 문제가 아니다

```text
CreateDataWriter(self: DataManager, typeId: TypeIdentifier) -> DataWriter
```

시그니처는 정상인데 **모든 식별자에 대해 `None` 을 반환**합니다
(Sbdf / Stdf / Excel / CSV 전부). 예외도 나지 않습니다.
`Application.GetService[DataManager]()` 로 얻은 객체는 `Document.Data` 와
**같은 객체**이고 결과도 동일했습니다.

→ 호출 방식 문제가 아니라 **환경 제약**(라이선스 또는 배포 설정으로 데이터 내보내기
비활성화)으로 보입니다. 표 시각화에 `ExportDataEnabled` 속성이 따로 있는 것이 방증입니다.
예제 9에 이 내용을 명시하고, 오류가 났을 때 코드가 아니라 권한을 확인하도록 안내했습니다.

#### 예제 10의 정답 — `DataSelection`

```text
DataTableDataSource(dataTable: DataTable)
DataTableDataSource(dataTable: DataTable, updateBehavior: DataTableDataSourceUpdateBehavior)
DataTableDataSource(dataTable: DataTable, dataSelection: DataSelection)
```

세 번째 오버로드가 **행 부분집합을 직접 받습니다.**
writer · 메모리 스트림 · STDF/SBDF 변환이 전부 불필요해집니다.
게다가 내보내기 권한 제약의 영향도 받지 않습니다.

원래 예제보다 훨씬 단순하고 견고한 코드가 됩니다.

#### 확인된 대안 경로

| 경로 | 상태 |
|------|------|
| `TablePlot.ExportText(writer)` | **존재 확인** |
| `TablePlot.ExportData(...)` | 존재 확인 |
| `TablePlot.ExportDataEnabled` | 존재 확인 — 내보내기 가능 여부를 코드에서 판별 가능 |
| `DataTable.ExportDataToLibrary(...)` | 존재 확인 — 라이브러리 저장이라 Web Player 안전 |
| `Spotfire.Dxp.Data.Export.DataWriterFactory` | 존재. 시그니처 확인 중 |

#### `Spotfire.Dxp.Data.Export` 전체

```text
DataWriter    DataWriterFactory    DataWriterTypeIdentifiers    OutputFileTypes
```

`DataWriter` 는 추상 클래스입니다 (`CanWriteFromReader`, `Write`, `WriteCore`).


---

### 6차 — 차트 페이지 재실행 + 내보내기 확정 (2026-08-12)

**결과: 통과 17 / 21** (차트가 있는 페이지에서 실행하여 축 관련 항목이 모두 검증됨)

#### 축 관련 항목 전부 확인

| 항목 | 결과 |
|------|------|
| `YAxis.Expression` 쓰기 | 가능 (예제 3) |
| `SizeAxis.Expression` 쓰기 | 가능 (예제 3) |
| `MarkerSize` 쓰기 | 가능 (예제 4) |
| `XAxis.ZoomRange` 쓰기 | 가능 (예제 6) |
| `YAxis.Range` 쓰기 | 가능 (예제 7) |
| `Trellis.PanelAxis.Expression` 읽기 | 가능 (예제 20) |
| `Render` | 차트 4개 성공, 텍스트 영역만 실패 (예제 8) |

#### 예제 18 확정 — 하네스 버그가 맞았음

```text
scheme[table][column]  ->  Step: (KB073100, KB268900, KB425000)
Reset 존재: True
```

3차에서 실패로 나온 것은 검사 코드가 `Tables[0]` 을 썼기 때문이었고,
**예제 18 본문은 정상**입니다.

#### 예제 9의 답 — `ExportData` (시그니처 확정)

```text
ExportData(self: TablePlot, typeIdentifier: TypeIdentifier, stream: Stream)
ExportText(self: TablePlotBase, writer: TextWriter)
ExportDataToLibrary(self: DataTable, libraryItem: LibraryItem, title: str) -> LibraryItem
```

`CreateDataWriter` 를 거치지 않고 **식별자와 스트림을 직접** 넘길 수 있습니다.
예제 9를 이 방식으로 재작성했습니다. `ExportDataEnabled` 는 `True` 였습니다.

#### `CreateDataWriter` 가 `None` 인 이유 — 라이선스

`DataWriterFactory` 의 멤버에 결정적 단서가 있었습니다.

```text
Create  CreateCore  DataWriterType  Description  DisplayName
IsLicensed  IsUiVisible  SupportedFileExtension  TypeId  requiredLicenses
```

**`IsLicensed` 와 `requiredLicenses`** — writer 종류마다 라이선스가 걸려 있고,
없으면 조용히 `None` 이 돌아오는 구조로 보입니다. 코드 문제가 아닙니다.

#### 예제 10 — `DataSelection` 은 추상 클래스

```text
Cannot create instances of DataSelection because it is abstract
```

직접 만들 수 없습니다. 대신 **마킹과 필터링이 `DataSelection` 의 구체 클래스**일
가능성이 높아, `DataTableDataSource(table, 마킹)` 형태를 7차에서 확인합니다.

참고로 `ColumnSelection` 은 존재하지 않았고, `RowSelection` 생성자는 이렇습니다.

```text
RowSelection(rowCount: int, includedRows: IEnumerable[int])
RowSelection(indexSet: IndexSet)
```

#### `IndexSet` 실제 멤버 — `AddIndex` 가 있다

```text
AddIndex  AddIndexes  RemoveIndex  RemoveIndexes  Item
And  Or  Not  Xor  Subtract  Intersects
Clear  Fill  Clone  Contains  HasIndex  Count  Capacity
First  Last  IsEmpty  IsFull  GetNextIndex  GetPreviousIndex
```

`indexSet[i] = True` 인덱서도 동작하지만, **`AddIndex(i)` 가 의도가 더 분명**합니다.
예제 12를 `AddIndex` 로 바꿨습니다.

#### 남은 하네스 버그

예제 1 검사가 `contents[0]` (첫 시각화)을 쓰는데, 그것이 텍스트 영역이면
`'HtmlTextArea' object has no attribute 'Data'` 가 납니다.
**예제 1 본문은 `try/except` 로 감싸므로 무관**합니다.


---

### 7차 — 내보내기 경로 확정 (2026-08-12)

#### 예제 10 해법 확정

```text
마킹 타입   : DataMarkingSelection     isinstance(마킹, DataSelection)   -> True
필터링 타입 : DataFilteringSelection   isinstance(필터링, DataSelection) -> True

DataTableDataSource(table, 마킹)   -> 생성 성공
DataTableDataSource(table, 필터링) -> 생성 성공
```

**마킹과 필터링이 곧 `DataSelection` 의 구체 클래스**입니다.
별도 객체를 만들 필요 없이 그대로 넘기면 됩니다. 예제 10을 이 방식으로 교체했습니다.

보너스로 **필터링을 넘기면 "현재 필터를 통과한 행만" 새 테이블**이 됩니다.
같은 코드로 두 가지 기능이 나옵니다.

`DataTableDataSourceUpdateBehavior` 값은 `Automatic` 과 `Manual` 두 가지인데,
`(dataTable, updateBehavior)` 오버로드에서만 지정 가능하므로 `dataSelection` 과
동시에 줄 수는 없습니다.

#### 예제 9 — `ExportData` 도 실패, `ExportText` 만 동작

| 경로 | 결과 |
|------|------|
| `Document.Data.CreateDataWriter(...)` | `None` 반환 |
| `TablePlot.ExportData(식별자, 스트림)` | **실패** |
| `TablePlot.ExportText(writer)` | **성공** (408,144 글자, 탭 구분) |

`ExportData` 의 실패 메시지가 결정적이었습니다.

```text
The writer with typeidentifier Spreadsheet CSV UTF8 data writer cannot write from reader.
```

`DataWriter` 에 `CanWriteFromReader` 멤버가 있는 것으로 보아, 이 writer 들이
**reader 기반 쓰기를 지원하지 않는** 구조입니다.
6차에서 `ExportData` 를 "권장"으로 적었던 것은 시그니처만 보고 판단한 것이라 틀렸습니다.

**예제 9를 `ExportText` 기준으로 다시 썼습니다.** 출력이 탭 구분이므로
CSV 변환 코드와, 모든 표를 한 번에 내보내는 일괄 코드를 함께 넣었습니다.

> 교훈: 시그니처가 맞다고 동작하는 것은 아닙니다.
> 5차에서 `ExportData` 시그니처를 확인하고 "확정"이라고 했지만, 실제로 호출해 보니
> 실패했습니다. **호출까지 해 봐야 검증입니다.**


---

### 8차 — 예제 10 최종 확정 (2026-08-12)

```text
10행 마킹 -> 새 테이블 생성    -> 새 테이블 10행   [OK] 부분집합 적용됨
마킹을 20행으로 변경           -> 새 테이블 10행   변하지 않음
새 테이블의 IsRefreshable      -> False
```

**결론: 생성 시점에 고정되는 진짜 스냅샷입니다.**

`DataTableDataSource(sourceTable, 마킹)` 세 줄이면 끝나고, 이후 마킹을 바꿔도
스냅샷은 그대로 남습니다. 원래 의도했던 동작 그대로입니다.

예제 10을 최종본으로 교체했습니다. 필터링을 넘기는 변형도 함께 넣었습니다.

---

## 최종 정리 — 이 검증으로 잡은 교안 오류

여덟 차례 실행을 통해 **교안 오류 8건**과 **검증 스크립트 자체의 버그 4건**을 잡았습니다.

### 교안 오류 (실제로 깨지던 것)

| # | 문제 | 실제 |
|---|------|------|
| 1 | `VisualTypeIdentifiers.TreemapChart` | `Treemap` |
| 2 | `IndexSet.Add(i)` | `Add` 없음. `AddIndex(i)` 또는 `indexSet[i] = True` |
| 3 | 마킹 이름 `"Marking"` 하드코딩 | 한국어 UI는 `"마킹"`. `ActiveMarkingSelectionReference` 사용 |
| 4 | `StdfDataSource` | 존재하지 않음. `DataTableDataSource` 로 대체 |
| 5 | `RenderSync` | 존재하지 않음. `RenderAsync` 만 있음 |
| 6 | `Document.Data.Tables[0]` | 숫자 인덱스 불가 (`Tables` 만 예외) |
| 7 | `CreateDataWriter` 의존 | `None` 반환. `ExportText` 로 대체 |
| 8 | `ScriptLog` 문서 속성 없이 예제 실행 | 마지막 줄에서 실패. 사전 준비 절 신설 |

### 검증 스크립트 버그 (교안은 멀쩡했음)

| 증상 | 원인 | 교훈 |
|------|------|------|
| `CreateDataWriter(Equals)` 실패 6건 | `dir()` 에서 .NET 기본 메서드 미제외 | — |
| 예제 18 실패 오탐 | 검사 코드가 `Tables[0]` 사용 | 검사 코드도 예제와 같은 방식을 써야 한다 |
| `CreateDataWriter` "성공" 오보고 | 반환값을 확인하지 않음 | **예외가 안 났다 ≠ 동작한다** |
| `ExportData` "확정" 오판 | 시그니처만 보고 판단 | **시그니처가 맞다 ≠ 동작한다** |

뒤의 두 가지가 특히 중요합니다. 검증 코드는 **호출하고, 반환값을 확인하고,
결과를 대조**해야 합니다.
