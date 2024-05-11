import copy
import json
import random

import streamlit as st

from utils import (
    st_get_osm_geometries,
    st_plot_all,
    get_colors_from_style,
    gdf_to_bytesio_geojson,
)
from prettymapp.geo import get_aoi
from prettymapp.settings import STYLES

st.set_page_config(
    page_title="daetripp", page_icon="🖼️", initial_sidebar_state="collapsed"
)

# Add survey questions with sliders
# st.write("---")
st.markdown("## DaeTraveler's Type Survey")

sites_data = {
    'Daejeon Expo Park': {'lat': 36.3730, 'lon': 127.3847},
    'Yuseong Hot Springs': {'lat': 36.3565, 'lon': 127.3279},
    'National Science Museum': {'lat': 36.3746, 'lon': 127.3722},
    'Hanbat Arboretum': {'lat': 36.3058, 'lon': 127.3381},
    'Daejeon Museum of Art': {'lat': 36.3519, 'lon': 127.3891},
    'Gyejoksan Mountain': {'lat': 36.2908, 'lon': 127.3338},
    'Ppuri Park': {'lat': 36.3414, 'lon': 127.3938},
    'Daejeon O-World': {'lat': 36.2902, 'lon': 127.4011}
}

questions = [
    "I prefer travel experiences that incorporate technology and efficiency.",
    "I enjoy participating in local events and engaging with the community when traveling.",
    "I seek practical and convenient leisure activities during my travels.",
    "I am open to trying new and adventurous activities during my trips.",
    "I prioritize comfort and relaxation over exploring new places.",
    "I value cultural immersion and learning about local traditions.",
    "I am willing to splurge on high-end accommodations and dining experiences.",
]

# Create sliders for each question
responses = []
for i, question in enumerate(questions):
    response = st.slider(
        question,
        min_value=1,
        max_value=5,
        value=3,
        key=f"question_{i}",
    )
    responses.append(response)

# Define weights for each question and traveler type
weights = {
    "Tech-savvy": [0.20, -0.10, -0.05, 0.15, -0.10, -0.05, 0.15],
    "Community-focused": [-0.10, 0.20, -0.05, 0.05, -0.05, 0.20, 0.05],
    "Practical Leisure Seeker": [-0.05, -0.05, 0.20, -0.10, 0.20, -0.05, 0.15],
}

if st.button("Finalize Survey"):
    # Calculate scores for each traveler type
    traveler_scores = {
        traveler_type: round(sum(response * weight for response, weight in zip(responses, weights[traveler_type])), 1)
        for traveler_type in weights
    }

    # Determine the traveler type based on the highest score
    traveler_type = max(traveler_scores, key=traveler_scores.get)

    # Touristic spots for each traveler type
    tech_savvy_spots = ['National Science Museum', 'Daejeon Expo Park', 'Daejeon O-World']
    community_focused_spots = ['Ppuri Park', 'Daejeon Museum of Art', 'Hanbat Arboretum']
    leisure_seeker_spots = ['Yuseong Hot Springs', 'Gyejoksan Mountain', 'Hanbat Arboretum']

    # Calculate the center coordinates for each traveler type
    def calculate_center_coordinates(spots):
        latitudes = [sites_data[spot]['lat'] for spot in spots]
        longitudes = [sites_data[spot]['lon'] for spot in spots]
        center_lat = sum(latitudes) / len(latitudes)
        center_lon = sum(longitudes) / len(longitudes)
        return center_lat, center_lon

    tech_savvy_coordinates = calculate_center_coordinates(tech_savvy_spots)
    community_focused_coordinates = calculate_center_coordinates(community_focused_spots)
    leisure_seeker_coordinates = calculate_center_coordinates(leisure_seeker_spots)


    # Customize map style and coordinates based on traveler type
    if traveler_type == "Practical Leisure Seeker":
        style = "Peach"
        radius = 4000
        coordinates = leisure_seeker_coordinates
        recommended_sites = {site: sites_data[site] for site in leisure_seeker_spots}
    elif traveler_type == "Community-focused":
        style = "Flannel"
        radius = 4000
        coordinates = community_focused_coordinates
        recommended_sites = {site: sites_data[site] for site in community_focused_spots}
    else:  # Tech-savvy
        style = "Citrus"
        radius = 4000
        coordinates = tech_savvy_coordinates
        recommended_sites = {site: sites_data[site] for site in tech_savvy_spots}
        
    st.write(f"## Hello, {traveler_type} traveler!")
    st.write(traveler_scores)

    # Use the fixed coordinates for Daejeon, South Korea
    from datetime import date
    today = date.today()
    address = f"DaeTRIP for Daejeon, South Korea, {today}"
    # coordinates = [36.3504, 127.3845]
    rectangular = False

    result_container = st.empty()
    with st.spinner("Creating map... (may take up to a minute)"):
        aoi = get_aoi(coordinates=coordinates, radius=radius, rectangular=rectangular)
        df = st_get_osm_geometries(aoi=aoi)
        draw_settings = STYLES[style]
        config = {
            "aoi_bounds": aoi.bounds,
            "draw_settings": draw_settings,
            "name_on": True,
            "name": address,
            "font_size": 20,
            "font_color": "black",
            "text_x": 0,
            "text_y": -55,
            "text_rotation": 0,
            "shape": "circle",
            "contour_width": 2,
            "contour_color": "black",
            "bg_shape": "rectangle",
            "bg_buffer": 20,
            "bg_color": "white"
        }
        st.write("## Your Recommended Sites")
        fig = st_plot_all(_df=df, recommended_sites=recommended_sites, **config)
        st.write("---")
        st.write("## Share your Instagram-Ready Trip Map!")
        st.pyplot(fig, pad_inches=0, bbox_inches="tight", transparent=True, dpi=300)

    st.markdown("</br>", unsafe_allow_html=True)
    st.markdown("</br>", unsafe_allow_html=True)
    ex1, ex2 = st.columns(2)

    with ex1.expander("Export geometries as GeoJSON"):
        st.write(f"{df.shape[0]} geometries")
        st.download_button(
            label="Download",
            data=gdf_to_bytesio_geojson(df),
            file_name=f"prettymapp_{address[:10]}.geojson",
            mime="application/geo+json",
        )

    config = {"address": address, **config}
    with ex2.expander("Export map configuration"):
        st.write(config)

    st.markdown("---")
    st.write(
        "Share on social media with the hashtag [#DaeTRIP](https://www.instagram.com/daejeontourism/) !"
    )
    # st.markdown("More infos and :star: at [github.com/youngjuene/RecMap/](https://github.com/youngjuene/RecMap/)")