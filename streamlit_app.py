import os
import streamlit as st
import pandas as pd
import base64
from langchain.chat_models import ChatOpenAI
from langchain_experimental.agents.agent_toolkits.pandas.base import (
    create_pandas_dataframe_agent,
)
from langchain.agents.agent_types import AgentType
import datetime
from streamlit import spinner as st_spinner
import openai
 
openai.api_key = os.environ["OPENAI_API_KEY"]

USERS_FILE = 'users.txt'

# Define a file to store user query counts
QUERY_COUNT_FILE = 'query_counts.txt'

DAILY_QUERY_LIMIT = 10

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
            for line in count_file:
                user, date, count = line.strip().split(':')
                if user not in query_counts:
                    query_counts[user] = {}
                query_counts[user][date] = int(count)
            return query_counts
    return {}

def save_query_counts(query_counts):
    with open(QUERY_COUNT_FILE, 'w') as count_file:
        for user, data in query_counts.items():
            for date, count in data.items():
                count_file.write(f"{user}:{date}:{count}\n")

def is_query_limit_reached(username, query_counts, limit=DAILY_QUERY_LIMIT):
    today = datetime.date.today().isoformat()
    user_data = query_counts.get(username, {})
    
    if today in user_data:
        return user_data[today] >= limit
    return False


st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')



def load_csv():
    df = pd.read_csv("data.csv")
    return df

def generate_response(input_query):
    llm = ChatOpenAI(model_name='gpt-3.5-turbo-0125', temperature=0, openai_api_key=openai.api_key)
    df = load_csv()
    # Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
    input_query = input_query.replace("POSS+/-", "((Interceptions per 90 + Sliding tackles per 90 + (Defensive duels per 90 * Defensive duels won, % / 100)) * ((Passes per 90 + Offensive duels per 90)/100) - (((100 - Accurate passes, %)*(Passes per 90 / 100)+(100 - Offensive duels won, %)*(Offensive duels per 90 / 100)) * (100/(Passes per 90 + Offensive duels per 90))))")
    # Perform Query using the Agent
    response = agent.run(input_query)
    if response:
        st.success(response)
        return True
    else:
        st.error('Query execution failed.')
        return False
        


username = st.text_input('', placeholder='Username')
query_text = st.text_input('', placeholder='Enter query here ...')

query_counts = load_query_counts()



if user_exists(username):
    if not is_query_limit_reached(username, query_counts):
        st.header('Output')
        with st_spinner(""):  # Use st_spinner to display a spinner while processing the query
            if generate_response(query_text):
    # Only increment the count if the query was successful
                user_data = query_counts.get(username, {})
                today = datetime.date.today().isoformat()
                user_data[today] = user_data.get(today, 0) + 1
                query_counts[username] = user_data
                save_query_counts(query_counts)

    else:
        st.error('Daily query limit (10) reached for this user.')
else:
    st.error('User not found. Check your username in your DataMB Pro account.')
