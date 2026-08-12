# -*- coding: utf-8 -*-
# 예제 9. 여러 데이터 테이블을 한 번에 파일로 내보내기
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-data.html
# 이 파일은 content/09-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 표 시각화의 데이터를 탭 구분 텍스트 파일로 내보낸다. (Analyst 전용)
#
# 매개변수:
#   vTable (Visualization) 표(Table) 시각화

from Spotfire.Dxp.Application.Visuals import TablePlot
from System.IO import StreamWriter
from System.Text import Encoding

PATH = "C:/temp/export.txt"

plot = vTable.As[TablePlot]()

if not plot.ExportDataEnabled:
    Document.Properties["ScriptLog"] = u"이 시각화는 데이터 내보내기가 비활성화되어 있습니다."
else:
    # 한글이 있으면 UTF-8 로 명시한다
    writer = StreamWriter(PATH, False, Encoding.UTF8)
    try:
        plot.ExportText(writer)
    finally:
        writer.Close()
    Document.Properties["ScriptLog"] = u"내보내기 완료: " + PATH
