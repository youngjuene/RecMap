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
st.markdown("## Traveler's Type Survey")

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

# Calculate scores for each traveler type
traveler_scores = {
    traveler_type: round(sum(response * weight for response, weight in zip(responses, weights[traveler_type])), 1)
    for traveler_type in weights
}

# Determine the traveler type based on the highest score
traveler_type = max(traveler_scores, key=traveler_scores.get)

# Customize map style based on traveler type
if traveler_type == "Practical Leisure Seeker":
    style = "Peach"
    radius = 2000
elif traveler_type == "Community-focused":
    style = "Flannel"
    radius = 2000
else:  # Tech-savvy
    style = "Citrus"
    radius = 2000
    
st.write(f"Based on your responses, you seem to be a {traveler_type} traveler!")
st.write(traveler_scores)

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