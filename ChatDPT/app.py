import os
import openai
from dataclasses import dataclass
from typing import Literal
import pandas as pd
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.globals import set_verbose, get_verbose
from langchain_community.callbacks.manager import get_openai_callback
from langchain.chains.conversation.memory import ConversationSummaryMemory
import streamlit.components.v1 as components
import re


set_verbose(False)
openai.api_key = st.secrets["openai_api_key"]

from utils import (
    st_get_osm_geometries,
    st_plot_all,
    get_colors_from_style,
    gdf_to_bytesio_geojson,
)
from prettymapp.geo import get_aoi
from prettymapp.settings import STYLES


st.set_page_config(
    page_title="DaeTrip - Discover Daejeon's Hidden Gems",
    page_icon="🌟",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .subtitle {
            font-size: 24px;
            color: #616161;
            text-align: center;
            margin-bottom: 40px;
            font-style: italic;
        }
        .question {
            font-size: 20px;
            color: #424242;
            margin-bottom: 10px;
        }
        .section-title {
            font-size: 28px;
            font-weight: bold;
            color: #1E88E5;
            margin-top: 40px;
            margin-bottom: 20px;
            text-transform: uppercase;
            border-bottom: 2px solid #1E88E5;
            padding-bottom: 5px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        .stButton button {
            background-color: #1E88E5;
            color: white;
            font-size: 20px;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background-color 0.3s ease;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #1565C0;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">✨ DaeTrip ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Uncover the Enchanting Wonders of Daejeon</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">🌟 Welcome Survey 🌟</div>', unsafe_allow_html=True)

# Survey questions
questions = [
    "I prefer travel experiences that incorporate technology and efficiency.",
    "I enjoy participating in local events and engaging with the community when traveling.",
    "I am open to trying new and adventurous activities during my trips.",
    "I prioritize comfort and relaxation over exploring new places.",
    "I value cultural immersion and learning about local traditions.",
    "I prefer using public transportation over private transportation when traveling."
]

# Create sliders for each question
responses = []
for i, question in enumerate(questions):
    response = st.slider(
        question,
        min_value=1,
        max_value=5,
        key=f"question_{i}_slider",  # Unique key for each slider
        help="1: Strongly disagree, 2: Disagree, 3: Neutral, 4: Agree, 5: Strongly agree"
    )
    responses.append(response)

# Initialize prompt
prompt = ""
daejeon_sites_csv = pd.read_csv('daejeon_touristic_sites_en.csv')

# Traveler type configuration
traveler_type_config = {
    "Tech-savvy": {"style": "Citrus", "radius": 4000},
    "Community-focused": {"style": "Flannel", "radius": 4000},
    "Practical Leisure Seeker": {"style": "Peach", "radius": 4000}
}

# Function to extract traveler type from OpenAI response
def extract_traveler_type(response):
    pattern = r"\*\*Traveler Type:\*\* ([\w\s-]+)"
    match = re.search(pattern, response)
    if match:
        return match.group(1).strip()
    return None

# Function to extract recommended sites from OpenAI response
def extract_recommended_sites(response):
    pattern = r"\*\*Recommended Sites:\*\*\n(.*?)(?=\n\n|$)"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        sites_text = match.group(1).strip()
        sites = [site.strip().lstrip('- ').strip() for site in sites_text.split("\n") if site.strip()]
        return sites
    return []

# Function to calculate center coordinates for recommended sites
def calculate_center_coordinates(sites):
    latitudes = [float(daejeon_sites_csv[daejeon_sites_csv['Name'] == site]['lat'].values[0]) for site in sites]
    longitudes = [float(daejeon_sites_csv[daejeon_sites_csv['Name'] == site]['lon'].values[0]) for site in sites]
    center_lat = sum(latitudes) / len(latitudes)
    center_lon = sum(longitudes) / len(longitudes)
    return center_lat, center_lon

# Submit button
if st.button("Discover My Perfect Trip"):
    # Collect the responses and create a prompt        
    prompt = f"Based on the six responses to the travel preference questions answered on a scale of 1 (strongly disagree) to 5 (strongly agree), please classify my traveler type into one of the following categories: Tech-savvy, Community-focused, or Practical Leisure Seeker. Provide a brief explanation for your classification.\n\nThen, recommend three to four relevant touristic sites or activities specifically in Daejeon, South Korea, by selecting them from the following CSV data:\n\n{daejeon_sites_csv.to_string(index=False)}\n\nEnsure that the recommended sites are exactly matched with the names provided in the CSV data. Do not include any sites that are not present in the CSV.\n\nFinally, present the recommendations as a connected single-day itinerary, including estimated travel times between each location based on the preferred mode of transportation (public or private). Present the information in an organized markdown format with concise details and proper usage of bold fonts for better readability, using the following format:\n\n**Traveler Type:** <traveler_type>\n\n**Explanation:** <explanation>\n\n**Recommended Sites:**\n- <site1>\n- <site2>\n- <site3>\n\n**Itinerary:** <itinerary>\n"
    
    for i, (question, response) in enumerate(zip(questions, responses)):
        prompt += f"{i+1}. {question} (Response: {response})\n"

    # Send the prompt to the OpenAI API using the ConversationChain
    result = st.session_state.conversation.invoke(prompt)
    summary = result['response']

    # Display the summary
    st.write(summary)
    prompt = summary
    
    # Parse the OpenAI response to extract traveler type and recommended sites
    traveler_type = extract_traveler_type(summary)
    recommended_sites = extract_recommended_sites(summary)
    
    if traveler_type and recommended_sites:
        # Retrieve map style, color, and size based on traveler type
        style = traveler_type_config.get(traveler_type, {}).get("style", "Citrus")
        radius = traveler_type_config.get(traveler_type, {}).get("radius", 4000)

        # Filter recommended sites based on the daejeon_sites_csv data
        filtered_sites = [site for site in recommended_sites if site in daejeon_sites_csv['Name'].values]

        if filtered_sites:
            # Calculate center coordinates for filtered recommended sites
            latitudes = [float(daejeon_sites_csv[daejeon_sites_csv['Name'] == site]['lat'].values[0]) for site in filtered_sites]
            longitudes = [float(daejeon_sites_csv[daejeon_sites_csv['Name'] == site]['lon'].values[0]) for site in filtered_sites]
            center_lat = sum(latitudes) / len(latitudes)
            center_lon = sum(longitudes) / len(longitudes)
            coordinates = (center_lat, center_lon)

            # Use the fixed coordinates for Daejeon, South Korea
            from datetime import date
            today = date.today()
            address = f"DaeTRIP for Daejeon, South Korea, {today}"
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
                recommended_sites_dict = {site: daejeon_sites_csv[daejeon_sites_csv['Name'] == site][['lat', 'lon']].to_dict(orient='records')[0] for site in recommended_sites if site in daejeon_sites_csv['Name'].values}
                fig = st_plot_all(_df=df, recommended_sites=recommended_sites_dict, **config)
                st.write("---")
                st.write("## Share your Instagram-Ready Trip Map!")
                st.pyplot(fig, pad_inches=0, bbox_inches="tight", transparent=True, dpi=300)
        else:
            st.write(f"{recommended_sites}\nNone of the recommended sites are found in the Daejeon touristic sites data.")
    else:
        st.write(f"{traveler_type}\n{recommended_sites}\nUnable to extract traveler type and recommended sites from the response.")

keyword_urls = {
    "Tourist Attractions": "https://daejeontour.co.kr/en/board.do?menuIdx=234",
    "Tour Routes": "https://daejeontour.co.kr/en/board.do?menuIdx=235", 
    "Daejeon's Food": "https://daejeontour.co.kr/en/board.do?menuIdx=244",
    "Shopping": "https://daejeontour.co.kr/en/board.do?menuIdx=251",
    "Accommodation": "https://daejeontour.co.kr/en/page.do?menuIdx=252"
}

# After displaying the summary
if prompt:
    st.markdown('<div class="section-title">🗺️ Explore More about Daejeon Tourism 🗺️</div>', unsafe_allow_html=True)

    num_columns = len(keyword_urls)
    columns = st.columns(num_columns)

    for i, (button_text, url) in enumerate(keyword_urls.items()):
        with columns[i]:
            st.link_button(button_text, url)
    
@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
    st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "conversation" not in st.session_state:
        llm = ChatOpenAI(
            temperature=0,
            openai_api_key=st.secrets["openai_api_key"],
            model_name="gpt-4o" #"gpt-3.5-turbo-0125"
        )
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),
        )

def on_click_callback():
    with get_openai_callback() as cb:
        human_prompt = st.session_state.human_prompt
        result = st.session_state.conversation.invoke(human_prompt)
        llm_response = result['response']
        st.session_state.history.append(Message("human", human_prompt))
        st.session_state.history.append(Message("ai", llm_response))
        st.session_state.token_count += cb.total_tokens

load_css()
initialize_session_state()

st.markdown('<div class="section-title">💬 ChatDPT - Your Personal Travel Assistant 💬</div>', unsafe_allow_html=True)
chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
token_usage_placeholder = st.empty()

with chat_placeholder:
    for chat in st.session_state.history:
        icon_path = "static/kkum.png" if chat.origin == "ai" else "static/tourist.png"
        if chat.origin == "human":
            message_col, icon_col = st.columns([9, 1])  # Swap the order for human messages
        else:
            icon_col, message_col = st.columns([1, 9])  # Keep the order for AI messages
        with icon_col:
            st.image(icon_path, width=32)
        with message_col:
            message_class = "ai-bubble" if chat.origin == "ai" else "human-bubble"
            st.markdown(f'<div class="chat-bubble {message_class}">{chat.message}</div>', unsafe_allow_html=True)
    for _ in range(3):
        st.markdown("")

with prompt_placeholder:
    st.markdown("**Chat**")
    cols = st.columns((5, 2))
    cols[0].text_input(
        "Chat",
        value="Among these places, where should I visit first?",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Send",
        type="primary",
        on_click=on_click_callback,
    )

token_usage_placeholder.caption(f"""
    Used {st.session_state.token_count} tokens.
""")

components.html("""
<script>
    const streamlitDoc = window.parent.document;
    const buttons = Array.from(
        streamlitDoc.querySelectorAll('.stButton > button')
    );
    const submitButton = buttons.find(
        el => el.innerText === 'Send'
    );
    streamlitDoc.addEventListener('keydown', function(e) {
        switch (e.key) {
            case 'Enter':
                submitButton.click();
                break;
        }
    });
</script>
""", height=0, width=0)



st.markdown("---")
st.write(
    "Share on social media with the hashtag [#DaeTRIP](https://www.instagram.com/daejeontourism/) !"
)