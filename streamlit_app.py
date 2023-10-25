import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import sqlite3
import datetime

st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')

# Define the rate-limiting settings
MAX_QUERIES_PER_DAY = 4  # Adjust this value according to your needs
DB_FILE = "user_query_counts.db"

def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def load_query_count(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT query_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    return 0

def update_query_count(user_id, query_count):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, query_count) VALUES (?, ?)", (user_id, query_count))
    conn.commit()

def load_csv():
    df = pd.read_csv("data.csv")
    return df

def generate_response(input_query):
    user_id = st.session_state.user_id

    # Load the user's current query count
    query_count = load_query_count(user_id)

    if query_count >= MAX_QUERIES_PER_DAY:
        st.error(f"Rate limit exceeded. You can make {MAX_QUERIES_PER_DAY} queries per day.")
        return

    llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0, openai_api_key=openai_api_key)
    df = load_csv()
    
    # Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
    
    # Perform Query using the Agent
    response = agent.run(input_query)

    # Update the query count and store it in the database
    query_count += 1
    update_query_count(user_id, query_count)

    st.success(response)

OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
openai_api_key = "sk-" + OPAK_KEY

# Use user-specific session state to store the user ID
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Create the users table in the database if it doesn't exist
conn = create_connection()
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, query_count INTEGER)")
conn.commit()

query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')

st.header('Output')
generate_response(query_text)
