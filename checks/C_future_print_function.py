# -*- coding: utf-8 -*-
# 테스트 C — __future__ 로 print 를 함수로 바꿀 수 있나?
#
# 주의: 테스트 A, B 와 따로, 이것만 붙여 넣고 실행하세요.
#
# 실행 방법:
#   붙여 넣고 [실행(Execute)] -> 출력 또는 오류 메시지를 알려 주세요.

from __future__ import print_function

print("a", "b", sep="-")

# 성공하면: a-b
#   -> IronPython 2.7 이 print_function 을 지원함
#   -> 원하면 Python 3 스타일 print 를 쓸 수 있다고 교안에 안내 가능
#
# 실패하면: SyntaxError 또는 ImportError
#   -> 이 방법은 쓸 수 없음
