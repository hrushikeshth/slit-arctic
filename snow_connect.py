import streamlit as st
import pandas as pd

def get_tables2():
        conn = st.connection("snowflake")
        df = conn.query("SELECT TABLE_NAME FROM AMZ_VENDOR_DATA.INFORMATION_SCHEMA.TABLES;", ttl=600)
        return df["TABLE_NAME"].tolist()
