# Modified from Johannes Rieke's example code
import streamlit as st
from snowflake.snowpark import Session

# Establish Snowflake session
@st.cache_resource
def create_session():
    return Session.builder.configs(st.secrets.snowflake).create()

# Load data table
@st.cache_data
def load_data(table_name):
    
    ## Calling session
    session = create_session()

    ## Read in data tbl
    table = session.table(table_name)
    
    ## Do some computation on it
    table = table.limit(100)
    
    ## Collect the results. This will run the query and download the data
    table = table.collect()
    return table
