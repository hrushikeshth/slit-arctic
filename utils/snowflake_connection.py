from typing import Any, Dict
import pandas as pd
import streamlit as st
import snowflake.connector
import logger
import numpy
from snowflake.snowpark.session import Session
from snowflake.connector.errors import DatabaseError

class SnowflakeConnection:
    def __init__(self):
        self.connection_parameters = self._get_connection_parameters_from_env()
        self.session = None
        self.connector = None
        self.connection_failed = False

    @staticmethod
    def _get_connection_parameters_from_env() -> Dict[str, Any]:
        connection_parameters = {
            "account": st.secrets["account"],
            "user": st.secrets["user"],
            "password": st.secrets["password"],
            "warehouse": st.secrets["warehouse"],
            "database": st.secrets["database"],
            "schema": st.secrets["schema"],
            "role": st.secrets["role"],
        }
        return connection_parameters

    def get_session(self):
        if self.session is None:
            try:
                self.session = Session.builder.configs(self.connection_parameters).create()
                self.session.sql_simplifier_enabled = True
            except DatabaseError:
                self.connection_failed = True
                return None
        return self.session

    def get_connector(self):
        if self.connector is None:
            try:
                self.connector = snowflake.connector.connect(
                    account=self.connection_parameters["account"],
                    user=self.connection_parameters["user"],
                    password=self.connection_parameters["password"],
                    warehouse=self.connection_parameters["warehouse"],
                    database=self.connection_parameters["database"],
                    schema=self.connection_parameters["schema"],
                    role=self.connection_parameters["role"],
                )
            except DatabaseError:
                self.connection_failed = True
                return None
        return self.connector
    
    @st.cache_data(ttl=600)
    def get_db(_self):  # Renaming 'self' to '_self'
        query = "SELECT database_name FROM snowflake.information_schema.databases"
        conn = _self.get_connector()
        if conn:
            try:
                df = pd.read_sql(query, conn)
                return df["DATABASE_NAME"].tolist()
            except DatabaseError:
                _self.connection_failed = True
                return []
        else:
            return []

    @st.cache_data(ttl=600)
    def get_schema(_self, dbname):  # Renaming 'self' to '_self'
        query = f"SELECT schema_name FROM {dbname}.information_schema.schemata"
        conn = _self.get_connector()
        if conn:
            try:
                df = pd.read_sql(query, conn)
                return df["SCHEMA_NAME"].tolist()
            except DatabaseError:
                _self.connection_failed = True
                return []
        else:
            return []

    @st.cache_data(ttl=600)
    def get_tables(_self, dbname, schemaname):  # Renaming 'self' to '_self'
        query = f"SELECT table_name FROM {dbname}.information_schema.tables where table_schema = '{schemaname}'"
        conn = _self.get_connector()
        if conn:
            try:
                df = pd.read_sql(query, conn)
                logger.info('Complete')
                return df["TABLE_NAME"].tolist()
            except DatabaseError:
                _self.connection_failed = True
                return []
        else:
            return []

    @st.cache_data(ttl=600)
    def get_sample_data(_self, dbname, schemaname, table_name, limit=3):  # Renaming 'self' to '_self'
        query = f"SELECT * FROM {dbname}.{schemaname}.{table_name} LIMIT {limit}"
        conn = _self.get_connector()
        if conn:
            try:
                df = pd.read_sql(query, conn)
                return df
            except DatabaseError:
                _self.connection_failed = True
                return pd.DataFrame()
        else:
            return pd.DataFrame()
    
    @st.cache_data(ttl=600)
    def get_ddl(_self, dbname, schemaname, table_name):
        query = f"SELECT GET_DDL('table', '{dbname}.{schemaname}.{table_name}')"
        conn = _self.get_connector()
        if conn:
            try:
                df = pd.read_sql(query, conn)
                return df
            except DatabaseError:
                _self.connection_failed = True
                return pd.DataFrame()
        else:
            return pd.DataFrame()

    def close_session(self):
        if self.session is not None:
            self.session.close()
            self.session = None
        if self.connector is not None:
            self.connector.close()
            self.connector = None
