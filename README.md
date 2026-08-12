# Spotfire IronPython 2.7 교안

Spotfire의 IronPython 2.7 스크립팅 한국어 교안과, 바로 실행할 수 있는 예제 스크립트 27종입니다.

**프로그래밍을 해 본 적 없어도** 따라올 수 있도록 개념부터 시작하고,
**생성형 AI로 원하는 스크립트를 얻어내는 절차**까지 다룹니다.

📖 **교안 사이트: https://cozytk.github.io/spotfire-iron-python-scripts/**

---

## 구성

| 장 | 내용 |
|----|------|
| 1~2 | **시작하기** — 가능/불가능한 일, Python 데이터 함수와의 차이, 실행 환경 |
| 3~5 | **언어** — 프로그래밍 기초 개념, Python 2.7 문법, .NET 상호운용 |
| 6 | **Spotfire API 객체 모델** — `Document` 아래로 내려가는 지도 |
| 7 | **스크립팅의 현실** — 실제로 부딪힌 함정 모음. 이 교안만의 내용 |
| 8 | **생성형 AI로 만들기** — 5단계 틀, 프롬프트 템플릿, 검증 체크리스트 |
| 9~12 | **예제 27선** — 위험도 배지 포함 |
| 13~14 | **레퍼런스** — 실무 팁, 치트시트 & FAQ |

코딩 경험이 있으면 3장은 건너뛰고, 1 → 2 → 4.1 → 5 → 6 → 7 순으로 보면 됩니다.

## 이 교안의 목표

파이썬 개발자를 만드는 것이 아니라, 다음 세 가지를 할 수 있게 하는 것입니다.

1. **코드를 읽을 수 있게** — 남이 준 스크립트가 뭘 하는지 알아보기
2. **뭐가 가능한지 알게** — "이건 스크립트로 되겠다"를 판단하기
3. **AI에게 제대로 시킬 수 있게** — 원하는 코드를 받아내고, 검증하고, 고치기

## 예제 선정 기준

"스크립트로 굳이 짤 필요가 없는 것"은 넣지 않았습니다. 다음 중 **하나 이상**에 해당하는 것만 골랐습니다.

1. **기본 기능만으로는 하기 어렵거나 불가능한 것**
2. **여러 시각화·여러 페이지에 한 번에 적용할 수 있어서 유용한 것**

여기에 더해, Spotfire 관련 Q&A에서 반복적으로 올라오는 주제(필터 초기화, 마킹 제어,
이미지·데이터 내보내기, 문서 속성 조작, 시각화 순회)를 우선 반영했습니다.

## 예제 27선

예제는 **무엇을 다루는지**로 묶었고, 각 예제에 위험도를 표시했습니다.

새 환경에서 처음 시작한다면 **예제 23(실행 환경 진단 리포트)** 을 먼저 실행하세요.
읽기 전용이면서, 이 환경이 Analyst인지 Web Player인지·마킹의 실제 이름·내보내기
가능 여부를 한 번에 알려 줍니다.

### 9장 · 시각화 일괄 제어 — [`scripts/01-visuals/`](scripts/01-visuals)

| # | 예제 | 위험도 |
|---|------|--------|
| 1 | 모든 시각화에 데이터 제한 표현식 일괄 적용 | 중간 |
| 2 | 축 표현식 동시 전환 (측정지표 스위처) | 중간 |
| 3 | 범례·제목·서식 일괄 통일 (+마커 크기) | 낮음 |
| 4 | 여러 차트의 축 범위 동시 고정 | 낮음 |
| 5 | 모든 차트의 줌·축 범위 초기화 | 낮음 |
| 6 | 시각화 유형 일괄 토글 | 중간 |
| 7 | 모든 시각화의 데이터 테이블 일괄 교체 | **높음** |
| 24 | 모든 시각화의 툴팁 일괄 통일 | 중간 · 미검증 |
| 25 | 축 눈금 서식 일괄 통일 | 낮음 · 미검증 |

### 10장 · 필터·마킹·페이지 상태 — [`scripts/02-state/`](scripts/02-state)

| # | 예제 | 위험도 |
|---|------|--------|
| 8 | 마킹 결과를 문서 속성으로 넘기기 | 낮음 |
| 9 | 키 컬럼으로 다른 테이블에 마킹 전파 | 낮음 |
| 10 | 대시보드 전체 상태 초기화 | 낮음 |
| 11 | 원하는 컬럼의 필터만 선택적으로 초기화 | 낮음 |
| 12 | 역할별 필터 패널 구성 | 낮음 |
| 13 | 문서 속성 값으로 페이지 표시/숨김 | 낮음 |
| 26 | 마킹한 행에 태그 붙이기 | 중간 · 미검증 |
| 27 | 마킹으로 대시보드 전체 좀혀보기 | 중간 · 미검증 |

### 11장 · 데이터와 내보내기 — [`scripts/03-data/`](scripts/03-data)

| # | 예제 | 위험도 |
|---|------|--------|
| 14 | 모든 페이지의 시각화를 PNG로 일괄 내보내기 | 낮음 · Analyst 전용 |
| 15 | 여러 표를 한 번에 파일로 내보내기 | 낮음 · 환경 의존 |
| 16 | 마킹한 행을 새 데이터 테이블로 스냅샷 | 중간 |
| 17 | 모든 데이터 테이블 일괄 새로고침 | 낮음 |

### 12장 · 문서 생성과 진단 — [`scripts/04-create/`](scripts/04-create)

| # | 예제 | 위험도 |
|---|------|--------|
| 18 | 문서 전체 시각화 인벤토리 만들기 | **읽기 전용** |
| 19 | 표현식 전수 검사 (문서 감사 리포트) | 중간 |
| 20 | 마킹한 값별로 시각화 자동 생성 | **높음** |
| 21 | 산점도 매트릭스 자동 생성 (NxN) | **높음** |
| 22 | 문서 안의 스크립트 전수 조사 | **읽기 전용** · Spotfire 12.0+ |
| 23 | 실행 환경 진단 리포트 | **읽기 전용** |

각 스크립트의 **문제 상황, 매개변수 설정법, 검증 포인트**는 교안 사이트의 해당 장에 있습니다.

## AI로 스크립트 만들기

Spotfire IronPython은 AI 학습 데이터가 적은 분야라, 그냥 물어보면 Python 3 문법을 쓰거나
**존재하지 않는 API를 자신 있게 만들어 냅니다.** 그래서 두 가지를 준비해 두었습니다.

### 프롬프트 파일 — 어떤 AI에서나

[`prompts/`](prompts) 폴더의 파일을 대화창에 붙여 넣으면 됩니다.

| 파일 | 언제 |
|------|------|
| [`00-context.md`](prompts/00-context.md) | **항상 먼저.** 환경 제약과 Spotfire 함정 |
| [`01-request-template.md`](prompts/01-request-template.md) | 새 스크립트를 요청할 때 |
| [`02-debug-template.md`](prompts/02-debug-template.md) | 오류가 났을 때 |
| [`03-verify-checklist.md`](prompts/03-verify-checklist.md) | 받은 코드를 실행하기 전에 |

### Claude Code 스킬 — 자동 적용

[`.claude/skills/spotfire-ironpython/`](.claude/skills/spotfire-ironpython) 에 스킬이 있습니다.
이 저장소에서 작업하면 자동으로 인식되고, 어디서나 쓰려면 개인 스킬 폴더로 복사하세요.

```bash
cp -r .claude/skills/spotfire-ironpython ~/.claude/skills/
```

스킬에는 실측으로 확인한 API 목록, 존재하지 않는 이름 목록, 예제 27종 색인이 들어 있어
프롬프트를 따로 붙여 넣을 필요가 없습니다.

## 스크립트 사용법

> [!IMPORTANT]
> 예제를 돌리기 전에 [`scripts/00_setup_document_properties.py`](scripts/00_setup_document_properties.py)
> 를 **한 번 실행**하세요. 예제 대부분이 결과를 `Document.Properties["ScriptLog"]` 에 쓰는데,
> 그 문서 속성이 없으면 마지막 줄에서 실패합니다.

1. Spotfire에서 텍스트 영역을 편집 모드로 열고 **액션 컨트롤 삽입** → 유형 **스크립트**
2. `scripts/` 의 `.py` 내용을 붙여 넣기
3. 파일 상단 주석의 **매개변수** 항목대로 스크립트 매개변수를 설정
4. **실행(Execute)** 으로 시험

이 파일들은 **생성형 AI에게 줄 재료**이기도 합니다.
하고 싶은 일과 가장 비슷한 스크립트를 프롬프트에 붙여 넣으면 결과 품질이 크게 올라갑니다.
자세한 절차는 교안 8장을 참고하세요.

> [!WARNING]
> 스크립트는 되돌리기(Undo)가 되지 않는 변경을 만들 수 있습니다.
> 특히 데이터 테이블 교체·삭제, 시각화 일괄 변경 계열은 **반드시 분석 파일 사본에서 먼저**
> 시험하세요. 각 예제의 "검증 포인트"에 위험 요소를 적어 두었습니다.

## 저장소 구조

```text
content/            교안 원본 (Markdown) — 내용은 여기서 수정
prompts/            AI 요청용 프롬프트 템플릿
.claude/skills/     Claude Code 스킬
assets/             사이트 CSS / JS
docs/               빌드 결과물 (GitHub Pages가 서빙)
scripts/            예제 스크립트 (content/ 에서 자동 생성)
├── 00_setup_document_properties.py   예제 실행 전 한 번 실행
├── 01-visuals/  02-state/  03-data/  04-create/
checks/             API 검증 하네스와 8차수 실측 기록
build.py            content/ -> docs/ 빌드
extract_scripts.py  content/ -> scripts/ 추출
```

`checks/README.md` 에는 실제 Spotfire(IronPython 2.7.12 / Spotfire 14.x)에서 확인한
API 실측 결과가 정리되어 있습니다. 교안의 "검증 포인트"는 이 결과를 근거로 합니다.

**예제 1~21이 사용하는 API는 여덟 차례 실행으로 전부 확인했습니다.**
그 과정에서 교안 오류 8건(`TreemapChart`, `IndexSet.Add`, 마킹 이름 하드코딩,
`StdfDataSource`, `RenderSync`, `Tables[0]`, `CreateDataWriter`, `ScriptLog` 미생성)을
잡아 고쳤습니다. 교안을 수정한 뒤에는 `checks/00_verify_all_examples.py` 로
회귀 확인을 할 수 있습니다.

나중에 추가한 **예제 22~27은 아직 실측하지 않았습니다.** Spotfire 15.0 API 레퍼런스,
공식 커뮤니티 문서, sf-ref.com을 근거로 작성했으며 교안의 해당 절과 목록에
`미검증` 을 표시해 두었습니다. 22·23은 읽기 전용이지만 24~27은 **문서를 변경하므로
반드시 사본에서 먼저 시험**하세요.

## 로컬에서 빌드하기

```bash
pip install -r requirements.txt
python build.py            # docs/ 생성
python extract_scripts.py  # scripts/ 생성
python -m http.server 8000 --directory docs
```

`docs/`와 `scripts/`는 **자동 생성물**입니다. 직접 고치지 말고 `content/*.md`를 수정한 뒤
두 명령을 다시 실행하세요.

## GitHub Pages 설정

저장소 **Settings → Pages** 에서 둘 중 하나를 고르세요.

- **Deploy from a branch** (간단): Branch = **저장소의 기본 브랜치**, 폴더 = `/docs`
- **GitHub Actions**: 포함된 [`.github/workflows/pages.yml`](.github/workflows/pages.yml) 이 `docs/`를 배포합니다

워크플로는 `main` 브랜치에서 동작하도록 설정되어 있습니다.
다른 브랜치를 쓰려면 `pages.yml` 의 `branches:` 목록에 추가하세요.

## 참고 자료

어느 자료를 언제 보는지까지 [14장 · 참고한 자료](https://cozytk.github.io/spotfire-iron-python-scripts/14-cheatsheet.html)에 정리해 두었습니다.

| 자료 | 언제 보나 |
|------|----------|
| [IronPython Scripting in Spotfire® – Overview](https://community.spotfire.com/articles/spotfire/ironpython-scripting-in-spotfire/) | "이런 것도 되나?" — 수백 개 예제의 분류 색인 |
| [Spotfire Analyst API Reference](https://docs.tibco.com/pub/doc_remote/sfire_dev/area/doc/api/tib_sfire-analyst_api/index.aspx) | 이름·시그니처·폐기 여부의 최종 근거 |
| [The Spotfire IronPython Quick Reference (sf-ref.com)](https://www.sf-ref.com/ironpython/) | 시각화 속성 대화상자 탭 ↔ 코드 대응 |
| [IronPython Example Scripts (제품 문서)](https://docs.tibco.com/pub/sfire-cloud/14.6.2/doc/html/en-US/TIB_sfire_client/client/topics/en-US/iron_python_example_scripts.html) | 공식 예제 3개와 매개변수 사용법 |
| [essejhsif/spotfire](https://github.com/essejhsif/spotfire) · [Gurudutt-Goswami/Spotfire-Ironpython](https://github.com/Gurudutt-Goswami/Spotfire-Ironpython) | 짧고 오래된 스니펫 모음 — 7장 체크리스트로 걸러서 |

스크립팅으로 안 되는 일(새 시각화 유형 만들기 등)의 경계는
[`CustomVisualView` API 문서](https://docs.tibco.com/pub/doc_remote/sfire_dev/area/doc/api/tib_sfire-analyst_api/index.aspx?topic=html/t_spotfire_dxp_application_extension_customvisualview.htm)를
근거로 [1.3절](https://cozytk.github.io/spotfire-iron-python-scripts/01-what-you-can-do.html)에
정리했습니다. 교안이 근거로 삼은 개별 공식 문서 목록은
[14장 · 참고한 자료](https://cozytk.github.io/spotfire-iron-python-scripts/14-cheatsheet.html)에
정리해 두었습니다.

## 라이선스

[MIT](LICENSE). Spotfire는 Cloud Software Group, Inc.의 상표이며, 본 저장소는 비공식 학습 자료입니다.
