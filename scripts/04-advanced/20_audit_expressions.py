# -*- coding: utf-8 -*-
# 예제 20. 표현식 전수 검사 (문서 감사 리포트)
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/11-examples-advanced.html
# 이 파일은 content/11-examples-advanced.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 문서 내 모든 시각화의 표현식을 수집해 "표현식 감사" 데이터 테이블로 만든다.
# searchTerm 이 주어지면 그 문자열을 포함한 표현식만 남긴다.
#
# 매개변수:
#   searchTerm (String) 찾을 문자열. 예: "Amount". 빈 문자열이면 전체

from Spotfire.Dxp.Application.Visuals import VisualContent
from Spotfire.Dxp.Data import DataType
from Spotfire.Dxp.Data.Import import TextFileDataSource, TextDataReaderSettings
from System.IO import MemoryStream, StreamWriter, SeekOrigin
from System.Text import Encoding

TABLE_NAME = u"표현식 감사"

# 조사할 축 이름들 — 시각화 유형에 따라 없는 것도 있으므로 전부 시도한다
AXIS_NAMES = ["XAxis", "YAxis", "ColorAxis", "SizeAxis", "ShapeAxis", "LabelAxis",
              "MeasureAxis", "HorizontalAxis", "VerticalAxis", "SectorSizeAxis",
              "CellValueAxis", "ValueAxis"]

term = (searchTerm or "").strip()

records = []      # (페이지, 시각화, 유형, 위치, 표현식)

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        typeName = visual.TypeId.Name

        # 1) 각 축의 표현식
        for axisName in AXIS_NAMES:
            try:
                expression = getattr(vc, axisName).Expression
            except:
                continue
            if expression:
                records.append((page.Title, visual.Title, typeName, axisName, expression))

        # 2) 데이터 제한 표현식
        try:
            where = vc.Data.WhereClauseExpression
            if where:
                records.append((page.Title, visual.Title, typeName,
                                "WhereClause", where))
        except:
            pass

        # 3) 트렐리스 분할 표현식
        try:
            panel = vc.Trellis.PanelAxis.Expression
            if panel:
                records.append((page.Title, visual.Title, typeName,
                                "Trellis", panel))
        except:
            pass

# 검색어 필터
if term:
    records = [r for r in records if term.lower() in r[4].lower()]

if not records:
    Document.Properties["ScriptLog"] = u"'%s' 를 포함한 표현식을 찾지 못했습니다." % term
else:
    # 탭 구분 텍스트로 만들어 데이터 테이블로 읽어들인다
    HEADERS = [u"페이지", u"시각화", u"유형", u"위치", u"표현식"]

    def clean(text):
        # 탭·줄바꿈은 구분자를 깨뜨리므로 공백으로 치환
        return (text or u"").replace(u"\t", u" ").replace(u"\r", u" ").replace(u"\n", u" ")

    stream = MemoryStream()
    writer = StreamWriter(stream, Encoding.UTF8)
    writer.WriteLine(u"\t".join(HEADERS))
    for record in records:
        writer.WriteLine(u"\t".join(clean(field) for field in record))
    writer.Flush()
    stream.Seek(0, SeekOrigin.Begin)

    settings = TextDataReaderSettings()
    settings.Separator = "\t"
    settings.AddColumnNameRow(0)
    for index in range(len(HEADERS)):
        settings.SetDataType(index, DataType.String)

    dataSource = TextFileDataSource(stream, settings)

    if Document.Data.Tables.Contains(TABLE_NAME):
        Document.Data.Tables[TABLE_NAME].ReplaceData(dataSource)
    else:
        Document.Data.Tables.Add(TABLE_NAME, dataSource)

    Document.Properties["ScriptLog"] = u"표현식 %d건을 '%s' 테이블로 정리했습니다." % (
        len(records), TABLE_NAME)
