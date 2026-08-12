# 동작 확인용 임시 스크립트

교안 내용 중 **실제 Spotfire에서 확인이 필요한 항목**을 검증하기 위한 스크립트입니다.
교안 예제가 아니므로 `scripts/` 와 분리해 두었습니다.

## 지금 확인 중인 것

`print("hello")` 가 IronPython 2.7에서 잘 동작하는 이유와, 그 한계가 어디까지인지.

- Python 2에서 `print` 는 **문(statement)** 이고, `("hello")` 는 함수 호출 괄호가 아니라
  단순히 값을 감싼 괄호입니다. 그래서 인자가 1개일 때는 Python 3처럼 보이지만
  실제로는 Python 2 문법입니다.
- 문제는 인자가 2개 이상일 때입니다. `print("a", "b")` 는 **오류 없이**
  `('a', 'b')` 라는 튜플을 출력합니다. 조용히 틀리는 경우라 위험합니다.

## 실행 방법

**세 파일을 반드시 따로 실행하세요.** B와 C는 문법 오류를 유발할 수 있고,
문법 오류는 스크립트 전체를 실행 불가로 만듭니다.

| 파일 | 목적 | 기대 결과 |
|------|------|-----------|
| [`A_runtime_behavior.py`](A_runtime_behavior.py) | 엔진 버전, print 동작, 정수 나눗셈 | 정상 출력 |
| [`B_print_keyword_arg.py`](B_print_keyword_arg.py) | `print("a", end="")` | **SyntaxError 예상** |
| [`C_future_print_function.py`](C_future_print_function.py) | `from __future__ import print_function` | `a-b` 또는 오류 |

1. Spotfire 스크립트 편집 창을 엽니다 (액션 컨트롤 → 스크립트, 또는 도구 → 개발 도구)
2. 파일 하나를 붙여 넣고 **실행(Execute)**
3. 하단 출력 영역의 내용 또는 오류 메시지를 기록
4. 다음 파일로 반복

`print` 출력은 **스크립트 편집 창에서 실행했을 때만** 보입니다.
액션 컨트롤 버튼으로 실행하면 어디에도 표시되지 않습니다.

## 문서를 변경하나요?

**A는 출력만 하므로 완전히 안전합니다.** B와 C는 문법 오류로 실행 자체가 안 되거나
문자열 하나를 출력할 뿐이라 역시 문서를 변경하지 않습니다.

## 결과 반영

확인 결과에 따라 교안의 다음 부분을 고칠 예정입니다.

- **4.1 Python 3와 다른 점** — `print("hello")` 도 동작한다는 사실을 명시
- **7.5 AI 검증 체크리스트** — "괄호가 있으면 Python 3 신호" 를
  "인자가 2개 이상인 `print(a, b)` 가 있는지" 로 정정
- **C가 성공하면** — `from __future__ import print_function` 사용법 안내 추가

---

## 확인 결과 (2026-08-12)

**환경: IronPython 2.7.12 (2.7.12.1000), .NET Framework 4.8.9332.0 (64-bit)**

| 테스트 | 결과 | 결론 |
|--------|------|------|
| `print("hello")` | `hello` | 정상 동작. 괄호는 값을 감싼 것일 뿐 |
| `print("a", "b")` | `('a', 'b')` | **튜플 출력.** `print` 는 문(statement)이 맞음 |
| `3 / 4` | `0` | 정수 나눗셈 확인 |
| `__builtin__` 에 `print` | `True` | 함수 객체 자체는 존재 |
| `print("a", end="")` | `SyntaxError: unexpected token '='` | 예상대로 실패 |
| `from __future__ import print_function` + `sep="-"` | `a-b` | **지원됨** |

### 결정적 증거

`print("a", end="")` 의 오류 스택에 다음이 찍혔습니다.

```text
IronPython.Compiler.Parser.ParsePrintStmt()
```

파서가 이 줄을 **print 문**으로 처리하다가 `=` 에서 실패했다는 뜻입니다.
`print` 가 함수라면 `ParseCallExpression` 계열이 찍혔을 것입니다.

### 교안 반영 완료

- **4.1** — `print("hello")` 가 동작하는 이유와 `print(a, b)` 함정, `__future__` 사용법 추가
- **7.5** — AI 검증 체크리스트 1번을 "인자 2개 이상인 `print(a, b)`" 로 정정
- **13 FAQ** — "Python 3 문법을 쓰면 안 되나요?" 답변에 예외 두 가지 추가
- **버전 정보** — 확인 환경(2.7.12 / .NET 4.8) 명시

### 남은 확인 사항

테스트 A의 5)·6) 항목(`type(u"한글")`, `type("한글")`)이 **빈 값으로 보였습니다.**
출력이 `<type 'unicode'>` 처럼 꺾쇠로 시작해서, 어딘가에서 HTML 태그로 인식되어
사라진 것으로 보입니다. 다음 한 줄로 다시 확인할 수 있습니다.

```python
print "5) 유니코드:", str(type(u"한글")).replace("<", "[").replace(">", "]")
print "6) 일반문자:", str(type("한글")).replace("<", "[").replace(">", "]")
```

기대: `[type 'unicode']` 와 `[type 'str']`

`from __future__ import division` 도 `print_function` 과 같은 방식이라
동작할 가능성이 높지만, 아직 직접 확인하지는 않았습니다.
