# -*- coding: utf-8 -*-
# 테스트 3 — 서비스와 타입 존재 확인
#
# 목적:  교안에서 "버전에 따라 다를 수 있다"고 표시해 둔 API들을 실제로 확인
# 위험도: 없음 (목록 출력만. 알림 하나를 띄우는 부분은 주석 처리해 둠)
# 실행:   붙여넣고 [실행(Execute)] -> 출력 전체 복사


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


def members(obj, keyword=None):
    result = []
    for name in dir(obj):
        if name.startswith("_"):
            continue
        if keyword and keyword.lower() not in name.lower():
            continue
        result.append(name)
    return result


print "=== 1. NotificationService (교안 예제 13) ==="
try:
    from Spotfire.Dxp.Framework.ApplicationModel import NotificationService
    ns = Application.GetService[NotificationService]()
    print "[OK] 서비스 획득"
    for name in members(ns, "Notification"):
        print "   ", name
    # 실제로 알림을 띄워 보려면 아래 주석을 푸세요
    # ns.AddInformationNotification(u"테스트", u"동작 확인", u"")
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 2. ProgressService (교안 12장 팁) ==="
try:
    from Spotfire.Dxp.Framework.ApplicationModel import ProgressService
    ps = Application.GetService[ProgressService]()
    print "[OK] 서비스 획득"
    for name in members(ps):
        print "   ", name
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 3. DataWriterTypeIdentifiers (교안 예제 9) ==="
try:
    from Spotfire.Dxp.Data.Export import DataWriterTypeIdentifiers
    for name in members(DataWriterTypeIdentifiers):
        print "   [OK]", name
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 4. Data.Import 의 DataSource 목록 (교안 예제 10의 StdfDataSource) ==="
try:
    import Spotfire.Dxp.Data.Import as imp
    for name in members(imp, "DataSource"):
        print "   [OK]", name
    print "   --- Settings 계열 ---"
    for name in members(imp, "Settings"):
        print "   [OK]", name
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 5. TextDataReaderSettings 메서드 (교안 예제 20) ==="
try:
    from Spotfire.Dxp.Data.Import import TextDataReaderSettings
    settings = TextDataReaderSettings()
    print "[OK] 인스턴스 생성"
    for name in members(settings):
        print "   ", name
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 6. 현재 사용자 이름 (교안 예제 15 변형) ==="
try:
    from System.Threading import Thread
    print "[OK]", clean(Thread.CurrentPrincipal.Identity.Name)
except Exception, e:
    print "[NO]", clean(str(e))
