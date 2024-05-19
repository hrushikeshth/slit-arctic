import streamlit as st
import pandas as pd
import replicate
import os
from transformers import AutoTokenizer
from template import get_template_message
from utils.snowflake_connection import SnowflakeConnection

# Set assistant & user icons
icons = {"assistant": "❄️", "user": "🙋🏻‍♂️"}

# App title
st.set_page_config(page_title="❄️ Arctic dbt Assistant")

# Initialize Snowflake connection
snowflake_conn = SnowflakeConnection()

# Get Snowflake session (optional if you don't need to use the session directly)
session = snowflake_conn.get_session()

# Get the list of databases from Snowflake
dblist = snowflake_conn.get_db()

# Replicate Credentials and Database/Table Selection in Sidebar
def setup_sidebar():
    with st.sidebar:
        st.image('./dbt-seeklogo.svg', width=35)
        st.title(':blue[Arctic] dbt Assistant')
        if 'REPLICATE_API_TOKEN' in st.secrets:
            replicate_api = st.secrets['REPLICATE_API_TOKEN']
            st.success('Fuyioh! API Key Already Provided!', icon='🥳')
        else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
            if not (replicate_api.startswith('r8_') and len(replicate_api) == 40):
                st.warning('Please enter your Replicate API token.', icon='⚠️')
                st.markdown("**Don't have an API token?** Visit [Replicate](https://replicate.com) to get one.")

        os.environ['REPLICATE_API_TOKEN'] = replicate_api

        selected_db = st.selectbox("Select a database", dblist, index=None, placeholder="None Selected")
        if selected_db:
            schema = snowflake_conn.get_schema(selected_db)
            selected_sch = st.selectbox("Select a schema", schema, index=None, placeholder="None Selected")
            if selected_sch:
                tables = snowflake_conn.get_tables(selected_db, selected_sch)
                selected_table = st.selectbox("Select a table", tables, index=None, placeholder="None Selected")
                return replicate_api, selected_db, selected_sch, selected_table
        return replicate_api, None, None, None

replicate_api, selected_db, selected_sch, selected_table = setup_sidebar()

# Accepting file input from User
file_upload = st.file_uploader("Upload your Table in CSV format (Only 1 file at a time)", type=['csv'])

# Reading the CSV file in a Dataframe
def read_csv_file(file_upload):
    if file_upload is not None:
        df = pd.read_csv(file_upload)
        return df.to_string(index=False)
    return ""

text = read_csv_file(file_upload)

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": get_template_message()}]
    st.session_state.messages.append({"role": "assistant", "content": "Hi. I'm your dbt Assistant, based on Arctic, a new & efficient language model by Snowflake. You can start by uploading your file above and maybe by asking me to generate a YAML file?"})

# Display or clear chat messages
for message in st.session_state.messages[3:]:
    with st.chat_message(message["role"], avatar=icons[message["role"]]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm your dbt Assistant, based on Arctic, a new & efficient language model by Snowflake. You can start by uploading your file above and maybe by asking me to generate a YAML file?"}]

st.sidebar.button('Clear chat history', on_click=clear_chat_history)

st.sidebar.caption('App by [Hrushi](https://www.linkedin.com/in/hrushikeshth/) as an Entrant in [The Future of AI is Open (Hackathon)](https://arctic-streamlit-hackathon.devpost.com/), demonstrating the new LLM by Snowflake called [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake)')
# st.sidebar.caption('The app repository can be found [here](https://github.com/hrushikeshth/slit-arctic)')

# To make sure users aren't sending too much text to the Model
@st.cache_resource(show_spinner=False)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("user\n" + dict_message["content"] + "")
        else:
            prompt.append("assistant\n" + dict_message["content"] + "")
    
    prompt.append("assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    
    if get_num_tokens(prompt_str) >= 5000:
        st.error("Conversation length too long.")
        st.button('Clear chat history', on_click=clear_chat_history, key="clear_chat_history")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": 0.3,
                                  "top_p": 0.9,
                                  }):
        yield str(event)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    if file_upload:
        st.session_state.messages.append({"role": "user", "content": 'csv upload' + text})
    elif selected_table:
        sample_data = snowflake_conn.get_sample_data(selected_db, selected_sch, selected_table)
        sample_dt_to_txt = sample_data.to_string(index=False)
        st.session_state.messages.append({"role": "user", "content": selected_table + sample_dt_to_txt})
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🙋🏻‍♂️"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="❄️"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
