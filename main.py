import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

API_BASE = "https://fastapi-auth-apiuvicorn-main-app-host-0.onrender.com"

st.title("アカウント認証API UI")

menu = st.sidebar.selectbox("メニューを選択", ["アカウント作成", "情報取得", "情報更新", "アカウント削除"])

if menu == "アカウント作成":
    st.header("\U0001F195 アカウント作成 (/signup)")
    user_id = st.text_input("ユーザーID", "TaroYamada")
    password = st.text_input("パスワード", "PaSSwd4TY")
    if st.button("アカウント作成"):
        res = requests.post(f"{API_BASE}/signup", json={"user_id": user_id, "password": password})
        st.code(res.json(), language="json")

elif menu == "情報取得":
    st.header("\U0001F50D ユーザー情報取得 (/users/{user_id})")
    user_id = st.text_input("ユーザーID", "TaroYamada")
    password = st.text_input("パスワード", "PaSSwd4TY")
    if st.button("情報取得"):
        res = requests.get(f"{API_BASE}/users/{user_id}", auth=HTTPBasicAuth(user_id, password))
        st.code(res.json(), language="json")

elif menu == "情報更新":
    st.header("\U0001F58A ユーザー情報更新 (/users/{user_id})")
    user_id = st.text_input("ユーザーID", "TaroYamada")
    password = st.text_input("パスワード", "PaSSwd4TY")
    nickname = st.text_input("ニックネーム", "たろー")
    comment = st.text_input("コメント", "僕は元気です")
    if st.button("情報更新"):
        body = {}
        if nickname:
            body["nickname"] = nickname
        if comment:
            body["comment"] = comment
        res = requests.patch(f"{API_BASE}/users/{user_id}", json=body, auth=HTTPBasicAuth(user_id, password))
        st.code(res.json(), language="json")

elif menu == "アカウント削除":
    st.header("\U0001F5D1 アカウント削除 (/close)")
    user_id = st.text_input("ユーザーID", "TaroYamada")
    password = st.text_input("パスワード", "PaSSwd4TY")
    if st.button("削除"):
        res = requests.post(f"{API_BASE}/close", auth=HTTPBasicAuth(user_id, password))
        st.code(res.json(), language="json")