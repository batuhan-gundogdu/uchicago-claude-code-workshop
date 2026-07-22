from xlsx_to_json import build_budget

def test_totals_match_spreadsheet():
    b = build_budget("budget_fake.xlsx")
    # Line structure
    ids = {l["id"] for l in b["settings"]["lines"]}
    assert "car_expenses" in ids and "car_loan" in ids
    assert len(b["settings"]["lines"]) == 17
    # Grocery entries capture every numeric cell under a month column,
    # including cells the spreadsheet's own SUM() range happened to skip.
    jan_entries = [e for e in b["entries"]
                   if e["line"] == "groceries" and e["date"].startswith("2026-01")]
    mar_entries = [e for e in b["entries"]
                   if e["line"] == "groceries" and e["date"].startswith("2026-03")]
    assert any(abs(e["amount"] - 65.06) < 0.01 for e in jan_entries)
    assert any(abs(e["amount"] - 42.20) < 0.01 for e in mar_entries)
    jan_groc = sum(e["amount"] for e in jan_entries)
    assert abs(jan_groc - 1197.78) < 0.01
    # Home expenses November total (813.1462)
    nov_home = sum(e["amount"] for e in b["entries"]
                   if e["line"] == "home_expenses" and e["date"].startswith("2025-11"))
    assert abs(nov_home - 813.1462) < 0.01
    # Funds ledger has the house-sale one-off
    assert any(abs(f["amount"] - 157100) < 0.01 for f in b["fundsLedger"])
