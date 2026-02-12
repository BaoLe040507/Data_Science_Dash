import streamlit as st
import Helpers
import pandas as pd
import plotly.express as px
import numpy as np

PRIMARY = "#A05AFF"
SECONDARY = "#FE9496"
TERTIARY = "#4BCBEB"
NEUTRAL_LIGHT = "#F5F3FA"  
ACCENT_GREEN = "#4ED1A1"   
ACCENT_YELLOW = "#FFD166" 
ACCENT_RED = "#EF476F"     
ACCENT_INDIGO = "#6C63FF"
BG_DARK = "#0f172a"

# Dashboard color palette for plots
dashboard_colors = [PRIMARY, SECONDARY, TERTIARY, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED, ACCENT_INDIGO]

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



tab1, tab2, tab3, tab4 = st.tabs([":material/candlestick_chart: Stock and Market Analysis",":material/home: Can You Retire?", ":material/add: Add Position", ":material/update: Update Prices"])
with tab1:
    st.markdown(f'<h3 class="section-header">Stock Analysis</h3>', unsafe_allow_html=True)
    st.caption("Compare selected stocks' performance over time. Use 'Actual Price' for raw values or 'Normalized Price' to start all stocks at 100% for relative growth comparison.")
    col_1, col_2, col_3 = st.columns([0.5, 1.5, 2], border=True)
    with col_1:
        stocks = Helpers.get_all_stocks()

        stock_options = pd.DataFrame(stocks)[['symbol','is_benchmark']]
        stock_options = stock_options[stock_options['is_benchmark'] == False]['symbol'].tolist()

        selected_stocks = st.multiselect("Select stocks to analyze:", stock_options)

        price_adjustment = st.selectbox("Price Adjustment:", ["Actual Price", "Normalized Price"], index=0)
        time_period = st.selectbox("Select time period:", ["1 week", "1 month", "3 month", "6 month", "1 year", "2 year", "5 year", "10 year", "15 year"], index=3)
    with col_2:
        st.markdown("#### Stock Price History")
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

            stock_history = stock_history[["symbol","price_date","adjusted_close"]]

            # normalize prices for comparison
            for stock in stock_history["symbol"].unique():
                stock_history.loc[stock_history["symbol"] == stock, "normalized_price"] = stock_history.loc[stock_history["symbol"] == stock, "adjusted_close"] / stock_history.loc[stock_history["symbol"] == stock, "adjusted_close"].iloc[0] 
            # plot price history
            if price_adjustment == "Actual Price":
                fig = px.line(stock_history, x="price_date", y="adjusted_close", title=f"Price History for {selected_stocks}", color="symbol", color_discrete_sequence=dashboard_colors)
            else:
                fig = px.line(stock_history, x="price_date", y="normalized_price", title=f"Price History for {selected_stocks}", color="symbol", color_discrete_sequence=dashboard_colors)
            
            # Apply consistent styling
            fig.update_layout(
                legend_title_text='Stock',
                xaxis_title='Date',
                yaxis_title='Price' if price_adjustment == "Actual Price" else 'Normalized Price',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font=dict(size=18),
                legend=dict(bgcolor='rgba(255,255,255,0.04)', bordercolor='rgba(255,255,255,0.08)'),
                hovermode='x unified'
            )
            fig.update_traces(line=dict(width=2))
            fig.update_xaxes(gridcolor='rgba(255,255,255,0.08)', zerolinecolor='rgba(255,255,255,0.08)')
            fig.update_yaxes(gridcolor='rgba(255,255,255,0.08)', zerolinecolor='rgba(255,255,255,0.08)')
            st.plotly_chart(fig, width='content', height=400, use_container_width=True)

            
        else:
            st.info("Please select at least one stock to analyze.")
    with col_3:
        st.markdown("#### Stock Financials Overview")
        if len(selected_stocks) >= 1:
            # Get financials for each selected stock
            all_financials = []
            for stock in selected_stocks:
                financial_data = Helpers.get_financials(stock)
                if financial_data:
                    all_financials.append(financial_data)
            
            if all_financials:
                stock_financials = pd.DataFrame(all_financials)

                # join stock financials with stock info to get company names
                stock_info = Helpers.get_all_stocks()
                stock_info_df = pd.DataFrame(stock_info)[['id','symbol','company_name']]
                stock_financials = stock_financials.merge(stock_info_df, left_on = 'stock_id', right_on= 'id', how='left')

                # join live price data to get current price for each stock
                current_prices_list = []
                for stock in selected_stocks:
                    price_data = Helpers.get_current_live_price(stock)
                    if price_data:
                        current_prices_list.append(price_data)
                
                if current_prices_list:
                    current_prices_df = pd.DataFrame(current_prices_list)
                    stock_financials = stock_financials.merge(current_prices_df, left_on='symbol', right_on='symbol', how='left')

                # Select key columns for display
                display_cols = ['symbol', 'market_cap', 'trailing_pe', 'forward_pe', 'eps_ttm', 'dividend_yield', 'beta', 'recommendation_key', 'current_price','target_mean_price']

                stock_financials["market_cap"] = stock_financials["market_cap"].apply(lambda x: f"${x/1e9:.2f}B" if x >= 1e9 else (f"${x/1e6:.2f}M" if x >= 1e6 else f"${x:.2f}"))
                # format large numbers and percentages
                stock_financials["dividend_yield"] = stock_financials["dividend_yield"].astype(str) + "%"
                # replace nan with 0 for dividend yield
                stock_financials["dividend_yield"] = stock_financials["dividend_yield"].replace("nan%", "0%")

                # round trailing PE, foward PE, and target mean price to 2 decimal places 
                stock_financials["trailing_pe"] = stock_financials["trailing_pe"].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                stock_financials["forward_pe"] = stock_financials["forward_pe"].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                stock_financials["target_mean_price"] = stock_financials["target_mean_price"].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
                stock_financials["eps_ttm"] = stock_financials["eps_ttm"].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
                stock_financials["beta"] = stock_financials["beta"].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
                stock_financials["current_price"] = stock_financials["current_price"].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")




                # Format recommendation with better labels
                recommendation_map = {
                    'strong_buy': 'Strong Buy',
                    'buy': 'Buy',
                    'hold': 'Hold',
                    'sell': 'Sell',
                    'strong_sell': 'Strong Sell'
                }
                stock_financials['recommendation_key'] = stock_financials['recommendation_key'].map(
                    lambda x: recommendation_map.get(x, x) if pd.notnull(x) else 'N/A'
                )
                
                # Apply color styling to recommendation column
                def color_recommendation(val):
                    if val == 'Strong Buy':
                        return 'background-color: #00a146; color: #0f172a; font-weight: bold'
                    elif val == 'Buy':
                        return 'background-color: #7FD8A6; color: #0f172a; font-weight: bold'
                    elif val == 'Hold':
                        return 'background-color: #FFD166; color: #0f172a; font-weight: bold'
                    elif val == 'Sell':
                        return 'background-color: #FE9496; color: #0f172a; font-weight: bold'
                    elif val == 'Strong Sell':
                        return 'background-color: #EF476F; color: white; font-weight: bold'
                    else:
                        return ''
                
                # Only show columns that exist in the data
                display_cols = [col for col in display_cols if col in stock_financials.columns]
                
                # Apply styling and display
                styled_df = stock_financials[display_cols].style.applymap(
                    color_recommendation, 
                    subset=['recommendation_key']
                )
                
                st.dataframe(styled_df, use_container_width=True,
                             column_config={
                        "symbol": "Stock",
                        "market_cap": "Market Cap",
                        "trailing_pe": "Trailing P/E",
                        "forward_pe": "Forward P/E",
                        "eps_ttm": "EPS (TTM)",
                        "dividend_yield": "Dividend Yield",
                        "beta": "Beta",
                        "recommendation_key": "Analyst Rec",
                        "target_mean_price": "Avg. Target Price"
                    }, hide_index=True
                )
            else:
                st.warning("No financial data available. Try updating prices first.")
        else:
            st.info("Financial data will appear here once you select stocks to analyze.")
    st.divider()
    st.markdown(f'<h3 class="section-header">What\'s Happening in the Market?</h3>'
    , unsafe_allow_html=True)
    st.caption("Compare key market indices, commodities, and volatility to understand the broader market context in which your stocks are operating. Current values and percentages changed over time are based off of live data pulled from Yahoo Finance.")
    
    # time period
    period = st.selectbox("Select time period for market analysis:", ["1 day", "5 day", "1 month", "3 month", "6 month", "1 year"], index=2)
    
    if "week" in period:
        days = 7
    elif "month" in period:
        days = int(period.replace("month", "")) * 31
    elif "year" in period:
        days = int(period.replace("year", "")) * 365
    elif "day" in period:
        days = int(period.replace(" day", ""))

    # Get stock history for all indices
    history = Helpers.get_stock_price_history(["^GSPC", "^DJI", "^IXIC", "GC=F", "SI=F", "^VIX", "^TNX"], days=days)
    stock_history = history[["symbol","price_date","adjusted_close"]]

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
    
    Helpers.plot_market_indices(stock_history, cols, indices, dashboard_colors)

    cols = st.columns([1, 1, 1], border=True)

# gold/silver, VIX, and treasury yield 
    indices = [
        {"symbol": ["GC=F", "SI=F"], "name": "Gold/Silver", "color": "#FFD700", "badge_color": "yellow",
         "description": "Gold and Silver futures prices for precious metals tracking"},
        {"symbol": "^VIX", "name": "VIX", "color": "#de9312", "badge_color": "orange",
         "description": "CBOE Volatility Index (market fear gauge)"},
        {"symbol": "^TNX", "name": "10Y Treasury", "color": ACCENT_GREEN, "badge_color": "green",
         "description": "10-Year U.S. Treasury yield (interest rate benchmark)"}
    ]

    Helpers.plot_market_indices(stock_history, cols, indices, dashboard_colors)

with tab2:
        st.write("#### Can You Retire? Let's Find Out.")
        st.caption("Find out your expected financial position at retirement based on your current savings, expected expenses, and investment growth assumptions. This is a simplified model and should be used for illustrative purposes only.")

        retirement_accounts = ["Roth IRA", "Pre-Tax 401(k)"]
        selection = st.pills("Select Retirement Account Type:", retirement_accounts)
        st.badge(f"You selected: {selection}", color = "violet")

    # personal inputs and timeline
        cols = st.columns([1,3], border=True)
        submitted = False  # Initialize submitted variable
        with cols[0]:
            if selection == "Roth IRA":
                with st.form("personal_inputs"):

                    current_age = st.number_input(
                        "Current Age", min_value=0, max_value=100, value=30
                    )

                    target_retirement_age = st.number_input(
                        "Target Retirement Age", min_value=0, max_value=100, value=65
                    )

                    years_in_retirement = st.number_input(
                        "Expected Years in Retirement", min_value=0, max_value=50, value=20
                    )

                    annual_contribution = st.number_input(
                        "Annual Contribution ($)", min_value=0, value=7500
                    )
                    st.info(
                        "Current Roth IRA contribution limit is \\$7,500/year (\\$8,500 if age 50+)"
                    )

                    return_rate = st.number_input(
                        "Expected Annual Return Rate (%)", min_value=0.0, value=7.0, step=0.5
                    )
                    st.info(
                        "Historical average stock market return is around 7% after adjusting for inflation"
                    )

                    current_balance = st.number_input(
                        "Current Account Balance ($)", min_value=0.0, value=0.0
                    )

                    withdrawal_rate = st.number_input(
                        "Expected Annual Withdrawal Rate in Retirement (%)",
                        min_value=0.0,
                        value=4.0
                    )
                    st.info(
                        "The 4% rule is a common guideline for sustainable withdrawals in retirement"
                    )

                    desired_income = st.number_input(
                        "Desired Annual Income in Retirement ($)", min_value=0.0, value=50000.0, step=5000.0
                    )

                    # ─────────────────────────────
                    # Derived values
                    # ─────────────────────────────

                    years_until_retirement = max(
                        target_retirement_age - current_age, 0
                    )

                    r = return_rate / 100
                    w = withdrawal_rate / 100

                    total_contributions = annual_contribution * years_until_retirement

                    # ─────────────────────────────
                    # Roth IRA calculations
                    # ─────────────────────────────

                    # 1️⃣ Grow current balance (lump sum)
                    future_current_balance = Helpers.get_future_value(
                        current_balance, r, years_until_retirement
                    )

                    # 2️⃣ Grow annual contributions (annuity)
                    if r > 0:
                        future_contributions = (
                            annual_contribution * ((1 + r) ** years_until_retirement - 1) / r
                        )
                    else:
                        future_contributions = total_contributions

                    # 3️⃣ Total Roth balance at retirement
                    roth_balance_at_retirement = (
                        future_current_balance + future_contributions
                    )

                    # 4️⃣ Tax-free growth
                    tax_free_growth = (
                        roth_balance_at_retirement
                        - current_balance
                        - total_contributions
                    )

                    # 5️⃣ Estimated annual tax-free income in retirement
                    tax_free_income = roth_balance_at_retirement * w

                    submitted = st.form_submit_button("Submit")
    
        with cols[1]:
            if submitted and selection == "Roth IRA":

                current_year = pd.Timestamp.now().year
                years = []
                balances = []
                HYSA_balances = []

                balance = current_balance
                hysa_balance = current_balance  # Separate variable for HYSA tracking
                r = return_rate / 100
                hysa_r = 3 / 100  # Assume 3% for HYSA

                # Start at current year with initial balance
                years.append(current_year)
                balances.append(current_balance)
                HYSA_balances.append(current_balance)

                for i in range(1, years_until_retirement + 1):
                    year = current_year + i
                    years.append(year)

                    # Grow existing balance
                    balance *= (1 + r)
                    hysa_balance *= (1 + hysa_r)

                    # Add annual contribution at end of year
                    balance += annual_contribution
                    hysa_balance += annual_contribution

                    balances.append(balance)
                    HYSA_balances.append(hysa_balance)

                roth_projection_df = pd.DataFrame({
                    "Year": years,
                    "Projected Roth IRA Balance": balances,
                    "HYSA Balance": HYSA_balances
                })

                fig = px.line(
                    roth_projection_df,
                    x="Year",
                    y=["Projected Roth IRA Balance", "HYSA Balance"],
                    title="Roth IRA Growth Projection",
                    color_discrete_sequence=[PRIMARY, ACCENT_GREEN],
                    markers=True
                )
                
                # Format y-axis with dollar signs and hover with 2 decimals
                fig.update_layout(
                    yaxis_tickprefix="$",
                    yaxis_tickformat=",.0f",
                    hovermode="x unified",
                    legend=dict(
                        title="Accounts",
                        orientation="h",
                        yanchor="top",
                        y=-0.15,
                        xanchor="center",
                        x=0.1
                    )
                )
                fig.update_traces(
                    hovertemplate="$%{y:,.2f}<extra></extra>"
                )

                st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.markdown("### Summary at Retirement")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Roth Balance", f"${roth_balance_at_retirement:,.0f}", border=True)
                with col2:
                    st.metric("Tax-Free Growth", f"${tax_free_growth:,.0f}", border=True)
                with col3:
                    st.metric("Contributions Total", f"${total_contributions:,.0f}", border=True)
                with col4:
                    st.metric("Est. Annual Tax-Free Income", f"${tax_free_income:,.0f}", border=True)

                if tax_free_income >= desired_income:
                    st.success("Congratulations! Based on your inputs, you are on track to meet or exceed your desired annual income in retirement.")
                else:
                    st.warning("Based on your inputs, you may need to adjust your savings or investment strategy to meet your desired annual income in retirement.")
                    # Calculate the total balance needed to generate desired income
                    desired_balance_at_retirement = desired_income / w
                    # Calculate the balance shortfall
                    balance_shortfall = desired_balance_at_retirement - roth_balance_at_retirement
                    # Calculate additional annual contribution needed using future value of annuity formula
                    if r > 0:
                        additional_contribution = balance_shortfall / (((1 + r) ** years_until_retirement - 1) / r)
                    else:
                        additional_contribution = balance_shortfall / years_until_retirement if years_until_retirement > 0 else 0
                    st.markdown(f"To cover the shortfall, consider increasing your annual contribution by approximately :green[${additional_contribution:,.0f}].")
with tab3:  
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

with tab4:
    st.markdown(f'<h3 class="section-header">Update All Stock Prices</h3>', unsafe_allow_html=True)
    col1 = st.columns([3])
    with col1[0]:
        period = st.selectbox("Select time period for price update:", ["1d", "7d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], index=2)
    
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