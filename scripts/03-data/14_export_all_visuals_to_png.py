# -*- coding: utf-8 -*-
# 예제 14. 모든 페이지의 시각화를 PNG로 일괄 내보내기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/11-examples-data.html
# 이 파일은 content/11-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

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


# Web Player에서는 로컬 폴더에 쓸 수 없다.
# 알 수 없는 .NET 예외 대신 사람이 읽을 수 있는 안내를 남긴다. → 7.7 참조
isAnalyst = "RichAnalysisApplication" in Application.GetType().ToString()

if not isAnalyst:
    Document.Properties["ScriptLog"] = (
        u"이미지 내보내기는 Spotfire Analyst(데스크톱)에서만 동작합니다.")
else:
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
                # 텍스트 영역·Mod 시각화는 여기로 빠진다 (아래 "왜 실패하나" 참조)
                failed.append(u"%s / %s" % (page.Title, visual.Title))

    msg = u"%d개 이미지를 저장했습니다: %s" % (saved, folder)
    if failed:
        msg += u" (건너뜀 %d개: %s)" % (len(failed), u", ".join(failed))

    Document.Properties["ScriptLog"] = msg
