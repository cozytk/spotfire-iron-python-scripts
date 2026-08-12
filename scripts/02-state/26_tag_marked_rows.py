# -*- coding: utf-8 -*-
# 예제 26. 마킹한 행에 태그 붙이기 (검토 결과 남기기)
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-state.html
# 이 파일은 content/10-examples-state.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 현재 마킹된 행에 지정한 태그를 붙인다.
#
# 매개변수:
#   sourceTable   (DataTable) 대상 테이블
#   tagColumnName (String)    태그 컬럼 이름
#   tagValue      (String)    붙일 태그 값
#
# 사전 준비: 대상 테이블에 태그 컬럼이 이미 있어야 한다.

from Spotfire.Dxp.Data import TagsColumn

# 1) 태그 컬럼이 있는지 먼저 확인한다 (없으면 캐스팅이 터진다)
if not sourceTable.Columns.Contains(tagColumnName):
    Document.Properties["ScriptLog"] = u"태그 컬럼 '%s' 이 없습니다. 데이터 > 태그 추가로 먼저 만드세요." % tagColumnName
else:
    column = sourceTable.Columns[tagColumnName]
    try:
        tagColumn = column.As[TagsColumn]()
    except:
        tagColumn = None

    if tagColumn is None:
        Document.Properties["ScriptLog"] = u"'%s' 은 태그 컬럼이 아닙니다." % tagColumnName
    else:
        # 2) 마킹 이름을 하드코딩하지 않는다 — 한국어 UI에서는 "마킹" → 7.1 참조
        marking = Document.ActiveMarkingSelectionReference
        selection = marking.GetSelection(sourceTable)
        markedCount = selection.AsIndexSet().Count

        if markedCount == 0:
            Document.Properties["ScriptLog"] = u"마킹된 행이 없습니다. 먼저 마킹하세요."
        else:
            # 3) 마킹된 행에만 태그를 붙인다
            tagColumn.Tag(tagValue, selection)

            Document.Properties["ScriptLog"] = u"'%s' 태그를 %d행에 적용했습니다." % (
                tagValue, markedCount)

print Document.Properties["ScriptLog"]
