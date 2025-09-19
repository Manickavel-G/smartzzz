import pytest
from engine.finance_engine import compute_summary, generate_insights

def test_summary_basic():
    income = 30000
    expenses = {"rent": 10000, "food": 5000}
    summary = compute_summary(income, expenses)
    assert summary["total_expenses"] == 15000
    assert summary["savings"] == 15000
    assert summary["savings_rate"] == 50.0

def test_insights_low_savings():
    summary = {"savings_rate": 5, "expense_pct": {"entertainment": 10, "food": 20}}
    tips = generate_insights(summary)
    assert any("Savings rate" in tip for tip in tips)
