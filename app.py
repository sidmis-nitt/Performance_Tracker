import streamlit as st
import pandas as pd
from dhanhq import dhanhq
from datetime import datetime
import yfinance as yf  # Ensure you have yfinance installed: pip install yfinance

# Title of the Streamlit app
st.title("Trade History, Holdings, and Profit/Loss Viewer")

# Input fields for user to provide access URL, from date, and to date in the main window
access_url = st.text_input("Access URL")
from_date = st.date_input("From Date", datetime(2024, 10, 1))
to_date = st.date_input("To Date", datetime.now())

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
    if st.button("Fetch Trade History"):
        try:
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
    if st.button("Fetch Holdings"):
        try:
            holdings_data = dhan.get_holdings()
            holdings_data_df = clean_holdings_data(holdings_data)
            if not holdings_data_df.empty:
                st.write("Holdings Data:")
                st.dataframe(holdings_data_df)  # Display as a table in Streamlit
            else:
                st.warning("No valid holdings data to display.")
        except Exception as e:
            st.error(f"Failed to fetch holdings data: {e}")

    # Section for Net Profit/Loss
    st.header("Net Profit/Loss for Holdings")
    if st.button("Fetch Profit/Loss"):
        try:
            holdings_data = dhan.get_holdings()
            
            if 'data' in holdings_data and isinstance(holdings_data['data'], list):
                holdings_list = holdings_data['data']
                net_profit_loss_list = []
                total_portfolio_profit_loss = 0

                for holding in holdings_list:
                    trading_symbol = holding.get('tradingSymbol', '')
                    avg_cost_price = holding.get('avgCostPrice', 0)
                    total_qty = holding.get('totalQty', 0)
                    
                    # Fetch the current market price from Yahoo Finance
                    yf_symbol = trading_symbol + ".NS"
                    ticker = yf.Ticker(yf_symbol)
                    current_market_price = ticker.history(period="1d")['Close'].iloc[-1]
                    
                    total_investment = avg_cost_price * total_qty
                    current_value = current_market_price * total_qty
                    net_profit_loss = current_value - total_investment
                    
                    net_profit_loss_list.append({
                        'Trading Symbol': trading_symbol,
                        'Total Quantity': total_qty,
                        'Average Cost Price': avg_cost_price,
                        'Current Market Price': current_market_price,
                        'Net Profit/Loss (INR)': net_profit_loss
                    })

                    total_portfolio_profit_loss += net_profit_loss
                
                df_profit_loss = pd.DataFrame(net_profit_loss_list)
                
                if not df_profit_loss.empty:
                    st.write("Holdings Net Profit/Loss Data:")
                    st.dataframe(df_profit_loss)
                    st.write(f"Overall Portfolio Profit/Loss: {total_portfolio_profit_loss:.2f} INR")
                else:
                    st.warning("No holdings data available.")
            else:
                st.error("Unexpected holdings data format")
        except Exception as e:
            st.error(f"Failed to fetch holdings data: {e}")
else:
    st.warning("Please enter the access URL.")
