# 오류 수정 요청 템플릿

스크립트가 실패했을 때 쓰는 형식입니다. **오류 메시지를 그대로** 주는 것이 핵심입니다.

---

```text
아래 Spotfire IronPython 스크립트에서 오류가 났어. 수정해 줘.

[오류 메시지]
(대화상자에 나온 내용을 그대로. 스택 트레이스가 있으면 그것도)

[실행한 코드]
(전체 코드)

[실제 속성 목록]
(아래 코드를 실행해서 얻은 결과를 붙여넣기)
```

---

## 함께 주면 결정적인 정보

AI는 실제 속성 이름을 모릅니다. **목록을 주면 그중에서 고릅니다.**

```python
# 객체가 실제로 가진 멤버 확인
DOTNET_BASE = ["Equals", "GetHashCode", "GetType", "MemberwiseClone",
               "ReferenceEquals", "ToString"]

target = viz.As[VisualContent]()          # 확인하고 싶은 객체로 바꾸세요
for name in dir(target):
    if not name.startswith("_") and name not in DOTNET_BASE:
        print name
```

메서드라면 시그니처까지 볼 수 있습니다.

```python
print Document.Data.CreateDataWriter.__doc__
# CreateDataWriter(self: DataManager, typeId: TypeIdentifier) -> DataWriter
```

## 오류별 원인 지도

| 오류 메시지 | 원인 | 먼저 확인할 것 |
|-------------|------|----------------|
| `NameError: name 'X' is not defined` | import 누락 | 그 타입의 `import` 문이 있나 |
| `AttributeError: ... has no attribute` | 없는 API를 지어냄 | `dir()` 로 실제 이름 확인 |
| `'NoneType' object has no attribute` | 대상을 못 찾음, 또는 API가 `None` 반환 | 반환값을 `print` 해 볼 것 |
| `expected str, got int` | 컬렉션 인덱싱 방식 | `Document.Data.Tables` 는 숫자 인덱스 불가 |
| `unexpected token '='` | `print(..., end="")` 등 | Python 2 방식으로 바꾸거나 `__future__` |
| `SyntaxError` (f-string 등) | Python 3 문법 | Python 2.7 문법으로 |
| `unexpected indent` | 탭/공백 혼용 | 편집기에서 직접 수정 (AI로는 잘 안 고쳐짐) |
| 실행은 되는데 변화 없음 | 조건이 아무것도 매칭 안 함 | 대상만 출력해 보기 (아래) |
| 일부 시각화에서만 실패 | 유형별 속성 차이 | `try/except` 로 감싸고 실패 목록 보고 |

## 아무 일도 안 일어날 때

**무엇이 대상인지부터** 확인하세요. 여기서 걸러지는 실수가 가장 많습니다.

```python
for page in Document.Pages:
    for visual in page.Visuals:
        print page.Title, "|", visual.Title, "|", visual.TypeId
```
