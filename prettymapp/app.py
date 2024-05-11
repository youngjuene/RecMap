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
    page_title="prettymapp", page_icon="🖼️", initial_sidebar_state="collapsed"
)
st.markdown("# Prettymapp")

# Add survey questions with sliders
st.write("---")
st.markdown("## Traveler's Type Survey")
tech_savvy_question = st.slider(
    "I prefer travel experiences that incorporate technology and efficiency.",
    min_value=1,
    max_value=5,
    value=2,
    key="tech_savvy_question",
)
community_question = st.slider(
    "I enjoy participating in local events and engaging with the community when traveling.",
    min_value=1,
    max_value=5,
    value=3,
    key="community_question",
)
leisure_question = st.slider(
    "I seek practical and convenient leisure activities during my travels.",
    min_value=1,
    max_value=5,
    value=2,
    key="leisure_question",
)
personalization_question = st.slider(
    "I value personalized recommendations based on my preferences and past behaviors.",
    min_value=1,
    max_value=5,
    value=4,
    key="personalization_question",
)

# Define weights for each question
tech_savvy_weight = 0.4
community_weight = 0.3
leisure_weight = 0.2
personalization_weight = 0.1

# Calculate weighted scores for each question
tech_savvy_score = tech_savvy_question * tech_savvy_weight
community_score = community_question * community_weight
leisure_score = leisure_question * leisure_weight
personalization_score = personalization_question * personalization_weight

# Determine the traveler type based on the highest weighted score
traveler_scores = {
    "Tech-savvy": tech_savvy_score,
    "Community-focused": community_score,
    "Practical Leisure Seeker": leisure_score,
}
traveler_type = max(traveler_scores, key=traveler_scores.get)

# Adjust the traveler type based on the personalization score
if personalization_score > 0.3:
    traveler_type = "Personalized " + traveler_type

# Customize map style based on traveler type
if traveler_type.endswith("Practical Leisure Seeker"):
    style = "Peach"
    radius = 500
elif traveler_type.endswith("Community-focused"):
    style = "Flannel"
    radius = 1000
else:  # Tech-savvy
    style = "Citrus"
    radius = 1500
    
st.write(f"You are a {traveler_type} traveler!")

# Use the fixed coordinates for Daejeon, South Korea
address = "Daejeon, South Korea"
coordinates = [36.3504, 127.3845]
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
        "text_y": -50,
        "text_rotation": 0,
        "shape": "circle",
        "contour_width": 2,
        "contour_color": "black",
        "bg_shape": "rectangle",
        "bg_buffer": 20,
        "bg_color": "white"
    }
    fig = st_plot_all(_df=df, **config)
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
    "Share on social media with the hashtag [#prettymaps](https://twitter.com/search?q=%23prettymaps&src=typed_query) !"
)
st.markdown(
    "More infos and :star: at [github.com/chrieke/prettymapp](https://github.com/chrieke/prettymapp)"
)