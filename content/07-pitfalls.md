# 7. Spotfire 스크립팅의 현실

앞 장들은 **"이렇게 하면 된다"** 를 다뤘습니다. 이 장은 **"이래서 안 된다"** 를 다룹니다.

Spotfire 스크립팅에서 시간을 잡아먹는 것은 문법이 아닙니다.
**분명히 맞게 썼는데 동작하지 않는 상황**입니다. 이 장은 그 패턴을 정리한 것입니다.

!!! note "이 장의 내용은 전부 실제로 확인한 것입니다"
    여기 나오는 함정은 추측이 아니라, 이 교안의 예제 21종을
    **Spotfire 14.x / IronPython 2.7.12 환경에서 여덟 차례 실행**하며 실제로 부딪힌 것들입니다.
    그 과정에서 이 교안 자체의 오류도 8건 나왔습니다.

    전체 기록은 저장소의
    [`checks/README.md`](https://github.com/cozytk/spotfire-iron-python-scripts/blob/main/checks/README.md)
    에 있습니다.

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

## 7.4 API가 조용히 실패한다

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

## 7.5 존재하지 않는 API가 널려 있다

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

## 7.6 환경이 기능을 막는다

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

### 코드에서 판별하기

가능 여부를 미리 물어볼 수 있는 속성이 있습니다.

```python
plot.ExportDataEnabled          # 이 시각화에서 내보내기가 켜져 있나
table.IsRefreshable             # 이 테이블을 새로고침할 수 있나
```

**막혔을 때 사용자에게 알려 주는 것**까지가 스크립트의 몫입니다.

```python
if not plot.ExportDataEnabled:
    Document.Properties["ScriptLog"] = u"이 시각화는 내보내기가 비활성화되어 있습니다."
```

---

## 7.7 되돌릴 수 없다

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

## 7.8 확인하는 다섯 가지 방법

문서를 신뢰할 수 없을 때 쓰는 도구들입니다. 위험이 낮은 순서입니다.

### ① `dir()` 로 존재 확인 — 위험 없음

7.5 참조. 가장 먼저 할 일입니다.

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

## 7.9 요약 — 스크립트를 쓸 때의 기본 자세

```text
□ 이름을 하드코딩하지 않았나          (7.1)
□ 컬렉션 인덱싱 방식이 맞나            (7.2)
□ 유형별로 속성이 다른 것을 감안했나    (7.3)
□ 반환값을 확인했나                   (7.4)
□ 쓰는 API가 실제로 존재하나           (7.5)
□ 이 환경에서 허용되는 기능인가        (7.6)
□ 되돌릴 수 없는 작업인가              (7.7)
□ 사본에서 먼저 시험했나
```

이 여덟 줄이 이 교안 전체에서 가장 실용적인 부분일 수 있습니다.

---

다음 장에서는 이 제약들을 **생성형 AI에게 알려 주는 방법**을 다룹니다.
AI는 위의 함정을 전혀 모르기 때문에, 알려 주지 않으면 그대로 밟습니다.
