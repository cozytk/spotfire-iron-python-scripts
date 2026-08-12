# 받은 코드 검증 체크리스트

**AI가 준 코드를 바로 실행하지 마세요.** 순서대로 확인하면 대부분의 사고를 막습니다.

## 0단계 — 처음 보는 API 이름 확인 (30초)

가장 먼저 할 일입니다. 이 한 단계가 "그럴듯하게 틀린 이름"을 전부 잡아냅니다.

```python
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
for name in dir(VisualTypeIdentifiers):
    if not name.startswith("_"):
        print name
```

## 1단계 — 눈으로 확인 (1분)

| # | 확인 | 왜 |
|---|------|-----|
| 1 | `print(a, b)` 처럼 인자가 2개 이상인가 | 오류 없이 튜플이 출력됨 |
| 2 | `f"..."` 문자열이 있나 | Python 3 전용. 반드시 오류 |
| 3 | `import pandas` 등이 있나 | IronPython에서 불가 |
| 4 | 쓰는 타입마다 `import` 줄이 있나 | 가장 흔한 실패 원인 |
| 5 | 마킹 이름을 하드코딩했나 | 한국어 UI에서 깨짐 |
| 6 | `Document.Data.Tables[0]` 이 있나 | 숫자 인덱스 불가 |
| 7 | 반복문 안에 `try/except` 가 있나 | 일괄 처리에 필수 |
| 8 | 반환값을 확인하지 않고 바로 쓰나 | `None` 이 올 수 있음 |
| 9 | 들여쓰기가 공백으로 통일됐나 | 탭 섞이면 즉시 오류 |
| 10 | `Remove`·`ReplaceData`·`Tables.Add` 가 있나 | **되돌리기 불가** |

## 2단계 — 위험도 판정

| 코드에 있는 것 | 위험도 | 조치 |
|---------------|--------|------|
| 읽기만 (`print`, 속성 읽기) | 없음 | 바로 실행 가능 |
| 속성 변경 (제목, 범례, 축 서식) | 낮음 | 사본 권장 |
| 축 표현식·시각화 유형 변경 | 중간 | **사본에서.** 원래 값을 기록해 둘 것 |
| `Remove`, `ReplaceData`, `Tables.Add`, `Pages.AddNew` | **높음** | **반드시 사본에서. 원본 저장 후** |
| 파일 쓰기 (`StreamWriter`, `FileStream`) | 중간 | 경로 확인. Web Player 불가 |

## 3단계 — 대상만 출력해 보기

**아무것도 바꾸지 않고** 무엇이 대상인지부터 확인합니다.

```python
for page in Document.Pages:
    for visual in page.Visuals:
        print page.Title, "|", visual.Title, "|", visual.TypeId
```

예상과 다르면 조건이 잘못된 것입니다. 대상이 맞으면 그때 실제 코드를 실행합니다.

## 4단계 — 사본에서 실행

Spotfire의 실행 취소는 스크립트 변경을 온전히 되돌리지 못합니다.
"잘 되겠지"로 원본에서 실행했다가 대시보드를 처음부터 다시 만드는 일이 실제로 생깁니다.

## 참고 — 두 가지 착각

검증하다 보면 빠지기 쉬운 함정입니다.

- **예외가 안 났다 ≠ 동작한다** — `CreateDataWriter` 는 예외 없이 `None` 을 반환합니다.
  반환값을 받는 호출은 반환값을 확인하세요.
- **시그니처가 맞다 ≠ 동작한다** — `TablePlot.ExportData(...)` 는 시그니처가 정확한데도
  writer 쪽에서 거부합니다. 호출까지 해 봐야 검증입니다.
