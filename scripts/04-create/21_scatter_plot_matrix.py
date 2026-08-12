# -*- coding: utf-8 -*-
# 예제 21. 산점도 매트릭스 자동 생성 (NxN 상관 분석)
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/12-examples-create.html
# 이 파일은 content/12-examples-create.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 문서 속성에 선택된 연속형 컬럼들로 NxN 산점도 매트릭스를 만들고 격자로 배치한다.

from Spotfire.Dxp.Application.Visuals import ScatterPlot
from Spotfire.Dxp.Application.Layout import LayoutDefinition
from Spotfire.Dxp.Data import DataPropertyClass
from System import String

# ---------- 설정 ----------
DATA_TABLE_NAME = "iris"          # 데이터 테이블 이름
PAGE_NAME = u"상관성 분석"          # 결과 페이지 (없으면 생성)
PROPERTY_NAME = "columns"         # 컬럼 목록이 담긴 문서 속성
TEXT_AREA_TITLE = u"텍스트 영역"    # 왼쪽에 유지할 텍스트 영역 제목 (없으면 무시)
TEXT_AREA_WIDTH = 10.0            # 왼쪽 텍스트 영역 폭 비율
GRID_WIDTH = 90.0                 # 오른쪽 격자 폭 비율
INCLUDE_DIAGONAL = True           # 대각선(자기 자신과의 산점도) 포함 여부


# ---------- 문서 속성에서 컬럼 목록 읽기 ----------
def get_selected_columns(propertyName):
    raw = Document.Properties[propertyName]
    if raw is None:
        raise Exception(u"문서 속성 '%s' 값이 비어 있습니다." % propertyName)

    columns = []
    if isinstance(raw, String):
        # 단일 문자열이면 쉼표로 분리
        for name in str(raw).split(","):
            if name.strip():
                columns.append(name.strip())
    else:
        # 문자열 목록이면 그대로 순회
        for name in raw:
            if name is not None and str(name).strip():
                columns.append(str(name).strip())

    if not columns:
        raise Exception(u"문서 속성 '%s'에 선택된 컬럼이 없습니다." % propertyName)
    return columns


# ---------- 보조 함수 ----------
def get_page_by_title(title):
    for page in Document.Pages:
        if page.Title == title:
            return page
    return None


def get_visual_by_title(page, title):
    for visual in page.Visuals:
        if visual.Title == title:
            return visual
    return None


def remove_existing_scatter_plots(page):
    """재실행 대비: 기존 산점도만 지운다. 텍스트 영역은 남긴다."""
    targets = []
    for visual in page.Visuals:
        try:
            if visual.As[ScatterPlot]() is not None:
                targets.append(visual)
        except:
            pass
    for visual in targets:
        try:
            page.Visuals.Remove(visual)
        except:
            pass


def column_expression(columnName):
    # 컬럼 이름에 ] 가 있으면 이스케이프
    return "<[" + columnName.replace("]", "]]") + "]>"


def add_scatter(page, dataTable, xCol, yCol):
    """산점도를 만들고, 레이아웃에 넣을 Visual 컨테이너를 반환한다."""
    scatter = page.Visuals.AddNew[ScatterPlot]()
    scatter.Data.DataTableReference = dataTable
    scatter.XAxis.Expression = column_expression(xCol)
    scatter.YAxis.Expression = column_expression(yCol)

    title = u"%s vs %s" % (yCol, xCol)
    scatter.Title = title

    # 격자에서는 축 선택기와 범례가 공간만 차지한다
    for setter in ["XAxis", "YAxis"]:
        try:
            getattr(scatter, setter).ShowAxisSelector = False
        except:
            pass
    try:
        scatter.Legend.Visible = False
    except:
        pass
    try:
        scatter.MarkerSize = 2
    except:
        pass

    # AddNew는 콘텐츠를 반환하므로, 배치에 쓸 Visual 컨테이너는 제목으로 찾는다
    visual = get_visual_by_title(page, title)
    if visual is None:
        raise Exception(u"생성한 시각화를 찾을 수 없습니다: " + title)
    return visual


def apply_grid_layout(page, textAreaVisual, grid):
    """왼쪽 텍스트 영역 + 오른쪽 NxN 격자로 배치한다."""
    layout = LayoutDefinition()

    def build_grid():
        rowCount = len(grid)
        for row in grid:
            if not row:
                continue
            layout.BeginSideBySideSection(100.0 / rowCount)
            for visual in row:
                layout.Add(visual, 100.0 / len(row))
            layout.EndSection()

    if textAreaVisual is not None:
        layout.BeginSideBySideSection()
        layout.Add(textAreaVisual, TEXT_AREA_WIDTH)
        try:
            layout.BeginStackedSection(GRID_WIDTH)
        except:
            layout.BeginStackedSection()
        build_grid()
        layout.EndSection()
        layout.EndSection()
    else:
        layout.BeginStackedSection()
        build_grid()
        layout.EndSection()

    page.ApplyLayout(layout)


# ---------- 실행 ----------
columns = get_selected_columns(PROPERTY_NAME)

if not Document.Data.Tables.Contains(DATA_TABLE_NAME):
    raise Exception(u"데이터 테이블을 찾을 수 없습니다: " + DATA_TABLE_NAME)
dataTable = Document.Data.Tables[DATA_TABLE_NAME]

missing = [c for c in columns if not dataTable.Columns.Contains(c)]
if missing:
    raise Exception(u"다음 컬럼을 찾을 수 없습니다: " + u", ".join(missing))

# 페이지 확보 (있으면 재사용)
page = get_page_by_title(PAGE_NAME)
if page is None:
    page = Document.Pages.AddNew(PAGE_NAME)
Document.ActivePageReference = page

textAreaVisual = get_visual_by_title(page, TEXT_AREA_TITLE)
remove_existing_scatter_plots(page)

# NxN 격자 생성
grid = []
for yCol in columns:
    rowVisuals = []
    for xCol in columns:
        if (not INCLUDE_DIAGONAL) and xCol == yCol:
            continue
        rowVisuals.append(add_scatter(page, dataTable, xCol, yCol))
    grid.append(rowVisuals)

apply_grid_layout(page, textAreaVisual, grid)

Document.Properties["ScriptLog"] = u"컬럼 %d개로 산점도 %d개를 '%s' 페이지에 생성했습니다." % (
    len(columns), sum(len(r) for r in grid), PAGE_NAME)
