# -*- coding: utf-8 -*-
# 테스트 A — IronPython 런타임 동작 확인
#
# 실행 방법:
#   Spotfire 스크립트 편집 창에 붙여 넣고 [실행(Execute)] 을 누른 뒤,
#   하단 출력 영역의 내용을 그대로 알려 주세요.
#
# 이 스크립트는 문서를 전혀 변경하지 않습니다. (출력만 함)

import sys

print "1) 엔진 버전:", sys.version

print ""
print "2) print 인자 1개 ---"
print("hello")
#    기대: hello

print ""
print "3) print 인자 2개 ---"
print("a", "b")
#    ('a', 'b') 가 나오면  -> print 는 문(statement). 괄호는 그냥 묶음일 뿐
#    a b        가 나오면  -> print 가 함수로 동작 중

print ""
print "4) 정수 나눗셈:", 3 / 4
#    기대: 0   (0.75 가 나오면 Python 3 방식으로 동작하는 것)

print ""
print "5) 한글 문자열 타입:", type(u"한글")
print "6) 일반 문자열 타입:", type("한글")

print ""
print "7) __builtin__ 에 print 함수가 있나:",
try:
    import __builtin__
    print hasattr(__builtin__, "print")
except Exception, e:
    print "확인 실패:", str(e)
