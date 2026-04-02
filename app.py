import streamlit as st
import pandas as pd
import os
import time
import datetime

st.set_page_config(page_title="Telsica KYC System", layout="wide")

# ---------- FILE SETUP ----------
data_file = "kyc_data.csv"

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Name","Address","Aadhar","PAN","Document","Status","Date"])
    df.to_csv(data_file, index=False)

df = pd.read_csv(data_file)

# ---------- SESSION ----------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ======================================================
# 🌐 CUSTOMER KYC FORM (NO LOGIN)
# ======================================================

st.title("🧾 Telsica KYC Submission Portal")

name = st.text_input("Full Name")
address = st.text_input("Address")
aadhar = st.text_input("Aadhar Number")
pan = st.text_input("PAN Number")
document = st.file_uploader("Upload Document")

if st.button("Submit KYC"):
    if name and address and aadhar and pan:

        filename = ""

        if document:
            if not os.path.exists("uploads"):
                os.makedirs("uploads")

            filename = str(int(time.time())) + "_" + document.name
            filepath = os.path.join("uploads", filename)

            with open(filepath, "wb") as f:
                f.write(document.read())

        date = datetime.date.today()

        new_data = pd.DataFrame(
            [[name, address, aadhar, pan, filename, "Pending", date]],
            columns=["Name","Address","Aadhar","PAN","Document","Status","Date"]
        )

        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(data_file, index=False)

        st.success("✅ KYC Submitted Successfully!")

    else:
        st.warning("Please fill all fields")

st.markdown("---")

# ======================================================
# 🔐 ADMIN LOGIN (SIDEBAR)
# ======================================================

st.sidebar.title("Admin Panel")

if not st.session_state.admin_logged_in:
    admin_user = st.sidebar.text_input("Username")
    admin_pass = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        if admin_user == "admin" and admin_pass == "1234":
            st.session_state.admin_logged_in = True
            st.sidebar.success("Logged in successfully")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")

# ======================================================
# 🧑‍💼 ADMIN PANEL (AFTER LOGIN)
# ======================================================

if st.session_state.admin_logged_in:

    # 🔴 Logout Button
    if st.sidebar.button("Logout"):
        st.session_state.admin_logged_in = False
        st.sidebar.success("Logged out")
        st.rerun()

    menu = st.sidebar.radio("Menu", ["Dashboard", "Verify KYC", "Analysis"])

    if menu == "Dashboard":
        st.subheader("📊 Dashboard")

        total = len(df)
        approved = len(df[df["Status"]=="Approved"])
        pending = len(df[df["Status"]=="Pending"])
        rejected = len(df[df["Status"]=="Rejected"])

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Total", total)
        c2.metric("Approved", approved)
        c3.metric("Pending", pending)
        c4.metric("Rejected", rejected)

        st.bar_chart(df["Status"].value_counts())

    elif menu == "Verify KYC":
        st.subheader("✅ Verify KYC")

        for i in range(len(df)):
            c1,c2,c3,c4,c5,c6 = st.columns(6)

            c1.write(df.iloc[i]["Name"])
            c2.write(df.iloc[i]["Aadhar"])
            c3.write(df.iloc[i]["PAN"])
            c4.write(df.iloc[i]["Status"])

            if c5.button("Approve", key=f"a{i}"):
                df.loc[df.index[i], "Status"] = "Approved"
                df.to_csv(data_file, index=False)
                st.rerun()

            if c6.button("Reject", key=f"r{i}"):
                df.loc[df.index[i], "Status"] = "Rejected"
                df.to_csv(data_file, index=False)
                st.rerun()

    elif menu == "Analysis":
        st.subheader("📊 Analysis")

        df["Date"] = pd.to_datetime(df["Date"])

        df["Risk"] = df["Status"].apply(lambda x:
            "Low" if x=="Approved" else "Medium" if x=="Pending" else "High"
        )

        st.bar_chart(df["Risk"].value_counts())

        trend = df.groupby("Date").size()
        st.line_chart(trend)

        st.download_button("Download CSV", df.to_csv(index=False), "kyc_data.csv")
