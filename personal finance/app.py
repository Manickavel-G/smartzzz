import streamlit as st
import pandas as pd
import plotly.express as px
import json
from engine.finance_engine import compute_summary, generate_insights
from engine.nlp import classify_intent
from engine.generator import generate_response
import os
from engine.db import init_db, insert_chat_log, save_user, save_expenses, load_user, load_expenses


st.set_page_config(page_title="Personal Finance Chatbot", layout="wide")
st.title("💬 Personal Finance Chatbot — Demo")

# Initialize database
init_db()

categories = ["rent", "food", "transport", "entertainment", "others"]

# Callback functions for saving/loading data
def on_user_change():
    user_data = load_user(st.session_state.user_name)
    if user_data:
        st.session_state.user_type = user_data["type"]
        st.session_state.income = user_data["income"]
    else:
        st.session_state.user_type = "student"
        st.session_state.income = 30000
    expenses_data = load_expenses(st.session_state.user_name)
    for cat in categories:
        st.session_state[cat] = expenses_data.get(cat, 0)

def save_user_callback():
    save_user(st.session_state.user_name, st.session_state.user_type, st.session_state.income)

def save_expenses_callback():
    expenses_dict = {cat: st.session_state[cat] for cat in categories}
    save_expenses(st.session_state.user_name, expenses_dict)

# Sidebar user profile
st.sidebar.header("👤 Profile")
user_name = st.sidebar.text_input("Your Name", "Alex", key="user_name", on_change=on_user_change)
user_type = st.sidebar.radio("User Type", ["student", "professional"], key="user_type", on_change=save_user_callback)
income = st.sidebar.number_input("Monthly Income (₹)", min_value=0, value=30000, key="income", on_change=save_user_callback)

# Expenses input
st.sidebar.subheader("Expenses")
expenses = {}
for cat in categories:
    expenses[cat] = st.sidebar.number_input(f"{cat.title()} (₹)", min_value=0, value=0, key=cat, on_change=save_expenses_callback)

# Session state for chat
if "history" not in st.session_state:
    st.session_state.history = []

# Chat UI
st.subheader("💬 Chat with your Finance Bot")
user_msg = st.text_input("Type your message:")

if st.button("Send") and user_msg:
    intent = classify_intent(user_msg)
    summary = compute_summary(income, expenses)

    # Check if IBM Granite usage is enabled
    use_granite = os.getenv("USE_GRANITE", "false").lower() == "true"

    reply = generate_response(user_type, intent["intent"], summary, user_msg)

    st.session_state.history.append((user_msg, reply))

    # Insert conversation into database
    insert_chat_log(user_name, user_type, user_msg, intent["intent"], reply)

# Display conversation
for user, bot in st.session_state.history:
    st.markdown(f"**🧑 You:** {user}")
    st.markdown(f"**🤖 Bot:** {bot}")

# Budget summary section
st.subheader("📊 Budget Summary")
summary = compute_summary(income, expenses)
insights = generate_insights(summary)

col1, col2 = st.columns(2)

with col1:
    st.metric("Monthly Savings (₹)", summary["savings"])
    st.metric("Savings Rate", f"{summary['savings_rate']}%")

with col2:
    df = pd.DataFrame({"Category": summary["expense_pct"].keys(),
                       "Percent": summary["expense_pct"].values()})
    fig = px.pie(df, names="Category", values="Percent", title="Expense Breakdown")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Detailed Expense Breakdown")
    st.dataframe(df)

st.markdown("### Insights")
for tip in insights:
    st.write("- " + tip)
