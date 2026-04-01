import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="KYC Banking System", layout="wide")

# ---------- DARK BANK UI ----------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.stApp {
    background-color: #0E1117;
    color: white;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------- FILE SETUP ----------
file_path = "kyc_data.csv"

if not os.path.exists(file_path):
    df = pd.DataFrame(columns=["Name", "Address", "Aadhar", "PAN", "Document", "Status"])
    df.to_csv(file_path, index=False)

# ---------- LOGIN ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🏦 KYC Banking System Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------- SIDEBAR ----------
st.sidebar.title("🏦 Banking Menu")

menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Add Customer",
    "Customer Records"
])

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Load data
df = pd.read_csv(file_path)

# ---------- DASHBOARD ----------
if menu == "Dashboard":
    st.title("📊 KYC Dashboard")

    total = len(df)
    approved = len(df[df["Status"] == "Approved"])
    pending = len(df[df["Status"] == "Pending"])
    rejected = len(df[df["Status"] == "Rejected"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Clients", total)
    c2.metric("Approved", approved)
    c3.metric("Pending", pending)
    c4.metric("Rejected", rejected)

    st.subheader("📊 Status Overview")
    st.bar_chart(df["Status"].value_counts())

    fig, ax = plt.subplots()
    df["Status"].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

# ---------- ADD CUSTOMER ----------
elif menu == "Add Customer":
    st.title("➕ Add New Customer")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Customer Name")

    with col2:
        address = st.text_input("Address")

    aadhar = st.text_input("Aadhar Number")
    pan = st.text_input("PAN Number")

    document = st.file_uploader("Upload Document")

    if st.button("Submit KYC"):
        if name and address and aadhar and pan:
            filename = ""

            if document:
                filename = str(int(time.time())) + "_" + document.name
                filepath = os.path.join("uploads", filename)

                if not os.path.exists("uploads"):
                    os.makedirs("uploads")

                with open(filepath, "wb") as f:
                    f.write(document.read())

            new_data = pd.DataFrame(
                [[name, address, aadhar, pan, filename, "Pending"]],
                columns=["Name", "Address", "Aadhar", "PAN", "Document", "Status"]
            )

            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(file_path, index=False)

            st.success("Customer Added Successfully!")
        else:
            st.warning("Fill all fields")

# ---------- RECORDS ----------
elif menu == "Customer Records":
    st.title("📋 Customer Records")

    df = pd.read_csv(file_path)

    for i in range(len(df)):
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

        c1.write(df.loc[i, "Name"])
        c2.write(df.loc[i, "Address"])
        c3.write(df.loc[i, "Aadhar"])
        c4.write(df.loc[i, "PAN"])
        c5.write(df.loc[i, "Document"])

        status = df.loc[i, "Status"]

        if c6.button("Approve", key=f"a{i}"):
            df.loc[i, "Status"] = "Approved"
            df.to_csv(file_path, index=False)
            st.rerun()

        if c7.button("Reject", key=f"r{i}"):
            df.loc[i, "Status"] = "Rejected"
            df.to_csv(file_path, index=False)
            st.rerun()

        st.write(f"Status: {status}")
        st.divider()
