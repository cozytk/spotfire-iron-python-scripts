# 7. Spotfire 스크립팅의 현실

앞 장들은 **"이렇게 하면 된다"** 를 다뤘습니다. 이 장은 **"이래서 안 된다"** 를 다룹니다.

Spotfire 스크립팅에서 시간을 잡아먹는 것은 문법이 아닙니다.
**분명히 맞게 썼는데 동작하지 않는 상황**입니다. 이 장은 그 패턴을 정리한 것입니다.

!!! note "근거를 밝혀 둡니다"
    **7.1 · 7.2 · 7.3 · 7.5 · 7.6 · 7.8 · 7.10** 는 추측이 아니라, 이 교안의 예제 21종을
    **Spotfire 14.x / IronPython 2.7.12 환경에서 여덟 차례 실행**하며 실제로 부딪힌 것들입니다.
    그 과정에서 이 교안 자체의 오류도 8건 나왔습니다.
    전체 기록은 저장소의
    [`checks/README.md`](https://github.com/cozytk/spotfire-iron-python-scripts/blob/main/checks/README.md)
    에 있습니다.

    **7.4(트랜잭션)** · **7.7(환경 판별)** · **7.9(문서가 예고하는 함정)** 은 Spotfire 공식 문서와
    외부 레퍼런스를 근거로 정리한 것이고,
    각 절에 출처를 링크해 두었습니다. 실측한 것과 문서로 확인한 것을 구분해 두었으니
    "우리 환경에서 그대로 되는가"는 각자 확인하세요.

---

## 7.1 이름은 환경마다 다르다

가장 흔하고, 가장 조용히 실패하는 원인입니다.

### 마킹 이름

인터넷에 돌아다니는 스크립트는 대부분 이렇게 시작합니다.

```python
marking = Document.Data.Markings["Marking"]     # 한국어 Spotfire에서 실패
```

**한국어 UI에서 기본 마킹 이름은 `"마킹"` 입니다.** 두 번째부터는 `"마킹 (2)"`, `"마킹 (3)"` 입니다.
영어 기준으로 쓴 스크립트가 한국어 환경에서 깨지는 대표적인 이유입니다.

```python
# 좋음 — 이름을 쓰지 않는다
marking = Document.ActiveMarkingSelectionReference
filtering = Document.ActiveFilteringSelectionReference
```

### 그 밖에 환경을 타는 이름

| 대상 | 위험 |
|------|------|
| 마킹 | UI 언어에 따라 다름 |
| 필터링 스킴 | 사용자가 자유롭게 명명 (`기본`, `이상치 제거` …) |
| 시각화 제목 | 사용자가 언제든 변경 |
| 페이지 제목 | 재구성 시 변경 |
| 데이터 테이블·컬럼 | **대소문자 구분**. 데이터 소스 변경 시 변경 |

**원칙: 이름 대신 참조를 쓰고, 참조를 못 쓰면 존재를 확인하세요.**

```python
# 스크립트 매개변수로 객체를 직접 받는 것이 최선
# 그게 안 되면 최소한 확인은 한다
if Document.Data.Tables.Contains(u"매출"):
    table = Document.Data.Tables[u"매출"]
```

---

## 7.2 컬렉션마다 인덱싱 방식이 다르다

같은 Spotfire API인데 **컬렉션마다 규칙이 다릅니다.**

| 컬렉션 | `[0]` 숫자 | `["이름"]` |
|--------|:----------:|:----------:|
| `Document.Data.Tables` | **불가** | 가능 |
| `table.Columns` | 가능 | 가능 |
| `Document.Pages` | 가능 | — |
| `Document.FilteringSchemes` | 가능 | — |

```python
Document.Data.Tables[0]
# TypeError: expected str, got int
```

**`Tables` 만 예외**라 특히 헷갈립니다. 확실하지 않으면 순회해서 꺼내세요.

```python
first = None
for t in Document.Data.Tables:
    first = t
    break
```

---

## 7.3 캐스팅이 성공해도 속성이 없을 수 있다

일괄 처리 루프에서 가장 자주 걸리는 함정입니다.

```python
vc = visual.As[VisualContent]()      # 텍스트 영역도 이 줄은 통과한다
print vc.Data.DataTableReference     # 여기서 실패
# 'HtmlTextArea' object has no attribute 'Data'
```

**`As[VisualContent]()` 성공 여부로는 대상을 걸러낼 수 없습니다.**  
실측 결과입니다.

| 시각화 | 캐스팅 | 실제 가진 속성 |
|--------|:------:|----------------|
| `Table` | 성공 | `Data.*`, `Legend`, `TableColumns`, `SortInfos` — **축 없음** |
| `HtmlTextArea` | 성공 | **아무것도 없음** |
| 막대·선·산점도 | 성공 | 축, 범례, 데이터 전부 |

그래서 이 교안의 일괄 처리 예제는 전부 **속성 단위로** 감쌉니다.

```python
for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue                      # 대상 아님

        try:
            vc.Legend.Visible = False     # 이 속성이 없을 수도 있다
        except:
            pass
```

### 유형별로 다른 축 이름

| 유형 | 값 축 |
|------|-------|
| 막대·선·산점도 | `YAxis` |
| 원형 차트 | `SectorSizeAxis` |
| 교차 표 | `MeasureAxis` |
| 트리맵 | `SizeAxis` |
| 히트 맵 | `CellValueAxis` |

"모든 차트의 Y축을 바꿔라"라는 요구는 **유형별 분기 없이는 성립하지 않습니다.**

---

## 7.4 스크립트는 트랜잭션 안에서 통째로 실행된다

이걸 모르면 **"코드는 맞는데 결과가 이상한"** 상황을 영원히 이해할 수 없습니다.

Spotfire는 스크립트를 **하나의 트랜잭션으로 감싸서** 실행합니다.
사용자가 실행 취소(Undo)로 되돌릴 수 있게 하기 위해서입니다.
그래서 스크립트 안에서 한 변경들은 **한 줄씩 즉시 반영되는 것이 아니라,
스크립트가 끝나는 순간 한꺼번에 문서에 적용**됩니다.

> 공식 문서의 표현: 트랜잭션이 동작하려면 스크립트 안의 개별 변경이 압축되어
> 스크립트가 끝날 때 한 단계로 적용되어야 하고, 이것이 스크립트 안에서 조작하는
> 객체에 영향을 준다.
> — [How to develop IronPython scripts and their limitations](https://community.spotfire.com/s/article/How-to-develop-IronPython-scripts-in-TIBCO-Spotfire-and-their-limitations)

여기서 네 가지 결과가 나옵니다.

### ① 중간 진행 상황을 화면에 못 보여 준다

```python
Document.Properties["ScriptLog"] = u"1단계 시작"
# ... 오래 걸리는 작업 ...
Document.Properties["ScriptLog"] = u"2단계 시작"
# ... 오래 걸리는 작업 ...
Document.Properties["ScriptLog"] = u"완료"
```

화면에는 **"완료"만 보입니다.** 1·2단계는 표시되지 않습니다.
문서 속성은 스크립트가 끝나야 갱신되기 때문입니다.

진행 상황을 정말 보여 주고 싶으면 `ProgressService` 를 쓰고,
**스크립트 대화상자의 "트랜잭션으로 감싸기" 체크를 해제**해야 합니다
→ [13.2 참조](13-tips.html)

### ② 바꾼 값을 같은 스크립트에서 다시 읽으면 옛날 값일 수 있다

축 표현식이나 데이터 제한을 바꾸면 시각화가 다시 계산되어야 하는데,
그 재계산은 트랜잭션이 끝난 뒤에 일어납니다.

```python
vc.Data.WhereClauseExpression = "[Year] = 2024"
rows = vc.Data.DataTableReference.RowCount    # 필터링 반영 전 값
```

**"바꾸고 → 그 결과를 읽어서 → 다시 판단"하는 흐름은 한 스크립트 안에서 성립하지 않습니다.**
필요하면 스크립트를 두 개로 나누고, 첫 번째가 문서 속성을 바꾸면
그 속성 변경 트리거로 두 번째가 실행되게 하세요.

### ③ 스냅샷이 필요한 작업이 실패한다

이미지 내보내기처럼 **문서의 정지 화면(snapshot)** 이 필요한 작업은,
트랜잭션 실행 중인 애플리케이션 스레드에서 스냅샷을 뜰 수 없어 실패합니다.

```text
System.InvalidOperationException:
Attempt take snapshot on application thread in state 'Executing'.
```

[예제 14](11-examples-data.html)에서 텍스트 영역이 실패한 것이 정확히 이 오류였습니다.
공식 해법은 **작업을 함수로 감싸 애플리케이션 스레드에 넘기는 것**입니다.
함수 안에서 바깥 변수를 참조하지 말고 **전부 기본 인자로 받아야** 합니다.

```python
from Spotfire.Dxp.Framework.ApplicationModel import ApplicationThread

app = Document.GetService(ApplicationThread)
target = "C:/temp/visual.png"


# 필요한 것을 전부 기본 인자로 받는다. 스레드가 바뀐 뒤에도 값이 살아 있어야 하기 때문이다.
def render(visual=visual, document=Document, target=target):
    ...        # 여기서는 바깥 변수를 쓰지 않고 인자로 받은 것만 쓴다


app.InvokeAsynchronously(render)
```

전체 코드는 [예제 14의 "텍스트 영역까지 포함하려면"](11-examples-data.html) 절에 있습니다.

### ④ 실패해도 클라이언트는 죽지 않는다 (다행인 쪽)

스크립트는 Spotfire 본체와 **격리되어 실행**됩니다.
스크립트가 예외로 죽어도 Spotfire가 함께 죽지는 않습니다.
같은 이유로 스크립트는 **신뢰(trusted)** 상태여야 경고 없이 실행됩니다.

---

## 7.5 API가 조용히 실패한다

예외를 던지지 않고 `None` 을 돌려주는 API가 있습니다.

```python
writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.SbdfDataWriter)
# 예외 없음. 그런데 writer 는 None
writer.Write(...)
# 여기서야 터진다: 'NoneType' object has no attribute 'Write'
```

메서드 시그니처는 멀쩡합니다.

```text
CreateDataWriter(self: DataManager, typeId: TypeIdentifier) -> DataWriter
```

**"예외가 안 났다"와 "동작했다"는 다릅니다.**  
반환값을 받는 호출은 반환값을 확인하세요.

```python
writer = Document.Data.CreateDataWriter(identifier)
if writer is None:
    Document.Properties["ScriptLog"] = u"내보내기를 사용할 수 없습니다."
else:
    writer.Write(...)
```

!!! danger "이건 제가 실제로 틀린 부분입니다"
    이 교안의 검증 과정에서, 저는 `CreateDataWriter` 를 호출만 해 보고
    **예외가 안 났다는 이유로 "동작함"이라고 기록**했습니다.
    두 차수 뒤에 반환값을 확인하고 나서야 `None` 이라는 것을 알았습니다.

---

## 7.6 존재하지 않는 API가 널려 있다

검증 과정에서 **이 교안의 초안이 사용한 API 4개가 아예 존재하지 않았습니다.**

| 초안이 쓴 것 | 실제 |
|--------------|------|
| `VisualTypeIdentifiers.TreemapChart` | `Treemap` |
| `IndexSet.Add(i)` | `AddIndex(i)` 또는 `indexSet[i] = True` |
| `StdfDataSource` | 존재하지 않음 (`StdfFileDataSource` 는 있음) |
| `Visual.RenderSync` | 존재하지 않음 (`RenderAsync` 만) |

전부 **그럴듯한 이름**입니다. `TreemapChart` 는 `BarChart`·`LineChart` 와 대칭이라
자연스러워 보이고, `IndexSet.Add` 는 파이썬 `set` 을 아는 사람이면 당연히 쓸 이름입니다.

**출처가 무엇이든 틀릴 수 있습니다.** 오래된 커뮤니티 글, 버전이 다른 문서,
생성형 AI, 그리고 사람의 기억 전부요.

### 확인 방법 — `dir()`

30초면 끝납니다.

```python
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
for name in dir(VisualTypeIdentifiers):
    if not name.startswith("_"):
        print name
```

객체의 속성을 볼 때는 .NET 기본 메서드를 걸러 내면 읽기 편합니다.

```python
DOTNET_BASE = ["Equals", "GetHashCode", "GetType", "MemberwiseClone",
               "ReferenceEquals", "ToString"]

def members(obj):
    result = []
    for name in dir(obj):
        if not name.startswith("_") and name not in DOTNET_BASE:
            result.append(name)
    return result

print members(someVisual.As[VisualContent]())
```

### 시그니처까지 보기

IronPython에서는 `__doc__` 으로 .NET 메서드의 오버로드를 볼 수 있습니다.

```python
print Document.Data.CreateDataWriter.__doc__
# CreateDataWriter(self: DataManager, typeId: TypeIdentifier) -> DataWriter

import Spotfire.Dxp.Data.Import as imp
print imp.DataTableDataSource.__doc__
# DataTableDataSource(dataTable: DataTable)
# DataTableDataSource(dataTable: DataTable, updateBehavior: ...)
# DataTableDataSource(dataTable: DataTable, dataSelection: DataSelection)
```

**이 교안의 예제 16(마킹 스냅샷)은 이 한 줄로 해결됐습니다.**  
세 번째 오버로드를 발견하고 나서 20줄짜리 코드가 3줄이 되었습니다.

!!! warning "시그니처가 맞다고 동작하는 것도 아닙니다"
    `TablePlot.ExportData(typeIdentifier, stream)` 는 시그니처가 정확히 맞았지만
    실제로 호출하니 실패했습니다.

    ```text
    The writer with typeidentifier ... cannot write from reader.
    ```

    **호출까지 해 봐야 검증입니다.** 저는 이것도 한 번 틀렸습니다.

---

## 7.7 환경이 기능을 막는다

코드가 맞아도 **그 환경에서 허용되지 않아** 실패하는 경우가 있습니다.

### 라이선스

`DataWriterFactory` 에 `IsLicensed` 와 `requiredLicenses` 멤버가 있습니다.
즉 **내보내기 형식마다 라이선스가 걸려 있고, 없으면 조용히 막힙니다.**

이 교안을 검증한 환경에서는 `CreateDataWriter` 가 모든 형식에 대해 `None` 을 반환했습니다.
같은 코드가 다른 조직에서는 잘 동작할 수 있습니다.

### Web Player

브라우저에서 여는 분석 파일에서는 다음이 **전부 불가능**합니다.

| 기능 | 이유 |
|------|------|
| `MessageBox`, 파일 대화상자 | `System.Windows.Forms` 의존 |
| 로컬 파일 읽기·쓰기 | 서버에서 실행되므로 |
| Outlook 등 COM 연동 | 클라이언트 전용 |

반대로 **문서 구조를 다루는 것은 전부 동작합니다** — 시각화, 축, 필터, 마킹, 문서 속성.

### 지금 Analyst인지 Web Player인지 코드로 알아내기

**클라이언트 종류를 직접 알려 주는 API는 없습니다.** 대신 `Application` 객체의
.NET 타입 이름을 보면 알 수 있습니다.

```python
def is_analyst():
    # Analyst  -> Spotfire.Dxp.Application.RichAnalysisApplication
    # Web Player -> Spotfire.Dxp.Web.WebAnalysisApplication
    return "RichAnalysisApplication" in Application.GetType().ToString()
```

파일을 쓰는 예제(예제 14·15) 맨 앞에 이 검사를 넣어 두면, Web Player 사용자가
버튼을 눌렀을 때 **알 수 없는 .NET 예외 대신 사람이 읽을 수 있는 메시지**가 나옵니다.

```python
if not is_analyst():
    Document.Properties["ScriptLog"] = (
        u"이 기능은 Spotfire Analyst(데스크톱)에서만 동작합니다.")
else:
    ...  # 파일을 쓰는 본 작업
```

근거: [How to determine the client type (Spotfire Community)](https://community.spotfire.com/s/article/how-determine-client-type-analyst-or-web-player-user-running-tibco-spotfire-using-ironpython)

### 기능별로 물어볼 수 있는 속성

가능 여부를 미리 물어볼 수 있는 속성도 있습니다.

```python
plot.ExportDataEnabled          # 이 시각화에서 내보내기가 켜져 있나
table.IsRefreshable             # 이 테이블을 새로고침할 수 있나
table.NeedsRefresh              # 갱신이 필요한 상태인가
```

**막혔을 때 사용자에게 알려 주는 것**까지가 스크립트의 몫입니다.

```python
if not plot.ExportDataEnabled:
    Document.Properties["ScriptLog"] = u"이 시각화는 내보내기가 비활성화되어 있습니다."
```

!!! tip "환경을 한 번에 진단하려면"
    [예제 23 · 실행 환경 진단 리포트](12-examples-create.html)를 먼저 돌려 보세요.
    클라이언트 종류, 마킹·필터링 스킴의 실제 이름, 내보내기 가능 여부를
    한 번에 출력합니다. 새 환경에 예제를 적용하기 전에 이것부터 실행하는 것이 가장 빠릅니다.

---

## 7.8 되돌릴 수 없다

Spotfire의 실행 취소는 **스크립트 변경을 온전히 되돌리지 못합니다.**

| 작업 | 복구 |
|------|------|
| 속성 변경 (제목, 범례, 축) | 대체로 가능 |
| 축 표현식 일괄 변경 | 어려움 — 원래 값을 기록해 두지 않으면 복구 불가 |
| 시각화 유형 변경 | 그 유형에 없는 설정은 소실 |
| 데이터 테이블 교체·삭제 | **불가** |
| 페이지·시각화 삭제 | **불가** |

**규칙 하나만 지키면 됩니다: 사본에서 먼저.**

그리고 위험한 스크립트를 만들 때는 **현재 상태를 먼저 기록**하세요.
이 교안의 예제 18(시각화 인벤토리)과 예제 19(표현식 감사)가 그 용도입니다.

---

## 7.9 문서가 예고하는 나머지 함정 세 가지

이 절은 실측이 아니라 **공식 문서·외부 레퍼런스에서 반복적으로 경고하는 것**을 모은 것입니다.
남의 코드를 가져다 썼을 때 가장 잘 터지는 지점들입니다.

### ① 서식은 데이터 타입을 틀리면 조용히 안 말듣는다

축 서식은 포매터 객체를 만들어 **데이터 타입에 맞는 속성**에 넣어야 합니다.
`Real` 컬럼인데 `IntegerFormatter` 에 넣으면 오류가 나거나 아무 일도 일어나지 않습니다.

```python
fmt = DataType.Real.CreateLocalizedFormatter()
vc.YAxis.Scale.Formatting.RealFormatter = fmt      # Real 컬럼이면 RealFormatter
```

대응표는 [6.10](06-api-map.html)에 있습니다. 문자열·범주형·빈 컬럼은 애초에 서식이 없습니다.

### ② 범주형 축은 `<[컬럼]>` 이다

트렉스·마커·색상축처럼 범주로 묶는 축은 꺠솠 괄호를 씁니다.

```python
vc.Trellis.PanelAxis.Expression = "<[Region]>"   # 맞음
vc.Trellis.PanelAxis.Expression = "[Region]"     # 틀림 — 집계로 해석되거나 오류
```

UI에서 먼저 설정한 뒤 **오른쪽 클릭 → 사용자 지정 표현식**으로 문자열을 그대로 복사해 오는
습관이 가장 안전합니다. 표현식을 머리로 지어내지 마세요.

### ③ 예제 코드의 연도를 보라

커뮤니티·GitHub의 예제들은 2012~2021년에 쓰인 것이 많고, 대부분 다음 세 가지를 가집니다.

| 예제에서 자주 보이는 코드 | 왜 위험한가 | 이 교안의 방식 |
|------------------------|-------------|--------------|
| `Document.Data.Markings["Marking"]` | 한국어 UI에서는 이름이 "마킹" | `Document.ActiveMarkingSelectionReference` (7.1) |
| `Document.Data.Tables[0]` | 숫자 인덱싱 불가 — `TypeError` | 순회해서 꺼내기 (7.2) |
| `writer = ...CreateDataWriter(...)` 바로 사용 | 라이선스 없으면 조용히 `None` | 반환값 검사 (7.5) |
| `MessageBox.Show(...)` | Web Player에서 실패 | `NotificationService` (2.5) |
| `Visual.Render(...)` | 폐기 예정 목록 | `RenderAsync` 확인 후 사용 (예제 14) |

공식 문서도 같은 주의를 달아 둡니다. 커뮤니티 스크립트는 **참고용 샘플이며
그대로 운영에 쓰라고 준 것이 아닙니다.**

---

## 7.10 확인하는 다섯 가지 방법

문서를 신뢰할 수 없을 때 쓰는 도구들입니다. 위험이 낮은 순서입니다.

### ① `dir()` 로 존재 확인 — 위험 없음

7.6 참조. 가장 먼저 할 일입니다.

### ② 대상만 출력해 보기 — 위험 없음

**무엇을 바꾸기 전에 무엇이 대상인지부터** 확인합니다.

```python
for page in Document.Pages:
    for visual in page.Visuals:
        print page.Title, "|", visual.Title, "|", visual.TypeId
```

예상과 다르면 조건이 잘못된 것입니다. 여기서 걸러지는 실수가 많습니다.

### ③ 반환값 검사 — 위험 없음

```python
result = someApi(...)
print type(result), result is None
```

7.4의 교훈입니다.

### ④ 같은 값 다시 쓰기 — 값이 변하지 않음

**setter 가 살아 있는지**만 확인하는 기법입니다.

```python
value = vc.Data.WhereClauseExpression    # 현재 값을 읽고
vc.Data.WhereClauseExpression = value    # 같은 값을 다시 쓴다
```

쓰기가 막혀 있으면 여기서 예외가 납니다. 값은 그대로이므로 안전합니다.
이 교안의 검증 하네스가 21개 예제를 문서 변경 없이 확인할 수 있었던 것이 이 방법 덕분입니다.

### ⑤ 소규모 왕복 시험 — 사본에서

만들고, 확인하고, 지웁니다. `finally` 로 정리를 보장합니다.

```python
TEMP = "__TEST__"
try:
    newTable = Document.Data.Tables.Add(TEMP, source)
    print "행 수:", newTable.RowCount
finally:
    if Document.Data.Tables.Contains(TEMP):
        Document.Data.Tables.Remove(Document.Data.Tables[TEMP])
```

이 방법으로 예제 16이 **진짜 스냅샷인지 실시간 뷰인지**를 판별했습니다.
10행 마킹 → 테이블 생성 → 20행으로 변경 → 테이블은 여전히 10행 → 스냅샷 확정.

---

## 7.11 요약 — 스크립트를 쓸 때의 기본 자세

```text
□ 이름을 하드코딩하지 않았나                    (7.1)
□ 컬렉션 인덱싱 방식이 맞나                      (7.2)
□ 유형별로 속성이 다른 것을 감안했나              (7.3)
□ 바꾼 값을 같은 스크립트에서 다시 읽고 있지 않나  (7.4)
□ 반환값을 확인했나                             (7.5)
□ 쓰는 API가 실제로 존재하나                     (7.6)
□ 이 환경에서 허용되는 기능인가                   (7.7)
□ 되돌릴 수 없는 작업인가                        (7.8)
□ 베끼온 코드의 오래된 관습을 걸러냈나               (7.9)
□ 사본에서 먼저 시험했나
```

이 열 줄이 이 교안 전체에서 가장 실용적인 부분일 수 있습니다.

---

다음 장에서는 이 제약들을 **생성형 AI에게 알려 주는 방법**을 다룹니다.
AI는 위의 함정을 전혀 모르기 때문에, 알려 주지 않으면 그대로 밟습니다.
