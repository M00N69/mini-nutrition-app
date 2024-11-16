import streamlit as st
import requests

BASE_URL = "https://mini-nutrition-app.onrender.com"  # URL du backend FastAPI déployé sur Render

st.title("Mini-projet Nutrition")

menu = st.sidebar.selectbox("Menu", ["Inscription", "Connexion", "Ajouter un repas", "Recommandation", "Voir utilisateurs", "Voir repas"])

if menu == "Inscription":
    st.header("Créer un compte")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    if st.button("S'inscrire"):
        response = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
        if response.status_code == 200:
            st.success("Inscription réussie !")
        else:
            st.error(f"Erreur lors de l'inscription : {response.json().get('detail', 'Erreur inconnue')}.")

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
            st.error(f"Échec de la connexion : {response.json().get('detail', 'Erreur inconnue')}.")

if menu == "Ajouter un repas":
    st.header("Ajouter un repas")
    name = st.text_input("Nom du repas")
    calories = st.number_input("Calories", min_value=0.0)
    proteins = st.number_input("Protéines", min_value=0.0)
    carbs = st.number_input("Glucides", min_value=0.0)
    fats = st.number_input("Lipides", min_value=0.0)
    if st.button("Ajouter"):
        token = st.session_state.get("token")
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{BASE_URL}/meals", json={"name": name, "calories": calories, "proteins": proteins, "carbs": carbs, "fats": fats}, headers=headers)
            if response.status_code == 200:
                st.success("Repas ajouté avec succès !")
            else:
                st.error(f"Erreur lors de l'ajout du repas : {response.json().get('detail', 'Erreur inconnue')}.")
        else:
            st.error("Vous devez être connecté pour ajouter un repas.")

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
        st.error(f"Erreur lors de la récupération des recommandations : {response.json().get('detail', 'Erreur inconnue')}.")

if menu == "Voir utilisateurs":
    st.header("Liste des utilisateurs")
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        users = response.json()
        for user in users:
            st.write(f"ID: {user['id']}, Email: {user['email']}")
    else:
        st.error(f"Erreur lors de la récupération des utilisateurs : {response.json().get('detail', 'Erreur inconnue')}.")

if menu == "Voir repas":
    st.header("Liste des repas")
    response = requests.get(f"{BASE_URL}/meals")
    if response.status_code == 200:
        meals = response.json()
        for meal in meals:
            st.write(f"Nom: {meal['name']}, Calories: {meal['calories']}, Protéines: {meal['proteins']}, Glucides: {meal['carbs']}, Lipides: {meal['fats']}")
    else:
        st.error(f"Erreur lors de la récupération des repas : {response.json().get('detail', 'Erreur inconnue')}.")
