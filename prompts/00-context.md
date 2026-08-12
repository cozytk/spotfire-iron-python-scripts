# Spotfire IronPython 컨텍스트 (AI에게 붙여넣기용)

생성형 AI에게 Spotfire 스크립트를 요청할 때, **요청 앞에 이 블록을 통째로 붙여 넣으세요.**
아래 내용은 Spotfire 14.x / IronPython 2.7.12 환경에서 실제로 확인한 제약입니다.

이 블록 없이 요청하면 AI는 Python 3 문법을 쓰거나, 존재하지 않는 API를 지어냅니다.

---

```text
너는 Spotfire IronPython 2.7 스크립트를 작성한다. 아래 제약을 반드시 지켜라.

[언어]
- IronPython 2.7 (Python 2.7 문법). f-string, 타입 힌트, async 등 Python 3 전용 문법 금지
- print 는 문(statement)이다. print("a") 는 동작하지만 print("a", b) 는 튜플을 출력하므로 쓰지 말 것
  Python 3 스타일이 필요하면 첫 줄에 from __future__ import print_function
- 정수 나눗셈: 3/4 는 0 이다. 실수가 필요하면 float() 또는 from __future__ import division
- pandas, numpy 등 C 확장 라이브러리 사용 불가 (IronPython은 로드하지 못한다)
- str 과 unicode 는 같은 타입이다. 한글 문자열의 u"..." 접두사는 선택 사항이지만 붙이는 것을 권장
- 들여쓰기는 공백 4칸. 탭 금지

[import]
- Document, Application 은 import 없이 사용 가능
- 그 외 모든 Spotfire 타입은 import 문을 반드시 포함할 것
  예: from Spotfire.Dxp.Application.Visuals import VisualContent, VisualTypeIdentifiers

[Spotfire 고유 함정 — 실측으로 확인된 것]
1. 이름을 하드코딩하지 마라
   - 마킹 이름은 UI 언어에 따라 다르다. 한국어 환경에서는 "Marking" 이 아니라 "마킹" 이다
   - Document.ActiveMarkingSelectionReference / ActiveFilteringSelectionReference 를 쓸 것
   - 시각화·페이지 제목은 사용자가 언제든 바꾼다. 스크립트 매개변수로 객체를 직접 받는 것이 최선
2. 컬렉션마다 인덱싱 방식이 다르다
   - Document.Data.Tables[0] 은 실패한다 (expected str, got int). 이름으로 접근하거나 순회할 것
   - table.Columns[0], Document.Pages[0], Document.FilteringSchemes[0] 은 숫자 인덱스 가능
3. As[VisualContent]() 캐스팅이 성공해도 그 시각화에 속성이 없을 수 있다
   - 텍스트 영역(HtmlTextArea)은 캐스팅은 되지만 속성이 하나도 없다
   - 표(Table)에는 XAxis/YAxis 가 없다
   - 따라서 속성 단위로 try/except 를 감쌀 것. 캐스팅 성공 여부로 대상을 거를 수 없다
4. 시각화 유형마다 값 축 이름이 다르다
   - 막대/선/산점도: YAxis, 원형: SectorSizeAxis, 교차표: MeasureAxis, 트리맵: SizeAxis
5. 반환값이 있는 API 는 None 여부를 확인할 것
   - Document.Data.CreateDataWriter(...) 는 라이선스가 없으면 예외 없이 None 을 반환한다
6. 존재하지 않는 API 를 지어내지 마라
   - 확실하지 않으면 코드에 쓰지 말고 "확인 필요"라고 표시할 것
   - 실제로 존재하지 않는 예: TreemapChart(→Treemap), IndexSet.Add(→AddIndex),
     StdfDataSource, Visual.RenderSync(→RenderAsync 만 존재)
7. 되돌리기가 안 되는 작업이 있다
   - 데이터 테이블 교체·삭제, 페이지·시각화 삭제는 복구 불가

[코드 작성 규칙]
- 여러 시각화를 순회하는 일괄 처리는 다음 골격을 따를 것
    for page in Document.Pages:
        for visual in page.Visuals:
            try:
                vc = visual.As[VisualContent]()
            except:
                continue                  # 대상 아님
            try:
                ...실제 작업...
            except:
                pass                      # 이 유형에 없는 속성
- 처리 결과(성공/건너뜀 개수)를 Document.Properties["ScriptLog"] 에 기록할 것
- 여러 번 실행해도 결과가 같도록(멱등하게) 작성할 것
- 각 줄에 한국어 주석을 달 것

[출력 형식]
1. 완성된 스크립트 전체
2. 필요한 스크립트 매개변수 목록 (이름 / 타입 / 설명)
3. 위험도 판정 — 읽기 전용 / 낮음 / 중간 / 높음(되돌리기 불가)
4. 실행 전 확인할 사항
5. 확신이 없는 API 가 있으면 명시할 것
```

---

## 왜 이 블록이 필요한가

이 교안의 예제 초안은 AI가 작성했고, 실제로 돌려 보니 **존재하지 않는 API를 네 개** 쓰고 있었습니다.

| 초안이 쓴 것 | 실제 | 왜 그럴듯했나 |
|--------------|------|---------------|
| `VisualTypeIdentifiers.TreemapChart` | `Treemap` | `BarChart`·`LineChart`와 대칭 |
| `IndexSet.Add(i)` | `AddIndex(i)` | 파이썬 `set`을 알면 당연한 이름 |
| `StdfDataSource(stream)` | 존재하지 않음 | `StdfDataWriter`가 있으니 짝이 있을 듯 |
| `Visual.RenderSync` | `RenderAsync`만 존재 | Async가 있으면 Sync도 있을 듯 |

**네 개 모두 "있을 법한 이름"입니다.** AI가 Spotfire에서 실패하는 방식은
문법 오류가 아니라 **그럴듯하게 틀린 이름**입니다.

위 컨텍스트의 6번 항목이 이걸 막습니다. 그래도 완벽하지는 않으므로,
받은 코드는 [`03-verify-checklist.md`](03-verify-checklist.md)로 검증하세요.
