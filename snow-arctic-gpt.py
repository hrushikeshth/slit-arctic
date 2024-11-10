import streamlit as st
import pandas as pd
import replicate
import os
import numpy
from transformers import AutoTokenizer
from template import get_template_message
from utils.snowflake_connection import SnowflakeConnection
from snowflake.connector.errors import DatabaseError  # Import DatabaseError

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
    try:
        snowflake_conn = SnowflakeConnection()
        dblist = snowflake_conn.get_db() if not snowflake_conn.connection_failed else []
        schema = []
        tables = []
    except DatabaseError as e:
        st.error(f"Snowflake connection failed: {e}", icon="⚠️")
        dblist = []
        schema = []
        tables = []

    # Select and display data table
    selected_db = st.selectbox("Select a database", dblist, index=None,
                               placeholder="None Selected")

    # Get the list of tables from the schema
    if selected_db:
        try:
            schema = snowflake_conn.get_schema(selected_db)
            selected_sch = st.selectbox("Select a schema", schema, index=None,
                                        placeholder="None Selected")
            if selected_sch:
                tables = snowflake_conn.get_tables(selected_db, selected_sch)
                selected_table = st.selectbox("Select a table", tables, index=None,
                                              placeholder="None Selected")
            else:
                selected_table = None
        except DatabaseError as e:
            st.error(f"Error fetching schema or tables: {e}", icon="⚠️")
            selected_sch = None
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
st.sidebar.caption('App by [Hrushi](https://www.linkedin.com/in/hrushikeshth/) as an Entrant in [The Future of AI is Open (Hackathon)](https://arctic-streamlit-hackathon.devpost.com/), demonstrating the new LLM - Arctic by Snowflake, Inc.')

# User-provided prompt
if prompt := st.chat_input(placeholder="Ask anything to your Assistant"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar=icons["user"]):
        st.write(prompt)

    # Including table data snippet if table is selected
    if selected_table:
        try:
            data_snippet = snowflake_conn.get_sample_data(selected_db, selected_sch, selected_table)
            data_snippet_str = data_snippet.to_string(index=False) if not data_snippet.empty else "No data available."
            st.session_state.data_snippets.append(data_snippet_str)

            template_message = get_template_message()
            template_message += f"\n\nHere is a snippet of the table '{selected_table}' from the schema '{selected_sch}' in the database '{selected_db}':\n{data_snippet_str}\n\n"

            st.session_state.messages.append({"role": "data", "content": template_message})

            # Display assistant response
            with st.chat_message("assistant", avatar=icons["assistant"]):
                with st.spinner("Thinking..."):
                    response = replicate.run(
                        "a16z-infra/arctic-chat:latest",
                        input={
                            "prompt": template_message,
                            "token_max_length": 1000,
                            "temperature": temperature,
                            "top_p": top_p
                        }
                    )
                    st.write(response['choices'][0]['message']['content'])
                    st.session_state.messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        except DatabaseError as e:
            st.error(f"Error fetching data from table: {e}", icon="⚠️")

    # Handle case when no table is selected but file is uploaded
    elif file_upload:
        template_message = get_template_message()
        data_snippet_str = read_csv_file(file_upload)
        st.session_state.data_snippets.append(data_snippet_str)
        template_message += f"\n\nHere is a snippet of the uploaded file:\n{data_snippet_str}\n\n"
        
        st.session_state.messages.append({"role": "data", "content": template_message})

        # Display assistant response
        with st.chat_message("assistant", avatar=icons["assistant"]):
            with st.spinner("Thinking..."):
                response = replicate.run(
                    "a16z-infra/arctic-chat:latest",
                    input={
                        "prompt": template_message,
                        "token_max_length": 1000,
                        "temperature": temperature,
                        "top_p": top_p
                    }
                )
                st.write(response['choices'][0]['message']['content'])
                st.session_state.messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})

    # Handle case when neither table is selected nor file is uploaded
    else:
        with st.chat_message("assistant", avatar=icons["assistant"]):
            with st.spinner("Thinking..."):
                response = replicate.run(
                    "a16z-infra/arctic-chat:latest",
                    input={
                        "prompt": prompt,
                        "token_max_length": 1000,
                        "temperature": temperature,
                        "top_p": top_p
                    }
                )
                st.write(response['choices'][0]['message']['content'])
                st.session_state.messages.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
