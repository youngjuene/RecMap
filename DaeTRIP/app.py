import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import pandas as pd

st.title('DaeTRIP - Daejeon Tourist Route Recommendation System')

# Fetch touristic sites data from Daejeon's centralized tourism database
def fetch_sites_data_from_database(user_preferences):
    # Placeholder function - replace with actual database fetch logic
    sites_data = {
        'Site A': {'lat': 36.3504, 'lon': 127.3845, 'description': 'Description of Site A', 'rating': 4.5},
        'Site B': {'lat': 36.3204, 'lon': 127.4285, 'description': 'Description of Site B', 'rating': 4.2},
        'Site C': {'lat': 36.3604, 'lon': 127.3985, 'description': 'Description of Site C', 'rating': 4.8},
    }
    return sites_data

# Generate personalized route recommendations
def generate_route_recommendations(selected_sites, sites_data, user_preferences, transportation_type, max_time):
    # Placeholder function - replace with actual recommendation logic
    recommended_route = selected_sites
    return recommended_route

# Fetch user-generated reviews from the database
def get_user_reviews_from_database():
    # Placeholder function - replace with actual database fetch logic
    user_reviews = [
        {'user': 'User1', 'site': 'Site A', 'review': 'Great experience!'},
        {'user': 'User2', 'site': 'Site B', 'review': 'Highly recommended.'},
        {'user': 'User3', 'site': 'Site C', 'review': 'Amazing place!'},
    ]
    return user_reviews

# User Inputs
user_preferences = {}  # Placeholder for user preferences
transportation_type = st.selectbox('Select Transportation Type', ['Walking', 'Public Transport', 'Car'])
max_time = st.slider('Maximum Time for Transportation (minutes)', min_value=10, max_value=120, step=5)

# Fetch sites data based on user preferences
sites_data = fetch_sites_data_from_database(user_preferences)
selected_sites = st.multiselect('Select Touristic Sites', list(sites_data.keys()))

# Placeholder for map
map_placeholder = st.empty()

if st.button('Recommend Route'):
    # Generate personalized route recommendations
    recommended_route = generate_route_recommendations(selected_sites, sites_data, user_preferences, transportation_type, max_time)
    
    # Initialize Folium map
    m = folium.Map(location=[sites_data[selected_sites[0]]['lat'], sites_data[selected_sites[0]]['lon']], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for selected sites
    for site in recommended_route:
        if site in sites_data:
            folium.Marker(
                location=[sites_data[site]['lat'], sites_data[site]['lon']],
                popup=f"<b>{site}</b><br>{sites_data[site]['description']}<br>User Rating: {sites_data[site]['rating']}",
            ).add_to(marker_cluster)
    
    # Display map
    folium_static(m)

# Display user-generated content and reviews
user_reviews = get_user_reviews_from_database()
st.subheader('User Reviews')
for review in user_reviews:
    st.write(f"User: {review['user']}")
    st.write(f"Site: {review['site']}")
    st.write(f"Review: {review['review']}")
    st.write('---')