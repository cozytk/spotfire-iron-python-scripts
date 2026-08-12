# -*- coding: utf-8 -*-
# 예제 17. 모든 데이터 테이블 일괄 새로고침
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/11-examples-data.html
# 이 파일은 content/11-examples-data.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 새로고침 가능한 모든 데이터 테이블을 새로고침하고 결과를 알린다.

from Spotfire.Dxp.Framework.ApplicationModel import NotificationService

refreshed = []
skipped = []
failed = []

for table in Document.Data.Tables:
    try:
        if not table.IsRefreshable:
            skipped.append(u"%s (새로고침 불가)" % table.Name)
            continue

        # NeedsRefresh 검사를 빼면 항상 강제로 새로고침한다
        table.Refresh()
        refreshed.append(table.Name)
    except Exception, e:
        failed.append(u"%s: %s" % (table.Name, str(e)))

summary = u"새로고침 %d개" % len(refreshed)
if refreshed:
    summary += u" — " + u", ".join(refreshed)
if failed:
    summary += u" / 실패 %d개" % len(failed)

Document.Properties["ScriptLog"] = summary

# 사용자에게 알림 (Web Player에서도 동작)
ns = Application.GetService[NotificationService]()
if failed:
    ns.AddWarningNotification(u"데이터 새로고침", summary, u"\n".join(failed))
else:
    ns.AddInformationNotification(u"데이터 새로고침", summary, u"")
