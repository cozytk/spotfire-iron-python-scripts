# Spotfire IronPython 2.7 교안

Spotfire의 IronPython 2.7 스크립팅 한국어 교안과, 바로 실행할 수 있는 예제 스크립트 21종입니다.

**프로그래밍을 해 본 적 없어도** 따라올 수 있도록 개념부터 시작하고,
**생성형 AI로 원하는 스크립트를 얻어내는 절차**까지 다룹니다.

📖 **교안 사이트: https://cozytk.github.io/spotfire-iron-python-scripts/**

---

## 구성

| 장 | 내용 |
|----|------|
| 1 | **무엇을 할 수 있나** — 가능/불가능한 일, **Python 데이터 함수와의 차이** |
| 2 | 스크립트 실행 환경 — 어디에 넣고, 어떻게 실행하고, 디버깅하는지 |
| 3 | **프로그래밍 기초 개념** — 변수·자료형·객체·속성·메서드·라이브러리·함수·반복 |
| 4 | IronPython 2.7 문법 — Python 2.7 전반, Python 3와의 차이 |
| 5 | .NET 상호운용 문법 — `clr`, `As[T]()`, 제네릭, .NET 타입 |
| 6 | Spotfire API 객체 모델 — `Document` 아래로 내려가는 지도 |
| 7 | **생성형 AI로 스크립트 만들기** — 5단계 틀, 프롬프트 템플릿, 검증 체크리스트 |
| 8~11 | 예제 21선 |
| 12 | 실무 팁과 함정 — 성능, Undo, Web Player 호환성 |
| 13 | 치트시트 & FAQ |

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

## 예제 21선

| # | 예제 | 스크립트 |
|---|------|----------|
| 1 | 문서 전체 시각화 인벤토리 만들기 | [`01_visual_inventory.py`](scripts/01-bulk/01_visual_inventory.py) |
| 2 | 모든 시각화에 데이터 제한 표현식 일괄 적용 | [`02_bulk_limit_expression.py`](scripts/01-bulk/02_bulk_limit_expression.py) |
| 3 | 축 표현식 동시 전환 (측정지표 스위처) | [`03_switch_measure_axis.py`](scripts/01-bulk/03_switch_measure_axis.py) |
| 4 | 범례·제목·서식 일괄 통일 (+마커 크기) | [`04_unify_legend_and_title.py`](scripts/01-bulk/04_unify_legend_and_title.py) |
| 5 | 모든 시각화의 데이터 테이블 일괄 교체 | [`05_swap_data_table.py`](scripts/01-bulk/05_swap_data_table.py) |
| 6 | 모든 차트의 줌 초기화 | [`06_reset_zoom_all_charts.py`](scripts/01-bulk/06_reset_zoom_all_charts.py) |
| 7 | 여러 차트의 축 범위 동시 고정 | [`07_fix_axis_range.py`](scripts/01-bulk/07_fix_axis_range.py) |
| 8 | 모든 페이지의 시각화를 PNG로 일괄 내보내기 | [`08_export_all_visuals_to_png.py`](scripts/02-data/08_export_all_visuals_to_png.py) |
| 9 | 여러 데이터 테이블을 한 번에 파일로 내보내기 | [`09_export_all_tables_to_file.py`](scripts/02-data/09_export_all_tables_to_file.py) |
| 10 | 마킹한 행을 새 데이터 테이블로 스냅샷 | [`10_snapshot_marked_rows.py`](scripts/02-data/10_snapshot_marked_rows.py) |
| 11 | 마킹 결과를 문서 속성으로 넘기기 | [`11_marking_to_document_property.py`](scripts/02-data/11_marking_to_document_property.py) |
| 12 | 키 컬럼으로 다른 테이블에 마킹 전파 | [`12_propagate_marking_by_key.py`](scripts/02-data/12_propagate_marking_by_key.py) |
| 13 | 모든 데이터 테이블 일괄 새로고침 | [`13_refresh_all_data_tables.py`](scripts/02-data/13_refresh_all_data_tables.py) |
| 14 | 대시보드 전체 상태 초기화 | [`14_reset_dashboard_state.py`](scripts/03-ui/14_reset_dashboard_state.py) |
| 15 | 문서 속성 값으로 페이지 표시/숨김 | [`15_toggle_pages_by_role.py`](scripts/03-ui/15_toggle_pages_by_role.py) |
| 16 | 역할별 필터 패널 구성 | [`16_configure_filter_panel.py`](scripts/03-ui/16_configure_filter_panel.py) |
| 17 | 시각화 유형 일괄 토글 | [`17_bulk_switch_visual_type.py`](scripts/03-ui/17_bulk_switch_visual_type.py) |
| 18 | 원하는 컬럼의 필터만 선택적으로 초기화 | [`18_reset_selected_column_filters.py`](scripts/03-ui/18_reset_selected_column_filters.py) |
| 19 | 마킹한 값별로 시각화 자동 생성 | [`19_generate_visuals_from_marking.py`](scripts/04-advanced/19_generate_visuals_from_marking.py) |
| 20 | 표현식 전수 검사 (문서 감사 리포트) | [`20_audit_expressions.py`](scripts/04-advanced/20_audit_expressions.py) |
| 21 | 산점도 매트릭스 자동 생성 (NxN) | [`21_scatter_plot_matrix.py`](scripts/04-advanced/21_scatter_plot_matrix.py) |

각 스크립트의 **문제 상황, 매개변수 설정법, 검증 포인트**는 교안 사이트의 해당 장에 있습니다.

## 스크립트 사용법

1. Spotfire에서 텍스트 영역을 편집 모드로 열고 **액션 컨트롤 삽입** → 유형 **스크립트**
2. `scripts/` 의 `.py` 내용을 붙여 넣기
3. 파일 상단 주석의 **매개변수** 항목대로 스크립트 매개변수를 설정
4. **실행(Execute)** 으로 시험

이 파일들은 **생성형 AI에게 줄 재료**이기도 합니다.
하고 싶은 일과 가장 비슷한 스크립트를 프롬프트에 붙여 넣으면 결과 품질이 크게 올라갑니다.
자세한 절차는 교안 7장을 참고하세요.

> [!WARNING]
> 스크립트는 되돌리기(Undo)가 되지 않는 변경을 만들 수 있습니다.
> 특히 데이터 테이블 교체·삭제, 시각화 일괄 변경 계열은 **반드시 분석 파일 사본에서 먼저**
> 시험하세요. 각 예제의 "검증 포인트"에 위험 요소를 적어 두었습니다.

## 저장소 구조

```text
content/            교안 원본 (Markdown) — 내용은 여기서 수정
assets/             사이트 CSS / JS
docs/               빌드 결과물 (GitHub Pages가 서빙)
scripts/            예제 스크립트 (content/ 에서 자동 생성)
build.py            content/ -> docs/ 빌드
extract_scripts.py  content/ -> scripts/ 추출
```

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

워크플로는 `main` 과 `claude/spotfire-ironpython-guide-m9nnv5` 브랜치에서 동작하도록
설정되어 있습니다. 다른 브랜치를 쓰려면 `pages.yml` 의 `branches:` 목록에 추가하세요.

## 참고 자료

- [IronPython Scripting in Spotfire® – Overview (Spotfire Community)](https://community.spotfire.com/articles/spotfire/ironpython-scripting-in-spotfire/)
- [essejhsif/spotfire](https://github.com/essejhsif/spotfire)
- [Gurudutt-Goswami/Spotfire-Ironpython](https://github.com/Gurudutt-Goswami/Spotfire-Ironpython)
- [IronPython Example Scripts (Spotfire 제품 문서)](https://docs.tibco.com/pub/sfire-analyst/12.0.6/doc/html/en-US/TIB_sfire-analyst_UsersGuide/text/text_ironpython_example_scripts.htm)
- [The Spotfire IronPython Quick Reference](https://www.sf-ref.com/ironpython/)

## 라이선스

[MIT](LICENSE). Spotfire는 Cloud Software Group, Inc.의 상표이며, 본 저장소는 비공식 학습 자료입니다.
