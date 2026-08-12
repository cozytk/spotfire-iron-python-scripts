# 2. IronPython 2.7 문법

Spotfire의 스크립트 엔진은 **IronPython 2.7**이고, 문법은 **Python 2.7**입니다.
Python 3만 써 본 사람은 여기서 반드시 한 번 걸립니다. 이 장은 문법 전체를 훑되,
**Spotfire 스크립트에서 실제로 쓰이는 것 위주**로 정리했습니다.

## 2.1 Python 3와 다른 점 (먼저 읽을 것)

| 항목 | Python 2.7 (IronPython) | Python 3 |
|------|------------------------|----------|
| print | `print "hello"` (문) | `print("hello")` (함수) |
| 정수 나눗셈 | `1 / 2` → `0` | `1 / 2` → `0.5` |
| 문자열 | `str`(바이트) / `unicode` 분리 | 모두 `str`(유니코드) |
| 유니코드 리터럴 | `u"한글"` 필요 | 기본이 유니코드 |
| 예외 문법 | `except E, e:` 또는 `except E as e:` | `except E as e:` |
| 딕셔너리 순회 | `d.iteritems()` 사용 가능 | `d.items()` |
| range | `range()`는 리스트, `xrange()`는 반복자 | `range()`가 반복자 |
| 나머지 | `<>` 부등호 사용 가능 | 삭제됨 |

특히 **정수 나눗셈**은 조용히 잘못된 결과를 만들어서 위험합니다.

```python
# 함정: 둘 다 정수면 결과도 정수로 잘림
progress = 3 / 4          # 0  (0.75가 아니다!)

# 해결 1: 한쪽을 실수로
progress = 3.0 / 4        # 0.75

# 해결 2: float()으로 변환
count, total = 3, 4
progress = float(count) / total   # 0.75

# 해결 3: 스크립트 맨 위에서 Python 3 방식으로 바꾸기
from __future__ import division
progress = 3 / 4          # 0.75
```

!!! tip "`from __future__ import division`을 습관화하세요"
    계산이 들어가는 스크립트라면 첫 줄에 넣어 두는 편이 안전합니다.
    단, 이 줄은 **반드시 파일의 맨 처음**(주석 제외)에 와야 합니다.

## 2.2 변수와 기본 자료형

```python
name = "Sales"            # 문자열
count = 42                # 정수 (int)
ratio = 0.75              # 실수 (float)
flag = True               # 불리언 (True / False — 대문자 시작)
nothing = None            # 널 값 (.NET의 null에 대응)

# 여러 개 한 번에
x, y = 10, 20
x, y = y, x               # 스왑
```

타입 선언이 없습니다. 필요하면 확인하고 변환합니다.

```python
print type(count)          # <type 'int'>
print isinstance(count, int)   # True

s = str(42)                # "42"
n = int("42")              # 42
f = float("3.14")          # 3.14
```

!!! warning "Spotfire 값에는 빈 값(null)이 섞여 있습니다"
    데이터에서 읽은 값은 `None`일 수 있습니다. 계산 전에 반드시 확인하세요.

    ```python
    value = cursor.CurrentValue
    if value is not None:
        total = total + value
    ```

## 2.3 연산자

```python
# 산술
7 + 3, 7 - 3, 7 * 3, 7 / 3, 7 % 3, 7 ** 2, 7 // 3

# 비교 — 결과는 True / False
a == b, a != b, a < b, a >= b

# 논리 — and / or / not (&&, ||, ! 아님)
if count > 0 and name != "":
    pass

# 멤버십
if "Region" in [c.Name for c in table.Columns]:
    pass

# 동일성: 값 비교는 ==, 객체 동일성은 is
if value is None:      # None 비교는 항상 is 를 쓴다
    pass
```

## 2.4 문자열

```python
s1 = "큰따옴표"
s2 = '작은따옴표'
s3 = """여러 줄
문자열"""

# 이어붙이기와 서식
title = "매출: " + str(1200)
title = "매출: %d 원" % 1200
title = "%s / %s" % ("2024", "Q1")
title = "{0} / {1}".format("2024", "Q1")
```

### 한글을 쓸 때

IronPython 2.7에서 한글 문자열은 **`u` 접두사**를 붙이세요. 붙이지 않으면 인코딩 오류나
글자 깨짐이 발생할 수 있습니다.

```python
Document.Properties["Msg"] = u"처리가 완료되었습니다."
label = u"%s 개 시각화를 변경했습니다." % 12
```

### 자주 쓰는 문자열 메서드

```python
s = "  Sales Amount  "
s.strip()               # 앞뒤 공백 제거
s.replace(" ", "_")
s.lower(), s.upper()
s.split(",")            # 리스트로 분해
",".join(["a", "b"])    # 리스트를 문자열로
s.startswith("Sales")
"Sales" in s            # 포함 여부
```

### Spotfire 표현식을 만들 때

Spotfire 표현식에서 컬럼은 `[컬럼명]` 형태이므로 문자열 조립이 잦습니다.

```python
col = "Revenue"
expression = "Sum([%s])" % col            # "Sum([Revenue])"

cols = ["Region", "Year"]
axis = ", ".join("[%s]" % c for c in cols)  # "[Region], [Year]"
```

경로에 역슬래시를 쓸 때는 **raw 문자열** `r"..."` 을 쓰거나 슬래시를 쓰세요.

```python
path = r"C:\Users\me\Desktop\out.csv"   # 권장
path = "C:/Users/me/Desktop/out.csv"    # 이것도 동작
path = "C:\\Users\\me\\out.csv"         # 이스케이프도 가능하지만 번거로움
```

## 2.5 리스트, 튜플, 딕셔너리, 집합

```python
# 리스트 — 순서 있고 변경 가능
names = ["Region", "Year", "Revenue"]
names.append("Cost")
names.insert(0, "ID")
names.remove("Year")
first = names[0]
last = names[-1]
part = names[1:3]          # 슬라이싱
print len(names)

# 튜플 — 변경 불가
pair = ("Region", "String")
key, dtype = pair          # 언패킹

# 딕셔너리 — 키/값
axes = {"X": "[Region]", "Y": "Sum([Revenue])"}
axes["Color"] = "[Category]"
print axes["X"]
print axes.get("Size", "없음")      # 키가 없어도 안전
for k, v in axes.items():
    print k, v
if "Color" in axes:
    del axes["Color"]

# 집합 — 중복 제거
unique = set(["A", "B", "A"])      # set(['A', 'B'])
```

### 리스트 컴프리헨션

Spotfire 스크립트에서 매우 자주 씁니다. **.NET 컬렉션도 그대로 순회**할 수 있습니다.

```python
# 데이터 테이블의 컬럼 이름 전부
names = [c.Name for c in table.Columns]

# 조건을 붙여 걸러내기
numericCols = [c.Name for c in table.Columns if c.DataType.IsNumeric]

# 모든 페이지의 모든 시각화를 한 리스트로 (중첩)
allVisuals = [v for page in Document.Pages for v in page.Visuals]
```

## 2.6 제어문

```python
# if / elif / else — 콜론과 들여쓰기 필수
if count > 100:
    level = "high"
elif count > 10:
    level = "mid"
else:
    level = "low"

# 삼항 연산
level = "high" if count > 100 else "low"

# for
for page in Document.Pages:
    print page.Title

for i in range(5):          # 0,1,2,3,4
    print i

for i, name in enumerate(names):    # 인덱스와 값 동시에
    print i, name

# while
i = 0
while i < 10:
    i += 1
    if i == 5:
        continue            # 다음 반복으로
    if i == 8:
        break               # 반복 종료
```

!!! warning "순회 중에 컬렉션을 변경하지 마세요"
    시각화를 순회하면서 삭제하거나 추가하면 예외가 나거나 일부가 누락됩니다.
    **먼저 리스트로 복사한 뒤** 변경하세요.

    ```python
    # 위험
    for v in page.Visuals:
        page.Visuals.Remove(v)

    # 안전
    targets = [v for v in page.Visuals]     # 파이썬 리스트로 복사
    for v in targets:
        page.Visuals.Remove(v)
    ```

## 2.7 함수

```python
def make_expression(column, aggregation="Sum"):
    """축 표현식 문자열을 만든다."""
    return "%s([%s])" % (aggregation, column)

print make_expression("Revenue")            # Sum([Revenue])
print make_expression("Cost", "Avg")        # Avg([Cost])
print make_expression(aggregation="Max", column="Qty")   # 키워드 인자
```

여러 값을 반환할 수 있습니다(실제로는 튜플).

```python
def axis_of(visual):
    vc = visual.As[VisualContent]()
    return vc.XAxis.Expression, vc.YAxis.Expression

x, y = axis_of(someVisual)
```

!!! tip "스크립트는 매번 새로 실행됩니다"
    한 스크립트에서 정의한 함수·변수는 **다른 스크립트로 이어지지 않습니다.**
    스크립트 간에 값을 넘기려면 **문서 속성**(`Document.Properties[...]`)을 쓰세요.
    이것이 Spotfire 스크립팅의 사실상 유일한 전역 저장소입니다.

## 2.8 예외 처리

```python
try:
    table = Document.Data.Tables["Sales"]
    table.Refresh()
except Exception, e:            # Python 2 문법 (as 도 가능)
    Document.Properties["ScriptLog"] = u"새로고침 실패: " + str(e)
finally:
    Document.Properties["Busy"] = "False"
```

일괄 적용 스크립트에서는 **일부 실패가 전체를 멈추지 않도록** 감싸는 것이 중요합니다.

```python
changed, failed = 0, 0
for page in Document.Pages:
    for visual in page.Visuals:
        try:
            visual.As[VisualContent]().Legend.Visible = False
            changed += 1
        except:
            failed += 1        # 범례가 없는 시각화 유형은 그냥 건너뛴다

Document.Properties["ScriptLog"] = u"%d개 적용, %d개 건너뜀" % (changed, failed)
```

!!! warning "무조건 `except:` 로 삼키면 원인을 못 찾습니다"
    개발 중에는 `except Exception, e:` 로 받아서 메시지를 로그에 남기세요.
    위처럼 조용히 넘기는 건 "시각화 유형별로 없는 속성이 있다"는 걸 이미 아는 경우에만 쓰세요.

## 2.9 클래스 (참고)

스크립트 하나가 짧아서 클래스를 쓸 일은 드물지만, 문법은 알아 두면 좋습니다.

```python
class VisualInfo(object):
    def __init__(self, page, visual):
        self.page = page
        self.visual = visual

    def describe(self):
        return u"%s / %s" % (self.page.Title, self.visual.Title)

infos = [VisualInfo(p, v) for p in Document.Pages for v in p.Visuals]
for info in infos:
    print info.describe()
```

## 2.10 모듈 import

표준 라이브러리 일부는 쓸 수 있습니다.

```python
import re                 # 정규표현식
import math
import datetime
import json               # 버전에 따라 가능
```

!!! danger "`pandas`, `numpy`는 쓸 수 없습니다"
    IronPython은 C 확장 모듈을 로드하지 못합니다. `numpy`, `pandas`, `requests` 등
    CPython용 네이티브 라이브러리는 **IronPython 스크립트에서 사용 불가**입니다.
    이런 계산이 필요하면 **Python 데이터 함수(CPython)** 를 쓰고, IronPython은
    데이터 함수를 실행/제어하는 역할만 맡기세요.

    대신 .NET 클래스 라이브러리 전체를 쓸 수 있습니다 → 3장.

## 2.11 자주 하는 실수 정리

```python
# 1) print를 함수처럼 쓰기 — 동작은 하지만 인자가 2개면 튜플이 출력된다
print ("a", "b")        # ('a', 'b')  ← 의도와 다름
print "a", "b"          # a b        ← Python 2 방식

# 2) True/False 대소문자
flag = true             # NameError! → True

# 3) 들여쓰기에 탭과 공백 혼용 → unexpected indent

# 4) 컬럼명 대소문자 — Spotfire는 구분한다
table.Columns["region"]     # 실패
table.Columns["Region"]     # 성공

# 5) 문자열과 숫자 직접 연결
msg = "총 " + 12            # TypeError
msg = "총 " + str(12)       # OK

# 6) 정수 나눗셈 (2.1 참조)
```

---

문법의 절반은 끝났습니다. 다음 장에서 **.NET 쪽 절반**을 봅니다.
`As[VisualContent]()` 같은 낯선 대괄호 문법이 왜 필요한지 설명합니다.
