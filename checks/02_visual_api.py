# -*- coding: utf-8 -*-
# 테스트 2 — 시각화 API 실측
#
# 목적:  교안 8~11장 예제가 쓰는 속성이 실제로 존재하는지, 시각화 유형별로 확인
# 위험도: 없음 (읽기만 함. 값을 바꾸지 않음)
# 실행:   여러 종류의 시각화(막대/선/산점도/표/교차표/텍스트영역)가 있는
#         페이지를 활성 페이지로 두고 실행하면 결과가 풍부합니다.

from Spotfire.Dxp.Application.Visuals import VisualContent

# 교안이 사용하는 속성 경로들
PATHS = [
    "Data.DataTableReference",
    "Data.WhereClauseExpression",
    "Data.MarkingReference",
    "Data.LimitingMarkingsEmptyMessage",
    "Legend.Visible",
    "XAxis.Expression",
    "YAxis.Expression",
    "ColorAxis.Expression",
    "SizeAxis.Expression",
    "MeasureAxis.Expression",
    "SectorSizeAxis.Expression",
    "XAxis.ZoomRange",
    "YAxis.Range",
    "XAxis.ShowAxisSelector",
    "MarkerSize",
    "Trellis.PanelAxis.Expression",
    "SortedBars",
    "TableColumns",
    "SortInfos",
]


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


def has_path(obj, path):
    """점으로 이어진 속성 경로가 실제로 읽히는지 확인한다."""
    current = obj
    for part in path.split("."):
        try:
            current = getattr(current, part)
        except:
            return False
    return True


page = Document.ActivePageReference
print "활성 페이지:", clean(page.Title)
print "시각화 개수:", page.Visuals.Count
print ""

for visual in page.Visuals:
    print "---------------------------------------------"
    print "제목  :", clean(visual.Title)
    print "TypeId:", clean(visual.TypeId)
    print "str() :", clean(str(visual.TypeId))

    try:
        vc = visual.As[VisualContent]()
        print "[OK] As[VisualContent]() 캐스팅 성공"
    except Exception, e:
        print "[NO] As[VisualContent]() 실패:", clean(str(e))
        continue

    available = []
    for path in PATHS:
        if has_path(vc, path):
            available.append(path)
    print "사용 가능한 속성:"
    for path in available:
        print "   [OK]", path

print ""
print "============================================="
print "AxisRange 확인"
try:
    from Spotfire.Dxp.Application.Visuals import AxisRange
    print "[OK] AxisRange import"
    print "[OK] DefaultRange:", clean(AxisRange.DefaultRange)
    try:
        print "[OK] AxisRange(0, 100):", clean(AxisRange(0, 100))
    except Exception, e:
        print "[NO] AxisRange(0, 100):", clean(str(e))
except Exception, e:
    print "[NO] AxisRange:", clean(str(e))

print ""
print "VisualTypeIdentifiers 전체 목록"
from Spotfire.Dxp.Application.Visuals import VisualTypeIdentifiers
for name in dir(VisualTypeIdentifiers):
    if not name.startswith("_"):
        print "   ", name
