# 프롬프트 모음

생성형 AI에게 Spotfire IronPython 스크립트를 요청할 때 쓰는 파일들입니다.
ChatGPT, Claude, Copilot 어디에나 그대로 붙여 넣으면 됩니다.

| 파일 | 언제 쓰나 |
|------|-----------|
| [`00-context.md`](00-context.md) | **항상 먼저.** 환경 제약과 Spotfire 함정을 알려 주는 블록 |
| [`01-request-template.md`](01-request-template.md) | 새 스크립트를 요청할 때 |
| [`02-debug-template.md`](02-debug-template.md) | 오류가 났을 때 |
| [`03-verify-checklist.md`](03-verify-checklist.md) | 받은 코드를 실행하기 전에 |

## 기본 사용 순서

```text
① 00-context.md 의 코드 블록을 대화창에 붙여넣기
② 01-request-template.md 를 채워서 요청
   + scripts/ 에서 가장 비슷한 예제를 재료로 함께 붙여넣기
③ 03-verify-checklist.md 로 받은 코드 검증
④ 사본에서 실행
⑤ 오류가 나면 02-debug-template.md 형식으로 되돌려주기
```

## Claude Code를 쓴다면

이 저장소에 [`.claude/skills/spotfire-ironpython/`](../.claude/skills/spotfire-ironpython)
스킬이 들어 있습니다. 위 내용이 자동으로 적용되므로 프롬프트를 붙여 넣을 필요가 없습니다.

```bash
# 이 저장소에서 작업하면 자동으로 인식됩니다.
# 어디서나 쓰려면 개인 스킬 폴더로 복사하세요.
cp -r .claude/skills/spotfire-ironpython ~/.claude/skills/
```

## 왜 이런 게 필요한가

Spotfire IronPython은 AI 학습 데이터가 적은 분야입니다.
그냥 물어보면 **Python 3 문법**을 쓰거나 **존재하지 않는 API**를 자신 있게 만들어 냅니다.

이 교안의 예제 초안도 AI가 작성했고, 실제로 돌려 보니 존재하지 않는 API를 네 개 쓰고
있었습니다. 자세한 내용은 교안
[7장 · 스크립팅의 현실](https://cozytk.github.io/spotfire-iron-python-scripts/07-pitfalls.html)
에 있습니다.
