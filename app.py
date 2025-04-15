import joblib
import streamlit as st
import requests
import pandas as pd

# Configuration de la page Streamlit
st.set_page_config(page_title="Système de Recommandation de Films", layout="wide")
st.header("🎬 Système de Recommandation de Films par Intelligence Artificielle")
st.markdown("---")

# Chargement des données avec gestion d'erreur
@st.cache_resource
def load_data():
    try:
        with open("tools/movie_dataset.joblib", "rb") as f:
            movies = joblib.load(f)
        with open("tools/similarity.joblib", "rb") as f:
            similarity = joblib.load(f)
        return movies, similarity
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        st.stop()

movies, similarity = load_data()

# Fonction pour récupérer les affiches avec gestion d'erreur
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur API : {str(e)}")
        return None
    except KeyError:
        return None

# Fonction de recommandation principale
def recommend(movie_title):
    try:
        index = movies[movies["title"] == movie_title].index[0]
        scores = list(enumerate(similarity[index]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]  # Top 5
        
        recommended_movies = []
        for i, _ in sorted_scores:
            movie_id = movies.iloc[i]["movie_id"]
            title = movies.iloc[i]["title"]
            poster = fetch_poster(movie_id)
            recommended_movies.append((title, poster))
            
        return recommended_movies
    
    except IndexError:
        st.error("Film non trouvé dans la base de données")
        return []

# Interface utilisateur
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_movie = st.selectbox(
            "🎥 Sélectionnez un film que vous aimez :",
            movies["title"].unique(),
            index=None,
            placeholder="Commencez à taper..."
        )
    
    with col2:
        st.markdown("##")
        if st.button("🚀 Voir les recommandations", use_container_width=True):
            if not selected_movie:
                st.warning("Veuillez sélectionner un film")
                st.stop()

# Affichage des résultats
if selected_movie:
    recommendations = recommend(selected_movie)
    
    if recommendations:
        st.subheader(f"🍿 Recommandations pour : {selected_movie}")
        cols = st.columns(5)
        
        for idx, (title, poster) in enumerate(recommendations):
            with cols[idx % 5]:
                st.markdown(f"**{title}**")
                if poster:
                    st.image(poster, 
                            use_container_width=True,  # Correction ici
                            caption=title)
                else:
                    st.warning("Affiche non disponible")
    else:
        st.error("Aucune recommandation trouvée")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    Données fournies par <a href="https://www.themoviedb.org/">TMDb</a>
</div>
""", unsafe_allow_html=True)