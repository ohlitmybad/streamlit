import streamlit as st
import pandas as pd
import os

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
    # Your OpenAI-related code here
    # ...

    OPAK_KEY = "QOxvASrYaXeRFFHgajIdT3BlbkFJkQ37OFVOZVOc8t07WJI5"
    openai_api_key = "sk-" + OPAK_KEY

username = st.text_input('Username:')
password = st.text_input('Password:', type="password")
query_text = st.text_input('Enter your query:', placeholder='Enter query here ...')

if st.button('Login'):
    if authenticate_user(username, password):
        st.header('Output')
        generate_response(query_text)
    else:
        st.error('Authentication failed. Please check your credentials.')

