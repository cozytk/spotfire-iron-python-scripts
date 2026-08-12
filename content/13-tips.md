# 13. 실무 팁과 함정

예제를 자기 분석 파일에 적용할 때 실제로 걸리는 것들입니다.

## 13.1 Analyst 전용 코드와 Web Player

배포 대상이 브라우저(Web Player)라면 **쓸 수 없는 것**이 있습니다.

| 기능 | Analyst | Web Player | 대안 |
|------|:-------:|:----------:|------|
| `MessageBox`, `FolderBrowserDialog` | O | **X** | 문서 속성, `NotificationService` |
| 로컬 경로 파일 읽기/쓰기 | O | **X** | 라이브러리 저장, 데이터 테이블로 표시 |
| `System.Windows.Forms` 전반 | O | **X** | — |
| Outlook 등 COM 연동 | O | **X** | 서버 측 자동화 |
| 시각화/축/필터/마킹/속성 제어 | O | O | — |
| `NotificationService` | O | O | — |

즉 **문서 구조를 다루는 스크립트는 전부 Web Player에서 동작**하고,
**파일 시스템과 윈도우 UI를 건드리는 것만** 안 됩니다.

```python
# 두 환경에서 모두 안전한 사용자 알림
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService
ns = Application.GetService[NotificationService]()
ns.AddInformationNotification(u"완료", u"12개 시각화를 변경했습니다.", u"")
```

### 두 환경에서 같은 파일을 쓴다면

Analyst 전용 기능이 들어간 스크립트는 **맨 앞에서 클라이언트를 판별**해
Web Player 사용자에게 안내를 남기세요. 그러지 않으면 알 수 없는 .NET 예외 대화상자가 뜹니다.

```python
if "RichAnalysisApplication" not in Application.GetType().ToString():
    Document.Properties["ScriptLog"] = u"이 기능은 Analyst에서만 동작합니다."
else:
    ...   # 파일을 쓰는 본 작업
```

`Application` 의 .NET 타입 이름이 판별 기준입니다 → [7.7 참조](07-pitfalls.html).
현재 환경 전체를 한 번에 보고 싶으면 [예제 23](12-examples-create.html)을 실행하세요.

## 13.2 성능

### 반복 안에서 비싼 호출을 하지 마세요

```python
# 느림 — 매 반복마다 테이블을 다시 찾는다
for i in range(1000):
    value = Document.Data.Tables["Sales"].Columns["Revenue"]

# 빠름 — 루프 밖으로 뺀다
table = Document.Data.Tables["Sales"]
column = table.Columns["Revenue"]
for i in range(1000):
    value = column
```

### 행 순회는 최소한으로

`GetRows`로 수백만 행을 도는 것은 느립니다. 가능하면 Spotfire에게 시키세요.

```python
# 느림 — 파이썬에서 전부 훑는다
count = 0
for row in table.GetRows(allRows, cursor):
    if cursor.CurrentValue == "East":
        count += 1

# 빠름 — 표현식으로 Spotfire가 처리
selection = table.Select("[Region] = 'East'")
count = selection.AsIndexSet().Count
```

### 조회는 set으로

```python
# 느림 — 리스트 검색은 O(n)
if value in bigList:
    ...

# 빠름 — 집합 검색은 O(1)
bigSet = set(bigList)
if value in bigSet:
    ...
```

### 긴 작업에는 진행 표시와 취소 버튼

수십 초 이상 걸리는 스크립트는 사용자 눈에 **Spotfire가 멈춘 것**으로 보입니다.
`ProgressService` 로 작업을 감싸면 몇 초 뒤 진행 대화상자가 자동으로 뜨고,
사용자가 취소할 수 있게 됩니다. Web Player에서도 동작합니다.

```python
from Spotfire.Dxp.Framework.ApplicationModel import ProgressService

ps = Application.GetService[ProgressService]()


def work():
    try:
        # ① 얼마나 걸릴지 모르는 단계
        ps.CurrentProgress.ExecuteSubtask(u"데이터 확인 중")
        ...

        # ② 횟수를 아는 단계 — 진행률 막대가 찬다
        pages = [p for p in Document.Pages]
        with ps.CurrentProgress.BeginSubtask(u"페이지 처리", len(pages), u"{0} / {1}"):
            for page in pages:
                ps.CurrentProgress.CheckCancel()      # 취소를 눌렀으면 여기서 예외
                ...
                ps.CurrentProgress.TryReportProgress()
    except:
        pass          # 사용자가 취소한 경우도 여기로 온다


ps.ExecuteWithProgress(u"일괄 처리", u"모든 페이지를 처리하고 있습니다.", work)
```

!!! danger "이걸 쓰려면 '트랜잭션으로 감싸기'를 꺼야 합니다"
    스크립트 편집 대화상자에서 **트랜잭션 래핑 체크를 해제**해야 진행 표시가 뜹니다
    → [7.4 참조](07-pitfalls.html)

    체크를 끄면 **실행 취소(Undo)가 되지 않습니다.**
    그래서 진행 표시는 "오래 걸리지만 되돌릴 일이 없는 작업"(내보내기, 새로고침,
    읽기 전용 조사)에 어울립니다. 되돌릴 수 있어야 하는 일괄 변경에는 쓰지 마세요.

    근거: [Progress bar and cancellation option (Spotfire Community)](https://community.spotfire.com/s/article/How-to-Add-Progress-Bar-and-Cancellation-Option-when-Executing-IronPython-Scripts-in-TIBCO-Spotfire)

## 13.3 되돌리기(Undo)를 믿지 마세요

!!! danger "스크립트 변경은 되돌아가지 않는 경우가 많습니다"
    특히 다음은 **복구가 어렵습니다.**

    - 데이터 테이블 교체·삭제 (`ReplaceData`, `Tables.Remove`)
    - 페이지·시각화 삭제
    - 축 표현식 일괄 변경
    - 시각화 유형 변경

    **반드시 지킬 것:**

    1. 위험한 스크립트는 **분석 파일 사본**에서 먼저 실행
    2. 실행 전에 **예제 18(시각화 인벤토리)이나 예제 19(표현식 감사)** 로 현재 상태를 기록
    3. 사용자에게 배포하는 버튼은 **읽기 전용이거나 되돌릴 수 있는 것**만

## 13.4 이름에 의존하지 않기

가장 흔한 고장 원인은 **이름이 바뀌는 것**입니다.

| 의존 대상 | 위험 | 대안 |
|-----------|------|------|
| 시각화 제목 | 사용자가 언제든 바꿈 | **스크립트 매개변수**로 전달 |
| 페이지 제목 | 자주 바뀜 | 인덱스 또는 매개변수 |
| 데이터 테이블 이름 | 재구성 시 바뀜 | 매개변수 (`DataTable` 타입) |
| 컬럼 이름 | 데이터 소스 변경 시 | 존재 확인 후 사용 |
| 마킹 이름 | **한국어 UI에서는 `"마킹"`** (실측 확인) | `ActiveMarkingSelectionReference` |

!!! danger "마킹 이름은 UI 언어에 따라 다릅니다"
    한국어 Spotfire에서 기본 마킹 이름은 `"Marking"` 이 아니라 **`"마킹"`** 입니다.
    두 번째부터는 `"마킹 (2)"`, `"마킹 (3)"` 이 됩니다.
    영어 UI 기준으로 쓴 스크립트가 한국어 환경에서 조용히 실패하는 대표적인 원인입니다.

```python
# 가장 좋은 방법: 이름을 쓰지 않는다
markedRows = Document.ActiveMarkingSelectionReference.GetSelection(table).AsIndexSet()

# 특정 마킹을 꼭 지목해야 한다면, 존재 확인 후 사용
markingNames = [m.Name for m in Document.Data.Markings]
print markingNames        # 예: ['마킹', '마킹 (2)', '마킹 (3)']
```

!!! tip "제목 대신 Id"
    "이 시각화만 제외" 같은 규칙이 필요할 때, 제목 문자열 대신 **`visual.Id`** 를 쓰세요.
    사용자가 제목을 바꿔도 `Id` 는 그대로입니다. 페이지도 `page.Id` 를 가집니다.

    ```python
    for page in Document.Pages:
        for visual in page.Visuals:
            print visual.Id, "|", visual.Title      # 한 번 뽑아서 스크립트에 박아 둔다
    ```

## 13.5 여러 번 실행해도 안전하게 (멱등성)

사용자는 버튼을 두 번 누릅니다. 스크립트는 **두 번 눌러도 같은 결과**여야 합니다.

```python
# 나쁨 — 누를 때마다 접미사가 붙는다
visual.Title = visual.Title + u" (수정됨)"

# 좋음 — 이미 있으면 붙이지 않는다
suffix = u" (수정됨)"
if not visual.Title.endswith(suffix):
    visual.Title = visual.Title + suffix
```

```python
# 나쁨 — 누를 때마다 테이블이 늘어난다
Document.Data.Tables.Add(name, dataSource)

# 좋음 — 있으면 교체
if Document.Data.Tables.Contains(name):
    Document.Data.Tables[name].ReplaceData(dataSource)
else:
    Document.Data.Tables.Add(name, dataSource)
```

## 13.6 일괄 처리 루프의 표준 형태

9~12장 예제가 전부 이 형태입니다. 새 스크립트를 짤 때 그대로 베끼세요.

```python
# -*- coding: utf-8 -*-
from Spotfire.Dxp.Application.Visuals import VisualContent

done, skipped, errors = 0, 0, []

for page in Document.Pages:
    for visual in page.Visuals:
        # 1) 껍데기 → 알맹이 캐스팅 (실패하면 대상 아님)
        try:
            vc = visual.As[VisualContent]()
        except:
            skipped += 1
            continue

        # 2) 대상인지 판정 (유형·테이블·제목 등)
        # if visual.TypeId != VisualTypeIdentifiers.BarChart:
        #     skipped += 1
        #     continue

        # 3) 실제 작업 — 개별 실패가 전체를 멈추지 않게 감싼다
        try:
            # ... 여기에 작업 ...
            done += 1
        except Exception, e:
            errors.append(u"%s / %s: %s" % (page.Title, visual.Title, str(e)))

# 4) 결과 보고
message = u"완료 %d개 / 건너뜀 %d개" % (done, skipped)
if errors:
    message += u"<br>오류:<br>" + u"<br>".join(errors)
Document.Properties["ScriptLog"] = message
```

## 13.7 자주 만나는 오류와 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| `unexpected indent` | 탭/공백 혼용 | 들여쓰기를 공백 4칸으로 통일 |
| `'NoneType' object has no attribute` | 대상을 못 찾음 | 이름 확인, 매개변수 설정 확인 |
| `Column '...' was not found` | 컬럼명 오타/대소문자 | `for c in table.Columns: print c.Name` |
| 특정 시각화에서만 실패 | 그 유형에 해당 속성이 없음 | `try/except`로 감싸고 `TypeId`로 분기 |
| 표현식이 오류 상태로 표시됨 | Spotfire 표현식 문법 오류 | UI에서 손으로 넣어 먼저 검증 |
| 아무 일도 안 일어남 | 매개변수가 연결 안 됨 | 스크립트 편집 창의 매개변수 목록 확인 |
| 한글이 깨짐 | `u""` 미사용 | 문자열에 `u` 접두사, 파일 상단에 인코딩 선언 |
| Web Player에서만 실패 | Analyst 전용 API | 13.1 표 확인 |
| 값이 이상하게 잘림 | 정수 나눗셈 | `from __future__ import division` |

## 13.8 보안과 신뢰

- 스크립트 **작성**에는 `Author Scripts` 라이선스가 필요합니다
- 라이브러리에 저장된 분석 파일의 스크립트는 **신뢰(trusted)** 표시가 되어야 경고 없이 실행됩니다
- 신뢰되지 않은 스크립트는 사용자에게 확인을 요구합니다
- **모르는 출처의 스크립트는 반드시 읽어 보고 실행하세요.** 스크립트는 파일 시스템 접근,
  데이터베이스 쓰기 등 강력한 작업을 할 수 있습니다

!!! warning "데이터베이스 접속 정보를 스크립트에 넣지 마세요"
    스크립트 안에 사용자 이름/비밀번호를 하드코딩하면 분석 파일을 받은 사람 누구나
    볼 수 있습니다. 자격 증명은 **정보 링크나 데이터 연결의 인증 설정**에 두세요.

## 13.9 스크립트 관리

분석 파일에 스크립트가 20개씩 들어가면 관리가 안 됩니다.

- 스크립트 이름에 **접두사로 분류**를 붙이세요: `[초기화] 대시보드 리셋`, `[내보내기] 이미지 일괄`
- 스크립트 첫 줄에 **목적과 매개변수를 주석**으로 남기세요 (이 교안 예제 형식)
- 같은 로직이 여러 스크립트에 복붙되어 있다면, **문서 속성으로 분기**해 하나로 합치세요
- 스크립트 원본을 **저장소에도 보관**하세요. 분석 파일 안에만 있으면 이력 추적이 안 됩니다

### 목록을 코드로 뽑기 (Spotfire 12.0+)

`Document.ScriptManager` 로 문서 안의 스크립트를 전부 열거할 수 있습니다.
버튼을 하나씩 열어 보지 않아도 됩니다.

```python
for script in Document.ScriptManager.GetScripts():
    print script.Name, "|", script.Language.Language, "|", len(script.ScriptCode.splitlines())
```

같은 이름의 스크립트가 여러 벌 남아 있는 것이 실무에서 가장 흔한 문제입니다.

```python
# 이름이 같은 스크립트 전부 가져와 내용이 같은지 비교
for script in Document.ScriptManager.GetAllScriptsWithName(u"대시보드 초기화"):
    print script.IsEquivalentTo(기준정의)
```

정리 리포트를 만들어 주는 완성본은 [예제 22](12-examples-create.html)에 있습니다.

!!! warning "지우기·바꾸기는 신중하게"
    액션 컨트롤에 연결된 스크립트를 `Remove` 하면 **그 버튼을 손으로 다시 설정**해야 합니다.
    `Replace` 도 매개변수 이름·타입이 달라지면 연결된 액션이 비활성화됩니다.
    컬렉션을 **순회하면서 지우지 마세요.** 지울 목록을 먼저 모으고 순회가 끝난 뒤에 지웁니다.

---

마지막 장은 **한 장짜리 치트시트와 FAQ**입니다.
