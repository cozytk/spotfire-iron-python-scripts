# -*- coding: utf-8 -*-
# 테스트 4 — 데이터·마킹·필터 API 실측
#
# 위험도: 없음 (읽기만 함. 마킹과 필터를 변경하지 않음)
# 실행:   데이터 테이블이 하나 이상 있는 분석 파일에서 실행


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


def probe(label, fn):
    try:
        print "[OK]", label, "=", clean(fn())
    except Exception, e:
        print "[NO]", label, "->", clean(str(e))


print "=== 1. 데이터 테이블 ==="
for table in Document.Data.Tables:
    print "  -", clean(table.Name), "| 행:", table.RowCount, \
          "| 컬럼:", table.Columns.Count, \
          "| IsRefreshable:", table.IsRefreshable
    try:
        print "    NeedsRefresh:", table.NeedsRefresh
    except Exception, e:
        print "    [NO] NeedsRefresh ->", clean(str(e))

if Document.Data.Tables.Count == 0:
    print "  (데이터 테이블이 없습니다. 이후 항목은 건너뜁니다)"
else:
    table = Document.ActiveDataTableReference
    print ""
    print "기준 테이블:", clean(table.Name)

    print ""
    print "=== 2. 컬럼 ==="
    shown = 0
    for column in table.Columns:
        if shown >= 5:
            break
        print "  -", clean(column.Name), "|", clean(column.DataType), \
              "| IsNumeric:", column.DataType.IsNumeric
        shown += 1

    print ""
    print "=== 3. 커서로 값 읽기 ==="
    try:
        from Spotfire.Dxp.Data import DataValueCursor, IndexSet
        column = table.Columns[0]
        cursor = DataValueCursor.CreateFormatted(column)
        rows = IndexSet(table.RowCount, True)
        count = 0
        for row in table.GetRows(rows, cursor):
            count += 1
            if count <= 3:
                print "   값:", clean(cursor.CurrentValue)
            if count >= 3:
                break
        print "[OK] GetRows + DataValueCursor 동작"
    except Exception, e:
        print "[NO] GetRows ->", clean(str(e))

    print ""
    print "=== 4. GetDistinctRows ==="
    try:
        from Spotfire.Dxp.Data import DataValueCursor
        cursor = DataValueCursor.CreateFormatted(table.Columns[0])
        distinct = table.GetDistinctRows(None, cursor)
        distinct.Reset()
        n = 0
        while distinct.MoveNext():
            n += 1
            if n >= 200:
                break
        print "[OK] 고유값 개수(최대 200까지 셈):", n
    except Exception, e:
        print "[NO] GetDistinctRows ->", clean(str(e))

    print ""
    print "=== 5. 표현식으로 행 선택 (Select) ==="
    probe("table.Select 존재", lambda: hasattr(table, "Select"))

print ""
print "=== 6. 마킹 ==="
for marking in Document.Data.Markings:
    print "  - 이름:", clean(marking.Name)
probe("ActiveMarkingSelectionReference", lambda: Document.ActiveMarkingSelectionReference.Name)
probe("ActiveFilteringSelectionReference", lambda: Document.ActiveFilteringSelectionReference.Name)

print ""
print "=== 7. 필터링 스킴 ==="
count = 0
for scheme in Document.FilteringSchemes:
    count += 1
    try:
        print "  - 스킴:", clean(scheme.FilteringSelectionReference.Name), \
              "| ResetAllFilters:", hasattr(scheme, "ResetAllFilters")
    except Exception, e:
        print "  - [??] 스킴 정보 실패:", clean(str(e))
print "총 스킴 개수:", count

print ""
print "=== 8. scheme[table][column] 인덱싱 (교안 예제 18) ==="
try:
    scheme = Document.FilteringSchemes[0]
    table = Document.Data.Tables[0]
    column = table.Columns[0]
    columnFilter = scheme[table][column]
    print "[OK] 인덱싱 성공:", clean(columnFilter)
    print "     Reset 메서드:", hasattr(columnFilter, "Reset")
except Exception, e:
    print "[NO]", clean(str(e))

print ""
print "=== 9. 필터 패널 ==="
try:
    panel = Document.ActivePageReference.FilterPanel
    print "[OK] FilterPanel | Visible:", panel.Visible
    for group in panel.TableGroups:
        print "  테이블 그룹:", clean(group.FilterCollectionReference.DataTableReference.Name)
        n = 0
        for handle in group.FilterHandles:
            if n >= 5:
                break
            print "    -", clean(handle.FilterReference.Name), \
                  "|", clean(handle.FilterReference.TypeId), \
                  "| Visible:", handle.Visible
            n += 1
except Exception, e:
    print "[NO]", clean(str(e))
