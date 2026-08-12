# -*- coding: utf-8 -*-
# 예제 25. 축 눈금 서식 일괄 통일 (통화·천 단위·소수점)
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-visuals.html
# 이 파일은 content/09-examples-visuals.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 모든 차트의 Y축(산점도는 X축도) 숫자 서식을 통일한다.
#
# 매개변수:
#   decimals (String) 소수점 자릿수   예: "0"
#   useShort (String) "True" / "False"  축약 표기(1.2K) 사용 여부

from Spotfire.Dxp.Application.Visuals import VisualContent
from Spotfire.Dxp.Data import DataType
from Spotfire.Dxp.Data.Formatters import NumberFormatCategory

digits = int(decimals) if str(decimals).strip() else 0
shortForm = str(useShort).strip().lower() in ("true", "1", "y", "yes")


def make_formatter(dataType):
    """데이터 타입에 맞는 포매터를 만든다. 타입마다 별도 객체가 필요하다."""
    fmt = dataType.CreateLocalizedFormatter()
    fmt.Category = NumberFormatCategory.Number
    fmt.DecimalDigits = digits
    fmt.GroupSeparatorEnabled = True
    try:
        fmt.ShortFormattingEnabled = shortForm
    except:
        pass          # 버전에 따라 없을 수 있다
    return fmt


# 축의 실제 데이터 타입을 모르므로 숫자형 포매터를 전부 넣어 본다.
# 맞지 않는 속성은 실패하므로 try 로 감싼다. → 7.9 참조
FORMATTERS = [
    ("RealFormatter", DataType.Real),
    ("IntegerFormatter", DataType.Integer),
    ("LongIntegerFormatter", DataType.LongInteger),
    ("SingleRealFormatter", DataType.SingleReal),
    ("CurrencyFormatter", DataType.Currency),
]
AXES = ["YAxis", "XAxis"]

changed = 0
report = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
        except:
            continue

        touched = []
        for axisName in AXES:
            try:
                formatting = getattr(vc, axisName).Scale.Formatting
            except:
                continue                      # 그 축이 없는 유형

            for propName, dataType in FORMATTERS:
                try:
                    setattr(formatting, propName, make_formatter(dataType))
                    touched.append(u"%s.%s" % (axisName, propName))
                except:
                    pass                      # 그 타입이 아니면 조용히 넘어간다

        if touched:
            changed += 1
            report.append(u"%s — %s" % (visual.Title, u", ".join(touched)))

summary = u"서식 통일: 시각화 %d개\n%s" % (changed, u"\n".join(report))
Document.Properties["ScriptLog"] = summary
print summary
