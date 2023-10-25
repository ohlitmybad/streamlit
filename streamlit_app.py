import streamlit as st
import pandas as pd
import os
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

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

if authenticate_user(username, password):
        st.header('Output')
        generate_response(query_text)
else:
    st.error('Authentication failed. Please check your credentials.')

