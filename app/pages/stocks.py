import streamlit as st
import Helpers
import pandas as pd
import plotly.express as px
import numpy as np

PRIMARY = "#A05AFF"
SECONDARY = "#FE9496"
TERTIARY = "#4BCBEB"
BG_DARK = "#0f172a"

# page config
st.set_page_config(
    layout="wide",
    page_title="Stocks and Market Dashboard",
    page_icon="📈",
)

# Custom CSS to match home page styling
st.markdown(
    f"""
    <style>
        .hero-card {{
            background: linear-gradient(120deg, {PRIMARY}, #6b21a8);
            border-radius: 18px;
            padding: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 20px 45px rgba(160, 90, 255, 0.25);
            margin-bottom: 1.5rem;
        }}
        .info-card {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            height: 100%;
        }}
        .section-header {{
            color: {PRIMARY};
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 8px;
            padding: 10px 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(120deg, {PRIMARY}, #6b21a8) !important;
            border: none !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Hero header
st.markdown(
    """
    <div class="hero-card">
        <h1 style="margin-bottom:0.4rem;">📈 Stocks Dashboard</h1>
        <p style="font-size:1rem;margin:0;">
            Analyze stock performance, market reactions, and my personal investment positions all in one place!
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)



tab1, tab2, tab3 = st.tabs(["📊 Stock and Market Analysis", "➕ Add Position", "🔄 Update Prices"])
with tab1:
    st.markdown(f'<h3 class="section-header">Individual Stock Analysis</h3>', unsafe_allow_html=True)
    col_1, col_2 = st.columns([1, 3], border=True)
    with col_1:
        stocks = Helpers.get_all_stocks()

        stock_options = pd.DataFrame(stocks)[['symbol','is_benchmark']]
        stock_options = stock_options[stock_options['is_benchmark'] == False]['symbol'].tolist()

        selected_stocks = st.multiselect("Select stocks to analyze:", stock_options)

        price_adjustment = st.selectbox("Price Adjustment:", ["Actual Price", "Normalized Price"], index=0)
        time_period = st.selectbox("Select time period:", ["1 week", "1 month", "3 month", "6 month", "1 year", "2 year", "5 year", "10 year", "15 year"], index=7)
    with col_2:
        # get the time period in days
        if "week" in time_period:
            days = 7
        elif "month" in time_period:
            days = int(time_period.replace("month", "")) * 30
        elif "year" in time_period:
            days = int(time_period.replace("year", "")) * 365
        # return results of selected stocks
        if len(selected_stocks) >= 1:
            stock_history = Helpers.get_stock_price_history(selected_stocks, days=days)

            stock_history = stock_history[["symbol","price_date","close_price"]]

            # normalize prices for comparison
            for stock in stock_history["symbol"].unique():
                stock_history.loc[stock_history["symbol"] == stock, "normalized_price"] = stock_history.loc[stock_history["symbol"] == stock, "close_price"] / stock_history.loc[stock_history["symbol"] == stock, "close_price"].iloc[0] 

            # plot price history
            if price_adjustment == "Actual Price":
                fig = px.line(stock_history, x="price_date", y="close_price", title=f"Price History for {selected_stocks}", color="symbol")
            else:
                fig = px.line(stock_history, x="price_date", y="normalized_price", title=f"Price History for {selected_stocks}", color="symbol")
            
            # Apply consistent styling
            fig.update_layout(
                legend_title_text='Stocks',
                xaxis_title='Date',
                yaxis_title='Price' if price_adjustment == "Actual Price" else 'Normalized Price',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font=dict(color=PRIMARY, size=18),
                legend=dict(bgcolor='rgba(255,255,255,0.04)', bordercolor='rgba(255,255,255,0.08)'),
            )
            fig.update_traces(line=dict(width=2))
            fig.update_xaxes(gridcolor='rgba(255,255,255,0.08)', zerolinecolor='rgba(255,255,255,0.08)')
            fig.update_yaxes(gridcolor='rgba(255,255,255,0.08)', zerolinecolor='rgba(255,255,255,0.08)')
            st.plotly_chart(fig, width='content')

            
        else:
            st.info("Please select at least one stock to analyze.")
    st.divider()
    st.markdown(f'<h3 class="section-header">What\'s Happening in the Market?</h3>', unsafe_allow_html=True)
    
    # time period
    period = st.selectbox("Select time period for market analysis:", ["1 day", "5 day", "1 month", "3 month", "6 month", "1 year"], index=2)
    
    if "week" in period:
        days = 7
    elif "month" in period:
        days = int(period.replace("month", "")) * 30
    elif "year" in period:
        days = int(period.replace("year", "")) * 365
    elif "day" in period:
        days = int(period.replace(" day", ""))

    # Get stock history for all indices
    history = Helpers.get_stock_price_history(["^GSPC", "^DJI", "^IXIC"], days=days)
    stock_history = history[["symbol","price_date","close_price"]]

    # Market indices configuration
    indices = [
        {"symbol": "^GSPC", "name": "S&P 500", "color": PRIMARY, "badge_color": "violet", 
         "description": "Tracks 500 largest U.S. companies across all sectors"},
        {"symbol": "^DJI", "name": "Dow Jones", "color": SECONDARY, "badge_color": "red",
         "description": "30 major U.S. blue-chip companies (industrials, tech, finance)"},
        {"symbol": "^IXIC", "name": "NASDAQ", "color": TERTIARY, "badge_color": "blue",
         "description": "3,000+ tech-heavy companies including Apple, Microsoft, Tesla"}
    ]

    cols = st.columns([1, 1, 1], border=True)
    
    for idx, index_info in enumerate(indices):
        with cols[idx]:
            st.badge(index_info["name"], color=index_info["badge_color"])
            st.caption(index_info["description"])
            
            # Filter history for this index
            index_history = stock_history[stock_history["symbol"] == index_info["symbol"]]
            
            # Create and style chart
            fig = px.line(index_history, x="price_date", y="close_price", color_discrete_sequence=[index_info["color"]])
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Price',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                legend=dict(bgcolor='rgba(255,255,255,0.04)', bordercolor='rgba(255,255,255,0.08)'),
            )


            # Calculate and display metric with percentage change over the selected period
            live_price = Helpers.get_current_live_price(index_info["symbol"])
            if live_price and not index_history.empty:
                current_price = round(live_price['current_price'], 2)
                first_price = index_history['close_price'].iloc[0]  # First price in the period
                pct_change = np.round((current_price - first_price) / first_price * 100, 2)
                st.metric(label=f"{index_info['name']} Current Value", value=current_price, delta=f"{pct_change}%")
            else:
                st.metric(label=f"{index_info['name']} Current Value", value="N/A")
            
            st.plotly_chart(fig, width='content')

with tab2:
    # Initialize session state for login
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    password = st.secrets["positions"]["password"]
    
    if not st.session_state["logged_in"]:
        entered_password = st.text_input("Enter Admin Password to Add Position/Stock", type="password", key="add_position_password")
        
        if entered_password == password:
            st.session_state["logged_in"] = True
            st.success("Access Granted. You can now add a new stock, position, or transaction.")
            st.rerun()  # Refresh to hide the input and show the form
        elif entered_password:  # Only show error if something was entered
            st.error("Incorrect password. Please try again.")
    else:
        st.markdown(f'<h3 class="section-header">Add New Stock / Transaction</h3>', unsafe_allow_html=True)
        option = st.selectbox("Select what to add:", ["Add Stock", "Add Transaction"])
        if option == "Add Stock":
            # Handle input clearing
            if st.session_state.get("clear_stock_input", False):
                st.session_state["stock_symbol"] = ""
                st.session_state["clear_stock_input"] = False
            
            success_message = st.session_state.get("success_message", None)
            if success_message:
                st.success(success_message)
                del st.session_state["success_message"]
            
            with st.form("Add Stock Form"):
                stock_symbol = st.text_input("Stock Symbol", key="stock_symbol")
                benchmark = st.checkbox("Is Benchmark Stock?", value=False)
                submit_button = st.form_submit_button("Add Stock")
                
                if submit_button:
                    if not stock_symbol:
                        st.error("Please enter a stock symbol.")
                    else:
                        try:
                            Helpers.add_stock_to_db(stock_symbol, benchmark)
                            st.session_state["success_message"] = f"Added stock: {stock_symbol} into the database!"
                            st.session_state["clear_stock_input"] = True  # Flag to clear on next run
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {str(e)}")
        elif option == "Add Transaction":
            if Helpers.get_current_positions().empty:
                st.warning("No positions available. Please add a stock first.")

            # Initialize form counter to force reset
            if "transaction_form_key" not in st.session_state:
                st.session_state["transaction_form_key"] = 0

            success_message = st.session_state.get("transaction_success_message", None)
            if success_message:
                st.success(success_message)
                del st.session_state["transaction_success_message"]
            
            with st.form(f"Add Transaction Form {st.session_state['transaction_form_key']}"):
                # get stock options from database
                stock_options = Helpers.get_all_stocks()
                stock_options = pd.DataFrame(stock_options)['symbol'].tolist()
                selected_stock = st.selectbox("Select Stock", stock_options)

                # confirm transaction type
                transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell"])
                quantity = st.number_input("Quantity", min_value=0.0001, step=0.0001, format="%.3f")
                price = st.number_input("Price per Share", min_value=0.0, format="%.2f")
                date = st.date_input("Transaction Date")
                submit_transaction = st.form_submit_button("Add Transaction")
                
                if submit_transaction:
                    try:
                        Helpers.record_transaction(
                            symbol=selected_stock,
                            transaction_type=transaction_type,
                            quantity=quantity,
                            price=price,
                            transaction_date=date
                        )
                        st.session_state["transaction_success_message"] = f"Added {transaction_type} transaction for {selected_stock}."
                        st.session_state["transaction_form_key"] += 1  # Increment to create new form
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")

        # Optional: Add a logout button to reset
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

with tab3:
    st.markdown(f'<h3 class="section-header">Update All Stock Prices</h3>', unsafe_allow_html=True)
    col1 = st.columns([3])
    with col1[0]:
        period = st.text_input("Select period for price update (e.g., '1d', '5d', '1mo'):", value="max")
    
    if st.button("Update Prices"):
        try:
            # get all stocks first
            stocks = Helpers.get_all_stocks()
            stock_symbols = pd.DataFrame(stocks)['symbol'].tolist()
            updated_count = 0
            for symbol in stock_symbols:
                Helpers.update_stock_prices(symbol, period)
                updated_count += 1

            st.success(f"Successfully updated prices for {updated_count} stocks.")
        except Exception as e:
            st.error(f"An error occurred while updating prices: {str(e)}")