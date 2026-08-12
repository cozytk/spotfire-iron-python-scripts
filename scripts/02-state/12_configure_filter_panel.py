# -*- coding: utf-8 -*-
# 예제 12. 역할별 필터 패널 구성
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-state.html
# 이 파일은 content/10-examples-state.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 지정한 필터만 남기고 모든 페이지의 필터 패널을 정리한다.
#
# 매개변수:
#   filterList (String) 보여 줄 컬럼 이름을 쉼표로 구분. 예: "Region,Year,Category"
#                       빈 문자열이면 전부 표시

wanted = [name.strip() for name in (filterList or "").split(",") if name.strip()]
showAll = (len(wanted) == 0)

shown, hidden = 0, 0

for page in Document.Pages:
    filterPanel = page.FilterPanel

    for tableGroup in filterPanel.TableGroups:
        tableGroup.Expanded = True

        # 최상위 필터
        for handle in tableGroup.FilterHandles:
            visible = showAll or (handle.FilterReference.Name in wanted)
            handle.Visible = visible
            if visible:
                shown += 1
            else:
                hidden += 1

        # 하위 그룹 안의 필터
        for subGroup in tableGroup.SubGroups:
            groupHasVisible = False
            for handle in subGroup.FilterHandles:
                visible = showAll or (handle.FilterReference.Name in wanted)
                handle.Visible = visible
                if visible:
                    shown += 1
                    groupHasVisible = True
                else:
                    hidden += 1
            subGroup.Visible = groupHasVisible or showAll

Document.Properties["ScriptLog"] = u"필터 표시 %d개 / 숨김 %d개" % (shown, hidden)
