# 7. 예제 C · 동적 UI 제어

사용자가 보는 화면 자체를 스크립트로 바꾸는 예제입니다.
"권한에 따라 다른 화면", "한 번에 초기화" 같은 요구는 기본 기능만으로는 만들 수 없습니다.

---

## 예제 13. 대시보드 전체 상태 초기화

<ul class="meta">
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

## 예제 14. 문서 속성 값으로 페이지 표시/숨김

<ul class="meta">
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
    - `Page.Visible` 속성은 버전에 따라 동작이 다를 수 있습니다.
      실패하면 `for m in dir(Document.Pages[0]): print m` 으로 확인하세요.
    - 페이지를 숨긴 채로 저장하면 **다음에 열 때도 숨겨진 상태**입니다.
      문서를 열 때 자동 실행되는 초기화 스크립트에 이 로직을 넣어 두세요.
    - 사용자 이름 형식은 인증 방식에 따라 다릅니다. 먼저 출력해 보고 목록을 만드세요.

---

## 예제 15. 역할별 필터 패널 구성

<ul class="meta">
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
      값이 걸린 채 숨기면 사용자가 원인을 못 찾으므로, 숨기기 전에 예제 13으로 초기화하세요.
    - `filterPanel.TableGroups`는 **페이지별로 존재**합니다. 위 코드처럼 모든 페이지를 돌아야
      전체가 정리됩니다.
    - `FilterReference.Name`은 대개 컬럼 이름과 같습니다. 다르면 먼저 출력해 확인하세요.
    - `InteractiveSearchPattern`으로 필터 패널 검색창을 제어할 수도 있습니다.
      `filterPanel.InteractiveSearchPattern = "status:modified"` 로 수정된 필터만 보이게 할 수 있습니다.

---

## 예제 16. 시각화 유형 일괄 토글

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
</ul>

**문제 상황**  
같은 데이터를 **막대 차트로도 보고 선 차트로도** 보고 싶습니다.
차트가 6개인데 하나씩 유형을 바꾸면 축 설정이 흐트러집니다.

**기본 기능으로 어려운 이유**  
시각화 유형 변경은 개별 작업이고, 여러 개를 동시에 바꾸는 UI가 없습니다.
같은 페이지에 두 벌을 만들어 놓고 숨겼다 보였다 하는 방법은 유지보수가 어렵습니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `chartType` | String | 문서 속성 `ChartType` (`Bar` / `Line` / `Area`) |

```python
# -*- coding: utf-8 -*-
# 모든 페이지의 차트를 지정한 유형으로 바꾼다.
# 축 표현식은 Spotfire가 대체로 유지해 준다.
#
# 매개변수:
#   chartType (String) "Bar", "Line", "Area", "Scatter" 중 하나

from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers

TYPE_MAP = {
    "Bar":     VisualTypeIdentifiers.BarChart,
    "Line":    VisualTypeIdentifiers.LineChart,
    "Area":    VisualTypeIdentifiers.CombinationChart,
    "Scatter": VisualTypeIdentifiers.ScatterPlot,
}

# 서로 바꿔도 되는 유형들만 대상으로 한다 (표·텍스트 영역은 제외)
SWITCHABLE = [
    VisualTypeIdentifiers.BarChart,
    VisualTypeIdentifiers.LineChart,
    VisualTypeIdentifiers.CombinationChart,
    VisualTypeIdentifiers.ScatterPlot,
]

target = TYPE_MAP.get(chartType)

if target is None:
    Document.Properties["ScriptLog"] = u"알 수 없는 유형: %s" % chartType
else:
    changed = 0
    for page in Document.Pages:
        for visual in page.Visuals:
            try:
                if visual.TypeId in SWITCHABLE and visual.TypeId != target:
                    visual.TypeId = target
                    changed += 1
            except:
                pass

    Document.Properties["ScriptLog"] = u"%d개 시각화를 %s 로 전환했습니다." % (changed, chartType)
```

### 변형: 개별 시각화 토글 (버튼 하나로 왔다 갔다)

```python
# -*- coding: utf-8 -*-
# 매개변수: viz (Visualization)
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers

if viz.TypeId == VisualTypeIdentifiers.LineChart:
    viz.TypeId = VisualTypeIdentifiers.BarChart
elif viz.TypeId == VisualTypeIdentifiers.BarChart:
    viz.TypeId = VisualTypeIdentifiers.LineChart
```

!!! note "검증 포인트"
    - 유형을 바꾸면 **그 유형에 없는 축 설정은 사라집니다.**
      막대 ↔ 선은 대체로 안전하지만, 산점도로 바꾸면 집계가 풀립니다.
    - `SWITCHABLE` 목록에 표·교차 표·텍스트 영역을 넣지 마세요. 예외가 나거나 내용이 깨집니다.
    - 특정 차트를 제외하려면 제목 규칙을 두는 것이 편합니다.
      ```python
      if visual.Title.startswith(u"[고정]"):
          continue
      ```
    - **되돌리기가 완전하지 않을 수 있습니다.** 사본에서 먼저 시험하세요.

---

다음 장은 **심화 자동화** 두 편입니다.
