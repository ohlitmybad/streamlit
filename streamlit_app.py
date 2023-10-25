import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Define the path to the users.txt file
USERS_FILE = 'users.txt'

# Define a file to store user query counts
QUERY_COUNT_FILE = 'query_counts.txt'

# Function to check user credentials
def authenticate_user(username, password):
    with open(USERS_FILE, 'r') as users_file:
        for line in users_file:
            user, passwd = line.strip().split(':')
            if user == username and passwd == password:
                return True
    return False


def load_query_counts():
    if os.path.exists(QUERY_COUNT_FILE):
        with open(QUERY_COUNT_FILE, 'r') as count_file:
            query_counts = {}
            for line in count_file:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    user, count = parts
                    query_counts[user] = int(count)
            return query_counts
    return {}


# Function to save user query counts
def save_query_counts(query_counts):
    with open(QUERY_COUNT_FILE, 'w') as count_file:
        for user, count in query_counts.items():
            count_file.write(f"{user}:{count}\n")

# Function to check if a user has reached their query limit
def is_query_limit_reached(username, query_counts, limit=3):
    return query_counts.get(username, 0) >= limit

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

query_counts = load_query_counts()

if authenticate_user(username, password):
    if not is_query_limit_reached(username, query_counts):
        st.header('Output')
        generate_response(query_text)
        # Update the query count for the user
        query_counts[username] = query_counts.get(username, 0) + 1
        save_query_counts(query_counts)
    else:
        st.error('Query limit (10 queries per day) reached for this user.')
else:
    st.error('Authentication failed. Please check your credentials.')
