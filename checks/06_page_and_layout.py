# -*- coding: utf-8 -*-
# 테스트 6 — 페이지 속성과 레이아웃 API (교안 예제 15, 19, 21)
#
# *** 주의: 이 테스트만 문서를 변경합니다 ***
#   임시 페이지 "__API_TEST__" 를 만들어 시험한 뒤 마지막에 삭제합니다.
#   그래도 되돌리기가 완전하지 않을 수 있으니 반드시 사본에서 실행하세요.
#   중간에 오류가 나면 "__API_TEST__" 페이지가 남을 수 있습니다. 직접 지우시면 됩니다.
#
# 확인 항목:
#   - Page.Visible 속성이 존재하는가 (예제 15의 전제)
#   - page.Visuals.AddNew[T]() 가 무엇을 반환하는가 (예제 21의 함정)
#   - LayoutDefinition 의 메서드와 인자 형태

from Spotfire.Dxp.Application.Visuals import BarChart, VisualContent

TEST_PAGE = "__API_TEST__"


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


print "=== 1. Page.Visible 속성 (예제 15) ==="
page0 = Document.Pages[0]
print "  hasattr(page, 'Visible'):", hasattr(page0, "Visible")
try:
    print "[OK] 현재 값:", page0.Visible
except Exception, e:
    print "[NO] 읽기 실패:", clean(str(e))

print ""
print "=== 2. LayoutDefinition 메서드 목록 ==="
try:
    from Spotfire.Dxp.Application.Layout import LayoutDefinition
    layout = LayoutDefinition()
    print "[OK] LayoutDefinition() 생성"
    for name in dir(layout):
        if not name.startswith("_"):
            print "   ", name
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 3. 임시 페이지에서 실제 동작 확인 ==="

testPage = None
try:
    # 이전 실행이 남긴 것이 있으면 먼저 정리
    for page in [p for p in Document.Pages]:
        if page.Title == TEST_PAGE:
            Document.Pages.Remove(page)

    testPage = Document.Pages.AddNew(TEST_PAGE)
    print "[OK] Pages.AddNew 성공"

    # 3-1) AddNew 가 무엇을 반환하는가
    chart = testPage.Visuals.AddNew[BarChart]()
    print "[OK] Visuals.AddNew[BarChart]() 반환형:", clean(type(chart))
    print "     -> BarChart(콘텐츠)이면 레이아웃에 넣을 Visual 컨테이너를 따로 찾아야 함"

    chart.Title = "TEST_A"
    chart2 = testPage.Visuals.AddNew[BarChart]()
    chart2.Title = "TEST_B"

    # 3-2) Visual 컨테이너 찾기
    containerA = None
    containerB = None
    for visual in testPage.Visuals:
        print "     페이지 내 Visual 컨테이너:", clean(visual.Title), clean(type(visual))
        if visual.Title == "TEST_A":
            containerA = visual
        if visual.Title == "TEST_B":
            containerB = visual

    # 3-3) 레이아웃 적용
    if containerA is not None and containerB is not None:
        from Spotfire.Dxp.Application.Layout import LayoutDefinition

        print ""
        print "  --- BeginStackedSection 인자 형태 확인 ---"
        try:
            probe = LayoutDefinition()
            probe.BeginSideBySideSection()
            probe.Add(containerA, 50.0)
            probe.BeginStackedSection(50.0)
            probe.Add(containerB, 100.0)
            probe.EndSection()
            probe.EndSection()
            testPage.ApplyLayout(probe)
            print "[OK] BeginStackedSection(weight) 인자 O + ApplyLayout 성공"
        except Exception, e:
            print "[NO] BeginStackedSection(weight):", clean(str(e))
            try:
                probe = LayoutDefinition()
                probe.BeginSideBySideSection()
                probe.Add(containerA, 50.0)
                probe.BeginStackedSection()
                probe.Add(containerB, 100.0)
                probe.EndSection()
                probe.EndSection()
                testPage.ApplyLayout(probe)
                print "[OK] BeginStackedSection() 인자 X 형태는 성공"
            except Exception, e2:
                print "[NO] 인자 없는 형태도 실패:", clean(str(e2))
    else:
        print "[??] Visual 컨테이너를 제목으로 찾지 못함"

    # 3-4) 페이지 숨김 실제 적용
    try:
        testPage.Visible = False
        print "[OK] Page.Visible = False 적용됨 (현재값:", testPage.Visible, ")"
        testPage.Visible = True
    except Exception, e:
        print "[NO] Page.Visible 쓰기:", clean(str(e))

except Exception, e:
    print "[NO] 테스트 중 오류:", clean(str(e))

finally:
    # 반드시 정리
    try:
        for page in [p for p in Document.Pages]:
            if page.Title == TEST_PAGE:
                Document.Pages.Remove(page)
        print ""
        print "[OK] 임시 페이지 삭제 완료"
    except Exception, e:
        print ""
        print "[NO] 임시 페이지 삭제 실패 - '" + TEST_PAGE + "' 페이지를 직접 지워 주세요:", clean(str(e))
