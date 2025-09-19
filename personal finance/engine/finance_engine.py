def compute_summary(income, expenses):
    """
    Compute budget summary.
    income: int/float
    expenses: dict(category -> amount)
    """
    total_expenses = sum(expenses.values())
    savings = income - total_expenses
    savings_rate = (savings / income * 100) if income > 0 else 0

    expense_pct = {}
    for cat, amt in expenses.items():
        expense_pct[cat] = round((amt / total_expenses * 100), 2) if total_expenses > 0 else 0

    return {
        "income": income,
        "total_expenses": total_expenses,
        "savings": savings,
        "savings_rate": round(savings_rate, 2),
        "expense_pct": expense_pct
    }


def generate_insights(summary):
    """
    Generate basic rule-based insights from summary.
    """
    insights = []

    if summary["savings_rate"] < 10:
        insights.append("💡 Savings rate <10%. Automate 5–10% savings monthly.")

    for cat, pct in summary["expense_pct"].items():
        if cat == "entertainment" and pct > 20:
            insights.append("⚠️ Entertainment spend is high. Limit takeout/streaming.")
        if cat == "food" and pct > 30:
            insights.append("🍽️ Food spend is heavy. Plan meals & reduce outside dining.")

    if not insights:
        insights.append("✅ Your spending looks balanced. Keep tracking regularly!")

    return insights
