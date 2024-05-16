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

# Add survey questions with sliders
st.write("---")
st.markdown("# DaeTRIP Welcome Survey")
# Define the questions
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
        key=f"question_{i}_slider",  # Unique key for each slider
    )
    responses.append(response)

# Initialize prompt
prompt = ""

# Submit button
if st.button("Submit"):
    # Collect the responses and create a prompt
    prompt = "Based on the following responses to travel preference questions, please provide an analysis of my traveler type and recommend relevant touristic sites or activities specifically in Daejeon, South Korea:\n\n"
    for i, (question, response) in enumerate(zip(questions, responses)):
        prompt += f"{i+1}. {question} (Response: {response})\n"

    # Send the prompt to the OpenAI API using the ConversationChain
    result = st.session_state.conversation.invoke(prompt)
    summary = result['response']

    # Display the summary
    st.write(summary)
    prompt = summary

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

st.title("Hello DaeTRIPer 🌠")

chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()


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

credit_card_placeholder.caption(f"""
    Used {st.session_state.token_count} tokens.
""")
# credit_card_placeholder.caption(f"""
#     Used {st.session_state.token_count} tokens \n
#     Debug Langchain conversation: {st.session_state.conversation.memory.buffer}
# """)

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