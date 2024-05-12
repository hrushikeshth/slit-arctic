import streamlit as st

# Initialize connection.
conn = st.connection("snowflake")

class Snowflake_Connection:
    # Load the table as a dataframe using the Snowpark Session.
    @st.cache_data
    def load_table():
        session = conn.session()
        return session.table("PAYMENTS_INVOICES").to_pandas()

    df = load_table()

    # Print results.
    def displaytbl(df):
        for row in df.itertuples():
            snow_data = st.write()
        return snow_data
