
import streamlit as st
import pandas as pd
import datetime
import fitz  # PyMuPDF
import io

# ---------------------------
# User Authentication
# ---------------------------
users = {
    "admin": "password123",
    "user": "timebudget"
}

def login():
    st.title("Time Budgeting App - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("Invalid username or password")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ---------------------------
# App Main Interface
# ---------------------------
st.title("⏳ Time Budgeting App")

# Monthly setup
today = datetime.date.today()
days_in_month = (datetime.date(today.year, today.month % 12 + 1, 1) - datetime.timedelta(days=1)).day
total_hours = st.number_input("Total hours in the month", value=24 * days_in_month)

# Budget setup
st.subheader("📊 Time Budget Setup")
if "budget_df" not in st.session_state:
    st.session_state["budget_df"] = pd.DataFrame(columns=["Category", "Planned Hours", "Actual Hours (Week 1)", "Actual Hours (Week 2)", "Actual Hours (Week 3)", "Actual Hours (Week 4)"])

with st.form("budget_form"):
    category = st.text_input("Category (e.g., Sleep, Work, Reading)")
    planned = st.number_input("Planned Hours", min_value=0.0, step=0.5)
    submitted = st.form_submit_button("Add Category")
    if submitted and category:
        new_row = {"Category": category, "Planned Hours": planned,
                   "Actual Hours (Week 1)": 0, "Actual Hours (Week 2)": 0,
                   "Actual Hours (Week 3)": 0, "Actual Hours (Week 4)": 0}
        st.session_state["budget_df"] = pd.concat([st.session_state["budget_df"], pd.DataFrame([new_row])], ignore_index=True)

# Display and edit table
st.data_editor(st.session_state["budget_df"], num_rows="dynamic", key="editor")

# Dashboard
st.subheader("📈 Dashboard")
df = st.session_state["budget_df"]
if not df.empty:
    df["Total Actual"] = df[[col for col in df.columns if "Actual Hours" in col]].sum(axis=1)
    df["Difference"] = df["Planned Hours"] - df["Total Actual"]
    st.bar_chart(df.set_index("Category")[["Planned Hours", "Total Actual"]])

# Export
st.subheader("📤 Export Report")
export_format = st.selectbox("Choose format", ["CSV", "PDF"])
if st.button("Download Report"):
    if export_format == "CSV":
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "time_budget_report.csv", "text/csv")
    else:
        pdf_buffer = io.BytesIO()
        doc = fitz.open()
        page = doc.new_page()
        text = df.to_string(index=False)
        page.insert_text((72, 72), text, fontsize=10)
        doc.save(pdf_buffer)
        st.download_button("Download PDF", pdf_buffer.getvalue(), "time_budget_report.pdf", "application/pdf")

# Calendar Integration (Simulated)
st.subheader("📅 Calendar Integration")
st.info("This section is a placeholder for future integration with Google Calendar or other tools.")
