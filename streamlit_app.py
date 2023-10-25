import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from datetime import datetime

# Define the path to the users.txt file
USERS_FILE = 'users.txt'

# Function to check user credentials
def authenticate_user(username, password):
    with open(USERS_FILE, 'r') as users_file:
        for line in users_file:
            user, passwd = line.strip().split(':')
            if user == username and passwd == password:
                return True
    return False

st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')

# Function to load user data and reset query count daily
def load_user_data():
    data = {}
    today = datetime.now().date()
    with open("user_data.txt", "a+") as user_data_file:
        user_data_file.seek(0)
        for line in user_data_file:
            user, date, count = line.strip().split(':')
            if today != datetime.strptime(date, "%Y-%m-%d").date():
                # Reset query count for a new day
                data[user] = 0
            else:
                data[user] = int(count)
    return data

def generate_response(input_query):
    llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0, openai_api_key=openai_api_key)
    df = load_csv()
    # Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
    # Perform Query using the Agent
    response = agent.run(input_query)
    return st.success(response)

OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
openai_api_key = "sk-" + OPAK_KEY

username = st.text_input('Username:')
password = st.text_input('Password:', type="password")
query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')

user_data = load_user_data()

if authenticate_user(username, password):
    if user_data.get(username, 0) < 10:
        st.header('Output')
        generate_response(query_text)
        # Update the query count for the user
        user_data[username] = user_data.get(username, 0) + 1
        with open("user_data.txt", "a") as user_data_file:
            user_data_file.write(f"{username}:{datetime.now().date()}:{user_data[username]}\n")
    else:
        st.error('Query limit (10 queries per day) reached for this user.')
else:
    st.error('Authentication failed. Please check your credentials.')
