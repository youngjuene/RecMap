import os
import openai
from dataclasses import dataclass
from typing import Literal
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
import streamlit.components.v1 as components

openai.api_key = st.secrets["openai_api_key"]

st.set_page_config(
    page_title="daetripp", page_icon="🖼️", initial_sidebar_state="collapsed"
)
st.write("---")
st.markdown("# DaeTRIP Welcome Survey")

# Define the questions
questions = [
    "I prefer travel experiences that incorporate technology and efficiency.",
    "I enjoy participating in local events and engaging with the community when traveling.",
    "I am open to trying new and adventurous activities during my trips.",
    "I prioritize comfort and relaxation over exploring new places.",
    "I value cultural immersion and learning about local traditions."
]

# Create sliders for each question
responses = []
for i, question in enumerate(questions):
    response = st.slider(
        question,
        min_value=1,
        max_value=5,
        key=f"question_{i}_slider",  # Unique key for each slider
    )
    responses.append(response)

# Initialize prompt
prompt = ""

# Submit button
if st.button("Submit"):
    # Collect the responses and create a prompt
    prompt = "Based on the five responses to the travel preference questions answered on a scale of 1 to 5, please provide a holistic analysis of my traveler type with a singular, well-rounded description. Recommend three to four relevant touristic sites or activities specifically in Daejeon, South Korea, and provide explanations for how these recommendations align with the traveler type description. Additionally, present the recommendations as a connected single-day itinerary. Finally, present the information in an organized markdown format with concise details and proper usage of bold fonts for better readability.:\n"
    for i, (question, response) in enumerate(zip(questions, responses)):
        prompt += f"{i+1}. {question} (Response: {response})\n"

    # Send the prompt to the OpenAI API using the ConversationChain
    result = st.session_state.conversation.invoke(prompt)
    summary = result['response']

    # Display the summary
    st.write(summary)
    prompt = summary

# new part
import re
# Define a dictionary that maps keywords to relevant travel site URLs
keyword_urls = {
    "cultural": "https://daejeontour.co.kr/en/index.do",
    "nature": "https://www.visit.daejeon.go.kr/eng/attractions/natural_resources.asp",
    "food": "https://www.visit.daejeon.go.kr/eng/attractions/food.asp",
    "adventure": "https://www.visit.daejeon.go.kr/eng/attractions/activities.asp",
    "luxury": "https://www.visit.daejeon.go.kr/eng/attractions/accommodation.asp",
    # Add more keywords and URLs as needed
}

# After displaying the summary
if prompt:
    # Extract the recommended sites or activities from the summary
    recommended_sites = re.findall(r"[\w\s]+?\.", summary)

    # Create link buttons for each recommended site or activity
    for site in recommended_sites:
        site_name = site.strip(".")
        site_keywords = site_name.lower().split()

        for keyword in keyword_urls.keys():
            if keyword in site_keywords:
                url = keyword_urls[keyword]
                st.link_button(f"Visit {site_name}", url)
                break
        else:
            # If no matching keyword is found, use a default URL
            default_url = "https://www.visit.daejeon.go.kr/eng/attractions/index.asp"
            st.link_button(f"Visit {site_name}", default_url)

    # Add link buttons for general categories
    st.link_button("Cultural Sites", keyword_urls["cultural"])
    st.link_button("Nature Sites", keyword_urls["nature"])
    st.link_button("Food & Dining", keyword_urls["food"])
    st.link_button("Adventure Activities", keyword_urls["adventure"])
    st.link_button("Luxury Accommodations", keyword_urls["luxury"])
    
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

st.title("ChatDPT 🤖")
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
    cols = st.columns((6, 1))
    cols[0].text_input(
        "Chat",
        value="Among these places, where should I visit first?",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Submit",
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
        el => el.innerText === 'Submit'
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