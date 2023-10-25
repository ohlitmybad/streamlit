import streamlit as st
import sqlite3
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')

def load_csv():
    df = pd.read_csv("data.csv")
    return df

def authenticate_user(username, password):
    # Connect to the users database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Check if the provided username and password match any user in the database
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    conn.close()
    return user

def generate_response(input_query, username):
    # Check if the user is authenticated
    user = authenticate_user(username, input_query)

    if user is None:
        return st.error("Authentication failed. Please check your credentials.")
    
    llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0, openai_api_key=openai_api_key)
    df = load_csv()
    # Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
    # Perform Query using the Agent
    response = agent.run(input_query)
    return st.success(response)

OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
openai_api_key = "sk-" + OPAK_KEY

# User authentication
username = st.text_input('Username:', key='username')
password = st.text_input('Password:', key='password', type='password')

if st.button('Log In'):
    response = authenticate_user(username, password)
    if response:
        st.success("Authentication successful. You are now logged in.")
    else:
        st.error("Authentication failed. Please check your credentials.")
else:
    query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')
    st.header('Output')
    generate_response(query_text, username)
