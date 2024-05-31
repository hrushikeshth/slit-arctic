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

# Replicate Credentials
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

    # Hardcoding the temperature & sampling value to limit repetitive & nonsensical tokens.
    temperature = 0.3
    top_p = 0.9

    # Initialize Snowflake connection
    snowflake_conn = SnowflakeConnection()

    # Get Snowflake session (optional if you don't need to use the session directly)
    session = snowflake_conn.get_session()

    # Get the list of dbs from Snowflake
    dblist = snowflake_conn.get_db()

    # Select and display data table
    selected_db = st.selectbox("Select a database", dblist, index=None,
                               placeholder="None Selected")

    # Get the list of tables from the schema
    if selected_db is not None:
        schema = snowflake_conn.get_schema(selected_db)
        selected_sch = st.selectbox("Select a schema", schema, index=None,
                                    placeholder="None Selected")
        if selected_sch is not None:
            # Get the list of tables from the schema
            tables = snowflake_conn.get_tables(selected_db, selected_sch)
            # Display the tables in a dropdown menu
            selected_table = st.selectbox("Select a table", tables, index=None,
                                          placeholder="None Selected")
        else:
            selected_table = None
    else:
        selected_table = None

# Accepting file input from User
file_upload = st.file_uploader("Upload your Table in CSV format (Only 1 file at a time)", type=['csv'])

# Reading the CSV file in a Dataframe
def read_csv_file(file_upload):
    df = pd.read_csv(file_upload)
    text = df.to_string(index=False)  # Convert DataFrame to string
    return text

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": get_template_message()}]
    st.session_state.messages.append({"role": "assistant", "content": "Hi. I'm your dbt Assistant, based on Arctic, a new & efficient language model by Snowflake. You can start by uploading your file above and maybe by asking me to generate a YAML file?"})
    st.session_state.data_snippets = []  # Store historical data snippets

# Display or clear chat messages
for message in st.session_state.messages[1:]:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi. I'm your dbt Assistant, based on Arctic, a new & efficient language model by Snowflake. You can start by uploading your file above and maybe by asking me to generate a YAML file?"}]
    st.session_state.data_snippets = []  # Reset historical data snippets

st.sidebar.button('Clear chat history', on_click=clear_chat_history)
st.sidebar.caption('App by [Hrushi](https://www.linkedin.com/in/hrushikeshth/) as an Entrant in [The Future of AI is Open (Hackathon)](https://arctic-streamlit-hackathon.devpost.com/), demonstrating the new LLM by Snowflake called [Snowflake Arctic](https://www.snowflake.com/blog/arctic-open-and-efficient-foundation-language-models-snowflake)')
st.sidebar.caption('The app repository can be found [here](https://github.com/hrushikeshth/slit-arctic)')

# To make sure user aren't sending too much text to the Model
@st.cache_resource(show_spinner=False)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

# Function for generating Snowflake Arctic response
def generate_arctic_response(prompt_str):
    if st.session_state.messages[0]["role"] == "assistant":
        # Include the initial templated message in the prompt string
        prompt_str = "assistant\n" + st.session_state.messages[0]["content"] + "\n" + prompt_str
        
    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                                  input={"prompt": prompt_str,
                                         "prompt_template": r"{prompt}",
                                         "temperature": temperature,
                                         "top_p": top_p,
                                         }):
        yield str(event)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    # Construct the prompt string with all historical data snippets
    prompt_str = "\n".join(st.session_state.data_snippets) + "\n"
    
    if file_upload is not None:
        text = read_csv_file(file_upload)
        prompt_str += text + "\n"
    elif selected_table is not None:
        # Get sample data from the selected table
        sample_data = snowflake_conn.get_sample_data(selected_db, selected_sch, selected_table)
        sample_dt_to_txt = sample_data.to_string(index=False)  # Convert DataFrame to string
        data_snippet = f"Database: {selected_db}, Schema: {selected_sch}, Table: {selected_table}\nSample Data: {sample_dt_to_txt}"
        prompt_str += "CURRENT TABLE SELECTION - " + data_snippet + "\n"
        # Store the new data snippet in the session state
        data_snippet = "PREVIOUS TABLE SELECTION - " + data_snippet + "\n\n"
        st.session_state.data_snippets.append(data_snippet)
    
    prompt_str += "user\n" + prompt + "\nassistant\n"
    
    # Append user message to session state without data snippet
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🙋🏻‍♂️"):
        st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant", avatar="❄️"):
            response = generate_arctic_response(prompt_str)
            full_response = "".join(response)
            st.write(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
