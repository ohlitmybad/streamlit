import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
import datetime

st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')

# Define the rate-limiting settings
MAX_QUERIES_PER_DAY = 10  # Adjust this value according to your needs

# Define a dictionary to store the query counts for each user
user_query_counts = {}

def load_csv():
    df = pd.read_csv("data.csv")
    return df

def generate_response(input_query):
    user_id = st.session_state.user_id

    # Check if the user has exceeded their rate limit
    if user_id not in user_query_counts:
        user_query_counts[user_id] = 1
    else:
        user_query_counts[user_id] += 1

    if user_query_counts[user_id] > MAX_QUERIES_PER_DAY:
        st.error(f"Rate limit exceeded. You can make {MAX_QUERIES_PER_DAY} queries per day.")
        return

    llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0, openai_api_key=openai_api_key)
    df = load_csv()
    
    # Create Pandas DataFrame Agent
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
    
    # Perform Query using the Agent
    response = agent.run(input_query)
    st.success(response)

OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
openai_api_key = "sk-" + OPAK_KEY

# Use user-specific session state to store the user ID
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Reset the user's query count at the start of each day
today = datetime.date.today()
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = today
elif st.session_state.last_reset_date < today:
    user_query_counts = {}
    st.session_state.last_reset_date = today

query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')

st.header('Output')
generate_response(query_text)
