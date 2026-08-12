# -*- coding: utf-8 -*-
# 테스트 11 — 예제 10 최종 확인 (마지막입니다)
#
# 확인할 것 하나:
#   DataTableDataSource(table, 마킹) 으로 만든 테이블이
#     (A) 마킹 시점에 고정되는가        -> 진짜 스냅샷
#     (B) 마킹이 바뀌면 따라 바뀌는가    -> 실시간 뷰
#   둘 다 유용하지만 교안에서 설명하는 방식이 달라집니다.
#
# 이 스크립트가 마킹을 직접 설정하므로 미리 마킹해 두실 필요 없습니다.
#
# 위험도: 중간 — 다음을 건드립니다
#   - 활성 마킹을 바꿉니다 (끝나면 원래 상태로 되돌립니다)
#   - 임시 테이블 __SNAPSHOT_TEST__ 를 만들었다 지웁니다
#   반드시 사본에서 실행하세요.

TEMP_TABLE = "__SNAPSHOT_TEST__"

from Spotfire.Dxp.Data import IndexSet, RowSelection
from Spotfire.Dxp.Data.Import import DataTableDataSource


def clean(value):
    return str(value).replace("<", "[").replace(">", "]")


table = Document.ActiveDataTableReference
marking = Document.ActiveMarkingSelectionReference

print "기준 테이블:", clean(table.Name), "| 전체 행", table.RowCount
print "사용 마킹  :", clean(marking.Name)

if table.RowCount < 20:
    print "[NO] 행이 너무 적습니다. 20행 이상인 테이블이 활성 상태여야 합니다."
else:
    # 원래 마킹을 저장해 둔다
    originalRows = marking.GetSelection(table).AsIndexSet()
    print "원래 마킹된 행 수:", originalRows.Count

    def mark(count):
        """앞에서부터 count 개 행을 마킹한다."""
        selected = IndexSet(table.RowCount, False)
        for i in range(count):
            selected.AddIndex(i)
        marking.SetSelection(RowSelection(selected), table)
        return marking.GetSelection(table).AsIndexSet().Count

    try:
        # 1) 10행 마킹 후 테이블 생성
        print ""
        print "=== 1. 10행 마킹 후 테이블 생성 ==="
        n1 = mark(10)
        print "  마킹된 행 수:", n1

        if Document.Data.Tables.Contains(TEMP_TABLE):
            Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])

        source = DataTableDataSource(table, marking)
        newTable = Document.Data.Tables.Add(TEMP_TABLE, source)
        rowsAfterCreate = newTable.RowCount

        print "  새 테이블 행 수:", rowsAfterCreate
        if rowsAfterCreate == n1:
            print "  [OK] 마킹된 행만 들어왔습니다 (부분집합 적용됨)"
        elif rowsAfterCreate == table.RowCount:
            print "  [NO] 전체가 복사되었습니다 (부분집합 미적용)"
        else:
            print "  [??] 예상과 다른 행 수입니다"

        # 2) 마킹을 20행으로 늘린 뒤 새 테이블이 따라 바뀌는지 본다
        print ""
        print "=== 2. 마킹을 20행으로 바꾼 뒤 관찰 ==="
        n2 = mark(20)
        print "  마킹된 행 수:", n2

        rowsAfterChange = Document.Data.Tables[TEMP_TABLE].RowCount
        print "  새 테이블 행 수:", rowsAfterChange

        print ""
        print "=== 결론 ==="
        if rowsAfterChange == rowsAfterCreate:
            print "  (A) 스냅샷 — 생성 시점에 고정됩니다"
            print "      마킹을 바꿔도 테이블이 변하지 않았습니다"
        elif rowsAfterChange == n2:
            print "  (B) 실시간 뷰 — 마킹을 따라 바뀝니다"
            print "      진짜 스냅샷이 필요하면 별도 처리가 필요합니다"
        else:
            print "  (??) 판단 보류 — 생성 후", rowsAfterCreate, "-> 변경 후", rowsAfterChange

        # 3) 새로고침하면 달라지는지도 확인
        print ""
        print "=== 3. Refresh 후에는 어떤가 ==="
        try:
            temp = Document.Data.Tables[TEMP_TABLE]
            if temp.IsRefreshable:
                temp.Refresh()
                print "  Refresh 후 행 수:", temp.RowCount
            else:
                print "  IsRefreshable = False (새로고침 불가)"
        except Exception, e:
            print "  [NO] Refresh ->", clean(str(e))

    except Exception, e:
        print "[NO] 시험 중 오류 ->", clean(str(e))

    finally:
        # 임시 테이블 삭제
        try:
            if Document.Data.Tables.Contains(TEMP_TABLE):
                Document.Data.Tables.Remove(Document.Data.Tables[TEMP_TABLE])
                print ""
                print "[OK] 임시 테이블 삭제 완료"
        except Exception, e:
            print "[NO] 임시 테이블 삭제 실패 - '" + TEMP_TABLE + "' 을 직접 지워 주세요:", clean(str(e))

        # 마킹 원상 복구
        try:
            marking.SetSelection(RowSelection(originalRows), table)
            print "[OK] 마킹을 원래 상태로 되돌렸습니다 (%d행)" % (
                marking.GetSelection(table).AsIndexSet().Count)
        except Exception, e:
            print "[NO] 마킹 복구 실패:", clean(str(e))
