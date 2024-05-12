import streamlit as st

# Initialize connection.
@st.cache(allow_output_mutation=True)
def get_snowflake_connection():
    return st.connection("snowflake")

conn = get_snowflake_connection()

class SnowflakeConnection:
    # Load the table as a dataframe using the Snowflake connection.
    @staticmethod
    @st.cache(allow_output_mutation=True)
    def load_table():
        query = "SELECT * FROM PAYMENTS_INVOICES"
        return conn.fetch_pandas_all(query)

    df = load_table()

    # Display the dataframe.
    @staticmethod
    def display_table(df):
        st.write(df)

# Example usage:
# snowflake_conn = SnowflakeConnection()
# snowflake_conn.display_table(snowflake_conn.df)
