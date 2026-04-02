import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import time
import datetime

st.set_page_config(page_title="Telsica KYC System", layout="wide")

# ---------- GLASS UI CSS ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #e3f2fd, #ffffff);
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(12px);
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

/* Center login */
.center-box {
    display: flex;
    justify-content: center;
    margin-top: 80px;
}

/* Buttons */
.stButton>button {
    background-color: #2E86C1;
    color: white;
    border-radius: 8px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER LOGO ----------
col1, col2 = st.columns([6, 4])
with col1:
    st.write("")
with col2:
    st.markdown("<div style='text-align:right;'>", unsafe_allow_html=True)
    st.image("logo.png", width=250)

# ---------- FILE SETUP ----------
data_file = "kyc_data.csv"
user_file = "users.csv"

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Name","Username","Address","Aadhar","PAN","Document","Status","Date"])
    df.to_csv(data_file, index=False)

if not os.path.exists(user_file):
    users = pd.DataFrame(columns=["Username","Password"])
    users.to_csv(user_file, index=False)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "user" not in st.session_state:
    st.session_state.user = ""

users_df = pd.read_csv(user_file)

# ---------- LOGIN / SIGNUP ----------
if not st.session_state.logged_in:

    st.markdown("<div class='center-box'>", unsafe_allow_html=True)
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    st.markdown("### 🔐 Welcome to Telsica KYC System")

    auth_mode = st.radio("Select Option", ["Login", "Signup"])

    # SIGNUP
    if auth_mode == "Signup":
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Signup"):
            if new_user in users_df["Username"].values:
                st.error("User already exists")
            elif new_user and new_pass:
                new_data = pd.DataFrame([[new_user, new_pass]], columns=["Username","Password"])
                users_df = pd.concat([users_df, new_data], ignore_index=True)
                users_df.to_csv(user_file, index=False)
                st.success("Account created! Please login")
            else:
                st.warning("Fill all fields")

    # LOGIN
    elif auth_mode == "Login":
        role = st.selectbox("Login As", ["Client", "Admin"])

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if role == "Admin" and username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.role = "admin"
                st.rerun()

            elif role == "Client":
                user_match = users_df[
                    (users_df["Username"] == username) &
                    (users_df["Password"] == password)
                ]

                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.role = "client"
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------- LOGOUT ----------
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.rerun()

# ---------- LOAD DATA ----------
df = pd.read_csv(data_file)

# ======================================================
# 👤 CLIENT PANEL
# ======================================================
if st.session_state.role == "client":

    st.sidebar.title("👤 Client Panel")
    menu = st.sidebar.radio("Menu", ["Submit KYC", "My Status"])

    if menu == "Submit KYC":
        st.subheader("🧾 Submit KYC")

        name = st.text_input("Name")
        address = st.text_input("Address")
        aadhar = st.text_input("Aadhar")
        pan = st.text_input("PAN")
        document = st.file_uploader("Upload Document")

        if st.button("Submit"):
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
                    [[name, st.session_state.user, address, aadhar, pan, filename, "Pending", date]],
                    columns=["Name","Username","Address","Aadhar","PAN","Document","Status","Date"]
                )

                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(data_file, index=False)

                st.success("KYC Submitted!")

    elif menu == "My Status":
        st.subheader("📊 My Status")
        user_data = df[df["Username"] == st.session_state.user]
        st.dataframe(user_data, use_container_width=True)

# ======================================================
# 🧑‍💼 ADMIN PANEL
# ======================================================
elif st.session_state.role == "admin":

    st.sidebar.title("🧑‍💼 Admin Panel")
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
            c1,c2,c3,c4,c5,c6,c7 = st.columns(7)

            c1.write(df.iloc[i]["Name"])
            c2.write(df.iloc[i]["Username"])
            c3.write(df.iloc[i]["Aadhar"])
            c4.write(df.iloc[i]["PAN"])
            c5.write(df.iloc[i]["Status"])

            if c6.button("Approve", key=f"a{i}"):
                df.loc[df.index[i], "Status"] = "Approved"
                df.to_csv(data_file, index=False)
                st.rerun()

            if c7.button("Reject", key=f"r{i}"):
                df.loc[df.index[i], "Status"] = "Rejected"
                df.to_csv(data_file, index=False)
                st.rerun()

    elif menu == "Analysis":
        st.subheader("📊 Data Analysis")

        if "Date" not in df.columns:
            df["Date"] = pd.Timestamp.today()

        df["Date"] = pd.to_datetime(df["Date"])

        df["Risk"] = df["Status"].apply(lambda x:
            "Low" if x=="Approved" else "Medium" if x=="Pending" else "High"
        )

        st.bar_chart(df["Risk"].value_counts())

        trend = df.groupby("Date").size()
        st.line_chart(trend)

        st.download_button("📄 Download Data", df.to_csv(index=False), "kyc_data.csv")
