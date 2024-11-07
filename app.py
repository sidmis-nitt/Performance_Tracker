import streamlit as st
import pandas as pd
from dhanhq import dhanhq
from datetime import datetime

# Title of the Streamlit app
st.title("Trade History and Holdings Viewer")

# Input fields for user to provide access URL, from date, and to date
st.sidebar.header("Input Parameters")

access_url = st.sidebar.text_input("Access URL")
from_date = st.sidebar.date_input("From Date", datetime(2024, 10, 1))
to_date = st.sidebar.date_input("To Date", datetime.now())

# Only initialize the Dhan API when access_url is provided
if access_url:
    dhan = dhanhq("Team Name- Blue Management", access_url)

    # Function to clean trade history data
    def clean_trade_history(trade_data):
        if 'data' in trade_data and isinstance(trade_data['data'], list):
            cleaned_data = [{k: v for k, v in entry.items() if v != 'NA'} for entry in trade_data['data']]
            df = pd.DataFrame(cleaned_data)
            df.fillna('', inplace=True)
            return df
        else:
            st.error("Unexpected trade_data format")
            return pd.DataFrame()

    # Function to clean holdings data
    def clean_holdings_data(holdings_data):
        if 'data' in holdings_data and isinstance(holdings_data['data'], list):
            cleaned_data = [{k: v for k, v in entry.items() if v != 'NA'} for entry in holdings_data['data']]
            df = pd.DataFrame(cleaned_data)
            df.fillna('', inplace=True)
            return df
        else:
            st.error("Unexpected holdings_data format")
            return pd.DataFrame()

    # Fetch and display trade history
    st.header("Trade History")
    try:
        if st.sidebar.button("Fetch Trade History"):
            trade_history = dhan.get_trade_history(from_date=str(from_date), to_date=str(to_date))
            trade_history_df = clean_trade_history(trade_history)
            if not trade_history_df.empty:
                st.write("Trade History Data:")
                st.dataframe(trade_history_df)  # Display as a table in Streamlit
            else:
                st.warning("No valid trade history data to display.")
    except Exception as e:
        st.error(f"Failed to fetch trade history: {e}")

    # Fetch and display holdings data
    st.header("Current Holdings")
    try:
        if st.sidebar.button("Fetch Holdings"):
            holdings_data = dhan.get_holdings()
            holdings_data_df = clean_holdings_data(holdings_data)
            if not holdings_data_df.empty:
                st.write("Holdings Data:")
                st.dataframe(holdings_data_df)  # Display as a table in Streamlit
            else:
                st.warning("No valid holdings data to display.")
    except Exception as e:
        st.error(f"Failed to fetch holdings data: {e}")
else:
    st.warning("Please enter the access URL in the sidebar.")
