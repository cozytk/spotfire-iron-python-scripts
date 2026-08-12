# 11. 예제 C · 데이터와 내보내기

데이터를 **읽고, 복사하고, 파일로 꺼내는** 예제입니다.

!!! warning "이 장은 환경을 가장 많이 탑니다"
    파일 내보내기는 **Analyst 데스크톱 전용**이고, 일부는 **라이선스**에 막힙니다.
    실행했는데 안 된다면 코드가 아니라 환경 문제일 수 있습니다 →
    [7.7 참조](07-pitfalls.html)

---

## 예제 14. 모든 페이지의 시각화를 PNG로 일괄 내보내기

<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge analyst">Analyst 전용</li>
<li class="badge hard">기본 기능으로 어려움</li>
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
매주 보고서에 대시보드 차트 20개를 이미지로 넣어야 합니다.
지금은 시각화마다 우클릭 → 이미지로 복사 → 붙여넣기를 20번 반복합니다.

**기본 기능으로 어려운 이유**  
Spotfire의 이미지 내보내기는 **한 번에 하나씩**입니다.
"모든 페이지의 모든 시각화를 파일로" 하는 기능은 없습니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `outDir` | String | 문서 속성 `ExportFolder` (예: `C:/exports`) |

```python
# -*- coding: utf-8 -*-
# 모든 페이지의 모든 시각화를 PNG 파일로 저장한다. (Analyst 데스크톱 전용)
#
# 매개변수:
#   outDir (String) 저장할 폴더 경로. 예: "C:/exports"

import clr
clr.AddReference("System.Drawing")

from Spotfire.Dxp.Application.Visuals import VisualContent
from System.Drawing import Bitmap, Graphics, Rectangle
from System.IO import Directory, Path
from System import DateTime

WIDTH, HEIGHT = 1400, 900


# 파일명에 쓸 수 없는 문자 제거
def safe_name(text):
    result = []
    for ch in (text or u"untitled"):
        result.append(ch if ch not in u'\\/:*?"<>|\r\n\t' else u"_")
    return u"".join(result).strip()[:80] or u"untitled"


# Web Player에서는 로컬 폴더에 쓸 수 없다.
# 알 수 없는 .NET 예외 대신 사람이 읽을 수 있는 안내를 남긴다. → 7.7 참조
isAnalyst = "RichAnalysisApplication" in Application.GetType().ToString()

if not isAnalyst:
    Document.Properties["ScriptLog"] = (
        u"이미지 내보내기는 Spotfire Analyst(데스크톱)에서만 동작합니다.")
else:
    stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss")
    folder = Path.Combine(outDir, "spotfire_" + stamp)
    Directory.CreateDirectory(folder)

    saved = 0
    failed = []

    for pageIndex, page in enumerate(Document.Pages):
        for vizIndex, visual in enumerate(page.Visuals):
            try:
                vc = visual.As[VisualContent]()

                bitmap = Bitmap(WIDTH, HEIGHT)
                graphics = Graphics.FromImage(bitmap)
                vc.Render(graphics, Rectangle(0, 0, WIDTH, HEIGHT))

                fileName = u"%02d_%s__%02d_%s.png" % (
                    pageIndex + 1, safe_name(page.Title),
                    vizIndex + 1, safe_name(visual.Title))

                bitmap.Save(Path.Combine(folder, fileName))

                graphics.Dispose()
                bitmap.Dispose()
                saved += 1
            except:
                # 텍스트 영역·Mod 시각화는 여기로 빠진다 (아래 "왜 실패하나" 참조)
                failed.append(u"%s / %s" % (page.Title, visual.Title))

    msg = u"%d개 이미지를 저장했습니다: %s" % (saved, folder)
    if failed:
        msg += u" (건너뜀 %d개: %s)" % (len(failed), u", ".join(failed))

    Document.Properties["ScriptLog"] = msg
```

!!! danger "검증 포인트 — Analyst 전용입니다"
    - **Web Player에서는 동작하지 않습니다.** 로컬 파일 시스템에 쓰기 때문입니다.
      맨 앞의 클라이언트 판별로 미리 걸러 냅니다 → [7.7 참조](07-pitfalls.html)
    - `VisualContent.Render(Graphics, Rectangle)` 방식은 **동작을 확인했습니다.**(14.x)
      다만 `Visual.Render` 는 공식 API 문서에서 **폐기 예정(Obsolete)** 으로 표시되어
      있습니다. 지금은 동작하지만, 장기적으로는 아래 `RenderAsync` 쪽이 정식 경로입니다.
    - **`RenderSync` 는 존재하지 않습니다.** 실측 결과 `Visual` 객체에는
      `RenderAsync` 만 있습니다(`hasattr(visual, "RenderSync")` → `False`).
    - 폴더가 없으면 `Directory.CreateDirectory`가 만들어 줍니다. 쓰기 권한은 확인하세요.

### 왜 텍스트 영역에서 실패하나 — 그리고 어떻게 살리나

실측 오류 메시지는 이것이었습니다.

```text
System.InvalidOperationException:
Attempt take snapshot on application thread in state 'Executing'.
```

원인은 시각화 종류가 아니라 **스크립트가 트랜잭션 안에서 돌고 있다는 것**입니다.
렌더링은 문서의 정지 화면(snapshot)을 필요로 하는데, 트랜잭션 실행 중인 스레드에서는
스냅샷을 뜰 수 없습니다 → [7.4 참조](07-pitfalls.html)

공식 해법은 **작업을 함수로 감싸 애플리케이션 스레드에 넘기는 것**입니다.
이때 함수 안에서 바깥 변수를 참조하면 안 되고, **필요한 것을 전부 기본 인자로 받아야**
합니다. 스레드가 바뀐 뒤에도 값이 살아 있어야 하기 때문입니다.

```python
# -*- coding: utf-8 -*-
# 트랜잭션 밖(애플리케이션 스레드)에서 렌더링해 텍스트 영역까지 내보낸다.
#
# 매개변수:
#   visual (Visualization) 내보낼 시각화
#   outDir (String)        저장 폴더

import clr
clr.AddReference("System.Drawing")

from System.Drawing import Bitmap, Graphics, Rectangle
from System.IO import Path
from Spotfire.Dxp.Framework.ApplicationModel import ApplicationThread

app = Document.GetService(ApplicationThread)
image = Bitmap(1400, 900)
target = Path.Combine(outDir, "visual.png")


def render(visual=visual, document=Document, image=image, target=target,
           Graphics=Graphics, Rectangle=Rectangle):
    # 바깥 변수를 직접 쓰지 않는다. 전부 인자로 받은 것만 쓴다.
    try:
        gfx = Graphics.FromImage(image)
        rect = Rectangle(0, 0, image.Width, image.Height)
        # 페이지 배치상의 실제 비율에 맞춘 영역을 얻는다
        bounds = document.ActivePageReference.GetVisualBounds(visual, rect)
        visual.Render(gfx, bounds)
    except:
        return
    image.Save(target)


app.InvokeAsynchronously(render)
```

`Page.GetVisualBounds(visual, rect)` 는 **페이지에서 그 시각화가 차지하는 비율**에 맞는
사각형을 돌려줍니다. 고정 크기로 그릴 때 생기는 "글자만 작아 보이는" 문제를 줄여 줍니다.

!!! warning "이 변형은 이 교안의 검증 환경에서 실행해 보지 않았습니다"
    출처는 Spotfire 공식 문서
    ([Attempt take snapshot 오류 해결](https://community.spotfire.com/s/article/how-troubleshoot-exception-thrown-when-executing-ironpython-script-error-attempt-take-snapshot))
    입니다. `InvokeAsynchronously` 는 이름 그대로 **비동기**라, 스크립트가 끝난 뒤에
    파일이 만들어집니다. "저장했습니다" 메시지를 스크립트 끝에서 쓰면 거짓말이 됩니다.

### 참고 — RenderAsync (Spotfire 15.x 정식 경로)

`Visual.Render` 를 대체하는 API입니다. PNG 바이트를 바로 스트림에 씁니다.

```python
from Spotfire.Dxp.Application.Visuals import RenderResultSettings, VisualRenderSettings
from System.Drawing import Size
from System.Threading import CancellationToken
from System.IO import FileStream, FileMode

resultSettings = RenderResultSettings(Size(1400, 900))

visualSettings = VisualRenderSettings()
visualSettings.ShowTitle = True
visualSettings.ShowLegend = True
visualSettings.ShowAxisLabels = True

# CancellationToken.None 은 파이썬 문법 오류다 → 기본 생성자를 쓴다 (5.5 참조)
task = visual.RenderAsync(resultSettings, visualSettings, CancellationToken())
result = task.Result                     # 완료까지 대기

if result.IsValid:
    stream = FileStream("C:/temp/visual.png", FileMode.Create)
    try:
        result.WriteTo(stream)           # AsImage() 는 폐기 예정
    finally:
        stream.Close()
```

| API | 상태 | 비고 |
|-----|------|------|
| `Visual.Render(gfx, rect)` | **폐기 예정** | 이 교안 검증 환경에서 동작 확인 |
| `Visual.RenderAsync(...)` | 현행 | `Task<RenderResult>` 반환 → `.Result` 로 대기 |
| `RenderResult.WriteTo(stream)` | 현행 | PNG 바이트를 스트림에 기록 |
| `RenderResult.AsImage()` | **폐기 예정** | |
| `Page.RenderAsync(...)` | 현행 | **페이지 하나를 통째로** 이미지로. 시각화별로 도는 대신 |

"보고서에 페이지 스크린샷 한 장"이 필요한 경우라면 시각화를 하나씩 도는 대신
`Page.RenderAsync` 쪽이 훨씬 간단합니다. 두 번째 인자만 `PageRenderSettings` 로 바뀝니다.

**이 절의 코드도 검증 환경에서 실행해 보지 않았습니다.** 공식 API 문서의 시그니처를
그대로 옮긴 것이니, 쓰기 전에 [7.10의 확인 방법](07-pitfalls.html)으로 한 번 걸러 보세요.

---

## 예제 15. 여러 데이터 테이블을 한 번에 파일로 내보내기

<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge analyst">Analyst 전용</li>
<li class="badge env">환경 의존</li>
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
분석에 들어 있는 표 여러 개를 **현재 상태 그대로** 파일로 넘겨야 합니다.

**기본 기능으로 어려운 이유**  
`파일 > 내보내기 > 데이터`는 한 번에 하나입니다. 여러 번 반복해야 하고,
매번 저장 경로와 옵션을 다시 지정해야 합니다.

!!! danger "이 예제만 유독 환경을 많이 탑니다"
    Spotfire 14.x에서 내보내기 경로를 전부 시험한 결과입니다.

    | 경로 | 결과 |
    |------|------|
    | `Document.Data.CreateDataWriter(...)` | **`None` 반환** (예외조차 없음) |
    | `TablePlot.ExportData(식별자, 스트림)` | **실패** — `cannot write from reader` |
    | `TablePlot.ExportText(writer)` | **성공** (408,144 글자, 탭 구분) |

    널리 알려진 `CreateDataWriter` 방식이 **이 환경에서는 동작하지 않습니다.**
    `DataWriterFactory` 에 `IsLicensed` 와 `requiredLicenses` 멤버가 있는 것으로 보아
    **라이선스 제약**으로 보입니다. `ExportData` 는 시그니처가 맞는데도 writer 쪽에서
    거부합니다.

    ```text
    The writer with typeidentifier Spreadsheet CSV UTF8 data writer cannot write from reader.
    ```

    아래는 **실제로 동작을 확인한 코드**입니다. `CreateDataWriter` 방식은
    맨 아래에 참고용으로 남겨 두었습니다.

### 검증된 방법 — `ExportText`

```text
ExportText(self: TablePlotBase, writer: TextWriter)
```

출력은 **탭 구분 텍스트**입니다. 첫 줄이 컬럼 이름입니다.

```python
# -*- coding: utf-8 -*-
# 표 시각화의 데이터를 탭 구분 텍스트 파일로 내보낸다. (Analyst 전용)
#
# 매개변수:
#   vTable (Visualization) 표(Table) 시각화

from Spotfire.Dxp.Application.Visuals import TablePlot
from System.IO import StreamWriter
from System.Text import Encoding

PATH = "C:/temp/export.txt"

plot = vTable.As[TablePlot]()

# 실행 전 두 가지를 확인한다 → 7.7 참조
#   1) 지금 Analyst인가 (Web Player는 로컬 경로에 못 쓴다)
#   2) 이 시각화에서 내보내기가 켜져 있나
isAnalyst = "RichAnalysisApplication" in Application.GetType().ToString()

if not isAnalyst:
    Document.Properties["ScriptLog"] = (
        u"파일 내보내기는 Spotfire Analyst(데스크톱)에서만 동작합니다.")
elif not plot.ExportDataEnabled:
    Document.Properties["ScriptLog"] = u"이 시각화는 데이터 내보내기가 비활성화되어 있습니다."
else:
    # 한글이 있으면 UTF-8 로 명시한다
    writer = StreamWriter(PATH, False, Encoding.UTF8)
    try:
        plot.ExportText(writer)
    finally:
        writer.Close()
    Document.Properties["ScriptLog"] = u"내보내기 완료: " + PATH
```

### CSV가 필요하면 직접 변환

`ExportText` 는 탭 구분이므로, 쉼표가 필요하면 문자열로 받아서 바꿉니다.

```python
# -*- coding: utf-8 -*-
from Spotfire.Dxp.Application.Visuals import TablePlot
from System.IO import StringWriter, StreamWriter
from System.Text import Encoding

plot = vTable.As[TablePlot]()

# 1) 메모리로 받는다
buffer = StringWriter()
try:
    plot.ExportText(buffer)
    text = buffer.ToString()
finally:
    buffer.Close()

# 2) 탭을 쉼표로 (값에 쉼표가 있으면 따옴표로 감싼다)
lines = []
for line in text.split("\n"):
    fields = []
    for field in line.rstrip("\r").split("\t"):
        if "," in field or '"' in field:
            field = '"' + field.replace('"', '""') + '"'
        fields.append(field)
    lines.append(",".join(fields))

# 3) 파일로
writer = StreamWriter("C:/temp/export.csv", False, Encoding.UTF8)
try:
    writer.Write("\n".join(lines))
finally:
    writer.Close()
```

### 여러 표를 한 번에

원래 이 예제의 목적(일괄 내보내기)은 이렇게 달성합니다.

```python
# -*- coding: utf-8 -*-
# 모든 페이지의 모든 표 시각화를 각각 파일로 내보낸다.

from Spotfire.Dxp.Application.Visuals import TablePlot
from System.IO import StreamWriter, Path, Directory
from System.Text import Encoding
from System import DateTime

OUT_DIR = "C:/temp"

folder = Path.Combine(OUT_DIR, "export_" + DateTime.Now.ToString("yyyyMMdd_HHmmss"))
Directory.CreateDirectory(folder)

exported, skipped = [], []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            plot = visual.As[TablePlot]()
            if plot is None:
                continue
        except:
            continue

        if not plot.ExportDataEnabled:
            skipped.append(visual.Title)
            continue

        safe = (visual.Title or u"table").replace("/", "_").replace("\\", "_")
        path = Path.Combine(folder, safe + ".txt")

        writer = StreamWriter(path, False, Encoding.UTF8)
        try:
            plot.ExportText(writer)
        finally:
            writer.Close()
        exported.append(visual.Title)

Document.Properties["ScriptLog"] = u"%d개 내보냄 / %d개 건너뜀<br>%s" % (
    len(exported), len(skipped), folder)
```

!!! tip "표 시각화가 없다면"
    이 방법은 **표(Table) 시각화를 경유**합니다. 데이터 테이블만 있다면
    숨긴 페이지에 표를 하나 만들어 두고 그것을 대상으로 삼는 방식이 실무적입니다.

### 참고 — `CreateDataWriter` 방식 (라이선스가 있는 환경에서)

커뮤니티에 널리 퍼진 방식입니다. 이 환경에서는 `None` 이 반환되어 실패했지만,
내보내기 라이선스가 있는 환경에서는 동작합니다.

```python
# -*- coding: utf-8 -*-
# 참고용 — 이 환경에서는 CreateDataWriter 가 None 을 반환해 실패합니다.
from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from System.IO import File

table = Document.ActiveDataTableReference
filtered = Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()
columnNames = [c.Name for c in table.Columns]

writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.SpreadsheetDataCsvUtf8Writer)
if writer is None:
    Document.Properties["ScriptLog"] = u"내보내기 권한이 없습니다. ExportText 방식을 쓰세요."
else:
    stream = File.Create("C:/temp/data.csv")
    try:
        writer.Write(stream, table, filtered, columnNames)
    finally:
        stream.Close()
```

**반환값이 `None` 인지 반드시 확인하세요.** 확인하지 않으면
`'NoneType' object has no attribute 'Write'` 로 넘어갑니다.

Spotfire 14.x에서 확인된 식별자 전체 목록입니다.

```text
ExcelXlsDataWriter                    SpreadsheetDataSemicolonWriter
ExcelXlsxDataWriter                   SpreadsheetDataWriter
SbdfDataWriter                        SpreadsheetUtf8DataWriter
SpreadsheetDataCsvUtf8Writer          StdfDataWriter
SpreadsheetDataCsvWriter              StdfOneDataWriter
SpreadsheetDataSemicolonUtf8Writer
```

!!! note "검증 포인트"
    - 위 `ExportText` 방식은 **Analyst 전용**입니다(로컬 파일 쓰기).
      Web Player에서 데이터를 내보내야 한다면 `DataTable.ExportDataToLibrary` 를 보세요.

      ```text
      ExportDataToLibrary(self: DataTable, libraryItem: LibraryItem, title: str) -> LibraryItem
      ```

    - `ExportText` 출력은 **탭 구분**입니다. 쉼표가 필요하면 위 변환 코드를 쓰세요.
    - `StreamWriter` 에 `Encoding.UTF8` 을 명시하세요. 한글이 깨질 수 있습니다.
    - `plot.ExportDataEnabled` 로 **내보내기 가능 여부를 코드에서 판별**할 수 있습니다.

---

## 예제 16. 마킹한 행을 새 데이터 테이블로 스냅샷

<ul class="meta">
<li class="badge risk-mid">위험도 중간</li>
<li class="badge hard">기본 기능으로 어려움</li>
</ul>

**문제 상황**  
차트에서 이상치 30건을 마킹했습니다. 이 30건을 **따로 떼어내 별도 테이블로 보관**하고,
원본과 나란히 비교하고 싶습니다.

**기본 기능으로 어려운 이유**  
Spotfire UI에는 "마킹된 행을 새 데이터 테이블로 저장" 기능이 없습니다.
마킹은 휘발성이라 필터를 건드리면 사라집니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `sourceTable` | DataTable | 원본 테이블 |
| `snapshotName` | String | 문서 속성 `SnapshotName` |

```python
# -*- coding: utf-8 -*-
# 현재 마킹된 행만 새 데이터 테이블로 복사한다.
#
# 매개변수:
#   sourceTable  (DataTable) 원본 테이블
#   snapshotName (String)    만들 테이블 이름

from Spotfire.Dxp.Data.Import import DataTableDataSource

# 마킹 이름은 하드코딩하지 않는다 (한국어 UI에서는 "마킹")
marking = Document.ActiveMarkingSelectionReference
markedRows = marking.GetSelection(sourceTable).AsIndexSet()

if markedRows.Count == 0:
    Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 차트에서 선택하세요."
else:
    # 마킹을 그대로 데이터 원본에 넘긴다.
    # 마킹(DataMarkingSelection)이 곧 DataSelection 이므로 별도 변환이 필요 없다.
    source = DataTableDataSource(sourceTable, marking)

    if Document.Data.Tables.Contains(snapshotName):
        Document.Data.Tables[snapshotName].ReplaceData(source)
        action = u"갱신"
    else:
        Document.Data.Tables.Add(snapshotName, source)
        action = u"생성"

    Document.Properties["ScriptLog"] = u"'%s' 테이블을 %s했습니다. (%d행)" % (
        snapshotName, action, markedRows.Count)
```

### 변형: 현재 필터를 통과한 행만

마킹 대신 **필터링**을 넘기면 그대로 필터 결과 스냅샷이 됩니다. 코드는 한 줄만 다릅니다.

```python
# -*- coding: utf-8 -*-
from Spotfire.Dxp.Data.Import import DataTableDataSource

filtering = Document.ActiveFilteringSelectionReference
source = DataTableDataSource(sourceTable, filtering)
Document.Data.Tables.Add(u"필터 결과", source)
```

필터링도 마킹과 마찬가지로 `DataSelection` 의 구체 클래스이기 때문입니다.

| 넘기는 것 | 실제 타입 | 결과 |
|-----------|-----------|------|
| `Document.ActiveMarkingSelectionReference` | `DataMarkingSelection` | 마킹된 행만 |
| `Document.ActiveFilteringSelectionReference` | `DataFilteringSelection` | 필터를 통과한 행만 |

### 활용

- **What-if 비교**: 조건을 바꿔 가며 마킹 → 스냅샷을 여러 개 만들어 나란히 비교
- **검토 목록 관리**: 이상치를 마킹해 스냅샷으로 저장 → 그 테이블로만 표를 만들어 검토
- **원본 대비 고정**: 필터를 바꿔도, 마킹을 바꿔도 스냅샷은 그대로 남습니다

!!! success "실측으로 확인된 동작 (Spotfire 14.x)"
    ```text
    10행 마킹 -> 새 테이블 생성   -> 새 테이블 10행   (부분집합 적용됨)
    마킹을 20행으로 변경          -> 새 테이블 10행   (변하지 않음)
    새 테이블의 IsRefreshable     -> False
    ```

    **생성 시점에 고정되는 진짜 스냅샷입니다.** 이후 마킹을 바꿔도 따라 변하지 않습니다.

!!! note "검증 포인트"
    - 스냅샷 테이블은 **문서에 포함되어 저장**됩니다. 행이 많으면 파일 크기가 커집니다.
    - 마킹 이름을 하드코딩하지 않은 이유는 [7.1 참조](07-pitfalls.html)
    - `ReplaceData` 는 기존 테이블 내용을 지웁니다. 스냅샷 이름을 원본과 같게 두지 마세요.
    - `DataTableDataSourceUpdateBehavior` 에는 `Automatic` 과 `Manual` 이 있지만,
      `(dataTable, updateBehavior)` 오버로드에서만 지정할 수 있어 선택과 동시에 줄 수 없습니다.

!!! tip "예전에 널리 쓰이던 방법과의 차이"
    커뮤니티에는 **writer로 메모리에 STDF를 쓴 뒤 다시 읽어들이는** 방식이 많이 돌아다닙니다.

    ```python
    # 흔히 보이는 옛 방식 — 이 환경에서는 동작하지 않습니다
    writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.StdfDataWriter)
    writer.Write(stream, table, markedRows, columnNames)
    dataSource = StdfDataSource(stream)
    ```

    두 가지 이유로 권하지 않습니다.

    - `StdfDataSource` 라는 이름은 **존재하지 않습니다**(14.x 확인). `StdfFileDataSource` 입니다
    - `CreateDataWriter` 가 **`None` 을 반환**할 수 있습니다(예제 15 참조)

    위의 `DataTableDataSource` 방식은 20줄이 3줄로 줄고, 라이선스 제약도 받지 않습니다.

---

## 예제 17. 모든 데이터 테이블 일괄 새로고침

<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
정보 링크 기반 테이블이 8개인데, 최신 데이터를 보려면 하나씩 새로고침해야 합니다.

**기본 기능으로 어려운 이유**  
`파일 > 데이터 다시 로드`가 있긴 하지만, **어떤 테이블이 실제로 갱신이 필요한지**
가려서 처리하거나, 결과를 알림으로 남기거나, 일부만 골라 새로고침할 수는 없습니다.

**스크립트 매개변수**  
없음.

```python
# -*- coding: utf-8 -*-
# 새로고침 가능한 모든 데이터 테이블을 새로고침하고 결과를 알린다.

from Spotfire.Dxp.Framework.ApplicationModel import NotificationService

refreshed = []
skipped = []
failed = []

for table in Document.Data.Tables:
    try:
        if not table.IsRefreshable:
            skipped.append(u"%s (새로고침 불가)" % table.Name)
            continue

        # NeedsRefresh 검사를 빼면 항상 강제로 새로고침한다
        table.Refresh()
        refreshed.append(table.Name)
    except Exception, e:
        failed.append(u"%s: %s" % (table.Name, str(e)))

summary = u"새로고침 %d개" % len(refreshed)
if refreshed:
    summary += u" — " + u", ".join(refreshed)
if failed:
    summary += u" / 실패 %d개" % len(failed)

Document.Properties["ScriptLog"] = summary

# 사용자에게 알림 (Web Player에서도 동작)
ns = Application.GetService[NotificationService]()
if failed:
    ns.AddWarningNotification(u"데이터 새로고침", summary, u"\n".join(failed))
else:
    ns.AddInformationNotification(u"데이터 새로고침", summary, u"")
```

### 변형: 필요한 것만 새로고침

```python
for table in Document.Data.Tables:
    if table.IsRefreshable and table.NeedsRefresh:
        table.Refresh()
```

!!! note "검증 포인트"
    - `NeedsRefresh`는 **Spotfire가 갱신이 필요하다고 판단한 경우**에만 `True`입니다.
      외부 DB가 바뀐 것을 Spotfire가 모를 수 있으므로, 확실히 최신을 원하면 조건 없이
      `Refresh()`를 부르세요.
    - 임베디드(파일에 포함된) 데이터는 `IsRefreshable`이 `False`입니다.
    - 테이블이 많고 크면 실행에 시간이 걸립니다. 실행 중 Spotfire가 멈춘 것처럼 보일 수 있습니다.
    - `NotificationService` 는 `AddInformationNotification` ·
      `AddWarningNotification` · `AddErrorNotification` 세 가지와, 각각의
      `...WithActions` 변형을 제공합니다.

---

다음 장은 **문서를 만들어 내고 진단하는** 예제입니다.
