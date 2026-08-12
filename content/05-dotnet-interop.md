# 5. .NET 상호운용 문법

Spotfire 스크립트가 다루는 객체는 전부 **.NET 객체**입니다. 그래서 순수 Python에는 없는
문법이 몇 가지 등장합니다. 이 장에서 다루는 4가지만 알면 API 문서를 그대로 코드로 옮길 수 있습니다.

1. `import` / `clr.AddReference` — 네임스페이스 가져오기
2. `As[T]()` — 형 변환(캐스팅)
3. `AddNew[T]()` — 제네릭 메서드 호출
4. .NET 타입·컬렉션·열거형 다루기

## 5.1 네임스페이스 import

Spotfire API는 `Spotfire.Dxp.` 로 시작하는 네임스페이스에 들어 있습니다.
Python 모듈처럼 `from ... import ...` 로 가져옵니다.

```python
from Spotfire.Dxp.Application.Visuals import VisualContent, BarChart, VisualTypeIdentifiers
from Spotfire.Dxp.Data import DataValueCursor, IndexSet, RowSelection
from Spotfire.Dxp.Application.Filters import FilterTypeIdentifiers
```

와일드카드도 되지만, 이름 충돌이 나기 쉬우니 필요한 것만 명시하는 편이 낫습니다.

```python
from Spotfire.Dxp.Application.Visuals import *    # 동작하지만 비권장
```

### clr.AddReference가 필요한 경우

`Spotfire.Dxp.*` 는 이미 로드되어 있어 바로 `import` 하면 됩니다. 하지만 **Spotfire 밖의
.NET 어셈블리**(윈도우 폼, 그래픽, Office 등)를 쓰려면 먼저 참조를 추가해야 합니다.

```python
import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import MessageBox, FolderBrowserDialog
from System.Drawing import Bitmap, Size, Rectangle, Color
```

`System`, `System.IO` 같은 핵심 네임스페이스는 대개 `AddReference` 없이도 됩니다.

```python
from System import Array, String, Guid, DateTime
from System.IO import File, Path, StreamWriter, MemoryStream, SeekOrigin
```

## 5.2 As[T]() — 형 변환이 가장 중요한 문법

Spotfire에서 시각화를 순회하면 나오는 것은 **`Visual`** 객체입니다. 그런데 `Visual`에는
제목(`Title`)과 유형(`TypeId`) 정도밖에 없습니다. 축 표현식이나 범례 같은 실제 내용은
**`VisualContent`** 이하의 구체 타입에 들어 있습니다.

그래서 **"껍데기(Visual) → 알맹이(VisualContent)"** 로 캐스팅해야 합니다.

```python
from Spotfire.Dxp.Application.Visuals import VisualContent

for visual in Document.ActivePageReference.Visuals:
    print visual.Title            # Visual 수준 — 바로 접근 가능

    vc = visual.As[VisualContent]()   # 캐스팅
    print vc.Data.DataTableReference.Name    # VisualContent 수준
```

이 `As[T]()` 가 IronPython의 제네릭 메서드 호출 문법입니다. C#의 `visual.As<VisualContent>()`
와 같습니다.

### 어느 타입으로 캐스팅할 것인가

| 캐스팅 대상 | 얻는 것 | 용도 |
|-------------|---------|------|
| `VisualContent` | `Data`, `Title`, 공통 축 일부 | 유형을 가리지 않는 **일괄 처리**에 적합 |
| `BarChart`, `LineChart`, `ScatterPlot` … | 그 유형 고유의 모든 속성 | 특정 유형을 정밀 제어 |
| `TablePlot`, `CrossTablePlot` | 컬럼·정렬·내보내기 | 표 계열 처리 |

일괄 적용 스크립트에서는 `VisualContent`로 캐스팅한 뒤 **속성이 있는지 없는지를
`try/except`나 `hasattr`로 확인**하는 방식이 실전적입니다.

```python
from Spotfire.Dxp.Application.Visuals import VisualContent

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            vc.Legend.Visible = False       # 범례가 없는 유형이면 예외 → 건너뜀
        except:
            pass
```

### 캐스팅이 실패하는 경우

시각화 유형이 맞지 않으면 예외가 납니다. **먼저 `TypeId`로 확인**하고 캐스팅하세요.

```python
from Spotfire.Dxp.Application.Visuals import BarChart, VisualTypeIdentifiers

for visual in Document.ActivePageReference.Visuals:
    if visual.TypeId == VisualTypeIdentifiers.BarChart:
        bar = visual.As[BarChart]()
        bar.SortedBars = True         # 막대 차트 고유 속성
```

!!! warning "텍스트 영역과 Mod 시각화는 예외 처리하세요"
    텍스트 영역(`HtmlTextArea`), 필터 패널, 그리고 **Spotfire Mod 시각화**는 일반 차트와
    구조가 다릅니다. 일괄 처리 루프에서 `TypeId`로 걸러 내거나 `try/except`로 감싸 두지 않으면
    루프가 중간에 멈춥니다.

## 5.3 AddNew[T]() — 제네릭으로 객체 만들기

새 시각화를 만들 때도 같은 대괄호 문법을 씁니다.

```python
from Spotfire.Dxp.Application.Visuals import BarChart, LineChart

visuals = Document.ActivePageReference.Visuals
chart = visuals.AddNew[BarChart]()        # 막대 차트 생성

chart.Data.DataTableReference = Document.Data.Tables["Sales"]
chart.XAxis.Expression = "[Region]"
chart.YAxis.Expression = "Sum([Revenue])"
chart.ColorAxis.Expression = "[Category]"
chart.Title = u"지역별 매출"
```

`AddNew[T]()` 는 **이미 구체 타입**을 반환하므로 별도 캐스팅이 필요 없습니다.

DataValueCursor처럼 제네릭 정적 메서드도 같은 형식입니다.

```python
from Spotfire.Dxp.Data import DataValueCursor

cursor = DataValueCursor.CreateFormatted(column)     # 항상 문자열로 읽기
cursor = DataValueCursor.Create[str](column)         # 타입 지정
cursor = DataValueCursor.Create[float](column)       # 숫자로 읽기
```

!!! tip "`CreateFormatted` vs `Create[T]`"
    - `CreateFormatted(column)`: 화면에 보이는 **서식이 적용된 문자열**을 반환. 표시용에 적합
    - `Create[float](column)`: **원본 숫자 값**을 반환. 계산용에 적합. 빈 값은 `None`

## 5.4 .NET 컬렉션 다루기

Spotfire의 컬렉션은 파이썬 리스트가 아니라 .NET 컬렉션입니다. 순회는 동일하지만
**인덱싱과 조회 방식이 조금 다릅니다.**

```python
tables = Document.Data.Tables

# 순회 — 파이썬과 동일
for t in tables:
    print t.Name

# 이름/인덱스로 조회
sales = tables["Sales"]
first = tables[0]
sales = tables.Item["Sales"]     # Item 프로퍼티 명시 (동일)

# 존재 여부 — 파이썬의 in 대신 Contains를 쓰는 편이 안전
if tables.Contains("Sales"):
    pass

# 개수 — len() 대신 .Count
print tables.Count

# 파이썬 리스트로 바꾸기 (정렬·슬라이싱 하려면 필요)
tableList = [t for t in tables]
tableList.sort(key=lambda t: t.Name)
```

!!! warning "`len()`이 안 되는 컬렉션이 있습니다"
    .NET 컬렉션은 `.Count` 프로퍼티를 쓰세요. `len()`은 일부 타입에서만 동작합니다.

## 5.5 .NET 타입과 열거형

### 열거형(Enum)

Spotfire API 곳곳에서 상수 대신 열거형을 씁니다. 문자열이 아니라 **열거형 멤버를 그대로**
넘겨야 합니다.

```python
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers, TablePlotColumnSortMode
from Spotfire.Dxp.Data import DataType, DataPropertyClass

visual.TypeId = VisualTypeIdentifiers.BarChart          # "BarChart" 문자열 아님
sortMode = TablePlotColumnSortMode.Ascending
dtype = DataType.String
```

### .NET 배열

파이썬 리스트를 받지 않고 .NET 배열을 요구하는 API가 있습니다.

```python
from System import Array, String

names = ["Region", "Revenue"]
netArray = Array[String](names)          # String[] 으로 변환
```

### 자주 쓰는 System 타입

```python
from System import DateTime, Guid, Uri, TimeSpan
from System.IO import Path, File, Directory

stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss")
folder = Path.GetTempPath()
File.Exists(r"C:\data\a.csv")
Directory.CreateDirectory(r"C:\out")
```

## 5.6 서비스 가져오기 — GetService

문서에 속하지 않는 기능(알림, 진행 표시, 라이브러리 접근)은 **서비스**로 제공됩니다.
여기서도 제네릭 문법을 씁니다.

```python
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService, ProgressService
from Spotfire.Dxp.Data import DataManager

ns = Application.GetService[NotificationService]()
ns.AddInformationNotification(u"제목", u"설명", u"상세")

dataManager = Application.GetService[DataManager]()
marking = dataManager.Markings["Marking"]
```

`Document.GetService(...)` 형태도 있습니다(라이브러리 접근 등). API에 따라 다르니
예제 코드를 그대로 따르세요.

## 5.7 IronPython ↔ .NET 타입 매핑

| Python | .NET | 비고 |
|--------|------|------|
| `str` | `System.String` | 자동 변환 |
| `int` | `System.Int32` | 큰 수는 `System.Int64` |
| `float` | `System.Double` | |
| `bool` | `System.Boolean` | `True`/`False` |
| `None` | `null` | |
| `list` | — | .NET 배열이 필요하면 `Array[T](...)` |

대부분 자동으로 변환되지만, **타입 불일치 오류가 나면** 명시적으로 변환하세요.

```python
count = Document.Properties["Threshold"]      # 문자열일 수 있음
threshold = int(count)                        # 명시적 변환
```

## 5.8 API 문서를 코드로 옮기는 법

Spotfire API 레퍼런스는 C# 시그니처로 되어 있습니다. 변환 규칙은 단순합니다.

| C# 시그니처 | IronPython |
|-------------|-----------|
| `visual.As<VisualContent>()` | `visual.As[VisualContent]()` |
| `visuals.AddNew<BarChart>()` | `visuals.AddNew[BarChart]()` |
| `app.GetService<NotificationService>()` | `app.GetService[NotificationService]()` |
| `table.Columns["Region"]` | `table.Columns["Region"]` (동일) |
| `new IndexSet(count, true)` | `IndexSet(count, True)` |
| `DataType.String` | `DataType.String` (동일) |
| `out bool success` 매개변수 | 반환값이 튜플이 됨 (아래 참조) |

C#의 `out` 매개변수는 IronPython에서 **튜플 반환**으로 바뀝니다.

```csharp
// C#: bool TryGetItem(string path, LibraryItemType type, out LibraryItem item)
```

```python
# IronPython: 반환값이 (성공여부, 결과) 튜플
success, libraryFolder = libraryManager.TryGetItem(folderName, LibraryItemType.Folder)
if success:
    print libraryFolder.Title
```

!!! tip "속성 이름을 모를 때는 dir()로 탐색하세요"
    문서를 못 찾겠으면 객체가 가진 멤버를 직접 출력해 보는 것이 가장 빠릅니다.
    스크립트 편집 창에서 실행하면 출력 영역에 나옵니다.

    ```python
    vc = someVisual.As[VisualContent]()
    for member in dir(vc):
        if not member.startswith("_"):
            print member
    ```

    축 표현식을 찾고 싶으면 `Axis`가 들어간 이름을, 데이터 관련이면 `Data`를 눈으로 훑으면 됩니다.

---

문법은 여기까지입니다. 다음 장에서 **어떤 객체가 어디에 매달려 있는지** 지도를 그린 뒤,
7장에서 생성형 AI로 스크립트를 만드는 방법을 익힌 뒤 8장부터 예제로 들어갑니다.
