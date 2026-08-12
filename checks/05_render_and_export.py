# -*- coding: utf-8 -*-
# 테스트 5 — 이미지 렌더링과 데이터 내보내기 (교안 예제 8, 9)
#
# 위험도: 낮음
#   - 이미지는 메모리에만 그리고 파일로 저장하지 않습니다
#   - 데이터 writer는 만들기만 하고 파일에 쓰지 않습니다
#   - 문서를 변경하지 않습니다
# 실행:   차트가 있는 페이지를 활성 페이지로 두고 실행


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


print "=== 1. System.Drawing 사용 가능 여부 ==="
drawingOk = False
try:
    import clr
    clr.AddReference("System.Drawing")
    from System.Drawing import Bitmap, Graphics, Rectangle, Size
    drawingOk = True
    print "[OK] System.Drawing import"
except Exception, e:
    print "[NO]", clean(str(e))
    print "     -> 2번 항목은 건너뜁니다"

print ""
print "=== 2. VisualContent.Render(Graphics, Rectangle) ==="
from Spotfire.Dxp.Application.Visuals import VisualContent

page = Document.ActivePageReference
for visual in (page.Visuals if drawingOk else []):
    title = clean(visual.Title)
    try:
        vc = visual.As[VisualContent]()
    except Exception, e:
        print "[??]", title, "- 캐스팅 불가 (렌더링 대상 아님)"
        continue

    try:
        bitmap = Bitmap(400, 300)
        graphics = Graphics.FromImage(bitmap)
        vc.Render(graphics, Rectangle(0, 0, 400, 300))
        graphics.Dispose()
        bitmap.Dispose()
        print "[OK]", title, "- Render 성공"
    except Exception, e:
        print "[NO]", title, "-", clean(str(e))

print ""
print "=== 3. 신형 렌더링 API 존재 여부 ==="
for visual in page.Visuals:
    print "  ", clean(visual.Title), \
          "| RenderSync:", hasattr(visual, "RenderSync"), \
          "| RenderAsync:", hasattr(visual, "RenderAsync")
    break

print ""
print "=== 4. 데이터 writer 생성 (파일에 쓰지 않음) ==="
try:
    from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
    for name in dir(DataWriterTypeIdentifiers):
        if name.startswith("_"):
            continue
        try:
            identifier = getattr(DataWriterTypeIdentifiers, name)
            writer = Document.Data.CreateDataWriter(identifier)
            print "[OK]", name, "- writer 생성됨"
        except Exception, e:
            print "[NO]", name, "-", clean(str(e))
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 5. 필터 적용된 행 개수 확인 ==="
try:
    table = Document.ActiveDataTableReference
    filtered = Document.ActiveFilteringSelectionReference.GetSelection(table).AsIndexSet()
    print "[OK] 전체:", table.RowCount, "| 필터 통과:", filtered.Count
except Exception, e:
    print "[NO]", clean(str(e))
