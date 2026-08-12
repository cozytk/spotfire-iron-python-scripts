# 동작 확인용 스크립트

교안 내용 중 **실제 Spotfire에서 확인이 필요한 항목**을 검증하는 스크립트입니다.
교안 예제가 아니므로 `scripts/` 와 분리해 두었습니다.

확인이 끝난 스크립트는 저장소에서 내리고, 결과만 아래 "확인 완료" 절에 남깁니다.

---

## 먼저 이것부터 — 예제 21종 일괄 검증

예제를 하나씩 실제로 돌리는 것은 현실적이지 않으므로,
**예제 21개가 쓰는 API를 한 번에 확인하는 하네스**를 만들었습니다.

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

## 지금 확인할 것 (3차)

### [`07_snapshot_datasource.py`](07_snapshot_datasource.py)

2차에서 **예제 10(마킹 행 스냅샷)이 깨진다는 것**이 드러났습니다.
`StdfDataSource` 라는 이름이 존재하지 않습니다. 무엇으로 대체할지 확정하기 위한 확인입니다.

| 단계 | 내용 | 문서 변경 |
|------|------|:---------:|
| 1 | 컬렉션별 숫자 인덱싱 가능 여부 (`Tables[0]` 이 왜 실패했는지 특정) | 없음 |
| 2 | `SbdfDataWriter` / `StdfDataWriter` 로 메모리에 기록 | 없음 |
| 3 | `SbdfFileDataSource` 등이 **메모리 스트림을 받는지** | 없음 |
| 4 | 실제 왕복 — 임시 테이블 생성 후 삭제 | **있음** |

4단계는 `__SNAPSHOT_TEST__` 테이블을 만들었다 지웁니다.
부담스러우면 파일 맨 위의 `RUN_ROUNDTRIP = True` 를 `False` 로 바꾸면 1~3단계만 돕니다.
**사본에서 실행**하시길 권합니다.

마지막 "요약" 절에 예제 10 에 쓸 조합이 나옵니다. 그것만 주셔도 됩니다.

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
