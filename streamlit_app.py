import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Function to check if a user exists in the 'users.txt' file
def user_exists(username):
    with open('users.txt', 'r') as users_file:
        for line in users_file:
            user, _ = line.strip().split(':')
            if user == username:
                return True
    return False

# Your OpenAI key
openai_api_key = "YOUR_OPENAI_API_KEY"

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

username = st.text_input('Username:')

# Check if the user exists in the 'users.txt' file
if user_exists(username):
    st.header('Output')
    query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')
    if generate_response(query_text):
        st.success('Query successful.')
else:
    st.error('User not found. Please check your username.')

# Note: There is no need for password input or query count in this simplified version.
