import streamlit as st
import pandas as pd
import numpy as np
from fuzzywuzzy import process
import plotly.express as px
import plotly.graph_objects as go

def find_song(song_name):
    song_name = song_name.strip().lower() 
    exact_match = df[df['name'].str.lower().str.strip() == song_name]
    if not exact_match.empty:
        return exact_match.iloc[0].to_dict()
    all_song_names = df['name'].str.strip().tolist()  
    best_match, score = process.extractOne(song_name, all_song_names)
    if score >= 80: 
        song = df[df['name'].str.strip() == best_match]
        return song.iloc[0].to_dict()
    return "Sorry, the song is not found!"

def get_song_data(song_name):
    song = find_song(song_name)
    if isinstance(song, str): 
        return song
    return {
        'name': song['name'],
        'valence': song['valence'],
        'danceability': song['danceability'],
        'energy': song['energy'],
        'tempo': song['tempo'],
        'cluster': song['cluster']
    }

def get_mean_vector(all_songs):
    numeric_features = ['valence', 'acousticness','danceability', 'energy','instrumentalness','liveness' , 'loudness','popularity', 'speechiness', 'tempo']
    vectors = []
    for song_name in all_songs:
        song = find_song(song_name)
        if isinstance(song, str):  
            continue
        vectors.append([song[feature] for feature in numeric_features])
    if not vectors:
        raise ValueError("No valide song found in the list.")
    return np.mean(vectors, axis=0)

def recommend_songs(searched_song, n_recommendations=5):
    mean_vector = get_mean_vector([searched_song])
    numeric_features = ['valence', 'acousticness', 'danceability', 'energy', 
                        'instrumentalness', 'liveness', 'loudness', 
                        'popularity', 'speechiness', 'tempo']
    df['distance'] = df[numeric_features].apply(
        lambda row: np.linalg.norm(row - mean_vector), axis=1
    )
    recommendations = df[df['name'].str.lower() != searched_song.lower()] \
                        .sort_values('distance') \
                        .head(n_recommendations)
    return recommendations[['name', 'artists', 'valence', 'danceability', 'energy', 'tempo']].to_dict(orient='records')

# Streamlit 
def main():
    st.markdown("""
        <style>
        .stApp {
            background-color: #FFCC00;
            color: #000000;
        }
        .sidebar .sidebar-content {
            background-color: #FFCC00;
            color: #000000;
        }
        .sidebar .sidebar-content h2 {
            color: #000000;
        }
        input {
            background-color: #FFCC00;
            color: #000000;
            border: 1px solid #000000;
        }
        .stButton>button {
            background-color: #000000;
            color: #FFCC00;
        }
        .stTable tbody tr td {
            background-color: #FFCC00;
            color: #000000;
        }
        h3, h2, .sidebar-title, .stMarkdown {
            color: #000000;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎵 TuneMatch 🎶")

    if "username" not in st.session_state:
        st.session_state.username = ""
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "liked_songs" not in st.session_state:
        st.session_state.liked_songs = []  

    if st.session_state.page == "welcome":
        username = st.text_input("👤 Enter your name:", value=st.session_state.username)

        if username:
            st.session_state.username = username
            st.write(f"<h3 style='color:#000000;'><strong>Welcome, {username}! 👋</strong></h3>", unsafe_allow_html=True)
            st.markdown("<p style='color:#000000;'>Looking for unforgettable moments, whether with friends, family, or on your own?</p>", unsafe_allow_html=True)
            st.markdown("<p style='color:#000000;'>TuneMatch offers you a unique musical journey with thousands of songs across all genres. Whether you're after good vibes, emotions, or new discoveries, this app lets you listen to, analyze, and compare tracks that reflect your personality and world. Explore an infinite soundscape and find the music that will accompany every moment of your life!</p>", unsafe_allow_html=True)

            if st.button("🎵 Start Exploring Music"):
                st.session_state.page = "explore_music"

    elif st.session_state.page == "explore_music":
        explore_music()

def explore_music():
    st.sidebar.markdown("""
        <style>
        .sidebar-title {
            color: #000000;
            font-size: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<h2 class='sidebar-title'>🎧 Welcome to TuneMatch</h2>", unsafe_allow_html=True)
    st.sidebar.write("<p style='color:#000000;'>Search, compare, and like your favorite songs! 💖</p>", unsafe_allow_html=True)

    song_input = st.text_input("🔍 Search for a song:")

    if song_input:
        song_data = get_song_data(song_input)
        if isinstance(song_data, str):
            st.warning(f"⚠️ {song_data}")
        else:
            st.subheader("🎼 Song Details")
            song_df = pd.DataFrame([song_data])
            st.table(song_df.style.set_table_styles(
                [{"selector": "", "props": [("background-color", "#FFCC00"), ("color", "#000000")] }]
            ))

            if st.button("💖 Like this song"):
                st.session_state.liked_songs.append(song_data['name'])  
                st.success(f"'🎵 {song_data['name']}' added to Liked Songs! 💾")

            st.subheader("🎤 Recommended Songs")
            recommendations = recommend_songs(song_input)
            recommendations_df = pd.DataFrame(recommendations)
            st.table(recommendations_df.style.set_table_styles(
                [{"selector": "", "props": [("background-color", "#FFCC00"), ("color", "#000000")] }]
            ))

            if st.button("📊 Compare Song Features"):
                comparison_data = recommendations_df[['name', 'valence', 'danceability', 'energy', 'tempo']]
                comparison_data.loc[-1] = [song_data['name'], song_data['valence'], song_data['danceability'], song_data['energy'], song_data['tempo']]
                comparison_data.index = range(comparison_data.shape[0])

                st.subheader("✨ Feature Comparison")
                for feature in ['valence', 'danceability', 'energy', 'tempo']:
                    fig = px.bar(
                        comparison_data, 
                        x='name', 
                        y=feature, 
                        title=f"{feature.capitalize()} Comparison 🎶",
                        color='name',
                        color_discrete_sequence=["#800020" ,"#808000"]  
                    )
                    fig.update_layout(
                        xaxis_title="Song", 
                        yaxis_title=feature.capitalize(), 
                        template="plotly_dark",
                        plot_bgcolor="#FFCC00",
                        paper_bgcolor="#FFCC00",
                        font=dict(color="#000000")
                    )
                    st.plotly_chart(fig)

    if st.sidebar.button("💾 View Liked Songs"):
        st.sidebar.subheader("💖 Liked Songs")
        if st.session_state.liked_songs:
            liked_songs_display = "\n".join(st.session_state.liked_songs)
            st.sidebar.text(liked_songs_display)
        else:
            st.sidebar.write("No songs liked yet. 😢")
if __name__ == "__main__":
    df = pd.read_csv('DATA/data_with_clusters.csv')
    main()
