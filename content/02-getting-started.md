# 2. 스크립트 실행 환경

문법으로 들어가기 전에, **스크립트를 어디에 넣고 어떻게 실행하는지**부터 정리합니다.
이 장을 건너뛰면 4장 이후 코드를 어디에 붙여 넣어야 할지 알 수 없습니다.

## 2.1 IronPython이란

IronPython은 **.NET 위에서 도는 Python 구현체**입니다. Spotfire에는 IronPython 2.7이 내장되어 있고,
스크립트는 Spotfire의 .NET 자동화 API(`Spotfire.Dxp.*`)를 직접 호출합니다.

여기서 나오는 두 가지 성질이 이 교안 전체를 관통합니다.

- **문법은 Python 2.7이다.** `print`는 문(statement)이고, `1/2`는 `0`입니다.
- **다루는 객체는 .NET 객체다.** 파이썬 리스트가 아니라 .NET 컬렉션이고, 제네릭 메서드를
  `As[VisualContent]()` 같은 대괄호 문법으로 호출합니다.

즉 **"Python 2.7 문법으로 .NET API를 호출한다"** 가 전부입니다. 4장에서 앞의 절반을, 5장에서
뒤의 절반을 다룹니다.

!!! note "CPython(데이터 함수)과는 다릅니다"
    Spotfire에는 IronPython 말고도 **Python 데이터 함수**(CPython 3.x, `pandas` 사용 가능)가 있습니다.
    둘은 완전히 다른 물건입니다.

    - **IronPython 스크립트**: 문서·시각화·필터·마킹 같은 **UI와 문서 구조**를 조작. `pandas` 사용 불가.
    - **Python 데이터 함수**: 데이터 테이블을 입력받아 **계산 결과 테이블**을 반환. UI 조작 불가.

    이 교안은 전자만 다룹니다.

## 2.2 스크립트를 넣는 위치

### 액션 컨트롤 (가장 흔한 방법)

텍스트 영역(Text Area)에 버튼/링크를 만들어 클릭 시 실행합니다.

1. 텍스트 영역을 **편집 모드**로 전환 (연필 아이콘)
2. 툴바에서 **액션 컨트롤 삽입** (`Insert Action Control`)
3. 컨트롤 유형을 **버튼** 또는 **링크**로 선택
4. 왼쪽 목록에서 **스크립트(Script)** 선택 → **새로 만들기(New)**
5. 스크립트 본문을 붙여 넣고 이름 지정 → **실행(Execute)** 으로 시험

이 방식은 **Web Player(브라우저)에서도 동작**하므로 배포용으로 가장 무난합니다.

### 문서 속성 변경 시 자동 실행

`도구 > 문서 속성 > 속성` 에서 속성을 만들고, **스크립트** 탭에서 해당 속성이 바뀔 때 실행할
스크립트를 등록합니다. 드롭다운/슬라이더 값 변경에 반응하는 대시보드를 만들 때 씁니다.

### 그래픽 표·KPI 차트의 항목 클릭

**차트 안의 항목을 클릭했을 때** 스크립트를 실행할 수도 있습니다.
그래픽 표(Graphical Table)나 KPI 차트에서만 되는데, "클릭한 그 값"을 스크립트가
받을 수 있어서 드릴다운 대시보드를 만들 때 유용합니다.

1. 그래픽 표 속성 → **축(Axes)** → 컬럼 선택 → **액션(Actions)**
2. **클릭 시 액션 수행** 체크 → **설정(Settings…)**
3. 새 Spotfire 스크립트 추가

이 자리에서만 쓸 수 있는 **`Context`** 객체가 주어집니다 (2.3 참조).

### 기타 실행 지점

| 위치 | 특징 |
|------|------|
| 문서를 열 때 자동 실행 | `파일 > 문서 속성 > 스크립트`. 초기화 로직에 사용 |
| 마킹/필터 변경 시 | 문서 속성을 경유해 간접 트리거(직접 이벤트 훅은 없음) |
| 도구 > 개발 도구 > 스크립트 | 즉석 실행/시험용. 문서에 저장되지 않음 |
| 텍스트 영역의 JavaScript | JavaScript API로 액션 컨트롤 버튼을 대신 눌러 간접 실행 |

### "트랜잭션으로 감싸기" 체크박스

스크립트 편집 대화상자에는 스크립트를 **트랜잭션으로 감쌀지** 정하는 체크박스가 있습니다.
기본값은 켜짐이고, 그 상태에서는 **스크립트의 모든 변경이 끝날 때 한꺼번에 적용**됩니다.
실행 취소(Undo)가 되는 대신, 중간 진행 상황을 화면에 못 보여 줍니다.

이 하나로 설명되는 현상이 여러 개라 [7.4에 따로 정리](07-pitfalls.html)해 두었습니다.
**진행 표시줄(`ProgressService`)을 쓰려면 이 체크를 꺼야 합니다.**

!!! warning "라이선스가 필요합니다"
    스크립트를 **작성**하려면 `Author Scripts`(스크립트 작성) 라이선스 기능이 필요합니다.
    관리자가 사용자 그룹에 이 권한을 주지 않았다면 스크립트 편집 UI 자체가 보이지 않습니다.
    **실행**만 하는 사용자는 이 라이선스가 필요 없습니다.

    또한 라이브러리에 저장된 분석 파일의 스크립트는 **신뢰(trusted)** 상태여야 경고 없이
    실행됩니다. 신뢰되지 않은 스크립트는 실행 전에 사용자에게 확인을 요구합니다.

## 2.3 미리 정의된 객체

스크립트 안에서는 `import` 없이 바로 쓸 수 있는 객체가 있습니다.

| 객체 | 타입 | 의미 | 어디서 |
|------|------|------|--------|
| `Document` | `Spotfire.Dxp.Application.Document` | 현재 분석 문서. 페이지·데이터·속성의 최상위 진입점 | 어디서나 |
| `Application` | `AnalysisApplication` | 애플리케이션 수준. 서비스 조회, 문서 열기/저장 | 어디서나 |
| `Context` | `MiniatureVisualizationActionContext` | **클릭된 항목**의 값과 시각화 | 그래픽 표·KPI 차트의 클릭 액션에서만 |

`Application.Document`와 `Document`는 같은 객체를 가리킵니다. 짧은 쪽을 쓰면 됩니다.

```python
# 이 둘은 동일하다
print Document.ActivePageReference.Title
print Application.Document.ActivePageReference.Title
```

### Context — 클릭한 항목 받기

그래픽 표·KPI 차트의 **클릭 시 액션**으로 등록한 스크립트에서만 쓸 수 있습니다.

```python
val = Context.Value                    # 클릭한 셀의 값
key = Context.HierarchyPathValues[0]   # 같은 행의 기준 값 (행 축의 값)
vis = Context.Visualization            # 클릭된 미니어처 시각화 객체
```

!!! warning "Context는 편집 창의 '실행' 버튼으로 시험할 수 없습니다"
    `Context` 는 **사용자가 실제로 항목을 클릭할 때** 채워집니다.
    스크립트 편집 창에서 실행하면 존재하지 않아 오류가 납니다.
    개발 중에는 값을 문서 속성에 써 두고 텍스트 영역에서 확인하세요.

    ```python
    Document.Properties["ScriptLog"] = u"클릭한 값: %s" % Context.Value
    ```

    근거: [How to use Miniature Visualization Action Scripts (Spotfire Community)](https://community.spotfire.com/s/article/How-to-use-Miniature-Visualization-Action-Scripts-using-IronPython-in-TIBCO-Spotfire)

## 2.4 스크립트 매개변수

스크립트 편집 창 아래쪽에서 **매개변수(Parameters)** 를 정의하면, 문서의 객체를 스크립트 안의
변수로 넘길 수 있습니다. 이 교안 예제 대부분이 매개변수를 씁니다.

매개변수 추가 시 지정하는 것:

- **Name**: 스크립트 안에서 쓸 변수명 (예: `viz`)
- **Type**: 넘길 값의 종류 (`Visualization`, `DataTable`, `Column`, `String`, `Integer` …)
- **Value**: 실제로 연결할 대상. 문서 속성을 연결하면 **실행 시점의 속성 값**이 들어옵니다.

```python
# 매개변수: viz (Visualization) = 대상 시각화
# 매개변수: newTitle (String) = 문서 속성 "ChartTitle"

viz.Title = newTitle
```

### 왜 매개변수를 쓰는가

시각화를 이름으로 찾는 코드는 **제목을 바꾸는 순간 깨집니다.**

```python
# 나쁜 예: 제목 문자열에 의존 → 사용자가 제목을 바꾸면 실패
for v in Document.ActivePageReference.Visuals:
    if v.Title == "매출 추이":
        v.Title = "Revenue Trend"
```

매개변수로 시각화 자체를 넘기면 제목과 무관하게 항상 올바른 대상을 가리킵니다.
**하드코딩된 이름 대신 매개변수를 쓰는 것이 기본기입니다.**

!!! tip "예외: 일괄 적용 스크립트"
    8장처럼 "모든 시각화에 적용" 하는 스크립트는 애초에 특정 대상을 지목하지 않으므로
    매개변수 없이 `Document.Pages`를 순회합니다. 이 경우엔 이름 의존 문제가 없습니다.

## 2.5 출력 확인과 디버깅

### print의 출력 위치

`print`의 출력은 **스크립트 편집 창에서 실행(Execute)했을 때만** 하단 출력 영역에 보입니다.
액션 컨트롤 버튼으로 실행하면 **아무 데도 보이지 않습니다.** 개발 중에만 쓰세요.

!!! tip "버튼으로 실행할 때도 print를 보고 싶다면"
    Analyst에서 **도구 > 지원 진단 및 로깅(Support Diagnostics and Logging)** 의
    로그 수준을 `TRACE` 로 올리면 `print` 출력이 Analyst 디버그 로그에 기록됩니다.
    개발 장비에서 원인을 좁힐 때만 쓰세요. 로그가 매우 커집니다.

### 사용자에게 보여주는 3가지 방법

```python
# 1) 문서 속성에 써서 텍스트 영역에 표시 — Web Player에서도 동작. 가장 무난함
Document.Properties["ScriptLog"] = "처리 완료: 12개 시각화"
```

```python
# 2) 알림 서비스 — Analyst 우측 하단 알림. Web Player에서도 동작
from Spotfire.Dxp.Framework.ApplicationModel import NotificationService
ns = Application.GetService[NotificationService]()
ns.AddInformationNotification("내보내기 완료", "12개 이미지를 저장했습니다.", "")
```

```python
# 3) 윈도우 메시지 박스 — Analyst 전용. Web Player에서는 실패한다
import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import MessageBox
MessageBox.Show("완료")
```

!!! warning "문서 속성은 스크립트가 끝나야 갱신됩니다"
    위 1번 방법으로 **중간 진행 상황**을 여러 번 쓰더라도, 화면에는 **마지막 값 하나만**
    보입니다. 스크립트 전체가 하나의 트랜잭션으로 묶여 있기 때문입니다
    → [7.4 참조](07-pitfalls.html)

    그래서 `Document.Properties["ScriptLog"] = ...` 는 **끝난 뒤의 요약**을 남기는 용도로만
    쓰고, 단계별 추적이 필요하면 메시지를 리스트에 모았다가 마지막에 한 번에 쓰세요.

    ```python
    log = []
    log.append(u"1단계 완료")
    log.append(u"2단계 완료")
    Document.Properties["ScriptLog"] = u" / ".join(log)
    ```

!!! danger "MessageBox와 파일 대화상자는 Web Player에서 동작하지 않습니다"
    `System.Windows.Forms`에 의존하는 코드(`MessageBox`, `FolderBrowserDialog`,
    `OpenFileDialog`)와 로컬 경로 파일 쓰기는 **Analyst 데스크톱 클라이언트 전용**입니다.
    브라우저에서 여는 분석 파일에 넣으면 서버에서 실행되거나 오류가 납니다.
    배포 대상이 Web Player라면 문서 속성이나 `NotificationService`를 쓰세요.

### 오류 메시지 읽기

스크립트가 실패하면 대화상자에 .NET 예외가 그대로 나옵니다. 자주 보는 것들:

| 메시지 | 원인 |
|--------|------|
| `'NoneType' object has no attribute ...` | 찾으려던 객체가 없음. 이름 오타이거나 매개변수 미설정 |
| `Object reference not set to an instance of an object` | 위와 같은 상황의 .NET 버전 |
| `... is not callable` / `expected X, got Y` | .NET 타입 불일치. 5장 참조 |
| `Column '...' was not found` | 컬럼명 오타 또는 대소문자 불일치(**대소문자를 구분합니다**) |
| `unexpected indent` | 탭과 공백을 섞음. 2.6 참조 |

### 방어적으로 짜기

```python
# 존재 확인 후 접근하는 습관
tableName = "Sales"
if Document.Data.Tables.Contains(tableName):
    table = Document.Data.Tables[tableName]
else:
    Document.Properties["ScriptLog"] = u"데이터 테이블 '%s' 을(를) 찾을 수 없습니다." % tableName
```

## 2.6 반드시 지켜야 할 편집 습관

!!! danger "탭과 공백을 섞지 마세요"
    Spotfire 스크립트 편집기는 일반 코드 편집기가 아닙니다. 웹이나 다른 문서에서 코드를
    복사해 붙이면 **탭과 공백이 섞여서** `unexpected indent` 오류가 납니다.

    **들여쓰기는 공백 4칸으로 통일**하고, 붙여 넣은 코드는 들여쓰기를 한 번 정리하고 쓰세요.
    이 교안의 모든 코드는 공백 4칸을 씁니다.

그 밖에:

- **한글 주석/문자열을 쓸 때는 유니코드 리터럴** `u"..."` 을 쓰세요 (2.4 참조)
- 스크립트가 길어지면 **문서 속성에 로그를 남기며** 단계별로 확인하세요
- 실행 취소가 안 되는 작업이 있으므로 **작업 전 파일을 저장**하세요

---

다음 장은 프로그래밍 기초 개념입니다. 코딩 경험이 있으면 [4장](04-python-syntax.html)으로
바로 넘어가되, **4.1 "Python 3와 다른 점"** 만큼은 반드시 보고 가세요.
