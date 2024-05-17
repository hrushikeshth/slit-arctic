from typing import Any, Dict
import pandas as pd
import streamlit as st
#from snowflake.snowpark.session import Session
#from snowflake.snowpark.version import VERSION
"""
class SnowflakeConnection:
    def __init__(self):
        #self.connection_parameters = self._get_connection_parameters_from_env()
        self.conn = None

    @staticmethod
    def _get_connection_parameters_from_env() -> Dict[str, Any]:
        connection_parameters = {
            "account": st.secrets["account"],
            "user": st.secrets["user_name"],
            "password": st.secrets["password"],
            "warehouse": st.secrets["warehouse"],
            "database": st.secrets["database"],
            "schema": st.secrets["schema"],
            "role": st.secrets["role"],
        }
        return connection_parameters

    def get_session(self):
        if self.session is None:
            self.session = Session.builder.configs(self.connection_parameters).create()
            self.session.sql_simplifier_enabled = True
        return self.session

    def get_conn(self):
        if self.conn is None:
            # Initialize connection.
            conn = st.connection("snowflake")
        return self.conn

    
    def get_tables(self):
        conn = st.connection("snowflake")
        query = "SELECT TABLE_NAME FROM AMZ_VENDOR_DATA.INFORMATION_SCHEMA.TABLES"
        df = pd.read_sql(query, conn)
        return df["TABLE_NAME"].tolist()

    def get_data(self, table_name, limit=50):
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        df = pd.read_sql(query, self.conn)
        return df
"""