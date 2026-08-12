# -*- coding: utf-8 -*-
# 사전 준비 · 문서 속성 만들기
#
# 예제를 실행하기 전에 이 스크립트를 한 번 실행하세요.
# 설명: https://cozytk.github.io/spotfire-iron-python-scripts/09-examples-visuals.html
# 이 파일은 content/09-examples-visuals.md 에서 자동 생성됩니다. 직접 수정하지 마세요.

# 교안 예제들이 사용하는 문서 속성을 한 번에 만든다.
# 이미 있는 속성은 그대로 두므로 여러 번 실행해도 안전하다.

from Spotfire.Dxp.Data import DataProperty, DataType, DataPropertyClass

# (속성 이름, 타입, 초기값, 쓰는 예제)
PROPERTIES = [
    ("ScriptLog",        DataType.String,  "",          u"모든 예제 공통 - 실행 결과 로그"),
    ("InventoryReport",  DataType.String,  "",          u"예제 18"),
    ("LimitExpression",  DataType.String,  "",          u"예제 1"),
    ("SelectedMeasure",  DataType.String,  "",          u"예제 2"),
    ("SelectedAgg",      DataType.String,  "Sum",       u"예제 2"),
    ("ShowLegend",       DataType.String,  "True",      u"예제 3"),
    ("ExportFolder",     DataType.String,  "C:/temp",   u"예제 14, 9"),
    ("SnapshotName",     DataType.String,  "Snapshot",  u"예제 16"),
    ("MarkedLabel",      DataType.String,  "",          u"예제 8"),
    ("MarkedInList",     DataType.String,  "",          u"예제 8"),
    ("MarkedCount",      DataType.Integer, 0,           u"예제 8"),
    ("UserRole",         DataType.String,  u"관리자",     u"예제 13"),
    ("VisibleFilters",   DataType.String,  "",          u"예제 12"),
    ("ChartType",        DataType.String,  "Bar",       u"예제 6"),
    ("ResetTargets",     DataType.String,  "",          u"예제 11"),
    ("AuditSearch",      DataType.String,  "",          u"예제 19"),
]


def property_exists(name):
    # Contains 시그니처는 버전에 따라 다를 수 있어, 목록을 훑는 방식이 안전하다
    for prop in Document.Data.Properties.GetProperties(DataPropertyClass.Document):
        if prop.Name == name:
            return True
    return False


created = []
existing = []
failed = []

for name, dataType, default, usedBy in PROPERTIES:
    if property_exists(name):
        existing.append(name)
        continue
    try:
        prototype = DataProperty.CreateCustomPrototype(
            name, dataType, DataProperty.DefaultAttributes)
        Document.Data.Properties.AddProperty(DataPropertyClass.Document, prototype)
        Document.Properties[name] = default
        created.append(name)
    except Exception, e:
        failed.append("%s: %s" % (name, str(e)))

print u"새로 만듦 (%d개): %s" % (len(created), u", ".join(created))
print u"이미 있음 (%d개): %s" % (len(existing), u", ".join(existing))
if failed:
    print u"실패 (%d개):" % len(failed)
    for message in failed:
        print u"   ", message
