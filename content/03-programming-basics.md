# 3. 프로그래밍 기초 개념

**코드를 한 줄도 써 본 적 없는 분을 기준으로 쓴 장입니다.**
여기서는 문법을 외우지 않습니다. 대신 코드에 나오는 **말들이 무슨 뜻인지** 정리합니다.

이 어휘를 알아야 [8장](08-ai-workflow.html)에서 생성형 AI에게 제대로 요청할 수 있고,
AI가 준 코드를 읽고 검증할 수 있습니다.

!!! tip "이미 프로그래밍을 아신다면"
    이 장은 건너뛰고 [4장](04-python-syntax.html)으로 가세요.
    단 4.1 "Python 3와 다른 점"은 꼭 보고 가세요.

---

## 3.1 코드는 "지시서"다

프로그램은 **위에서 아래로 순서대로 실행되는 지시 목록**입니다.
요리 레시피와 같습니다.

```python
table = Document.Data.Tables["매출"]      # ① 매출 테이블을 꺼내서 table 이라 부르자
count = table.RowCount                    # ② 그 테이블의 행 개수를 세서 count 라 부르자
Document.Properties["행수"] = count        # ③ 그 값을 화면의 "행수" 칸에 써넣자
```

`#` 뒤는 **주석(comment)** 입니다. 사람이 읽으라고 쓴 메모이고, 컴퓨터는 무시합니다.
좋은 코드에는 주석이 많습니다. 주석만 읽어도 흐름이 보이면 잘 쓴 코드입니다.

---

## 3.2 변수 — 값에 이름 붙이기

**변수(variable)** 는 값에 붙인 이름표입니다. `=` 는 "같다"가 아니라 **"넣어라"** 입니다.

```python
count = 100          # count 라는 이름에 100을 넣는다
count = count + 1    # count에 들어있던 값(100)에 1을 더해 다시 넣는다 → 101
```

이름은 자유롭게 지을 수 있지만, 관례가 있습니다.

```python
table       # 소문자로 시작, 의미가 드러나게
rowCount    # 두 단어면 두 번째 단어 첫 글자를 대문자로 (카멜 표기법)
MAX_CHARTS  # 전부 대문자면 "바꾸지 않을 설정값"이라는 신호
```

!!! warning "이름은 대소문자를 구분합니다"
    `table`과 `Table`은 **다른 이름**입니다. Spotfire의 컬럼 이름·테이블 이름도 마찬가지입니다.
    `Region`과 `region`은 다릅니다. 오류의 절반은 여기서 납니다.

---

## 3.3 자료형 — 값의 종류

값에는 **종류(자료형, data type)** 가 있습니다. 종류가 다르면 할 수 있는 일이 다릅니다.

| 자료형 | 뜻 | 예 |
|--------|-----|-----|
| **문자열** (string) | 글자. 따옴표로 감쌈 | `"매출"`, `u"한글"` |
| **정수** (int) | 소수점 없는 수 | `100`, `-3` |
| **실수** (float) | 소수점 있는 수 | `3.14`, `0.75` |
| **불리언** (bool) | 참/거짓 둘 중 하나 | `True`, `False` |
| **None** | "값이 없음" | `None` |

숫자 `100`과 문자열 `"100"`은 **다릅니다.**

```python
100 + 1        # 101   (숫자 계산)
"100" + "1"    # "1001" (글자 이어붙이기)
"100" + 1      # 오류!  (종류가 달라 못 붙임)
```

이럴 때 **형 변환(type conversion)** 을 합니다.

```python
str(100)       # 100 → "100"   숫자를 글자로
int("100")     # "100" → 100   글자를 숫자로
```

### 여러 값을 담는 그릇

| 자료형 | 뜻 | 예 |
|--------|-----|-----|
| **리스트** (list) | 순서 있는 값 묶음 | `["동부", "서부", "남부"]` |
| **딕셔너리** (dict) | 이름표-값 짝의 묶음 | `{"동부": 100, "서부": 250}` |
| **집합** (set) | 중복 없는 묶음 | `set(["동부", "서부"])` |

```python
regions = ["동부", "서부", "남부"]
print regions[0]       # 동부   ← 번호는 0부터 센다!
print len(regions)     # 3      ← 개수

sales = {"동부": 100, "서부": 250}
print sales["동부"]     # 100    ← 이름표로 꺼낸다
```

!!! warning "번호는 0부터 셉니다"
    첫 번째가 `[0]`, 두 번째가 `[1]`입니다.
    `Document.Pages[0]`은 **첫 번째 페이지**입니다.

---

## 3.4 객체·속성·메서드 — Spotfire 코드의 핵심

이 절이 이 장에서 가장 중요합니다. Spotfire 코드의 90%가 이 구조입니다.

### 객체 (object)

**객체**는 "데이터 + 그 데이터로 할 수 있는 동작"을 하나로 묶은 덩어리입니다.
Spotfire의 페이지, 시각화, 데이터 테이블, 필터가 전부 객체입니다.

비유하자면 **자동차**가 객체입니다.

### 속성 (property) — 객체가 "가진 것"

자동차의 **색상, 속도, 연료량**처럼, 객체가 가진 값입니다.
**점(`.`)으로 접근**합니다.

```python
visual.Title              # 시각화가 "가진" 제목
table.RowCount            # 데이터 테이블이 "가진" 행 개수
page.Visible              # 페이지가 "가진" 표시 여부
```

속성은 **읽기도 하고 바꾸기도** 합니다.

```python
print visual.Title            # 읽기: 현재 제목이 뭐지?
visual.Title = u"매출 추이"     # 쓰기: 제목을 이걸로 바꿔라
```

### 메서드 (method) — 객체가 "하는 것"

자동차의 **출발한다, 멈춘다**처럼, 객체가 수행하는 동작입니다.
역시 점으로 접근하지만, **끝에 괄호 `()` 가 붙습니다.**

```python
table.Refresh()               # 테이블아, 새로고침해라
scheme.ResetAllFilters()      # 필터링 스킴아, 필터를 전부 초기화해라
page.Visuals.Remove(visual)   # 이 시각화를 제거해라 (괄호 안은 "무엇을")
```

괄호 안에 넣는 값을 **인자(argument)** 라고 합니다. "무엇을, 어떻게" 할지 알려 주는 재료입니다.

!!! tip "괄호가 있으면 동작, 없으면 값"
    이것만 기억하면 코드가 훨씬 잘 읽힙니다.

    - `table.RowCount` → 괄호 없음 → **값** (행 개수)
    - `table.Refresh()` → 괄호 있음 → **동작** (새로고침 실행)

### 점으로 계속 파고들기

객체 안에 객체가 들어 있습니다. 점을 이어서 안으로 들어갑니다.

```python
Document.Data.Tables["매출"].Columns["지역"].Name
```

이걸 왼쪽부터 읽으면 이렇습니다.

```text
Document              문서에서
  .Data               데이터 부분으로 가서
  .Tables["매출"]      "매출" 이라는 테이블을 찾고
  .Columns["지역"]     그 안의 "지역" 컬럼을 찾아서
  .Name               그 이름을 꺼낸다
```

**폴더를 열어 들어가는 것과 같습니다.** 어떤 폴더에 뭐가 있는지가
[6장 API 지도](06-api-map.html)입니다.

---

## 3.5 라이브러리·패키지·모듈·네임스페이스

코드 맨 위에 항상 나오는 `import` 줄의 정체입니다.

### 개념 정리

| 용어 | 뜻 | 비유 |
|------|-----|------|
| **모듈** (module) | 코드가 담긴 파일 하나 | 책 한 권 |
| **패키지** (package) | 모듈을 모아 둔 폴더 | 책장 한 칸 |
| **라이브러리** (library) | 남이 만들어 둔 코드 모음 전체 | 도서관 |
| **네임스페이스** (namespace) | 이름이 겹치지 않게 나눠 둔 구역 | 도서관의 분류 체계 |

### import — "이 도구를 꺼내 오겠다"

파이썬은 모든 도구를 처음부터 들고 있지 않습니다. **필요한 것만 꺼내 씁니다.**

```python
from Spotfire.Dxp.Application.Visuals import VisualContent
```

이 줄을 읽으면:

```text
from Spotfire.Dxp.Application.Visuals    ← 이 서랍(네임스페이스)에서
import VisualContent                     ← VisualContent 라는 도구를 꺼내 오겠다
```

꺼내 온 뒤에야 그 이름을 쓸 수 있습니다. **import를 빼먹으면 "그런 이름 없다"는 오류**가 납니다.

### Spotfire의 서랍 구조

Spotfire 도구는 전부 `Spotfire.Dxp.` 로 시작하는 서랍에 들어 있습니다.

| 서랍 | 들어 있는 것 |
|------|-------------|
| `Spotfire.Dxp.Application.Visuals` | 시각화 관련 (막대 차트, 산점도, 축…) |
| `Spotfire.Dxp.Application.Filters` | 필터 관련 |
| `Spotfire.Dxp.Application.Layout` | 레이아웃(배치) 관련 |
| `Spotfire.Dxp.Data` | 데이터 관련 (테이블, 컬럼, 행 선택…) |
| `Spotfire.Dxp.Data.Import` | 데이터 가져오기 |
| `Spotfire.Dxp.Data.Export` | 데이터 내보내기 |
| `System`, `System.IO` | .NET 기본 도구 (파일, 날짜…) |

!!! note "왜 Spotfire 코드에는 import가 많은가"
    Spotfire API는 도구가 수천 개라 전부 미리 꺼내 두면 느립니다.
    그래서 쓸 것만 명시합니다. AI에게 코드를 받았는데 `NameError`가 난다면,
    **import 줄이 빠진 경우가 대부분**입니다 ([7.6](08-ai-workflow.html#86-5-ai) 참조).

### 예외: import 없이 쓰는 것

`Document`와 `Application`은 Spotfire가 미리 준비해 둡니다. 바로 쓰면 됩니다.

```python
Document        # 현재 분석 문서 — import 불필요
Application     # Spotfire 애플리케이션 — import 불필요
```

---

## 3.6 함수 — 작업에 이름 붙이기

같은 작업을 여러 번 하면, 묶어서 이름을 붙입니다. 그게 **함수(function)** 입니다.

```python
def make_expression(column, aggregation):     # ① 이름과 재료를 정하고
    return aggregation + "([" + column + "])" # ② 결과를 돌려준다

print make_expression("매출", "Sum")            # Sum([매출])
print make_expression("수량", "Avg")            # Avg([수량])
```

- `def` = "define(정의한다)"
- 괄호 안 `column`, `aggregation` = **매개변수(parameter)**. 함수가 받는 재료
- `return` = 결과를 돌려주기

메서드는 **객체에 붙어 있는 함수**입니다. 본질은 같습니다.

---

## 3.7 조건과 반복 — 코드가 판단하고 되풀이하게

### 조건 (if)

```python
if count > 100:                # 만약 count가 100보다 크면
    level = "높음"              #   ← 들여쓴 줄만 실행된다
else:                          # 아니면
    level = "낮음"
```

### 반복 (for)

**일괄 적용 스크립트의 심장**입니다. 묶음의 값을 하나씩 꺼내 같은 일을 반복합니다.

```python
for page in Document.Pages:        # 모든 페이지를 하나씩 꺼내서 page 라 부르고
    print page.Title               #   그 페이지의 제목을 출력한다
```

중첩하면 "모든 페이지의 모든 시각화"가 됩니다.

```python
for page in Document.Pages:            # 페이지마다
    for visual in page.Visuals:        #   그 안의 시각화마다
        visual.Title = u"통일된 제목"    #     제목을 바꾼다
```

이 6줄이 **"마우스로 40번 할 일을 한 번에"** 를 만들어 냅니다.

### 들여쓰기가 문법이다

다른 언어의 중괄호 `{ }` 역할을 **파이썬에서는 들여쓰기(공백)** 가 합니다.

```python
for page in Document.Pages:
    print page.Title          # 들여씀 → 반복 안에 포함. 페이지마다 실행
print "끝"                     # 안 들여씀 → 반복 밖. 딱 한 번 실행
```

!!! danger "들여쓰기는 공백 4칸으로 통일하세요"
    탭과 공백을 섞으면 `unexpected indent` 오류가 납니다.
    웹이나 문서에서 코드를 복사해 붙일 때 특히 자주 발생합니다.
    AI가 준 코드도 붙여 넣은 뒤 들여쓰기를 한 번 확인하세요.

---

## 3.8 오류 다루기

### 오류는 정상입니다

코드를 실행하면 오류가 납니다. **오류 메시지는 혼내는 게 아니라 힌트입니다.**

```text
AttributeError: 'NoneType' object has no attribute 'Title'
```

이건 "`Title`을 꺼내려는데, 그 대상이 `None`(없음)이다" 라는 뜻입니다.
→ 찾으려던 시각화가 없다는 얘기입니다.

### try / except — 실패해도 계속 가기

일괄 처리에서는 **일부가 실패해도 나머지는 계속**되어야 합니다.

```python
for page in Document.Pages:
    for visual in page.Visuals:
        try:                                  # 시도해 보고
            visual.As[VisualContent]().Legend.Visible = False
        except:                               # 실패하면
            pass                              #   그냥 넘어간다
```

범례가 없는 시각화(표, 텍스트 영역)에서는 실패하는데, 그때 멈추지 않고 계속 갑니다.

!!! tip "이게 Spotfire 스크립트에 try가 많은 이유입니다"
    시각화 유형마다 가진 속성이 달라서, "전부 다 해봐라, 안 되는 건 넘어가라"는 방식이
    가장 실용적입니다. AI가 준 코드에 `try`가 없다면 넣어 달라고 요청하세요.

---

## 3.9 이 코드를 읽어 보세요

여기까지 읽었으면 아래 코드가 해석됩니다. 한 줄씩 짚어 보세요.

```python
from Spotfire.Dxp.Application.Visuals import VisualContent   # ① 도구 꺼내오기

count = 0                                                    # ② 셈 시작

for page in Document.Pages:                                  # ③ 페이지마다
    for visual in page.Visuals:                              # ④   시각화마다
        try:                                                 # ⑤     시도:
            vc = visual.As[VisualContent]()                  # ⑥       알맹이 꺼내서
            vc.Legend.Visible = False                        # ⑦       범례 끄고
            count = count + 1                                # ⑧       하나 셌다
        except:                                              # ⑨     실패하면
            pass                                             # ⑩       넘어간다

Document.Properties["결과"] = u"%d개 처리 완료" % count          # ⑪ 결과를 화면에
```

| 줄 | 개념 |
|----|------|
| ① | import — 도구 꺼내기 (3.5) |
| ② | 변수 — 값에 이름 (3.2) |
| ③④ | 반복 — 전부 순회 (3.7) |
| ⑥ | 메서드 호출 — 괄호 있음 (3.4) |
| ⑦ | 속성 쓰기 — 괄호 없음 (3.4) |
| ⑤⑨⑩ | 예외 처리 (3.8) |
| ⑪ | 문서 속성으로 결과 전달 |

`As[VisualContent]()` 의 대괄호만 아직 낯설 텐데, [5장](05-dotnet-interop.html)에서 설명합니다.
지금은 **"시각화 껍데기에서 알맹이를 꺼내는 동작"** 정도로 알아 두면 충분합니다.

---

## 3.10 이 장의 어휘 정리

AI에게 요청할 때 이 단어들을 쓰면 훨씬 정확한 코드를 받습니다.

| 용어 | 한 줄 정의 |
|------|-----------|
| 변수 | 값에 붙인 이름 |
| 자료형 | 값의 종류 (문자열/숫자/참거짓/목록…) |
| 객체 | 데이터와 동작이 묶인 덩어리 |
| 속성 | 객체가 가진 값. `visual.Title` (괄호 없음) |
| 메서드 | 객체가 하는 동작. `table.Refresh()` (괄호 있음) |
| 인자 | 메서드 괄호 안에 넣는 재료 |
| 모듈/패키지 | 코드 파일 / 그 묶음 |
| 라이브러리 | 남이 만들어 둔 코드 모음 |
| 네임스페이스 | 이름 충돌을 막는 구역. `Spotfire.Dxp.Data` 같은 것 |
| import | 도구를 꺼내 오는 선언 |
| 함수 | 이름 붙인 작업 묶음 |
| 매개변수 | 함수가 받는 재료 |
| 반복문 | 묶음을 하나씩 처리 |
| 예외 처리 | 실패해도 계속 가게 하는 장치 |

---

다음 장은 파이썬 문법입니다. 여기서 배운 개념이 실제로 어떻게 쓰이는지 봅니다.
