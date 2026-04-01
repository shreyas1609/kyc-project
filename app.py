import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="KYC System", layout="wide")

# ---------- CUSTOM UI ----------
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- FILE SETUP ----------
file_path = "kyc_data.csv"

if not os.path.exists(file_path):
    df = pd.DataFrame(columns=["Name", "Address", "Document", "Status"])
    df.to_csv(file_path, index=False)

# ---------- LOGIN SYSTEM ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 KYC System Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

if not st.session_state.logged_in:
    login()
    st.stop()

# ---------- MAIN APP ----------
st.title("📊 Client KYC Data Analysis System")

# Logout button
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# Load data
df = pd.read_csv(file_path)

# ---------- KPI DASHBOARD ----------
total = len(df)
approved = len(df[df["Status"] == "Approved"])
pending = len(df[df["Status"] == "Pending"])
rejected = len(df[df["Status"] == "Rejected"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Clients", total)
col2.metric("Approved", approved)
col3.metric("Pending", pending)
col4.metric("Rejected", rejected)

# ---------- CREATE UPLOAD FOLDER ----------
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ---------- FORM ----------
st.subheader("➕ Add Customer")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Customer Name")

with col2:
    address = st.text_input("Address")

document = st.file_uploader("Upload Document")

if st.button("Submit KYC"):
    if name and address:
        filename = ""

        if document:
            filename = str(int(time.time())) + "_" + document.name
            filepath = os.path.join("uploads", filename)

            with open(filepath, "wb") as f:
                f.write(document.read())

        status = "Pending"

        new_data = pd.DataFrame(
            [[name, address, filename, status]],
            columns=["Name", "Address", "Document", "Status"]
        )

        df = pd.read_csv(file_path)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(file_path, index=False)

        st.success("KYC Submitted Successfully!")
    else:
        st.warning("Please fill all details")

# ---------- DATA VIEW ----------
st.subheader("📋 Customer Records")

df = pd.read_csv(file_path)

for i in range(len(df)):
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.write(df.loc[i, "Name"])
    col2.write(df.loc[i, "Address"])
    col3.write(df.loc[i, "Document"])

    status = df.loc[i, "Status"]

    if col4.button("Approve", key=f"approve{i}"):
        df.loc[i, "Status"] = "Approved"
        df.to_csv(file_path, index=False)
        st.rerun()

    if col5.button("Reject", key=f"reject{i}"):
        df.loc[i, "Status"] = "Rejected"
        df.to_csv(file_path, index=False)
        st.rerun()

    st.write(f"Status: {status}")
    st.divider()

# ---------- DASHBOARD ----------
st.subheader("📊 KYC Status Summary")

status_count = df["Status"].value_counts()
st.bar_chart(status_count)

# ---------- PIE CHART ----------
st.subheader("📊 KYC Distribution (Pie Chart)")

fig, ax = plt.subplots()
df["Status"].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
ax.set_ylabel("")
st.pyplot(fig)