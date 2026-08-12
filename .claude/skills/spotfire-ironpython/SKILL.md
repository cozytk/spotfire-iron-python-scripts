---
name: spotfire-ironpython
description: Write, debug, or review Spotfire IronPython 2.7 scripts — the scripting engine inside Spotfire Analyst that controls visualizations, axes, filters, markings, pages, and document properties. Use this skill whenever the user mentions Spotfire scripting, IronPython, a Spotfire action control or button, `Document.Properties`, `Spotfire.Dxp.*` APIs, marking/filtering schemes, or asks to automate anything in a Spotfire dashboard — including vague asks like "make a button that resets all the filters" or "apply this to every chart" when the context is Spotfire. Also use it to diagnose Spotfire script errors such as `'NoneType' object has no attribute`, `expected str, got int`, or `unexpected token '='`. Spotfire IronPython has many non-obvious traps (Python 2.7 syntax, UI-language-dependent marking names, APIs that silently return None, plausible-sounding APIs that do not exist) that this skill covers with field-verified rules.
---

# Spotfire IronPython 2.7

Spotfire 스크립트는 **"Python 2.7 문법으로 .NET API를 호출하는 것"** 입니다.
실패의 대부분은 문법이 아니라 **환경과 API의 함정**에서 옵니다.

이 스킬의 규칙 대부분은 Spotfire 14.x / IronPython 2.7.12 환경에서 **여덟 차례 실제
실행으로 확인한 것**입니다. 나머지(트랜잭션·클라이언트 판별·`ScriptManager`·`RenderAsync`)는
**Spotfire 공식 문서를 근거로 한 것**이며, `references/verified-apis.md` 에서 둘을 구분해
두었습니다. 실측한 것과 문서로만 아는 것을 사용자에게 구분해서 알려 주세요.

## 작업 순서

1. **대상과 범위를 먼저 확정한다** — 무엇을 / 어디에 / 어떻게 / 무엇이 실행시키는지
2. **비슷한 검증된 예제를 재료로 삼는다** — `references/example-catalog.md` 참고
3. **아래 제약을 지켜 작성한다**
4. **위험도를 판정해 사용자에게 알린다** — 되돌릴 수 없는 작업이면 사본을 권한다
5. **확신이 없는 API는 지어내지 말고 확인 방법을 제시한다**

## 언어 제약

- **Python 2.7 문법.** f-string, 타입 힌트, `async` 금지
- `print` 는 문(statement). `print("a")` 는 되지만 `print("a", b)` 는 튜플을 출력한다
- `3/4` 는 `0`. 실수가 필요하면 `float()` 또는 `from __future__ import division`
- `pandas`·`numpy` 사용 불가 (C 확장 모듈을 로드하지 못한다).
  계산이 필요하면 **Python 데이터 함수**가 맞는 도구라고 안내한다
- `str` 과 `unicode` 는 같은 타입. 한글에 `u"..."` 는 선택이지만 의도가 드러나므로 권장
- 들여쓰기는 공백 4칸. 탭을 섞으면 즉시 오류
- `Document` 와 `Application` 은 import 없이 사용. **그 외 모든 Spotfire 타입은 import 필수**

## Spotfire 함정 — 이것 때문에 코드가 깨진다

### 1. 이름을 하드코딩하지 않는다

마킹 이름은 **UI 언어에 따라 다르다.** 한국어 환경에서는 `"Marking"` 이 아니라 `"마킹"` 이다.
인터넷 예제가 한국어 Spotfire에서 깨지는 가장 흔한 이유다.

```python
marking = Document.ActiveMarkingSelectionReference       # 좋음
marking = Document.Data.Markings["Marking"]              # 나쁨
```

시각화·페이지 제목도 사용자가 언제든 바꾼다. 가능하면 **스크립트 매개변수로 객체를 직접 받는다.**

### 2. 컬렉션마다 인덱싱 방식이 다르다

```python
Document.Data.Tables[0]      # TypeError: expected str, got int
table.Columns[0]             # 가능
Document.Pages[0]            # 가능
Document.FilteringSchemes[0] # 가능
```

`Tables` 만 예외라 특히 헷갈린다. 확실하지 않으면 순회해서 꺼낸다.

### 3. 캐스팅이 성공해도 속성이 없을 수 있다

`As[VisualContent]()` 는 텍스트 영역에서도 통과한다. 그런데 그 객체엔 **속성이 하나도 없다.**
표(`Table`)에는 축이 없다. **캐스팅 성공으로 대상을 거를 수 없다.**

일괄 처리는 항상 이 골격을 쓴다.

```python
from Spotfire.Dxp.Application.Visuals import VisualContent

done, skipped, errors = 0, 0, []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            skipped += 1
            continue                      # 대상 아님

        try:
            vc.Legend.Visible = False     # 이 유형에 없는 속성일 수 있다
            done += 1
        except Exception, e:
            errors.append(u"%s: %s" % (visual.Title, str(e)))

Document.Properties["ScriptLog"] = u"완료 %d / 건너뜀 %d" % (done, skipped)
```

### 4. 시각화 유형마다 값 축 이름이 다르다

| 유형 | 값 축 |
|------|-------|
| 막대·선·산점도 | `YAxis` |
| 원형 차트 | `SectorSizeAxis` |
| 교차 표 | `MeasureAxis` |
| 트리맵 | `SizeAxis` |
| 히트 맵 | `CellValueAxis` |

"모든 차트의 Y축을 바꿔라"는 **유형별 분기 없이는 성립하지 않는다.**

### 5. API가 조용히 실패한다

```python
writer = Document.Data.CreateDataWriter(identifier)
# 예외 없음. 그런데 라이선스가 없으면 None
```

**반환값을 받는 호출은 반환값을 확인한다.** "예외가 안 났다"와 "동작했다"는 다르다.

### 6. 존재하지 않는 API를 지어내지 않는다

실제로 존재하지 않는데 그럴듯해서 자주 쓰이는 이름들이다.

| 틀린 것 | 실제 |
|---------|------|
| `VisualTypeIdentifiers.TreemapChart` | `Treemap` |
| `IndexSet.Add(i)` | `AddIndex(i)` 또는 `indexSet[i] = True` |
| `StdfDataSource` | 없음. `DataTableDataSource` 를 쓴다 |
| `Visual.RenderSync` | `RenderAsync` 만 존재 |
| `TileMode.Grid` | `Horizontally`/`Vertically`/`Evenly`/`Maximize` |
| `Bookmark.Name` | `DisplayName` |
| `CancellationToken.None` | 파이썬 문법 오류. `CancellationToken()` 을 쓴다 |

확신이 없으면 **코드에 쓰지 말고 확인 방법을 제시한다.**

```python
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
for name in dir(VisualTypeIdentifiers):
    if not name.startswith("_"):
        print name

print Document.Data.CreateDataWriter.__doc__     # 시그니처와 오버로드
```

### 7. 환경이 기능을 막는다

**Web Player(브라우저)에서 불가능한 것**: `MessageBox`·파일 대화상자, 로컬 파일 읽기/쓰기,
COM 연동. 반면 시각화·축·필터·마킹·문서 속성 조작은 전부 동작한다.

**라이선스로 막히는 것**: 데이터 내보내기. `plot.ExportDataEnabled`,
`table.IsRefreshable` 로 코드에서 판별할 수 있다.

사용자가 Web Player 배포를 언급하면 **로컬 파일 경로를 쓰는 코드를 제안하지 않는다.**

Analyst 전용 기능을 쓸 수밖에 없다면 **맨 앞에서 클라이언트를 판별해** 안내를 남긴다.
클라이언트 종류를 직접 알려 주는 API는 없고, `Application` 의 .NET 타입 이름으로 판별한다.

```python
if "RichAnalysisApplication" not in Application.GetType().ToString():
    Document.Properties["ScriptLog"] = u"이 기능은 Analyst에서만 동작합니다."
else:
    ...   # 파일을 쓰는 본 작업
```

### 8. 스크립트 전체가 하나의 트랜잭션이다

이것 하나로 설명되는 현상이 여럿이다.

- 스크립트 **중간에** `Document.Properties` 에 쓴 값은 화면에 나타나지 않는다.
  끝날 때 한꺼번에 반영되므로 **로그는 리스트에 모았다가 마지막에 한 번만 쓴다**
- 속성을 바꾼 뒤 그 **재계산 결과를 같은 스크립트에서 읽을 수 없다.**
  "바꾸고 → 읽고 → 판단" 흐름이 필요하면 스크립트를 둘로 나누고 문서 속성 트리거로 잇는다
- 이미지 렌더링처럼 스냅샷이 필요한 작업은
  `Attempt take snapshot on application thread in state 'Executing'` 로 실패한다.
  `ApplicationThread.InvokeAsynchronously(fn)` 로 우회하되, `fn` 은 바깥 변수를 참조하지 말고
  **필요한 것을 전부 기본 인자로 받아야** 한다
- `ProgressService` 로 진행 표시를 하려면 스크립트 대화상자의
  **"트랜잭션으로 감싸기" 체크를 꺼야** 한다. 대신 실행 취소를 잃는다

## 위험도 판정

작성한 코드가 어디에 해당하는지 **사용자에게 항상 알린다.**

| 코드에 있는 것 | 위험도 | 안내 |
|---------------|--------|------|
| 읽기만 | 없음 | 바로 실행 가능 |
| 속성 변경 (제목·범례·서식) | 낮음 | 사본 권장 |
| 축 표현식·시각화 유형 변경 | 중간 | 사본에서. 원래 값을 기록해 둘 것 |
| `Remove`, `ReplaceData`, `Tables.Add`, `Pages.AddNew` | **높음** | **반드시 사본에서** |
| 파일 쓰기 | 중간 | 경로 확인. Web Player 불가 |

Spotfire의 실행 취소는 스크립트 변경을 온전히 되돌리지 못한다.
특히 데이터 테이블 교체·삭제와 페이지·시각화 삭제는 **복구 불가**다.

## 결과를 사용자에게 보여주기

`print` 출력은 **스크립트 편집 창에서 실행할 때만** 보인다.
액션 컨트롤 버튼으로 실행하면 아무 데도 안 나온다.

```python
# 가장 무난함 — Web Player에서도 동작
Document.Properties["ScriptLog"] = u"12개 시각화를 변경했습니다."
```

`ScriptLog` 문서 속성이 없으면 **이 줄에서 실패한다.**
스크립트를 처음 건네줄 때 속성을 만들어야 한다고 함께 안내한다.

## 참고 자료

필요할 때만 읽는다.

| 파일 | 내용 |
|------|------|
| `references/api-map.md` | 객체 모델 지도와 자주 쓰는 코드 조각 |
| `references/verified-apis.md` | 실측으로 확인된 API 목록과 존재하지 않는 이름들 |
| `references/example-catalog.md` | 예제 23종 — 어떤 요청에 무엇을 재료로 쓸지 |

사용자가 **"왜 안 되는지 모르겠다"** 고 하면, 코드를 고치기 전에
교안 예제 23(실행 환경 진단 리포트)을 먼저 돌려 보게 한다. 읽기 전용이며
클라이언트 종류·마킹의 실제 이름·내보내기 가용성을 한 번에 알려 준다.

교안 전문: <https://cozytk.github.io/spotfire-iron-python-scripts/>
