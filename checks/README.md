# 동작 확인용 스크립트

교안 내용 중 **실제 Spotfire에서 확인이 필요한 항목**을 검증하는 스크립트입니다.
교안 예제가 아니므로 `scripts/` 와 분리해 두었습니다.

확인이 끝난 스크립트는 저장소에서 내리고, 결과만 아래 "확인 완료" 절에 남깁니다.

---

## 지금 확인할 것 (2차)

교안에서 **"검증 포인트"에 버전 의존적이라고 표시해 둔 API들**입니다.
확인되면 그 표시를 지우거나, 정확한 대안으로 바꿀 수 있습니다.

| 파일 | 확인 대상 | 문서 변경 | 관련 교안 |
|------|-----------|:---------:|-----------|
| [`01_environment.py`](01_environment.py) | `__future__ division`, 표준 라이브러리, .NET 접근, 문자열 타입 | 없음 | 4장 |
| [`02_visual_api.py`](02_visual_api.py) | 시각화 유형별로 어떤 속성이 실제 존재하는지, `AxisRange`, 유형 식별자 전체 목록 | 없음 | 6장, 예제 3·4·6·7 |
| [`03_services_and_types.py`](03_services_and_types.py) | `NotificationService`·`ProgressService` 메서드명, `DataWriterTypeIdentifiers`, `StdfDataSource` 존재, `TextDataReaderSettings` | 없음 | 예제 9·10·13·20 |
| [`04_data_and_filters.py`](04_data_and_filters.py) | 커서·`GetDistinctRows`·마킹·필터링 스킴, `scheme[table][column]` 인덱싱 | 없음 | 6장, 예제 11·12·18 |
| [`05_render_and_export.py`](05_render_and_export.py) | `VisualContent.Render`, `RenderSync` 존재, writer 생성 | 없음 | 예제 8·9 |
| [`06_page_and_layout.py`](06_page_and_layout.py) | `Page.Visible`, `AddNew` 반환형, `LayoutDefinition` 인자 형태 | **있음** | 예제 15·19·21 |

### 실행 순서

**01 → 05 는 전부 읽기 전용**이라 원본에서 실행해도 안전합니다.
결과를 이슈에 붙여 주시면 됩니다. 한 번에 다 하실 필요 없고, 편한 것부터 주셔도 됩니다.

**06 은 문서를 변경합니다.** 반드시 **분석 파일 사본**에서 실행하세요.

- `__API_TEST__` 라는 임시 페이지를 만들어 시험하고 마지막에 삭제합니다
- 중간에 오류가 나면 그 페이지가 남을 수 있습니다. 직접 지우시면 됩니다
- 06이 부담스러우면 건너뛰셔도 됩니다. 해당 API는 교안에 "확인 필요"로 남겨 두겠습니다

### 준비하면 결과가 풍부해지는 것

- **02, 05**: 막대·선·산점도·표·교차표·텍스트 영역이 **여러 종류 섞인 페이지**를 활성 페이지로 두고 실행
- **04**: 데이터 테이블과 필터가 있는 분석 파일

### 출력 규칙

- 각 줄이 `[OK]` / `[NO]` / `[??]` 로 시작합니다
- 꺾쇠(`<` `>`)는 대괄호(`[` `]`)로 바꿔서 출력합니다
  — 1차 때 `<type 'unicode'>` 가 HTML 태그로 인식되어 사라졌기 때문입니다
- 출력 전체를 그대로 복사해 붙여 주시면 됩니다

---

## 확인 완료

### 1차 — print 동작 (2026-08-12)

**환경: IronPython 2.7.12 (2.7.12.1000), .NET Framework 4.8.9332.0 (64-bit)**

| 테스트 | 결과 | 결론 |
|--------|------|------|
| `print("hello")` | `hello` | 정상 동작. 괄호는 값을 감싼 것일 뿐 |
| `print("a", "b")` | `('a', 'b')` | **튜플 출력.** `print` 는 문(statement)이 맞음 |
| `3 / 4` | `0` | 정수 나눗셈 확인 |
| `__builtin__` 에 `print` | `True` | 함수 객체 자체는 존재 |
| `print("a", end="")` | `SyntaxError: unexpected token '='` | 예상대로 실패 |
| `from __future__ import print_function` + `sep="-"` | `a-b` | **지원됨** |

**결정적 증거** — `print("a", end="")` 의 오류 스택:

```text
IronPython.Compiler.Parser.ParsePrintStmt()
```

파서가 이 줄을 **print 문**으로 처리하다 `=` 에서 실패했다는 뜻입니다.
`print` 가 함수였다면 호출식(call expression) 파싱 경로가 찍혔을 것입니다.

**교안 반영 완료**

- 4.1 — `print("hello")` 가 동작하는 이유, `print(a, b)` 함정, `__future__` 사용법 추가
- 7.5 — AI 검증 체크리스트 1번을 "인자 2개 이상인 `print(a, b)`" 로 정정
- 13 FAQ — Python 3 문법 답변에 예외 두 가지 추가
- 버전 정보 — 확인 환경 명시

미확인으로 남은 것(`type()` 출력, `__future__ division`)은 2차 `01_environment.py` 에 포함했습니다.
