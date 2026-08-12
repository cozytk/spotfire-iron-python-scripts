# -*- coding: utf-8 -*-
# 예제 8. 모든 페이지의 시각화를 PNG로 일괄 내보내기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-data.html
# 이 파일은 content/09-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 모든 페이지의 모든 시각화를 PNG 파일로 저장한다. (Analyst 데스크톱 전용)
#
# 매개변수:
#   outDir (String) 저장할 폴더 경로. 예: "C:/exports"

import clr
clr.AddReference("System.Drawing")

from Spotfire.Dxp.Application.Visuals import VisualContent
from System.Drawing import Bitmap, Graphics, Rectangle
from System.IO import Directory, Path
from System import DateTime

WIDTH, HEIGHT = 1400, 900

# 파일명에 쓸 수 없는 문자 제거
def safe_name(text):
    result = []
    for ch in (text or u"untitled"):
        result.append(ch if ch not in u'\\/:*?"<>|\r\n\t' else u"_")
    return u"".join(result).strip()[:80] or u"untitled"

stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss")
folder = Path.Combine(outDir, "spotfire_" + stamp)
Directory.CreateDirectory(folder)

saved = 0
failed = []

for pageIndex, page in enumerate(Document.Pages):
    for vizIndex, visual in enumerate(page.Visuals):
        try:
            vc = visual.As[VisualContent]()

            bitmap = Bitmap(WIDTH, HEIGHT)
            graphics = Graphics.FromImage(bitmap)
            vc.Render(graphics, Rectangle(0, 0, WIDTH, HEIGHT))

            fileName = u"%02d_%s__%02d_%s.png" % (
                pageIndex + 1, safe_name(page.Title),
                vizIndex + 1, safe_name(visual.Title))

            bitmap.Save(Path.Combine(folder, fileName))

            graphics.Dispose()
            bitmap.Dispose()
            saved += 1
        except:
            failed.append(u"%s / %s" % (page.Title, visual.Title))

msg = u"%d개 이미지를 저장했습니다: %s" % (saved, folder)
if failed:
    msg += u" (건너뜀 %d개: %s)" % (len(failed), u", ".join(failed))

Document.Properties["ScriptLog"] = msg
