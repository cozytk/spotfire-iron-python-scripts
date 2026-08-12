# 8. 생성형 AI로 스크립트 만들기

여기까지 오면 코드를 **읽을 수** 있습니다. 하지만 빈 화면에서 처음부터 **쓰는** 것은
여전히 어렵습니다. 그럴 필요도 없습니다.

이 장은 **생성형 AI(ChatGPT, Claude, Copilot 등)에게 원하는 Spotfire 스크립트를
받아내고, 검증하고, 고치는 절차**를 틀로 만든 것입니다.

!!! warning "AI는 Spotfire를 잘 모릅니다"
    Spotfire IronPython은 학습 데이터가 적은 분야입니다. AI에게 그냥 물어보면
    **그럴듯하지만 존재하지 않는 API**를 자신 있게 만들어 냅니다.

    그래서 "잘 물어보는 법"이 아니라 **"재료를 쥐여 주고, 결과를 검증하는 법"** 이
    핵심입니다. 아래 5단계 틀은 전부 이 문제를 해결하기 위한 것입니다.

    검증 단계에서 무엇을 봐야 하는지는 [7장](07-pitfalls.html)에 정리되어 있습니다.
    **7장을 읽지 않고 이 장만 보면 검증을 제대로 못 합니다.**

### 실제 사례 — 이 교안의 초안이 그랬습니다

이 교안의 예제 초안은 상당 부분 AI(저)가 작성했습니다.
그리고 실제 Spotfire에서 돌려 보니 **존재하지 않는 API를 네 개나 쓰고 있었습니다.**

| 초안이 쓴 것 | 실제 | 왜 그럴듯했나 |
|--------------|------|---------------|
| `VisualTypeIdentifiers.TreemapChart` | `Treemap` | `BarChart`·`LineChart` 와 대칭이라 자연스러움 |
| `IndexSet.Add(i)` | `AddIndex(i)` | 파이썬 `set` 을 아는 사람이면 당연히 쓸 이름 |
| `StdfDataSource(stream)` | 존재하지 않음 | `StdfDataWriter` 가 있으니 짝이 있을 것 같음 |
| `Visual.RenderSync` | `RenderAsync` 만 존재 | Async 가 있으면 Sync 도 있을 것 같음 |

**네 개 모두 "있을 법한 이름"입니다.** 이것이 AI가 Spotfire API에서 실패하는 전형적인
방식입니다. 문법이 틀린 게 아니라 **이름이 그럴듯하게 틀립니다.**

그래서 이 장의 ④ 검증 단계가 ③ 요청 단계보다 중요합니다.

---

## 8.1 전체 틀 — 5단계 루프

```text
① 목표 정의    무엇을, 어디에, 언제 → 한 문장으로
      ↓
② 재료 제공    API 지도 + 비슷한 예제 코드 + 제약조건을 프롬프트에 붙여넣기
      ↓
③ 요청        정해진 템플릿으로 요청
      ↓
④ 검증        체크리스트로 코드 읽기 → 사본에서 실행
      ↓
⑤ 수정 요청    오류 메시지를 그대로 되돌려주기 → ④로
```

**②가 이 틀의 핵심입니다.** 재료 없이 요청하면 환각(없는 API)이 나옵니다.
재료를 주면 정확도가 크게 올라갑니다.

---

## 8.2 ① 목표 정의 — 한 문장으로 만들기

요청하기 전에 다음 네 가지를 스스로 정합니다.

| 항목 | 질문 | 예 |
|------|------|-----|
| **무엇을** | 어떤 대상을 바꾸나 | 모든 막대 차트의 Y축 범위 |
| **어디에** | 범위는 어디까지인가 | "매출분석" 페이지에 있는 것만 |
| **어떻게** | 어떤 값으로 | 문서 속성 `최소`, `최대` 값으로 |
| **언제** | 무엇이 실행시키나 | 버튼 클릭 시 |

한 문장으로 합치면:

> "매출분석 페이지의 모든 막대 차트 Y축 범위를, 문서 속성 최소/최대 값으로,
> 버튼 클릭 시 한 번에 고정하고 싶다."

이 문장이 안 만들어지면 **AI에게 물어봐도 소용없습니다.** 요구사항이 아직 흐린 겁니다.

---

## 8.3 ② 재료 제공 — 무엇을 붙여 넣나

프롬프트에 아래 세 가지를 함께 넣습니다. 길어져도 괜찮습니다.

### 재료 A — 환경 제약 (항상 고정, 복사해서 쓰세요)

```text
[환경]
- Spotfire IronPython 2.7 스크립트 (Python 2.7 문법)
- print는 문(statement)이다. print("a", b) 처럼 인자를 2개 이상 넘기면 튜플이 출력된다
  (Python 3 스타일이 필요하면 첫 줄에 from __future__ import print_function)
- f-string, 타입 힌트, Python 3 전용 문법 사용 금지
- pandas, numpy 등 C 확장 라이브러리 사용 불가
- 한글 문자열에는 u"..." 접두사 사용
- 들여쓰기는 공백 4칸
- Document, Application 객체는 import 없이 사용 가능
- 그 외 모든 Spotfire 타입은 반드시 import 문을 포함할 것

[Spotfire 고유 제약]
- 마킹 이름을 하드코딩하지 말 것. Document.ActiveMarkingSelectionReference 를 쓸 것
  (한국어 UI에서 기본 마킹 이름은 "Marking" 이 아니라 "마킹" 이다)
- Document.Data.Tables 는 숫자 인덱스를 받지 않는다. 순회하거나 이름으로 접근할 것
- As[VisualContent]() 캐스팅이 성공해도 그 시각화에 해당 속성이 없을 수 있다.
  속성 단위로 try/except 를 감쌀 것
- 반환값이 있는 API 는 None 여부를 확인할 것
```

이 네 줄은 [7장](07-pitfalls.html)에서 실제로 부딪힌 것들입니다.
AI는 이걸 모르므로 알려 주지 않으면 그대로 밟습니다.

### 재료 B — 비슷한 예제 코드

**가장 효과가 큰 재료입니다.** 이 교안의 예제([9~12장](09-examples-visuals.html))나
이미 쓰고 있는 스크립트 중 **하고 싶은 일과 가장 비슷한 것**을 통째로 붙여 넣습니다.

```text
[참고: 동작이 검증된 유사 코드]
from Spotfire.Dxp.Application.Visuals import VisualContent
for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            vc.Legend.Visible = False
        except:
            pass

이 코드의 구조와 API 사용 방식을 따라서 작성해 줘.
```

AI는 **붙여 넣은 코드의 스타일과 API를 모방**합니다.
검증된 코드를 주면 검증된 API를 씁니다.

### 재료 C — API 지도

[6장](06-api-map.html)의 객체 모델 구조나 [14장 치트시트](14-cheatsheet.html)의
해당 부분을 붙여 넣습니다. 특히 **속성 이름이 정확해야 하는 작업**에서 효과가 큽니다.

---

## 8.4 ③ 요청 — 프롬프트 템플릿

아래를 복사해서 대괄호만 채우세요.

```text
Spotfire IronPython 2.7 스크립트를 작성해 줘.

[하고 싶은 일]
(8.2에서 만든 한 문장)

[대상 범위]
- 페이지: (전체 / 특정 페이지 이름)
- 시각화: (전체 / 막대 차트만 / 특정 제목만)
- 데이터 테이블: (이름)

[입력]
- 문서 속성: (속성 이름과 예상 값)
- 스크립트 매개변수: (이름과 타입)

[환경]
- Spotfire IronPython 2.7 (Python 2.7 문법)
- print는 문(statement). f-string·타입 힌트 등 Python 3 문법 금지
- pandas/numpy 사용 불가
- 한글 문자열에는 u"..." 사용
- 들여쓰기 공백 4칸
- Document, Application 외의 모든 Spotfire 타입은 import 문을 반드시 포함

[참고: 동작이 검증된 유사 코드]
(재료 B 붙여넣기)

[요구사항]
1. 시각화 유형마다 속성이 다르므로 try/except로 감싸서 실패해도 계속 진행할 것
2. 처리 결과(성공 개수/건너뛴 개수)를 Document.Properties["ScriptLog"]에 기록할 것
3. 여러 번 실행해도 결과가 같도록(멱등하게) 작성할 것
4. 각 줄에 한국어 주석을 달 것
5. 확실하지 않은 API는 추측하지 말고 "확인 필요"라고 표시할 것

[출력 형식]
- 완성된 스크립트 전체
- 필요한 스크립트 매개변수 목록 (이름/타입/설명)
- 실행 전 확인할 사항
```

!!! tip "요구사항 5번이 환각을 크게 줄입니다"
    "모르면 모른다고 해"라고 명시하면, AI가 없는 API를 지어내는 대신
    "이 부분은 버전 확인이 필요합니다"라고 표시하는 경우가 늘어납니다.

---

## 8.5 ④ 검증 — 실행 전 체크리스트

**AI가 준 코드를 바로 실행하지 마세요.** 아래를 순서대로 확인합니다.

### 0단계 — 처음 보는 API 이름은 `dir()` 로 확인 (30초)

**AI가 쓴 Spotfire 타입·속성 이름 중 처음 보는 것이 있으면, 코드를 읽기 전에 먼저 확인하세요.**

```python
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
for name in dir(VisualTypeIdentifiers):
    if not name.startswith("_"):
        print name
```

메서드라면 시그니처까지 볼 수 있습니다.

```python
print Document.Data.CreateDataWriter.__doc__
```

이 한 단계가 위 사례의 네 가지 오류를 **전부 잡아냅니다.**

### 눈으로 확인 (1분)

| # | 확인 | 왜 |
|---|------|-----|
| 1 | `print(a, b)` 처럼 인자가 **2개 이상**인가? | 오류 없이 튜플이 출력됨. 인자 1개면 괄호를 써도 정상 |
| 2 | `f"..."` 문자열이 있나? | Python 3 전용. 반드시 오류 |
| 3 | `import pandas` 등이 있나? | IronPython에서 불가 |
| 4 | 쓰는 타입마다 `import` 줄이 있나? | 가장 흔한 실패 원인 |
| 5 | 한글 문자열에 `u` 접두사가 있나? | 인코딩 오류 방지 |
| 6 | 들여쓰기가 공백으로 통일됐나? | 탭 섞이면 즉시 오류 |
| 7 | 반복문 안에 `try/except`가 있나? | 일괄 처리에 필수 |
| 8 | 삭제·교체(`Remove`, `ReplaceData`)가 있나? | **되돌리기 불가**. 특히 주의 |

### 위험도 판정

| 코드에 있는 것 | 위험도 | 조치 |
|---------------|--------|------|
| 읽기만 (`print`, 속성 읽기) | 낮음 | 바로 실행 가능 |
| 속성 변경 (제목, 범례, 축) | 중간 | 사본에서 먼저 |
| `Remove`, `ReplaceData`, `Tables.Add` | **높음** | **반드시 사본에서. 원본 저장 후** |
| 파일 쓰기 (`File.OpenWrite`) | 중간 | 경로 확인, Web Player 불가 |

### 실행으로 확인 (안전한 순서)

```python
# 1단계: 아무것도 바꾸지 않고, 대상만 확인한다
for page in Document.Pages:
    for visual in page.Visuals:
        print page.Title, visual.Title, visual.TypeId
```

먼저 **"무엇이 대상인지"만 출력**해 보세요. 예상과 다르면 조건이 잘못된 겁니다.
대상이 맞으면 그때 실제 변경 코드를 실행합니다.

!!! danger "반드시 분석 파일 사본에서 시험하세요"
    스크립트 변경은 되돌리기가 안 되는 경우가 많습니다.
    "잘 되겠지"로 원본에서 실행했다가 대시보드를 처음부터 다시 만드는 일이 실제로 생깁니다.

---

## 8.6 ⑤ 수정 요청 — AI가 자주 틀리는 것과 대처

### 오류가 났을 때: 메시지를 그대로 되돌려주기

가장 효과적인 수정 요청은 이 형태입니다.

```text
아래 오류가 났어. 수정해 줘.

[오류 메시지]
AttributeError: 'ScatterPlot' object has no attribute 'MarkerSize2'

[실행한 코드]
(전체 코드 붙여넣기)

[추가 정보]
dir()로 확인한 실제 속성 목록:
MarkerSize, MarkerShape, MarkerLayout, ...
```

**`dir()` 결과를 함께 주는 것이 결정적입니다.** AI는 실제 속성 이름을 모르지만,
목록을 주면 그중에서 맞는 것을 고릅니다.

```python
# 실제 속성 이름 확인용 — 이 결과를 AI에게 주세요
vc = viz.As[VisualContent]()
for m in dir(vc):
    if not m.startswith("_"):
        print m
```

### 자주 나오는 실패 유형

| 증상 | 원인 | 대처 프롬프트 |
|------|------|--------------|
| `NameError: name 'X' is not defined` | import 누락 | "X에 필요한 import 문을 추가해 줘" |
| `AttributeError: ... has no attribute` | 없는 API를 지어냄 | `dir()` 결과를 주고 "이 목록에서 골라 다시 써 줘" |
| `SyntaxError: unexpected token '='` | `print(..., end="")` 등 | 첫 줄에 `from __future__ import print_function` 추가 또는 Python 2 방식으로 |
| `SyntaxError` (f-string 등) | Python 3 전용 문법 | "Python 2.7 문법으로 전부 바꿔 줘" |
| `unexpected indent` | 탭/공백 혼용 | 편집기에서 직접 수정 (AI로는 잘 안 고쳐짐) |
| 실행은 되는데 아무 변화 없음 | 조건이 아무것도 매칭 안 함 | 8.5의 1단계 출력으로 대상 확인 |
| 일부 시각화에서만 실패 | 유형별 속성 차이 | "try/except로 감싸고 실패한 것을 목록으로 보고해 줘" |
| `pandas`를 쓰라고 제안함 | 데이터 함수와 혼동 | "IronPython은 pandas 불가. 순수 파이썬으로" ([1.4](01-what-you-can-do.html#14-python)) |

### AI가 특히 자주 지어내는 것

실제 경험상 다음은 **항상 의심**하세요. 자세한 배경은 [7.6 참조](07-pitfalls.html)

- **축 이름** — 시각화 유형마다 다릅니다. 산점도에 `MeasureAxis`는 없습니다
- **레이아웃 API** — 시각화 배치는 API가 까다롭습니다. [예제 21](12-examples-create.html) 참고
- **필터 조작** — 필터 유형별로 메서드가 다릅니다
- **이벤트 훅** — "마킹이 바뀌면 자동 실행"은 없습니다. AI가 있다고 우기면 틀린 겁니다
- **"대칭이니까 있겠지" 하는 이름** — `Async`가 있으니 `Sync`도, `Row`가 있으니 `Column`도,
  격자니까 `Grid`도 있을 것 같지만 전부 없습니다
  (`RenderSync` ✗ / `ColumnSelection` ✗ / `TileMode.Grid` ✗)

### AI가 모르는 것 — 요청에 미리 넣어야 하는 것

AI는 다음을 거의 알려 주지 않습니다. **먼저 말해 주지 않으면 그냥 빠집니다.**

| 빠지는 것 | 요청에 넣을 문장 |
|-----------|------------------|
| 트랜잭션 | "스크립트 중간에 문서 속성을 쓰지 말고, 로그는 리스트에 모았다가 마지막에 한 번만 써 줘" |
| 클라이언트 판별 | "Analyst 전용 기능이면 맨 앞에서 클라이언트를 판별하고 Web Player면 안내만 남겨 줘" |
| 반환값 `None` | "반환값이 있는 호출은 `None` 인지 확인하는 코드를 넣어 줘" |
| 멱등성 | "버튼을 두 번 눌러도 결과가 같게 만들어 줘" |

이 네 가지는 [`prompts/00-context.md`](https://github.com/cozytk/spotfire-iron-python-scripts/blob/main/prompts/00-context.md)
에 이미 들어 있습니다. 그 블록을 붙여 넣으면 따로 말할 필요가 없습니다.

---

## 8.7 실전 예시 — 나쁜 요청과 좋은 요청

### 나쁜 요청

```text
스팟파이어에서 차트 축 범위 바꾸는 파이썬 코드 줘
```

받게 되는 것: Python 3 문법, import 누락, 존재하지 않는 속성명, matplotlib 얘기.

### 좋은 요청

```text
Spotfire IronPython 2.7 스크립트를 작성해 줘.

[하고 싶은 일]
"매출분석" 페이지에 있는 모든 막대 차트와 선 차트의 Y축 범위를,
문서 속성 "최소"와 "최대"의 값으로 한 번에 고정하고 싶다. 버튼 클릭으로 실행한다.

[환경]
- Spotfire IronPython 2.7 (Python 2.7 문법). print는 문. f-string 금지
- pandas 불가. 한글 문자열은 u"..." 사용. 들여쓰기 공백 4칸
- Document, Application 외의 Spotfire 타입은 import 문을 반드시 포함

[참고: 동작이 검증된 유사 코드]
from Spotfire.Dxp.Application.Visuals import *
AxisMin = Document.Properties["최소"]
AxisMax = Document.Properties["최대"]
for page in Document.Pages:
    if page.Title == "페이지":
        for vis in page.Visuals:
            if str(vis.TypeId) == "TypeIdentifier:Spotfire.BarChart":
                vc = vis.As[VisualContent]()
                vc.YAxis.Range = AxisRange(AxisMin, AxisMax)

[요구사항]
1. 선 차트도 함께 처리할 것
2. try/except로 감싸 실패해도 계속 진행할 것
3. 처리 개수를 Document.Properties["ScriptLog"]에 기록할 것
4. 한국어 주석을 달 것
5. 확실하지 않은 API는 "확인 필요"로 표시할 것
```

검증된 코드 조각 하나를 붙였을 뿐인데 결과 품질이 크게 달라집니다.
**이 교안의 예제가 그 재료입니다.**

---

## 8.8 AI에게 시키기 좋은 일 / 나쁜 일

| 잘 되는 것 | 이유 |
|-----------|------|
| 기존 예제를 내 컬럼·테이블 이름에 맞게 고치기 | 구조가 이미 정해져 있음 |
| 반복문 조건 바꾸기 (특정 페이지만, 특정 유형만) | 순수 파이썬 로직 |
| 주석 달기, 코드 설명하기 | 언어 이해 자체는 잘함 |
| 오류 메시지 해석 | 일반적인 파이썬 오류는 잘 앎 |
| 여러 예제를 하나로 합치기 | 구조 조합은 잘함 |

| 잘 안 되는 것 | 대처 |
|--------------|------|
| 처음 보는 Spotfire API 이름 맞히기 | `dir()`로 확인해서 알려 주기 |
| 버전별 API 차이 | 직접 시험해 보기 |
| 레이아웃·필터 세부 조작 | 검증된 예제를 재료로 주기 |
| "이게 Spotfire 기본 기능으로 되나?"의 판단 | [1장](01-what-you-can-do.html) 참고 |

---

## 8.9 요약 — 실무 체크리스트

작업할 때 이 순서대로만 하면 됩니다.

```text
□ 1. 목표를 한 문장으로 쓴다 (무엇을/어디에/어떻게/언제)
□ 2. 이 교안에서 가장 비슷한 예제를 찾는다
□ 3. 그 예제로 될 것 같으면 → 컬럼·테이블 이름만 고쳐 쓴다 (AI 불필요)
□ 4. 안 되면 → 8.4 템플릿 + 그 예제를 재료로 붙여 AI에게 요청
□ 5. 8.5 체크리스트로 코드를 눈으로 검증
□ 6. 분석 파일 사본을 연다
□ 7. 대상만 출력하는 코드로 먼저 확인
□ 8. 실제 코드 실행
□ 9. 오류가 나면 메시지 + dir() 결과를 AI에게 되돌려준다
□ 10. 되면 원본에 적용하고, 스크립트를 저장소에 보관한다
```

3번을 잊지 마세요. **AI를 안 쓰고 끝나는 게 가장 빠릅니다.**

---

다음 장부터 예제입니다. 이 예제들이 곧 여러분이 AI에게 줄 **재료**입니다.
