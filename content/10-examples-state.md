# 10. 예제 B · 필터·마킹·페이지 상태

대시보드의 **상태**를 다루는 예제입니다.
필터, 마킹, 페이지 표시 여부처럼 "사용자가 만지는 것"을 코드로 제어합니다.

이 장의 예제는 **문서 구조를 바꾸지 않아** 대체로 안전하고,
그대로 사용자용 버튼으로 배포할 수 있는 것이 많습니다.

---

## 예제 8. 마킹 결과를 문서 속성으로 넘기기


<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
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

---

## 예제 9. 키 컬럼으로 다른 테이블에 마킹 전파


<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
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

# 마킹 이름은 하드코딩하지 않는다 (한국어 UI에서는 "마킹")
marking = Document.ActiveMarkingSelectionReference

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
        hits.AddIndex(row.Index)      # IndexSet 은 Add() 가 아니라 AddIndex() 를 쓴다
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

---

## 예제 10. 대시보드 전체 상태 초기화


<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge hard">기본 기능으로 어려움</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
사용자가 필터를 이것저것 만지고 마킹도 해 놓은 뒤 "처음 상태로 돌려 줘"라고 합니다.
파일을 다시 여는 것 말고 버튼 하나로 하고 싶습니다.

**기본 기능으로 어려운 이유**  
액션 컨트롤의 **"모든 필터 재설정"은 현재 필터링 스킴 하나만** 초기화합니다.
페이지마다 다른 스킴을 쓰는 대시보드라면 다른 페이지의 필터는 그대로 남습니다.
게다가 마킹·문서 속성·줌 상태는 어떤 기본 기능으로도 함께 초기화되지 않습니다.

이 예제는 **가장 자주 요청되는 스크립트**입니다.

**스크립트 매개변수**
없음.

```python
# -*- coding: utf-8 -*-
# 대시보드를 초기 상태로 되돌린다.
#   1) 모든 필터링 스킴의 필터 초기화
#   2) 모든 마킹 해제
#   3) 문서 속성을 기본값으로
#   4) 모든 차트 줌 초기화
#   5) 첫 페이지로 이동

from Spotfire.Dxp.Data import IndexSet, RowSelection
from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

log = []

# 1) 모든 필터링 스킴 초기화 — 기본 버튼은 현재 스킴 하나만 처리한다
schemeCount = 0
for scheme in Document.FilteringSchemes:
    scheme.ResetAllFilters()
    schemeCount += 1
log.append(u"필터링 스킴 %d개 초기화" % schemeCount)

# 2) 모든 마킹 해제 (모든 테이블에 대해)
markingCount = 0
for marking in Document.Data.Markings:
    for table in Document.Data.Tables:
        try:
            empty = RowSelection(IndexSet(table.RowCount, False))
            marking.SetSelection(empty, table)
        except:
            pass
    markingCount += 1
log.append(u"마킹 %d개 해제" % markingCount)

# 3) 문서 속성 기본값 — 대시보드에 맞게 수정하세요
DEFAULTS = {
    "SelectedRegion": "All",
    "SelectedMeasure": "Revenue",
    "LimitExpression": "",
    "ScriptLog": "",
}
for name, value in DEFAULTS.items():
    try:
        Document.Properties[name] = value
    except:
        pass       # 없는 속성은 건너뛴다
log.append(u"문서 속성 %d개 복원" % len(DEFAULTS))

# 4) 모든 차트 줌 초기화
zoomReset = 0
for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            for axisName in ["XAxis", "YAxis"]:
                try:
                    getattr(vc, axisName).ZoomRange = AxisRange.DefaultRange
                    zoomReset += 1
                except:
                    pass
        except:
            pass
log.append(u"축 %d개 줌 초기화" % zoomReset)

# 5) 첫 페이지로
if Document.Pages.Count > 0:
    Document.ActivePageReference = Document.Pages[0]

Document.Properties["ScriptLog"] = u" / ".join(log)
```

!!! note "검증 포인트"
    - **`DEFAULTS` 딕셔너리는 반드시 자기 대시보드에 맞게 고치세요.** 그대로 두면
      존재하지 않는 속성에 대해 조용히 건너뜁니다.
    - `Document.FilteringSchemes` 순회 + `ResetAllFilters()` 가 이 예제의 핵심입니다.
      이 두 줄만으로 "모든 페이지의 모든 필터 초기화"가 됩니다.
    - 마킹 해제는 모든 마킹 × 모든 테이블 조합을 돌므로, 테이블이 아주 많으면 잠깐 걸립니다.
    - 이 스크립트는 **사용자에게 그대로 배포해도 안전**합니다. 문서 구조를 바꾸지 않습니다.

---

---

## 예제 11. 원하는 컬럼의 필터만 선택적으로 초기화


<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge hard">기본 기능으로 어려움</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
"기간 필터는 그대로 두고, 제품·지역 필터만 초기화" 하고 싶습니다.
전체 초기화([예제 10](11-examples-data.html))는 애써 맞춰 놓은 기간 설정까지 날려 버립니다.

**기본 기능으로 어려운 이유**  
Spotfire의 필터 초기화는 **전체 아니면 개별 수동**입니다.
"이 3개만 초기화"를 한 번에 하는 기능이 없습니다.
필터가 여러 필터링 스킴에 걸쳐 있으면 더 번거롭습니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `columnList` | String | 문서 속성 `ResetTargets` (쉼표 구분) |

```python
# -*- coding: utf-8 -*-
# 지정한 컬럼의 필터만 모든 필터링 스킴에서 초기화한다.
#
# 매개변수:
#   columnList (String) 초기화할 컬럼 이름을 쉼표로 구분. 예: "Category,Region,Product"

from Spotfire.Dxp.Data import *
from Spotfire.Dxp.Application.Filters import *

targets = [name.strip() for name in (columnList or "").split(",") if name.strip()]

reset = []
missing = []

# 모든 필터링 스킴 × 모든 데이터 테이블 × 대상 컬럼
for filteringScheme in Document.FilteringSchemes:
    for dataTable in Document.Data.Tables:
        for column in dataTable.Columns:
            if column.Name not in targets:
                continue
            try:
                # 스킴에서 [테이블][컬럼] 으로 필터를 직접 꺼낸다
                columnFilter = filteringScheme[dataTable][column]
                columnFilter.Reset()
                reset.append(u"%s.%s" % (dataTable.Name, column.Name))
            except Exception, e:
                # 그 스킴/테이블에 해당 필터가 없는 경우
                missing.append(u"%s.%s" % (dataTable.Name, column.Name))

message = u"필터 초기화 %d건" % len(reset)
if reset:
    message += u" — " + u", ".join(sorted(set(reset)))
if missing:
    message += u" / 해당 없음 %d건" % len(set(missing))

Document.Properties["ScriptLog"] = message
```

### 변형: 특정 컬럼만 빼고 전부 초기화

"기간만 유지하고 나머지 전부"가 실무에서 더 흔합니다.

```python
# -*- coding: utf-8 -*-
# KEEP 목록에 있는 컬럼만 남기고 나머지 필터를 전부 초기화한다.

from Spotfire.Dxp.Data import *
from Spotfire.Dxp.Application.Filters import *

KEEP = [u"기간", u"Date"]      # 이 컬럼들의 필터는 건드리지 않는다

reset = 0
for filteringScheme in Document.FilteringSchemes:
    for dataTable in Document.Data.Tables:
        for column in dataTable.Columns:
            if column.Name in KEEP:
                continue
            try:
                filteringScheme[dataTable][column].Reset()
                reset += 1
            except:
                pass

Document.Properties["ScriptLog"] = u"%d개 필터를 초기화했습니다. (유지: %s)" % (
    reset, u", ".join(KEEP))
```

!!! note "검증 포인트"
    - `filteringScheme[dataTable][column]` 이 **핵심 문법**입니다.
      필터링 스킴에서 테이블 → 컬럼 순으로 인덱싱하면 해당 컬럼의 필터가 나옵니다.
      반환값은 필터 객체이고 `Reset()` 을 가지고 있습니다.

      ```text
      scheme[table][column]  ->  Step: (KB073100, KB268900, KB425000)
      ```
    - 모든 스킴 × 모든 테이블 × 모든 컬럼을 순회하므로, 컬럼이 아주 많으면 잠깐 걸립니다.
      대상 테이블이 정해져 있다면 `Document.Data.Tables` 대신 특정 테이블만 도세요.
    - 해당 스킴에 필터가 없으면 예외가 납니다. 정상이므로 위 코드처럼 건너뛰면 됩니다.
    - **컬럼 이름은 대소문자를 구분합니다.** 초기화가 안 되면 이름부터 확인하세요.
    - 필터 하나만 초기화하려면 스킴 하나만 지정해도 됩니다.

      ```python
      Document.FilteringSchemes[0].ResetAllFilters()   # 첫 번째 스킴 전체 초기화
      ```

---

다음 장은 **심화 자동화**입니다.

---

## 예제 12. 역할별 필터 패널 구성


<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge bulk">일괄 적용</li>
</ul>

**문제 상황**  
필터 패널에 컬럼이 40개 나와서 사용자가 헤맵니다.
"이번 분석에 필요한 6개만" 보여 주고 싶고, 그 목록은 상황마다 다릅니다.

**기본 기능으로 어려운 이유**  
`필터 구성(Organize Filters)`으로 숨길 수는 있지만 **수동 작업이고 고정**입니다.
페이지가 여러 개면 페이지마다 반복해야 합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `filterList` | String | 문서 속성 `VisibleFilters` (쉼표 구분) |

```python
# -*- coding: utf-8 -*-
# 지정한 필터만 남기고 모든 페이지의 필터 패널을 정리한다.
#
# 매개변수:
#   filterList (String) 보여 줄 컬럼 이름을 쉼표로 구분. 예: "Region,Year,Category"
#                       빈 문자열이면 전부 표시

wanted = [name.strip() for name in (filterList or "").split(",") if name.strip()]
showAll = (len(wanted) == 0)

shown, hidden = 0, 0

for page in Document.Pages:
    filterPanel = page.FilterPanel

    for tableGroup in filterPanel.TableGroups:
        tableGroup.Expanded = True

        # 최상위 필터
        for handle in tableGroup.FilterHandles:
            visible = showAll or (handle.FilterReference.Name in wanted)
            handle.Visible = visible
            if visible:
                shown += 1
            else:
                hidden += 1

        # 하위 그룹 안의 필터
        for subGroup in tableGroup.SubGroups:
            groupHasVisible = False
            for handle in subGroup.FilterHandles:
                visible = showAll or (handle.FilterReference.Name in wanted)
                handle.Visible = visible
                if visible:
                    shown += 1
                    groupHasVisible = True
                else:
                    hidden += 1
            subGroup.Visible = groupHasVisible or showAll

Document.Properties["ScriptLog"] = u"필터 표시 %d개 / 숨김 %d개" % (shown, hidden)
```

### 변형: 수정된 필터만 찾아 보여 주기

"지금 어떤 필터가 걸려 있지?"를 알려 주는 스크립트입니다.

```python
# -*- coding: utf-8 -*-
# 현재 값이 변경된(modified) 필터 목록을 문서 속성에 기록한다.

page = Document.ActivePageReference
filterPanel = page.FilterPanel

modified = []
for tableGroup in filterPanel.TableGroups:
    tableName = tableGroup.FilterCollectionReference.DataTableReference.Name
    for handle in tableGroup.FilterHandles:
        if handle.FilterReference.Modified:
            modified.append(u"%s: %s" % (tableName, handle.FilterReference.ToString()))
    for subGroup in tableGroup.SubGroups:
        for handle in subGroup.FilterHandles:
            if handle.FilterReference.Modified:
                modified.append(u"%s: %s" % (tableName, handle.FilterReference.ToString()))

Document.Properties["ActiveFilters"] = (
    u"<br>".join(modified) if modified else u"적용된 필터 없음")
```

!!! note "검증 포인트"
    - `FilterHandle.Visible`을 `False`로 두면 **필터가 해제되는 것이 아니라 안 보이기만** 합니다.
      값이 걸린 채 숨기면 사용자가 원인을 못 찾으므로, 숨기기 전에 예제 10으로 초기화하세요.
    - `filterPanel.TableGroups`는 **페이지별로 존재**합니다. 위 코드처럼 모든 페이지를 돌아야
      전체가 정리됩니다.
    - `FilterReference.Name`은 대개 컬럼 이름과 같습니다. 다르면 먼저 출력해 확인하세요.
    - `InteractiveSearchPattern`으로 필터 패널 검색창을 제어할 수도 있습니다.
      `filterPanel.InteractiveSearchPattern = "status:modified"` 로 수정된 필터만 보이게 할 수 있습니다.

---

---

## 예제 13. 문서 속성 값으로 페이지 표시/숨김


<ul class="meta">
<li class="badge risk-low">위험도 낮음</li>
<li class="badge hard">기본 기능으로 어려움</li>
</ul>

**문제 상황**  
하나의 분석 파일을 **영업팀과 재무팀이 같이** 씁니다.
영업팀에게는 재무 페이지 3개를 아예 안 보이게 하고 싶습니다.

**기본 기능으로 어려운 이유**  
Spotfire에서 페이지 숨김은 **작성 시점에 고정**되는 설정입니다.
"사용자나 선택값에 따라 동적으로" 페이지를 보였다 숨겼다 하는 기능은 없습니다.
파일을 두 벌로 나누면 관리가 두 배가 됩니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `role` | String | 문서 속성 `UserRole` |

```python
# -*- coding: utf-8 -*-
# 역할에 따라 페이지를 보이거나 숨긴다.
#
# 매개변수:
#   role (String) 문서 속성 "UserRole" 의 값

# 역할별로 보여 줄 페이지 제목 목록
VISIBLE_PAGES = {
    u"영업":   [u"요약", u"매출 상세", u"지역 분석"],
    u"재무":   [u"요약", u"손익", u"원가 분석", u"예산 대비"],
    u"관리자": None,      # None 이면 전부 표시
}

allowed = VISIBLE_PAGES.get(role, [u"요약"])     # 모르는 역할은 요약만

shown, hidden = [], []

for page in Document.Pages:
    visible = (allowed is None) or (page.Title in allowed)
    try:
        page.Visible = visible
        (shown if visible else hidden).append(page.Title)
    except:
        pass

# 현재 페이지가 숨겨졌다면 보이는 첫 페이지로 이동
if not Document.ActivePageReference.Visible:
    for page in Document.Pages:
        if page.Visible:
            Document.ActivePageReference = page
            break

Document.Properties["ScriptLog"] = u"[%s] 표시 %d개 / 숨김 %d개" % (
    role, len(shown), len(hidden))
```

### 변형: 로그인 사용자로 자동 판별

```python
from System.Threading import Thread

userName = Thread.CurrentPrincipal.Identity.Name    # "DOMAIN\\user" 형태
Document.Properties["CurrentUser"] = userName

FINANCE_USERS = ["DOMAIN\\kim", "DOMAIN\\lee"]
role = u"재무" if userName in FINANCE_USERS else u"영업"
```

!!! danger "검증 포인트 — 보안 장치가 아닙니다"
    - **페이지 숨김은 보안이 아닙니다.** 데이터는 파일 안에 그대로 있고,
      스크립트를 실행할 수 있는 사람은 다시 보이게 만들 수 있습니다.
      진짜 접근 제어가 필요하면 **라이브러리 권한이나 정보 링크 수준에서** 처리하세요.
    - `Page.Visible` 은 읽기·쓰기 모두 동작합니다.
    - 페이지 숨김은 **보안 장치가 아닙니다** → [7.6 참조](07-pitfalls.html)
    - 페이지를 숨긴 채로 저장하면 **다음에 열 때도 숨겨진 상태**입니다.
      문서를 열 때 자동 실행되는 초기화 스크립트에 이 로직을 넣어 두세요.
    - 사용자 이름 형식은 인증 방식에 따라 다릅니다. 먼저 출력해 보고 목록을 만드세요.

---


---

다음 장은 **데이터를 읽고 내보내는** 예제입니다.
