import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import datetime


# Define the path to the users.txt file
USERS_FILE = 'users.txt'

# Define a file to store user query counts
QUERY_COUNT_FILE = 'query_counts.txt'

DAILY_QUERY_LIMIT = 2

def user_exists(username):
    with open(USERS_FILE, 'r') as users_file:
        for line in users_file:
            user, _ = line.strip().split(':')
            if user == username:
                return True
    return False

def load_query_counts():
    if os.path.exists(QUERY_COUNT_FILE):
        with open(QUERY_COUNT_FILE, 'r') as count_file:
            query_counts = {}
            today = datetime.date.today().isoformat()
            for line in count_file:
                parts = line.strip().split(':')
                if len(parts) == 3:
                    user, date, count = parts
                    if date == today:
                        query_counts[user] = {'date': date, 'count': int(count)}
            return query_counts
    return {}


def save_query_counts(query_counts):
    with open(QUERY_COUNT_FILE, 'w') as count_file:
        today = datetime.date.today().isoformat()
        for user, user_data in query_counts.items():
            if user_data['date'] == today:
                count_file.write(f"{user}:{today}:{user_data['count']}\n")


def is_query_limit_reached(username, query_counts, limit=DAILY_QUERY_LIMIT):
    today = datetime.date.today().isoformat()
    user_data = query_counts.get(username, {})
    
    if 'date' in user_data and user_data['date'] == today:
        return user_data.get('count', 0) >= limit
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
    if response:
        st.success(response)
        return True
    else:
        st.error('Query execution failed.')
        return False

OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
openai_api_key = "sk-" + OPAK_KEY

username = st.text_input('Username:')
query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')

query_counts = load_query_counts()

if user_exists(username):
    if not is_query_limit_reached(username, query_counts):
        st.header('Output')
        if generate_response(query_text):
            # Only increment the count if the query was successful
            query_counts[username] = query_counts.get(username, 0) + 1
            save_query_counts(query_counts)
    else:
        st.error('Query limit (25 successful queries per day) reached for this user.')
else:
    st.error('User not found. Please check your username.')
