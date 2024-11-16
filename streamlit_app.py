import streamlit as st
import requests

BASE_URL = "https://mini-nutrition-app.onrender.com"  # URL du backend FastAPI déployé sur Render

st.title("Mini-projet Nutrition")

menu = st.sidebar.selectbox("Menu", ["Inscription", "Connexion", "Ajouter un repas", "Recommandation"])

if menu == "Inscription":
    st.header("Créer un compte")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        response = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
        if response.status_code == 200:
            st.success("Inscription réussie !")
        else:
            st.error("Erreur lors de l'inscription.")

if menu == "Connexion":
    st.header("Se connecter")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})
        if response.status_code == 200:
            st.success("Connexion réussie !")
            st.session_state["token"] = response.json()["access_token"]
        else:
            st.error("Échec de la connexion.")

if menu == "Ajouter un repas":
    st.header("Ajouter un repas")
    name = st.text_input("Nom du repas")
    calories = st.number_input("Calories")
    proteins = st.number_input("Protéines")
    carbs = st.number_input("Glucides")
    fats = st.number_input("Lipides")
    if st.button("Ajouter"):
        token = st.session_state.get("token")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/meals", json={"name": name, "calories": calories, "proteins": proteins, "carbs": carbs, "fats": fats}, headers=headers)
        if response.status_code == 200:
            st.success("Repas ajouté avec succès !")
        else:
            st.error("Erreur lors de l'ajout du repas.")

if menu == "Recommandation":
    st.header("Recommandation de repas")
    response = requests.get(f"{BASE_URL}/recommendation")
    if response.status_code == 200:
        recommendation = response.json()
        st.write(f"Repas recommandé : {recommendation['meal']}")
        st.write(f"Calories : {recommendation['calories']}")
        st.write(f"Protéines : {recommendation['proteins']}")
        st.write(f"Glucides : {recommendation['carbs']}")
        st.write(f"Lipides : {recommendation['fats']}")
    else:
        st.error("Erreur lors de la récupération des recommandations.")

