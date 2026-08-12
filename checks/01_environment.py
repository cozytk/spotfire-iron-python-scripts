# -*- coding: utf-8 -*-
# 테스트 1 — 실행 환경과 표준 라이브러리
#
# 위험도: 없음 (출력만 함. 문서를 전혀 변경하지 않음)
# 실행:   스크립트 편집 창에 붙여넣고 [실행(Execute)] -> 출력 전체를 복사

from __future__ import division      # 이 줄이 오류면 division 미지원

import sys


def show(label, value):
    print label, str(value).replace("<", "[").replace(">", "]")


def probe(label, fn):
    try:
        show("[OK] " + label + ":", fn())
    except Exception, e:
        show("[NO] " + label + ":", str(e))


print "=== 1. 엔진 ==="
show("버전:", sys.version)
show("플랫폼:", sys.platform)

print ""
print "=== 2. __future__ division ==="
# 위에서 import 했으므로 3/4 가 0.75 여야 한다
show("3 / 4  =", 3 / 4)
show("3 // 4 =", 3 // 4)
print "  -> 0.75 / 0 이면 division 지원. 0 / 0 이면 미지원"

print ""
print "=== 3. 문자열 타입 (1차에서 확인 못한 항목) ==="
show("type(u'한글') =", type(u"한글"))
show("type('한글')  =", type("한글"))
show("len(u'한글')  =", len(u"한글"))
show("len('한글')   =", len("한글"))

print ""
print "=== 4. 표준 라이브러리 import 가능 여부 ==="
for name in ["re", "math", "datetime", "json", "csv", "collections",
             "itertools", "os", "codecs", "random", "time", "string"]:
    try:
        __import__(name)
        print "[OK]", name
    except Exception, e:
        show("[NO] " + name + ":", str(e))

print ""
print "=== 5. .NET 접근 ==="
try:
    import clr
    print "[OK] import clr"
except Exception, e:
    show("[NO] import clr:", str(e))

try:
    from System.IO import Path
    show("[OK] System.IO.Path.GetTempPath():", Path.GetTempPath())
except Exception, e:
    show("[NO] System.IO.Path:", str(e))

try:
    from System import DateTime
    show("[OK] System.DateTime.Now:", DateTime.Now)
except Exception, e:
    show("[NO] System.DateTime:", str(e))

try:
    from System.Collections.Generic import List
    items = List[str]()
    items.Add("a")
    show("[OK] List[str] (교안 예제 11 변형):", items.Count)
except Exception, e:
    show("[NO] List[str]:", str(e))

print ""
print "=== 6. 미리 정의된 객체 ==="
probe("Document.Pages.Count", lambda: Document.Pages.Count)
probe("Document.Data.Tables.Count", lambda: Document.Data.Tables.Count)
probe("Application (형식)", lambda: type(Application))
