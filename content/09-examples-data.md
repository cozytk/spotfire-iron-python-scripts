# 9. 예제 B · 데이터와 내보내기

데이터를 읽고, 마킹을 다루고, 파일로 내보내는 예제입니다.
이 장의 예제는 대부분 **Spotfire UI에 아예 없는 기능**이거나 **반복 작업을 한 번으로 줄이는** 것입니다.

---

## 예제 8. 모든 페이지의 시각화를 PNG로 일괄 내보내기

<ul class="meta">
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
            failed.append(u"%s / %s" % (page.Title, visual.Title))

msg = u"%d개 이미지를 저장했습니다: %s" % (saved, folder)
if failed:
    msg += u" (건너뜀 %d개: %s)" % (len(failed), u", ".join(failed))

Document.Properties["ScriptLog"] = msg
```

!!! danger "검증 포인트 — Analyst 전용입니다"
    - **Web Player에서는 동작하지 않습니다.** 로컬 파일 시스템에 쓰기 때문입니다.
    - `VisualContent.Render(Graphics, Rectangle)` 방식은 오래전부터 쓰인 방법이지만,
      **텍스트 영역과 Mod 시각화는 렌더링되지 않거나 빈 이미지가 나올 수 있습니다.**
      위 코드는 실패한 것을 목록으로 보고합니다.
    - 신형 API인 `RenderSync` / `RenderAsync`(7.12+)를 쓰면 **현재 테마가 적용된**
      이미지를 얻을 수 있습니다. 버전에 따라 시그니처가 다르므로, 위 방식이 잘 되면
      굳이 바꿀 필요는 없습니다.
    - 해상도를 키우면 텍스트가 상대적으로 작아집니다. 보고서용이면 `WIDTH/HEIGHT` 비율을
      실제 시각화 배치 비율과 비슷하게 맞추세요.
    - 폴더가 없으면 `Directory.CreateDirectory`가 만들어 줍니다. 쓰기 권한은 확인하세요.

---

## 예제 9. 여러 데이터 테이블을 한 번에 파일로 내보내기

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
분석에 들어 있는 데이터 테이블 6개를 **현재 필터가 적용된 상태 그대로** CSV로 넘겨야 합니다.

**기본 기능으로 어려운 이유**  
`파일 > 내보내기 > 데이터`는 한 번에 한 테이블입니다. 6번 반복해야 하고,
매번 저장 경로와 필터 적용 여부를 다시 지정해야 합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `outDir` | String | 문서 속성 `ExportFolder` |

```python
# -*- coding: utf-8 -*-
# 문서의 모든 데이터 테이블을, 현재 필터가 적용된 행만, 파일로 내보낸다.
# (Analyst 데스크톱 전용)
#
# 매개변수:
#   outDir (String) 저장 폴더 경로

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from System.IO import File, Path, Directory
from System import DateTime

# 형식 선택:
#   DataWriterTypeIdentifiers.ExcelXlsDataWriter  → .xls
#   DataWriterTypeIdentifiers.StdfDataWriter      → .stdf (Spotfire 이진 형식)
WRITER = DataWriterTypeIdentifiers.ExcelXlsDataWriter
EXTENSION = ".xls"

stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss")
folder = Path.Combine(outDir, "export_" + stamp)
Directory.CreateDirectory(folder)

exported = []

for table in Document.Data.Tables:
    # 현재 활성 필터링에서 살아남은 행만
    filtered = Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()

    # 전체 행을 내보내려면 위 줄 대신:
    # from Spotfire.Dxp.Data import IndexSet
    # filtered = IndexSet(table.RowCount, True)

    columnNames = [c.Name for c in table.Columns]

    writer = Document.Data.CreateDataWriter(WRITER)
    path = Path.Combine(folder, table.Name + EXTENSION)

    stream = File.OpenWrite(path)
    try:
        writer.Write(stream, table, filtered, columnNames)
    finally:
        stream.Close()

    exported.append(u"%s (%d행)" % (table.Name, filtered.Count))

Document.Properties["ScriptLog"] = u"%s<br>저장 위치: %s" % (u"<br>".join(exported), folder)
```

### 변형: 특정 컬럼만 내보내기

```python
# 이름에 "_internal" 이 붙은 컬럼은 제외
columnNames = [c.Name for c in table.Columns if "_internal" not in c.Name]
```

!!! note "검증 포인트"
    - **Analyst 전용**입니다(로컬 파일 쓰기).
    - `File.OpenWrite`는 기존 파일이 더 길면 뒷부분이 남을 수 있습니다.
      매번 새 폴더에 쓰는 위 방식이 안전합니다. 같은 파일에 덮어쓰려면
      `File.Create(path)`를 쓰세요.
    - `writer.Write`가 요구하는 컬럼 이름은 **파이썬 리스트로 넘어갑니다.**
      타입 오류가 나면 `Array[String](columnNames)`로 변환해 보세요 → [3.5 참조](05-dotnet-interop.html#55-net)
    - CSV(텍스트)로 내보내려면 확장자만 바꾸는 것으로는 안 됩니다.
      사용 가능한 `DataWriterTypeIdentifiers` 목록은 버전마다 다르므로
      `for m in dir(DataWriterTypeIdentifiers): print m` 으로 확인하세요.

---

## 예제 10. 마킹한 행을 새 데이터 테이블로 스냅샷

<ul class="meta">
<li class="badge hard">기본 기능으로 어려움</li>
</ul>

**문제 상황**  
차트에서 이상치 30건을 마킹했습니다. 이 30건을 **따로 떼어내 별도 테이블로 보관**하고,
원본과 나란히 비교하고 싶습니다.

**기본 기능으로 어려운 이유**  
Spotfire UI에는 "마킹된 행을 새 데이터 테이블로 저장" 기능이 없습니다.
마킹은 휘발성이라 필터를 건드리면 사라집니다.
"마킹된 행에서 데이터 테이블 만들기"를 하려면 내보냈다가 다시 불러와야 합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `sourceTable` | DataTable | 원본 테이블 |
| `snapshotName` | String | 문서 속성 `SnapshotName` |

```python
# -*- coding: utf-8 -*-
# 현재 마킹된 행을 새 데이터 테이블로 복사한다.
# 메모리 스트림에 STDF로 쓴 뒤 다시 읽어 들이는 방식.
#
# 매개변수:
#   sourceTable  (DataTable) 원본 테이블
#   snapshotName (String)    만들 테이블 이름

from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
from Spotfire.Dxp.Data.Import import StdfDataSource
from System.IO import MemoryStream, SeekOrigin

MARKING_NAME = "Marking"

marking = Document.Data.Markings[MARKING_NAME]
markedRows = marking.GetSelection(sourceTable).AsIndexSet()

if markedRows.Count == 0:
    Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 차트에서 선택하세요."
else:
    columnNames = [c.Name for c in sourceTable.Columns]

    # 1) 마킹된 행만 메모리에 STDF로 기록
    stream = MemoryStream()
    writer = Document.Data.CreateDataWriter(DataWriterTypeIdentifiers.StdfDataWriter)
    writer.Write(stream, sourceTable, markedRows, columnNames)

    # 2) 스트림을 처음으로 되감아 데이터 원본으로 사용
    stream.Seek(0, SeekOrigin.Begin)
    dataSource = StdfDataSource(stream)

    # 3) 같은 이름이 있으면 내용만 교체, 없으면 새로 추가
    if Document.Data.Tables.Contains(snapshotName):
        Document.Data.Tables[snapshotName].ReplaceData(dataSource)
        action = u"갱신"
    else:
        Document.Data.Tables.Add(snapshotName, dataSource)
        action = u"생성"

    Document.Properties["ScriptLog"] = u"'%s' 테이블을 %s했습니다. (%d행)" % (
        snapshotName, action, markedRows.Count)
```

### 활용

- **What-if 비교**: 조건을 바꿔 가며 마킹 → 스냅샷을 여러 개 만들어 나란히 비교
- **검토 목록 관리**: 이상치를 마킹해 스냅샷으로 저장 → 그 테이블로만 표를 만들어 검토
- **원본 대비 고정**: 필터를 바꿔도 스냅샷은 그대로 남습니다

!!! note "검증 포인트"
    - `StdfDataSource`의 위치(`Spotfire.Dxp.Data.Import`)는 **버전에 따라 다를 수 있습니다.**
      import에서 실패하면 다음으로 확인하세요.

      ```python
      import Spotfire.Dxp.Data.Import as imp
      for m in dir(imp):
          if "Stdf" in m or "Source" in m:
              print m
      ```
    - 스냅샷 테이블은 **문서에 포함되어 저장**됩니다. 행이 많으면 파일 크기가 커집니다.
    - 마킹 이름이 `"Marking"`이 아닐 수 있습니다. `for m in Document.Data.Markings: print m.Name`
      으로 실제 이름을 확인하세요.
    - `ReplaceData`는 기존 테이블 내용을 지웁니다. 스냅샷 이름을 원본과 같게 두지 마세요.

---

## 예제 11. 마킹 결과를 문서 속성으로 넘기기

<ul class="meta">
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
차트에서 지역 몇 개를 마킹하면, **다른 차트의 제목이나 텍스트 영역에**
"선택: East, West (2개)" 처럼 표시하고 싶습니다.
또는 마킹한 값들을 표현식에 넣어 다른 시각화를 제어하고 싶습니다.

**기본 기능으로 어려운 이유**  
마킹 값은 표현식에서 직접 참조할 수 없습니다.
문서 속성으로 옮겨 놓아야 제목·표현식·데이터 제한에서 쓸 수 있습니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `sourceTable` | DataTable | 마킹을 읽을 테이블 |
| `keyColumn` | String | 문서 속성 또는 고정값 (예: `Region`) |

```python
# -*- coding: utf-8 -*-
# 마킹된 행에서 특정 컬럼의 고유값을 모아 문서 속성에 저장한다.
#
# 매개변수:
#   sourceTable (DataTable) 대상 테이블
#   keyColumn   (String)    값을 모을 컬럼 이름

from Spotfire.Dxp.Data import DataValueCursor

# 마킹 이름을 하드코딩하지 않고 "현재 활성 마킹"을 쓴다.
# 마킹 이름이 "Marking"이 아니어도, 나중에 바뀌어도 동작한다.
markedRows = Document.ActiveMarkingSelectionReference.GetSelection(sourceTable).AsIndexSet()

cursor = DataValueCursor.CreateFormatted(sourceTable.Columns[keyColumn])

# set을 쓰면 중복 제거가 빠르다 (행이 많을 때 특히)
seen = set()
for row in sourceTable.GetRows(markedRows, cursor):
    value = cursor.CurrentValue
    if value is not None and value != "":
        seen.add(value)

values = sorted(seen)

# 1) 사람이 읽는 문자열
Document.Properties["MarkedLabel"] = (
    u"선택: %s (%d개)" % (u", ".join(values), len(values)) if values
    else u"선택 없음")

# 2) 표현식에 넣을 형태 — "'East','West'"
Document.Properties["MarkedInList"] = u",".join(u"'%s'" % v for v in values)

# 3) 개수만
Document.Properties["MarkedCount"] = len(values)
```

**활용 — 표현식에서 쓰기**

다른 시각화의 데이터 제한 표현식에 다음처럼 넣으면, 마킹이 다른 차트를 필터링합니다.

```text
${MarkedInList} = "" or [Region] in (${MarkedInList})
```

시각화 제목에는 이렇게 넣습니다.

```text
매출 추이 — ${MarkedLabel}
```

!!! note "검증 포인트"
    - 마킹이 바뀔 때마다 자동 실행되게 하려면, 이 스크립트를 **문서 속성 변경 트리거**에
      직접 걸 수는 없습니다. 실무에서는 **텍스트 영역의 버튼**으로 실행하거나,
      마킹에 연동된 계산된 값을 문서 속성에 넣는 우회 방법을 씁니다.
    - `MarkedCount`에 정수를 넣으려면 문서 속성 타입이 **Integer**여야 합니다.
      문자열 속성이면 `str(len(values))`로 넣으세요.
    - `Document.ActiveMarkingSelectionReference`는 **현재 활성 마킹**을 가리킵니다.
      특정 마킹을 고정하고 싶다면 `Document.Data.Markings["마킹이름"]`을 쓰세요.
      단, 마킹 이름이 바뀌면 깨집니다.
    - 결과를 .NET 문자열 목록으로 다뤄야 한다면 다음 형태도 자주 쓰입니다.
      동작은 같으니 익숙한 쪽을 쓰세요.

      ```python
      from System.Collections.Generic import List
      collected = List[str]()
      for row in sourceTable.GetRows(markedRows, cursor):
          if cursor.CurrentValue <> str.Empty:
              collected.Add(cursor.CurrentValue)
      values = List[str](set(collected))       # 중복 제거
      Document.Properties["token"] = ", ".join(values)
      ```

---

## 예제 12. 키 컬럼으로 다른 테이블에 마킹 전파

<ul class="meta">
<li class="badge hard">기본 기능으로 어려움</li>
</ul>

**문제 상황**  
`주문` 테이블에서 고객 5명을 마킹했습니다.
같은 고객의 행을 `클레임` 테이블에서도 자동으로 마킹하고 싶습니다.

**기본 기능으로 어려운 이유**  
Spotfire에서 테이블 간 마킹 연동은 **데이터 테이블 관계(relation)** 를 설정해야 하고,
관계는 조인 조건이 명확한 경우에만 만들 수 있습니다.
키가 여러 개거나 가공이 필요하면(대소문자 무시, 접두사 제거 등) 관계로는 처리하지 못합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `sourceTable` | DataTable | 마킹을 읽을 테이블 |
| `targetTable` | DataTable | 마킹을 적용할 테이블 |
| `sourceKey` | String | 원본 키 컬럼명 |
| `targetKey` | String | 대상 키 컬럼명 |

```python
# -*- coding: utf-8 -*-
# 원본 테이블의 마킹된 키 값을 읽어, 같은 키를 가진 대상 테이블 행을 마킹한다.
#
# 매개변수:
#   sourceTable (DataTable) 마킹을 읽을 테이블
#   targetTable (DataTable) 마킹을 적용할 테이블
#   sourceKey   (String)    원본 키 컬럼명
#   targetKey   (String)    대상 키 컬럼명

from Spotfire.Dxp.Data import DataValueCursor, IndexSet, RowSelection

MARKING_NAME = "Marking"
marking = Document.Data.Markings[MARKING_NAME]

# 1) 원본에서 마킹된 키 값을 집합으로 수집
markedRows = marking.GetSelection(sourceTable).AsIndexSet()
sourceCursor = DataValueCursor.CreateFormatted(sourceTable.Columns[sourceKey])

keys = set()
for row in sourceTable.GetRows(markedRows, sourceCursor):
    value = sourceCursor.CurrentValue
    if value is not None:
        keys.add(value.strip().upper())      # 대소문자·공백 차이 무시

# 2) 대상 테이블 전체를 훑으며 일치하는 행 인덱스를 모은다
targetCursor = DataValueCursor.CreateFormatted(targetTable.Columns[targetKey])
allTargetRows = IndexSet(targetTable.RowCount, True)

hits = IndexSet(targetTable.RowCount, False)
matched = 0

for row in targetTable.GetRows(allTargetRows, targetCursor):
    value = targetCursor.CurrentValue
    if value is not None and value.strip().upper() in keys:
        hits.Add(row.Index)
        matched += 1

# 3) 대상 테이블에 마킹 적용
marking.SetSelection(RowSelection(hits), targetTable)

Document.Properties["ScriptLog"] = u"키 %d개 → '%s' 테이블 %d행 마킹" % (
    len(keys), targetTable.Name, matched)
```

!!! note "검증 포인트"
    - 키 값을 `.strip().upper()` 로 정규화했습니다. **숫자 키라면 이 부분을 빼야 합니다**
      (`CreateFormatted`가 반환한 문자열의 서식이 두 테이블에서 다를 수 있으므로,
      숫자 키는 `DataValueCursor.Create[float](...)` 로 읽고 비교하세요).
    - 대상 테이블 전체를 순회하므로 행이 수백만 건이면 느립니다.
      그 경우 표현식 방식(`targetTable.Select("[Key] in (...)")`)이 빠르지만,
      키 개수가 많으면 표현식 길이 제한에 걸립니다. 상황에 맞게 고르세요.
    - 같은 마킹 이름을 두 테이블에 쓰므로, **원본 마킹이 갱신되면 이 스크립트를 다시 실행**해야 합니다.
    - 복합 키라면 두 컬럼 값을 이어 붙여 비교하세요.
      ```python
      key = u"%s|%s" % (c1.CurrentValue, c2.CurrentValue)
      ```

---

## 예제 13. 모든 데이터 테이블 일괄 새로고침

<ul class="meta">
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
    - `NotificationService`의 메서드 이름(`AddInformationNotification`,
      `AddWarningNotification`)은 버전에 따라 다를 수 있습니다. 실패하면
      `for m in dir(ns): print m` 으로 확인하세요.

---

다음 장은 **UI를 동적으로 제어**하는 예제입니다.
