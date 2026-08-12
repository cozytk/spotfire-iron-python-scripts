# -*- coding: utf-8 -*-
# 예제 13. 문서 속성 값으로 페이지 표시/숨김
#
# 설명과 검증 포인트: https://cozytk.github.io/spotfire-iron-python-scripts/10-examples-state.html
# 이 파일은 content/10-examples-state.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 역할에 따라 페이지를 보이거나 숨긴다.
#
# 매개변수:
#   role (String) 문서 속성 "UserRole" 의 값

# 역할별로 보여 줄 페이지 제목 목록
VISIBLE_PAGES = {
    u"영업":   [u"요약", u"매출 상세", u"지역 분석"],
    u"재무":   [u"요약", u"손익", u"원가 분석", u"예산 대비"],
    u"관리자": None,      # None 이면 전부 표시
}

allowed = VISIBLE_PAGES.get(role, [u"요약"])     # 모르는 역할은 요약만

shown, hidden = [], []

for page in Document.Pages:
    visible = (allowed is None) or (page.Title in allowed)
    try:
        page.Visible = visible
        (shown if visible else hidden).append(page.Title)
    except:
        pass

# 현재 페이지가 숨겨졌다면 보이는 첫 페이지로 이동
if not Document.ActivePageReference.Visible:
    for page in Document.Pages:
        if page.Visible:
            Document.ActivePageReference = page
            break

Document.Properties["ScriptLog"] = u"[%s] 표시 %d개 / 숨김 %d개" % (
    role, len(shown), len(hidden))
