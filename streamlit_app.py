import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title='DataMB Chat ⚽')
st.title('DataMB Chat ⚽')

def load_csv():
    df = pd.read_csv("data.csv")
    return df

def generate_response(input_query):
    user_id = st.session_state.user_id
    current_date = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect('user_activity.db')
    c = conn.cursor()

    # Retrieve user activity data from the database
    c.execute('SELECT query_count, last_query_date FROM user_activity WHERE user_id=?', (user_id,))
    user_data = c.fetchone()

    if user_data:
        query_count, last_query_date = user_data
        if last_query_date != current_date:
            # Reset the query count if it's a new day
            query_count = 0

        if query_count >= 3:
            st.error("You've reached your daily query limit (3 queries per day).")
            return

    # Create Pandas DataFrame Agent and perform the query
    llm = ChatOpenAI(model_name='gpt-3.5-turbo-0613', temperature=0, openai_api_key=openai_api_key)
    df = load_csv()
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)
    response = agent.run(input_query)

    # Update the user activity data in the database
    if user_data:
        query_count += 1
        c.execute('UPDATE user_activity SET query_count=?, last_query_date=? WHERE user_id=?',
                  (query_count, current_date, user_id))
    else:
        c.execute('INSERT INTO user_activity (user_id, query_count, last_query_date) VALUES (?, ?, ?)',
                  (user_id, 1, current_date))

    conn.commit()
    conn.close()
    st.success(response)

OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
openai_api_key = "sk-" + OPAK_KEY

if 'user_id' not in st.session_state:
    # Generate a user ID based on session information
    st.session_state.user_id = hash(str(st.session) + str(datetime.now()))

query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')

st.header('Output')
generate_response(query_text)
