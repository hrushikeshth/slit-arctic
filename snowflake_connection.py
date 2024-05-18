from typing import Any, Dict
import pandas as pd
import streamlit as st
from snowflake.snowpark.session import Session
from snowflake.snowpark.version import VERSION


class SnowflakeConnection:
    def __init__(self):
        self.connection_parameters = self._get_connection_parameters_from_env()
        self.session = None

    @staticmethod
    def _get_connection_parameters_from_env() -> Dict[str, Any]:
        connection_parameters = {
            "account": st.secrets["ACCOUNT"],
            "user": st.secrets["USER_NAME"],
            "password": st.secrets["PASSWORD"],
            "warehouse": st.secrets["WAREHOUSE"],
            "database": st.secrets["DATABASE"],
            "schema": st.secrets["SCHEMA"],
            "role": st.secrets["ROLE"],
        }
        return connection_parameters

    def get_session(self):
        if self.session is None:
            self.session = Session.builder.configs(self.connection_parameters).create()
            self.session.sql_simplifier_enabled = True
        return self.session
    
    def get_tables(self):
        query = "SELECT table_name FROM amz_vendor_data.information_schema.tables"
        df = pd.read_sql(query, self.session)
        return df["TABLE_NAME"].tolist()

    def get_sample_data(self, table_name, limit=50):
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(query, self.session)
        return df
