# -*- coding: utf-8 -*-
# 예제 27. 마킹으로 대시보드 전체 좀혀보기 (포커스 모드)
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-state.html
# 이 파일은 content/10-examples-state.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 현재 활성 마킹을 "데이터 제한" 으로 모든 시각화에 걸거나 해제한다.
#
# 매개변수:
#   targetTable (DataTable) 대상 테이블
#   mode        (String)    "on" 이면 적용, 그 외에는 해제
#
# 주의: 제한을 건 시각화에서는 마킹을 풀면 화면이 비거나 전체로 돌아간다.
#       아래에서 LimitingMarkingsEmptyBehavior 로 그 동작을 정한다.

from Spotfire.Dxp.Application.Visuals import VisualContent, LimitingMarkingsEmptyBehavior

turnOn = str(mode).strip().lower() in ("on", "true", "1", "y", "yes")

# 마킹 이름을 하드코딩하지 않는다 → 7.1 참조
marking = Document.ActiveMarkingSelectionReference

changed, skipped = 0, 0
report = []

for page in Document.Pages:
    for visual in page.Visuals:
        try:
            vc = visual.As[VisualContent]()
            if vc.Data.DataTableReference != targetTable:
                continue
            filterings = vc.Data.Filterings
        except:
            skipped += 1
            continue

        # 이 시각화 자신이 마킹을 만드는 곳이면 건드리지 않는다.
        # 그렇지 않으면 마킹하는 순간 자기 자신이 사라진다.
        try:
            if vc.Data.MarkingReference == marking:
                report.append(u"%s — 마킹 원본이라 유지" % visual.Title)
                continue
        except:
            pass

        try:
            if turnOn:
                if not filterings.Contains(marking):
                    filterings.Add(marking)
                # 마킹이 비었을 때 전체를 보여 준다 (빈 화면보다 덜 당황스럽다)
                vc.Data.LimitingMarkingsEmptyBehavior = LimitingMarkingsEmptyBehavior.ShowAll
            else:
                if filterings.Contains(marking):
                    filterings.Remove(marking)
            changed += 1
            report.append(u"%s — %s" % (visual.Title, u"제한 적용" if turnOn else u"제한 해제"))
        except Exception, err:
            skipped += 1
            report.append(u"  ! %s : %s" % (visual.Title, err))

summary = u"포커스 모드 %s: %d개 변경, %d개 건너뜀\n%s" % (
    u"켬" if turnOn else u"끔", changed, skipped, u"\n".join(report))
Document.Properties["ScriptLog"] = summary
print summary
