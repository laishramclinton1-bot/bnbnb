import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Bond Interest Calculator", layout="wide")

st.title("📊 Bond Interest & Cashflow Calculator (ISIN आधारित)")

st.markdown("Enter bond details to calculate expected coupon payments and schedule.")

# -----------------------------
# Helper Function
# -----------------------------
def generate_cashflows(isin, face_value, coupon_rate, issue_date, maturity_date, frequency):
    payments = []
    
    if frequency == "Annual":
        delta = relativedelta(years=1)
        periods_per_year = 1
    elif frequency == "Semi-Annual":
        delta = relativedelta(months=6)
        periods_per_year = 2
    else:
        return []

    coupon_payment = (face_value * coupon_rate / 100) / periods_per_year

    payment_date = issue_date + delta

    while payment_date <= maturity_date:
        payments.append({
            "ISIN": isin,
            "Payment Date": payment_date,
            "Coupon Payment": round(coupon_payment, 2)
        })
        payment_date += delta

    return payments

# -----------------------------
# Input Section
# -----------------------------
st.sidebar.header("➕ Add Bond")

isin = st.sidebar.text_input("ISIN")
face_value = st.sidebar.number_input("Face Value", value=1000)
coupon_rate = st.sidebar.number_input("Coupon Rate (%)", value=7.5)
issue_date = st.sidebar.date_input("Issue Date")
maturity_date = st.sidebar.date_input("Maturity Date")
frequency = st.sidebar.selectbox("Payment Frequency", ["Annual", "Semi-Annual"])

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

if st.sidebar.button("Add Bond"):
    if isin and issue_date < maturity_date:
        st.session_state.portfolio.append({
            "ISIN": isin,
            "Face Value": face_value,
            "Coupon Rate": coupon_rate,
            "Issue Date": issue_date,
            "Maturity Date": maturity_date,
            "Frequency": frequency
        })
        st.success(f"Bond {isin} added!")
    else:
        st.error("Invalid input!")

# -----------------------------
# Display Portfolio
# -----------------------------
if st.session_state.portfolio:
    st.subheader("📁 Bond Portfolio")

    df_portfolio = pd.DataFrame(st.session_state.portfolio)
    st.dataframe(df_portfolio)

    all_cashflows = []

    for bond in st.session_state.portfolio:
        flows = generate_cashflows(
            bond["ISIN"],
            bond["Face Value"],
            bond["Coupon Rate"],
            bond["Issue Date"],
            bond["Maturity Date"],
            bond["Frequency"]
        )
        all_cashflows.extend(flows)

    if all_cashflows:
        df_cashflows = pd.DataFrame(all_cashflows)
        df_cashflows.sort_values(by="Payment Date", inplace=True)

        st.subheader("📅 Cashflow Schedule")
        st.dataframe(df_cashflows)

        total_interest = df_cashflows["Coupon Payment"].sum()
        st.metric("💰 Total Expected Interest", f"{total_interest:,.2f}")

        # Download option
        csv = df_cashflows.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Cashflows CSV",
            csv,
            "bond_cashflows.csv",
            "text/csv"
        )

else:
    st.info("Add bonds from the sidebar to begin.")
