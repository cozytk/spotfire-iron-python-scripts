# -*- coding: utf-8 -*-
# 예제 18. 원하는 컬럼의 필터만 선택적으로 초기화
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-ui.html
# 이 파일은 content/10-examples-ui.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 지정한 컬럼의 필터만 모든 필터링 스킴에서 초기화한다.
#
# 매개변수:
#   columnList (String) 초기화할 컬럼 이름을 쉼표로 구분. 예: "Category,Region,Product"

from Spotfire.Dxp.Data import *
from Spotfire.Dxp.Application.Filters import *

targets = [name.strip() for name in (columnList or "").split(",") if name.strip()]

reset = []
missing = []

# 모든 필터링 스킴 × 모든 데이터 테이블 × 대상 컬럼
for filteringScheme in Document.FilteringSchemes:
    for dataTable in Document.Data.Tables:
        for column in dataTable.Columns:
            if column.Name not in targets:
                continue
            try:
                # 스킴에서 [테이블][컬럼] 으로 필터를 직접 꺼낸다
                columnFilter = filteringScheme[dataTable][column]
                columnFilter.Reset()
                reset.append(u"%s.%s" % (dataTable.Name, column.Name))
            except Exception, e:
                # 그 스킴/테이블에 해당 필터가 없는 경우
                missing.append(u"%s.%s" % (dataTable.Name, column.Name))

message = u"필터 초기화 %d건" % len(reset)
if reset:
    message += u" — " + u", ".join(sorted(set(reset)))
if missing:
    message += u" / 해당 없음 %d건" % len(set(missing))

Document.Properties["ScriptLog"] = message
