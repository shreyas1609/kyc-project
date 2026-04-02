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

# ======================================================
# 🌐 DIRECT KYC FORM (NO LOGIN)
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
# 🔐 ADMIN PANEL (OPTIONAL)
# ======================================================

st.sidebar.title("Admin Login")

admin_user = st.sidebar.text_input("Username")
admin_pass = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if admin_user == "admin" and admin_pass == "1234":

        st.sidebar.success("Logged in")

        menu = st.sidebar.radio("Menu", ["Dashboard", "Verify KYC"])

        if menu == "Dashboard":
            st.subheader("📊 Dashboard")

            total = len(df)
            approved = len(df[df["Status"]=="Approved"])
            pending = len(df[df["Status"]=="Pending"])
            rejected = len(df[df["Status"]=="Rejected"])

            st.write("Total:", total)
            st.write("Approved:", approved)
            st.write("Pending:", pending)
            st.write("Rejected:", rejected)

            st.bar_chart(df["Status"].value_counts())

        elif menu == "Verify KYC":
            st.subheader("✅ Verify KYC")

            for i in range(len(df)):
                col1, col2, col3, col4, col5, col6 = st.columns(6)

                col1.write(df.iloc[i]["Name"])
                col2.write(df.iloc[i]["Aadhar"])
                col3.write(df.iloc[i]["PAN"])
                col4.write(df.iloc[i]["Status"])

                if col5.button("Approve", key=f"a{i}"):
                    df.loc[df.index[i], "Status"] = "Approved"
                    df.to_csv(data_file, index=False)
                    st.rerun()

                if col6.button("Reject", key=f"r{i}"):
                    df.loc[df.index[i], "Status"] = "Rejected"
                    df.to_csv(data_file, index=False)
                    st.rerun()
    else:
        st.sidebar.error("Wrong credentials")
