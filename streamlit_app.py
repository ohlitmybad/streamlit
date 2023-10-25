import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from datetime import datetime

# Define the path to the users.txt file
USERS_FILE = 'users.txt'

# Define a file to store user query counts and timestamps
QUERY_COUNT_FILE = 'query_counts.txt'

# Function to check user credentials
def authenticate_user(username, password):
    with open(USERS_FILE, 'r') as users_file:
        for line in users_file:
            user, passwd = line.strip().split(':')
            if user == username and passwd == password:
                return True
    return False

# Function to load and update query counts
def update_query_counts(query_counts):
    current_time = datetime.now()
    for username, data in list(query_counts.items()):
        # Check if the data is within the current rolling month
        first_query_time = data['first_query']
        if current_time - first_query_time < timedelta(days=30):
            # Still within the rolling month, keep the data
            pass
        else:
            # It's a new rolling month, remove the old data
            query_counts.pop(username)
    return query_counts

# Function to check if a user has reached their rolling monthly query limit
def is_query_limit_reached(username, query_counts, limit=3):
    if username in query_counts:
        return query_counts[username]['count'] >= limit
    return False

st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')

def load_csv():
    df = pd.read_csv("data.csv")
    return df

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

query_counts = update_query_counts(query_counts)

if authenticate_user(username, password):
    if not is_query_limit_reached(username, query_counts):
        st.header('Output')
        generate_response(query_text)
        # Update the query count for the user
        current_time = datetime.now()
        if username in query_counts:
            query_counts[username]['count'] += 1
        else:
            query_counts[username] = {'count': 1, 'first_query': current_time}
        with open(QUERY_COUNT_FILE, 'w') as count_file:
            for user, data in query_counts.items():
                count_file.write(f"{user}:{data['count']}:{data['first_query']}\n")
    else:
        st.error('Query limit (1000 queries per rolling month) reached for this user.')
else:
    st.error('Authentication failed. Please check your credentials.')
