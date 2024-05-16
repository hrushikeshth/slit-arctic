import streamlit as st
import pandas as pd

def get_tables2():
        conn = st.connection("snowflake")
        query = "SELECT TABLE_NAME FROM AMZ_VENDOR_DATA.INFORMATION_SCHEMA.TABLES"
        df = pd.read_sql(query, conn)
        return df["TABLE_NAME"].tolist()