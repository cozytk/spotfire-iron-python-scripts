# 8. 예제 A · 여러 시각화·페이지에 일괄 적용

여기서부터 예제입니다. 이 장의 6개는 전부 **"시각화 하나씩 손으로 고치면 며칠 걸리는 일을
버튼 하나로 끝내는"** 유형입니다.

모든 예제는 다음 형식을 따릅니다.

- **문제 상황** — 무엇을 하려는가
- **기본 기능으로 어려운 이유** — 왜 스크립트가 필요한가
- **스크립트 매개변수** — 스크립트 편집 창에서 설정할 것
- **코드**
- **검증 포인트** — 실행 전에 확인할 것, 버전 의존성, 위험 요소

---

## 예제 1. 문서 전체 시각화 인벤토리 만들기

<ul class="meta">
<li class="badge hard">기본 기능으로 어려움</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
남이 만든 대시보드를 넘겨받았습니다. 페이지가 12개, 시각화가 40개인데
**어떤 시각화가 어떤 데이터 테이블을 쓰는지** 알 수 없습니다.
데이터 테이블 하나를 교체해야 하는데 영향 범위를 모릅니다.

**기본 기능으로 어려운 이유**  
Spotfire UI에는 "이 데이터 테이블을 참조하는 시각화 목록"을 보여 주는 화면이 없습니다.
시각화를 하나씩 열어 속성 대화상자를 확인하는 수밖에 없습니다.

**스크립트 매개변수**
없음.

```python
# -*- coding: utf-8 -*-
# 문서 전체의 페이지/시각화/데이터 테이블 목록을 문서 속성에 HTML로 기록한다.
# 결과를 보려면 텍스트 영역에 문서 속성 "InventoryReport" 를 삽입하세요.

from Spotfire.Dxp.Application.Visuals import VisualContent

rows = []
totalVisuals = 0

for page in Document.Pages:
    for visual in page.Visuals:
        totalVisuals += 1

        # 데이터 테이블 이름 — 텍스트 영역 등은 데이터가 없으므로 예외 처리
        try:
            tableName = visual.As[VisualContent]().Data.DataTableReference.Name
        except:
            tableName = u"(없음)"

        # 데이터 제한 표현식이 걸려 있는지도 함께 본다
        try:
            where = visual.As[VisualContent]().Data.WhereClauseExpression or u""
        except:
            where = u""

        rows.append(u"<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            page.Title,
            visual.Title,
            visual.TypeId.Name,
            tableName,
            where,
        ))

html = u"""
<table border="1" cellpadding="4" cellspacing="0">
<tr><th>페이지</th><th>시각화</th><th>유형</th><th>데이터 테이블</th><th>데이터 제한</th></tr>
%s
</table>
<p>페이지 %d개 / 시각화 %d개</p>
""" % (u"".join(rows), Document.Pages.Count, totalVisuals)

Document.Properties["InventoryReport"] = html
```

**사용법**  

1. 문서 속성 `InventoryReport`(문자열)를 미리 만들어 둡니다 → [4.7 참조](06-api-map.html#67)
2. 텍스트 영역에 속성 컨트롤로 이 속성을 삽입하고, 표시 형식을 **HTML 그대로**로 둡니다
3. 버튼을 눌러 스크립트 실행

!!! note "검증 포인트"
    - `visual.TypeId.Name`은 `"Spotfire.BarChart"` 같은 내부 식별자를 반환합니다.
      한글 이름이 필요하면 매핑 딕셔너리를 직접 만드세요.
    - 문서 속성에 넣은 HTML이 텍스트로 보이면, 텍스트 영역의 속성 컨트롤 설정에서
      HTML 렌더링 옵션을 확인하세요.
    - 문서를 변경하지 않으므로 **안전하게 여러 번 실행**해도 됩니다.

---

## 예제 2. 모든 시각화에 데이터 제한 표현식 일괄 적용

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
드롭다운에서 "최근 12개월"을 고르면 대시보드의 **모든 차트**가 그 범위만 보여 줘야 합니다.

**기본 기능으로 어려운 이유**  
데이터 제한 표현식(`Limit data using expression`)은 **시각화마다 개별 설정**입니다.
시각화가 30개면 30번 같은 표현식을 붙여 넣어야 하고, 조건이 바뀌면 30번 다시 고쳐야 합니다.
필터로 해결하려 해도 필터는 데이터 테이블 전체에 걸리므로, 일부 차트만 전체 기간을
보여 주는 구성은 만들 수 없습니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `expr` | String | 문서 속성 `LimitExpression` |
| `targetTable` | DataTable | 적용 대상 데이터 테이블 |

```python
# -*- coding: utf-8 -*-
# 지정한 데이터 테이블을 참조하는 모든 시각화에 데이터 제한 표현식을 적용한다.
#
# 매개변수:
#   expr        (String)    적용할 표현식. 빈 문자열이면 제한 해제
#   targetTable (DataTable) 이 테이블을 쓰는 시각화만 대상으로 함

from Spotfire.Dxp.Application.Visuals import VisualContent

applied = 0
skipped = 0

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            # 대상 테이블을 쓰는 시각화만
            if vc.Data.DataTableReference == targetTable:
                vc.Data.WhereClauseExpression = expr
                applied += 1
            else:
                skipped += 1
        except:
            # 텍스트 영역 등 데이터가 없는 시각화
            skipped += 1

Document.Properties["ScriptLog"] = u"%d개 시각화에 적용, %d개 건너뜀" % (applied, skipped)
```

**사용법**  
문서 속성 `LimitExpression`에 표현식을 넣고 이 스크립트를 실행합니다.
드롭다운 속성 컨트롤에 다음처럼 값을 넣어 두면 선택만으로 전체 대시보드가 바뀝니다.

| 표시 이름 | 값 |
|-----------|-----|
| 전체 기간 | (빈 문자열) |
| 최근 12개월 | `[Date] > DateAdd("month", -12, Date(Today()))` |
| 올해만 | `Year([Date]) = Year(Today())` |
| 동부 지역만 | `[Region] = "East"` |

!!! note "검증 포인트"
    - 표현식은 **Spotfire 표현식 문법**입니다. Python 문법이 아닙니다.
      먼저 시각화 하나에 손으로 넣어 동작을 확인한 뒤 스크립트에 넣으세요.
    - 잘못된 표현식을 넣으면 해당 시각화가 오류 상태가 됩니다.
      `expr = ""` 로 다시 실행하면 원상 복구됩니다.
    - 문서 속성을 표현식 안에서 참조하려면 `${PropertyName}` 문법을 씁니다.
      예: `"[Region] = '${SelectedRegion}'"`

---

## 예제 3. 축 표현식 동시 전환 (측정지표 스위처)

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
</ul>

**문제 상황**  
같은 대시보드를 **매출 기준**으로도 보고 **수량 기준**으로도 보고 싶습니다.
차트가 8개인데, 드롭다운 하나로 8개의 Y축을 동시에 바꾸고 싶습니다.

**기본 기능으로 어려운 이유**  
축에 문서 속성을 직접 꽂는 방법(`Sum([${Measure}])`)이 있지만,
**집계 함수까지 바꾸거나**(Sum ↔ Avg), 시각화 유형마다 다른 축(교차 표의 `MeasureAxis` 등)을
함께 다루려면 표현식만으로는 한계가 있습니다. 축 표현식 자체를 바꾸는 편이 확실합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `measure` | String | 문서 속성 `SelectedMeasure` (예: `Revenue`) |
| `agg` | String | 문서 속성 `SelectedAgg` (예: `Sum`) |

```python
# -*- coding: utf-8 -*-
# 모든 페이지의 차트 Y축(교차 표는 측정 축)을 지정한 측정지표로 한 번에 바꾼다.
#
# 매개변수:
#   measure (String) 컬럼 이름   예: "Revenue"
#   agg     (String) 집계 함수   예: "Sum", "Avg", "Max"

from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

expression = "%s([%s])" % (agg, measure)

# Y축을 가진 유형
Y_AXIS_TYPES = [
    VisualTypeIdentifiers.BarChart,
    VisualTypeIdentifiers.LineChart,
    VisualTypeIdentifiers.ScatterPlot,
    VisualTypeIdentifiers.CombinationChart,
]

changed = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()

            if visual.TypeId in Y_AXIS_TYPES:
                vc.YAxis.Expression = expression
                changed.append(visual.Title)

            elif visual.TypeId == VisualTypeIdentifiers.CrossTable:
                vc.MeasureAxis.Expression = expression
                changed.append(visual.Title)

            elif visual.TypeId == VisualTypeIdentifiers.PieChart:
                vc.SectorSizeAxis.Expression = expression
                changed.append(visual.Title)

            elif visual.TypeId == VisualTypeIdentifiers.Treemap:
                vc.SizeAxis.Expression = expression
                changed.append(visual.Title)
        except:
            pass

Document.Properties["ScriptLog"] = u"%s 기준으로 %d개 차트를 전환했습니다." % (
    expression, len(changed))
```

!!! note "검증 포인트"
    - 시각화마다 **축 이름이 다릅니다.** 위 목록에 없는 유형(히트 맵, KPI 등)을 쓰고 있다면
      `dir(vc)`로 축 이름을 확인해 분기를 추가하세요 → [3.8 참조](05-dotnet-interop.html#58-api)
    - 특정 차트만 고정하고 싶다면 `visual.Title`이 특정 접두사로 시작할 때 건너뛰는
      조건을 넣으세요. 예: `if visual.Title.startswith(u"[고정]"): continue`
    - 축 표현식은 되돌리기가 되지 않을 수 있습니다. **원래 표현식을 예제 1로 먼저 기록**해 두세요.

---

## 예제 4. 범례·제목·서식 일괄 통일

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
</ul>

**문제 상황**  
여러 사람이 만든 페이지들의 서식이 제각각입니다. 배포 전에 **모든 시각화의 범례를 끄고,
제목 표시 여부를 통일**하고 싶습니다.

**기본 기능으로 어려운 이유**  
Spotfire에는 "모든 시각화에 서식 일괄 적용" 기능이 없습니다.
시각화 하나씩 속성 대화상자를 열어야 합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `showLegend` | String | 문서 속성 `ShowLegend` (`"True"` / `"False"`) |

```python
# -*- coding: utf-8 -*-
# 모든 페이지의 모든 시각화에 대해 범례 표시 여부를 통일한다.
#
# 매개변수:
#   showLegend (String) "True" 또는 "False"

from Spotfire.Dxp.Application.Visuals import VisualContent

visible = (str(showLegend).lower() == "true")

changed = 0
noLegend = 0

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            vc.Legend.Visible = visible
            changed += 1
        except:
            # 범례 개념이 없는 시각화 (텍스트 영역, 표 등)
            noLegend += 1

Document.Properties["ScriptLog"] = u"범례 %s: %d개 적용, %d개 해당 없음" % (
    u"표시" if visible else u"숨김", changed, noLegend)
```

### 변형: 제목도 함께 정리하기

```python
# -*- coding: utf-8 -*-
# 범례를 끄고, 제목 앞뒤 공백을 정리하고, 데이터 테이블 이름을 제목에 덧붙인다.

from Spotfire.Dxp.Application.Visuals import VisualContent

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            vc.Legend.Visible = False

            # 제목 정리
            title = (visual.Title or u"").strip()

            # 이미 접미사가 붙어 있으면 중복 방지
            tableName = vc.Data.DataTableReference.Name
            suffix = u" (%s)" % tableName
            if not title.endswith(suffix):
                visual.Title = title + suffix
        except:
            pass
```

### 변형: 산점도 마커 크기 일괄 조정

점이 너무 작아 안 보이거나 너무 커서 뭉칠 때, 모든 산점도를 한 번에 조정합니다.

```python
# -*- coding: utf-8 -*-
# 모든 산점도의 마커 크기를 한 단계 키운다.
# 매개변수 없이 실행하거나, delta 를 문서 속성으로 받아 +1 / -1 버튼을 만들 수 있다.

from Spotfire.Dxp.Application.Visuals import ScatterPlot, VisualTypeIdentifiers

DELTA = 1        # 음수면 작아진다

changed = 0
for page in Document.Pages:
    for visual in page.Visuals:
        if visual.TypeId != VisualTypeIdentifiers.ScatterPlot:
            continue
        try:
            scatter = visual.As[ScatterPlot]()
            scatter.MarkerSize = scatter.MarkerSize + DELTA
            changed += 1
        except:
            pass

Document.Properties["ScriptLog"] = u"산점도 %d개의 마커 크기를 조정했습니다." % changed
```

`MarkerSize`는 **산점도 고유 속성**이라 `VisualContent`가 아니라 `ScatterPlot`으로
캐스팅해야 합니다 → [5.2 참조](05-dotnet-interop.html#52-ast)

!!! note "검증 포인트"
    - `Legend.Visible`은 대부분의 차트에 있지만 표(`TablePlot`)·텍스트 영역에는 없습니다.
      `except`로 건너뛰는 구조가 필수입니다.
    - 범례 안의 개별 항목(색 범례만 끄기 등)은 `vc.Legend.Items`를 순회해 각 항목의
      `Visible`을 조정합니다. 항목 구성은 시각화 유형마다 다르므로 먼저
      `for item in vc.Legend.Items: print item.Title` 로 확인하세요.
    - 제목 변형 스크립트는 **여러 번 실행해도 안전하도록** 중복 접미사를 막았습니다.
      일괄 스크립트를 짤 때 항상 신경 쓸 부분입니다.

---

## 예제 5. 모든 시각화의 데이터 테이블 일괄 교체

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
<li class="badge hard">기본 기능으로 어려움</li>
</ul>

**문제 상황**  
개발용 데이터 테이블 `Sales_DEV`로 대시보드를 다 만들었습니다.
이제 운영 테이블 `Sales_PROD`로 **전부** 바꿔야 합니다.

**기본 기능으로 어려운 이유**  
시각화마다 데이터 테이블을 하나씩 바꿔야 하고, 바꾸는 순간 **축 설정이 초기화**되는 경우가
많습니다. 40개 시각화를 다시 설정하는 것은 현실적으로 불가능합니다.

**스크립트 매개변수**

| 이름 | 타입 | 값 |
|------|------|-----|
| `oldTable` | DataTable | 교체 전 테이블 |
| `newTable` | DataTable | 교체 후 테이블 |

```python
# -*- coding: utf-8 -*-
# 특정 데이터 테이블을 참조하는 모든 시각화를 다른 테이블로 교체한다.
# 축 표현식은 최대한 보존한다 (컬럼 이름이 같다는 전제).
#
# 매개변수:
#   oldTable (DataTable) 교체 전
#   newTable (DataTable) 교체 후

from Spotfire.Dxp.Application.Visuals import VisualContent

# 보존을 시도할 축 이름들
AXIS_NAMES = ["XAxis", "YAxis", "ColorAxis", "SizeAxis", "ShapeAxis",
              "MeasureAxis", "HorizontalAxis", "VerticalAxis", "SectorSizeAxis"]

switched = 0
report = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        try:
            if vc.Data.DataTableReference != oldTable:
                continue
        except:
            continue

        # 1) 현재 축 표현식을 기억
        saved = {}
        for axisName in AXIS_NAMES:
            try:
                saved[axisName] = getattr(vc, axisName).Expression
            except:
                pass

        # 2) 데이터 테이블 교체
        vc.Data.DataTableReference = newTable

        # 3) 축 표현식 복원 — 컬럼이 없으면 그 축만 실패하고 넘어간다
        restored, lost = [], []
        for axisName, expression in saved.items():
            try:
                getattr(vc, axisName).Expression = expression
                restored.append(axisName)
            except:
                lost.append(axisName)

        switched += 1
        if lost:
            report.append(u"%s / %s → 복원 실패: %s" % (
                page.Title, visual.Title, u", ".join(lost)))

msg = u"%d개 시각화를 '%s' 로 교체했습니다." % (switched, newTable.Name)
if report:
    msg += u"<br><b>확인 필요:</b><br>" + u"<br>".join(report)

Document.Properties["ScriptLog"] = msg
```

!!! danger "검증 포인트 — 되돌릴 수 없습니다"
    - **반드시 분석 파일 사본에서 먼저 실행하세요.** 축 복원에 실패하면 수동 복구가 필요합니다.
    - 두 테이블의 **컬럼 이름이 같아야** 축이 복원됩니다. 이름이 다르면 매핑 딕셔너리를
      만들어 표현식을 치환하는 단계를 추가하세요.

      ```python
      RENAME = {"Amount": "Revenue", "Qty": "Quantity"}
      for oldName, newName in RENAME.items():
          expression = expression.replace("[%s]" % oldName, "[%s]" % newName)
      ```
    - 실행 전에 **예제 1의 인벤토리를 뽑아 두면** 무엇이 바뀌었는지 대조할 수 있습니다.
    - 데이터 제한 표현식(`WhereClauseExpression`)도 컬럼을 참조하므로, 필요하면 축과 같은
      방식으로 저장·복원 대상에 추가하세요.

---

## 예제 6. 모든 차트의 줌·축 범위 초기화

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
사용자들이 차트를 확대(줌)해 놓고 그대로 두는 바람에, 다음 사람이 열면
엉뚱한 범위만 보입니다. "원래 보기로" 버튼이 필요합니다.

**기본 기능으로 어려운 이유**  
줌 슬라이더는 시각화마다 개별 상태이고, 한 번에 되돌리는 UI가 없습니다.
북마크로 대신할 수 있지만 북마크는 필터·마킹까지 함께 되돌려서 부작용이 큽니다.

**스크립트 매개변수**
없음.

```python
# -*- coding: utf-8 -*-
# 모든 페이지의 모든 차트에서 축 줌 범위를 기본값으로 되돌린다.

from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

AXIS_NAMES = ["XAxis", "YAxis"]

reset = 0

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        for axisName in AXIS_NAMES:
            try:
                getattr(vc, axisName).ZoomRange = AxisRange.DefaultRange
                reset += 1
            except:
                pass

Document.Properties["ScriptLog"] = u"%d개 축의 줌을 초기화했습니다." % reset
```

!!! note "검증 포인트"
    - `AxisRange`는 `Spotfire.Dxp.Application.Visuals`에 있습니다.
    - 줌 슬라이더가 비활성인 시각화에서는 예외가 나므로 축별로 `try`를 감쌌습니다.
    - 축 범위를 특정 값으로 고정하고 싶다면 `AxisRange(min, max)` 형태를 씁니다.
      단, 타입(숫자/날짜)이 축과 맞아야 합니다.
    - 이 스크립트는 **되돌리기가 필요 없는 안전한 작업**입니다. 사용자용 "보기 초기화"
      버튼으로 그대로 배포해도 됩니다. 예제 15와 묶어 쓰면 더 좋습니다.

---

## 예제 7. 여러 차트의 축 범위 동시 고정

<ul class="meta">
<li class="badge bulk">일괄 적용</li>
<li class="badge">자주 묻는 질문</li>
</ul>

**문제 상황**  
차트 8개를 나란히 놓고 비교하는데, 각 차트가 **자기 데이터에 맞춰 축 범위를 따로 잡습니다.**
그래서 눈으로 비교가 안 됩니다. 모든 차트의 Y축을 같은 범위로 맞추고 싶고,
그 범위를 입력 상자로 조절하고 싶습니다.

**기본 기능으로 어려운 이유**  
축 범위 고정은 시각화마다 개별 설정입니다. 8개를 손으로 맞추고, 데이터가 바뀔 때마다
또 8번 고쳐야 합니다. 문서 속성으로 범위를 조절하는 방법도 기본 기능에는 없습니다.

**스크립트 매개변수**  
없음 (문서 속성 `최소`, `최대`를 직접 읽습니다).

```python
# -*- coding: utf-8 -*-
# 지정한 페이지의 막대/선 차트 Y축 범위를 문서 속성 값으로 한 번에 고정한다.
#
# 사전 준비: 문서 속성 "최소", "최대" (실수 또는 정수)

from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

TARGET_PAGE = u"매출분석"        # 빈 문자열이면 모든 페이지

AxisMin = Document.Properties["최소"]
AxisMax = Document.Properties["최대"]

# TypeId를 문자열로 비교하는 방식 — 열거형 import 없이도 동작한다
TARGET_TYPES = [
    "TypeIdentifier:Spotfire.BarChart",
    "TypeIdentifier:Spotfire.LineChart",
    "TypeIdentifier:Spotfire.CombinationChart",
]

applied = 0

for page in Document.Pages:
    if TARGET_PAGE and page.Title != TARGET_PAGE:
        continue

    for visual in page.Visuals:
        if str(visual.TypeId) not in TARGET_TYPES:
            continue
        try:
            vc = visual.As[VisualContent]()
            vc.YAxis.Range = AxisRange(AxisMin, AxisMax)
            applied += 1
        except:
            pass

Document.Properties["ScriptLog"] = u"%d개 차트의 Y축을 %s ~ %s 로 고정했습니다." % (
    applied, AxisMin, AxisMax)
```

### 변형: 축 범위 고정 해제 (자동 범위로 되돌리기)

```python
# -*- coding: utf-8 -*-
from Spotfire.Dxp.Application.Visuals import VisualContent, AxisRange

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            vc.YAxis.Range = AxisRange.DefaultRange
        except:
            pass
```

!!! note "검증 포인트"
    - `str(visual.TypeId)`는 `"TypeIdentifier:Spotfire.BarChart"` 형태의 문자열을 반환합니다.
      `VisualTypeIdentifiers.BarChart` 열거형과 비교하는 방식([예제 3](08-examples-bulk.html))과
      결과는 같습니다. **문자열 비교는 import가 덜 필요하고, 열거형 비교는 오타에 안전합니다.**
      어느 쪽을 써도 됩니다.
    - `AxisRange(min, max)`에 넘기는 값의 **타입이 축과 맞아야** 합니다.
      문서 속성이 문자열 타입이면 축이 숫자일 때 실패합니다.
      이 경우 `AxisRange(float(AxisMin), float(AxisMax))`로 변환하세요.
    - `Range`(고정 범위)와 `ZoomRange`(줌 슬라이더 위치)는 **다른 속성**입니다.
      "사용자가 확대해 놓은 걸 되돌리고 싶다"면 `ZoomRange`([예제 6](08-examples-bulk.html)),
      "축 눈금 자체를 고정하고 싶다"면 `Range`입니다.
    - 되돌리기가 필요하면 위 변형 스크립트를 버튼으로 함께 배포하세요.

---

다음 장에서는 **데이터를 읽고 내보내는** 예제를 봅니다.
