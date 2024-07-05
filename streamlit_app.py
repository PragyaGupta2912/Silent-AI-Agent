import streamlit as st
import openai
import psycopg2
from datetime import datetime
from llama_index.llms.openai import OpenAI

try:
    from llama_index import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader
except ImportError:
    from llama_index.core import VectorStoreIndex, ServiceContext, Document, SimpleDirectoryReader

# Set up the PostgreSQL connection and create table if it doesn't exist
def init_db():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="pgadmin2912",
        host="localhost",
        port=5432  # replace with your actual port, ensure it is an integer
    )
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "Flagged_Questions" (
            "ID" SERIAL PRIMARY KEY,
            "Date" VARCHAR(10),
            "Time" VARCHAR(8),
            "Question" TEXT,
            "SAIA Response" TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

# Save the high-rated response to the PostgreSQL table
def save_high_rated_response(question, response):
    conn, cursor = init_db()
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    cursor.execute('''
        INSERT INTO "Flagged_Questions" ("Date", "Time", "Question", "SAIA Response")
        VALUES (%s, %s, %s, %s)
    ''', (date, time, question, response))
    conn.commit()
    cursor.close()
    conn.close()

# Function to check if the response is relevant
def is_response_relevant(response):
    irrelevant_phrases = ["Apologies", "provided information does not specify", "document does not provide", "not detailed in the available content", " not explicitly provided", "not explicitly mentioned", "not elaborated", "not have the information", "lack of data", "not available"]
    for phrase in irrelevant_phrases:
        if phrase in response:
            return False
    return True

# Default prompt for irrelevant responses
default_prompt = "Please contact the live agent for your query at customerservice@tttech-auto.com"

st.set_page_config(page_title="Chat with TTTech Auto's Silent AI Agent", page_icon="🤖", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with TTTech Auto's Silent AI Agent to get your tech queries answered  💬🤖")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about TTTech Auto's Services!"}
    ]
    st.session_state.ratings = [None]  # Initialize the ratings history with None
    st.session_state.new_response_generated = False  # Track if a new response was generated

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the TTTech Auto docs – hang tight! This should take 1-2 minutes."):
        reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        docs = reader.load_data()
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You have expert level technical knowledge about TTTech Auto's products, specifically about Motionwise. If a question arises for which TTTech Auto has not provided information in the document, you must explicitly acknowledge the lack of data and clarify that the information is not available. You are an expert on the TTTech Auto's products and your job is to answer technical questions. Assume that all questions are related to the TTTech Auto's product specifications. Keep your answers technical and based on facts – do not hallucinate features."))
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys():  # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.new_response_generated = False  # Reset the new response flag

def display_rating_options(response_id):
    if st.session_state.ratings[response_id] is None:
        st.write("### How would you rate this response?")
        cols = st.columns(3)
        if cols[0].button('1', key=f'1_{response_id}'):
            st.session_state.ratings[response_id] = 1
            st.experimental_rerun()  # Refresh the page to show the rating
        if cols[1].button('2', key=f'2_{response_id}'):
            st.session_state.ratings[response_id] = 2
            st.experimental_rerun()  # Refresh the page to show the rating
        if cols[2].button('3', key=f'3_{response_id}'):
            st.session_state.ratings[response_id] = 3
            save_high_rated_response(st.session_state.messages[response_id - 1]["content"], st.session_state.messages[response_id]["content"])
            st.experimental_rerun()  # Refresh the page to show the rating

# Ensure ratings list is in sync with messages list
while len(st.session_state.ratings) < len(st.session_state.messages):
    st.session_state.ratings.append(None)

# Display the prior chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant" and st.session_state.ratings[i] is not None:
            st.write(f"You rated this response: {st.session_state.ratings[i]}")

# If the last message is from the assistant and a new response was generated, show rating options
if st.session_state.messages[-1]["role"] == "assistant" and st.session_state.new_response_generated:
    display_rating_options(len(st.session_state.messages) - 1)

# If the last message is not from the assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            if not is_response_relevant(response.response):
                response.response = default_prompt
                # Automatically save flagged question to database
                save_high_rated_response(prompt, response.response)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message)  # Add response to message
                st.session_state.ratings.append(None)  # Append a placeholder for the new rating
            else:
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message)  # Add response to message
                st.session_state.ratings.append(None)  # Append a placeholder for the new rating
                st.session_state.new_response_generated = True  # Mark that a new response was generated
                display_rating_options(len(st.session_state.messages) - 1)  # Display rating options for the new response
