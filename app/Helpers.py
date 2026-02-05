from nicegui import ui
import yfinance as yf
import supabase
import streamlit as st
from st_supabase_connection import SupabaseConnection
import datetime 
from datetime import datetime, timedelta, date
import pandas as pd

# connect to supabase
@st.cache_resource(ttl="10m")
def get_supabase_client():
    try:
        supabase = st.connection(
            name="supabase_connection",
            type=SupabaseConnection,
            url=st.secrets["supabase"]["SUPABASE_URL"],
            key=st.secrets["supabase"]["SUPABASE_KEY"],
            ttl="10m"
        )
        return supabase
    except Exception as e:
        st.error(f"Supabase connection failed: {e}")
        return None
    
supabase = get_supabase_client()


def navigation_menu():
    with ui.fab('menu', label='Navigation',color='#A05AFF').classes('text-white'):
        ui.fab_action('home', on_click=lambda: ui.navigate.to('/'),color='#A05AFF')
        ui.fab_action('bar_chart', on_click=lambda: ui.navigate.to('/Stocks_Dash'),color='#A05AFF')

def add_stock_to_db(symbol, is_benchmark=False):
    """Works for both stocks AND benchmarks"""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    
    if supabase is None:
        st.error("Cannot add stock to database because Supabase connection failed.")
        return

    # Stricter validation: Check if info is empty or missing key fields
    if not info or not info.get('longName'):
        raise ValueError(f"Invalid ticker symbol: '{symbol}'. Please enter a valid symbol (e.g., 'AAPL').")
    
    stock_data = {
        'symbol': symbol.upper(),
        'company_name': info.get('longName', ''),
        'exchange': info.get('exchange', ''),
        'sector': info.get('sector', ''),
        'industry': info.get('industry', ''),
        'is_benchmark': is_benchmark  # ✅ Just set the flag
    }
    
    supabase.table('stocks').upsert(stock_data, on_conflict='symbol').execute()

    get_all_stocks.clear()
    get_stock_id.clear()

@st.cache_data(ttl='10m')
def get_stock_id(symbol):
    """Helper: Get stock_id from symbol"""
    result = supabase.table('stocks').select('id').eq('symbol', symbol).execute()
    return result.data[0]['id'] if result.data else None

def update_stock_prices(symbol, period=None, interval="1d", force_refresh=False):
    """
    STEP 2: Fetch and store price data from Yahoo Finance
    
    Three usage modes:
    1. Initial load: update_stock_prices("AAPL", period="10y", interval="1d")
    2. Smart update: update_stock_prices("AAPL", interval="1d") - auto-detects what's missing
    3. Force refresh: update_stock_prices("AAPL", force_refresh=True, interval="1d")
    
    interval: Data interval (e.g., "1d" for daily, "1wk" for weekly, "1mo" for monthly)
    """
    
    stock_id = get_stock_id(symbol)
    if not stock_id:
        raise ValueError(f"Stock {symbol} not found. Add it first with add_stock_to_db()")
    
    # Determine what data to fetch
    if period:
        # Explicit period (e.g., "10y" for initial load)
        st.info(f"Fetching {period} of historical data for {symbol} at {interval} interval")
        hist = yf.Ticker(symbol).history(period=period, interval=interval)
    else: # Smart update: only fetch new data
        last_price = supabase.table('stock_prices')\
            .select('price_date')\
            .eq('stock_id', stock_id)\
            .order('price_date', desc=True)\
            .limit(1)\
            .execute()
        
        if last_price.data:
            last_date = datetime.fromisoformat(last_price.data[0]['price_date'])
            days_since_update = (datetime.now() - last_date).days
            
            # If updated today and not forcing, skip
            if days_since_update == 0 and not force_refresh:
                st.warning(f"{symbol} already updated today")
                return None
            
            # Fetch from last update to now
            start_date = (last_date - timedelta(days=1)).strftime('%Y-%m-%d')
            st.info(f"Fetching new data for {symbol} from {start_date} at {interval} interval")
            hist = yf.Ticker(symbol).history(start=start_date, interval=interval)
        else:
            # No data exists, fetch 1 year default
            st.info(f"No data found for {symbol}, fetching 1 year at {interval} interval")
            hist = yf.Ticker(symbol).history(period="1y", interval=interval)
    
    if hist.empty:
        st.warning(f"No data returned for {symbol}")
        return None
    
    # Prepare batch insert
    prices = []
    for date, row in hist.iterrows():
        prices.append({
            'stock_id': stock_id,
            'price_date': date.date().isoformat(),
            'open_price': float(row['Open']),
            'high_price': float(row['High']),
            'low_price': float(row['Low']),
            'close_price': float(row['Close']),
            'adjusted_close': float(row['Close']),
            'volume': int(row['Volume'])
        })
    
    # Upsert into database
    if prices:
        result = supabase.table('stock_prices').upsert(
            prices,
            on_conflict='stock_id,price_date'
        ).execute()
        st.success(f"✅ Updated {len(prices)} price records for {symbol}")
        return result.data
    
    # Clear cache
    get_latest_price_from_db.clear()
    get_stock_price_history.clear()
    get_current_positions.clear()

    return None

@st.cache_data(ttl='5m')
def get_latest_price_from_db(symbol):
    """
    STEP 3a: Get most recent price from database (fast, cached)
    Use this for displaying historical data
    """
    stock_id = get_stock_id(symbol)
    if not stock_id:
        return None
    
    latest = supabase.table('stock_prices')\
        .select('*')\
        .eq('stock_id', stock_id)\
        .order('price_date', desc=True)\
        .limit(1)\
        .execute()
    
    return latest.data[0] if latest.data else None

@st.cache_data(ttl='5m')
def get_current_live_price(symbol):
    """
    STEP 3b: Get current live price from Yahoo Finance
    Use this for real-time display (no database write)
    """
    ticker = yf.Ticker(symbol)
    current_data = ticker.history(period="1d")
    
    if current_data.empty:
        return None
    
    return {
        'symbol': symbol,
        'current_price': float(current_data['Close'].iloc[-1]),
        'open_price': float(current_data['Open'].iloc[-1]),
        'high_price': float(current_data['High'].iloc[-1]),
        'low_price': float(current_data['Low'].iloc[-1]),
        'volume': int(current_data['Volume'].iloc[-1]),
        'timestamp': datetime.now()
    }


@st.cache_data(ttl='5m')
def get_price_comparison(symbol):
    """
    STEP 3c: Compare latest DB price vs current live price
    Perfect for dashboard display showing both cached and live data
    """
    latest_db = get_latest_price_from_db(symbol)
    current_live = get_current_live_price(symbol)
    
    if not current_live:
        return None
    
    result = {
        'symbol': symbol,
        'latest_db_price': float(latest_db['close_price']) if latest_db else None,
        'latest_db_date': latest_db['price_date'] if latest_db else None,
        'current_price': current_live['current_price'],
        'difference': None,
        'percent_change': None,
        'is_stale': False
    }
    
    if latest_db:
        db_price = float(latest_db['close_price'])
        result['difference'] = current_live['current_price'] - db_price
        result['percent_change'] = ((current_live['current_price'] - db_price) / db_price) * 100
        
        # Check if data is stale (more than 1 day old)
        db_date = datetime.fromisoformat(latest_db['price_date'])
        result['is_stale'] = (datetime.now() - db_date).days > 1
    
    return result

@st.cache_data(ttl='10m')
def get_all_stocks():
    """Get all stocks from database"""
    return supabase.table('stocks').select('*').execute().data


@st.cache_data(ttl='10m')
def get_stock_price_history(symbols, days=30):
    """
    STEP 4: Get historical prices for charting
    Accepts a single symbol or a list of symbols.
    Returns pandas DataFrame with a `symbol` column.
    """
    if isinstance(symbols, str):
        symbols = [symbols]

    start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
    histories = []

    for symbol in symbols:
        stock_id = get_stock_id(symbol)
        if not stock_id:
            continue

        # Fetch all records using pagination to avoid limits
        all_prices = []
        page_size = 1000
        offset = 0
        
        while True:
            prices = supabase.table('stock_prices')\
                .select('stock_id, price_date, close_price')\
                .eq('stock_id', stock_id)\
                .gte('price_date', start_date)\
                .order('price_date', desc=False)\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not prices.data:
                break
                
            all_prices.extend(prices.data)
            
            # If we got less than page_size records, we've reached the end
            if len(prices.data) < page_size:
                break
                
            offset += page_size
        
        if all_prices:
            df = pd.DataFrame(all_prices)
            df["symbol"] = symbol
            histories.append(df)

    if histories:
        return pd.concat(histories, ignore_index=True)

    return pd.DataFrame()


def record_transaction(symbol, transaction_type, quantity, price, transaction_date, fees=0, notes=''):
    """
    STEP 5: Record a buy/sell transaction (manual entry)
    This is YOUR data that you input
    """
    stock_id = get_stock_id(symbol)
    if not stock_id:
        st.error(f"Stock {symbol} not found. Add it first!")
        return None
    
    transaction = {
        'stock_id': stock_id,
        'transaction_type': transaction_type.upper(),
        'quantity': quantity,
        'price_per_share': price,
        'total_amount': quantity * price,
        'transaction_date': transaction_date.isoformat() if isinstance(transaction_date, (datetime, date)) else transaction_date,
        'fees': fees,
        'notes': notes
    }
    
    result = supabase.table('transactions').insert(transaction).execute()
    st.success(f"✅ Recorded {transaction_type} of {quantity} shares of {symbol}")
    
    # Clear cache
    get_current_positions.clear()

    return result.data[0] if result.data else None

@st.cache_data(ttl='5m')
def get_current_positions():
    """
    Calculate current positions from all transactions
    Returns: DataFrame with current holdings
    """
    transactions = supabase.table('transactions')\
        .select('*, stocks(symbol, company_name)')\
        .execute()
    
    if not transactions.data:
        return pd.DataFrame()
    
    df = pd.DataFrame(transactions.data)
    
    # Calculate net shares per stock
    positions = []
    for stock_id in df['stock_id'].unique():
        stock_txns = df[df['stock_id'] == stock_id]
        
        # Sum up buys and sells
        buys = stock_txns[stock_txns['transaction_type'] == 'BUY']
        sells = stock_txns[stock_txns['transaction_type'] == 'SELL']
        
        total_bought = buys['quantity'].sum() if not buys.empty else 0
        total_sold = sells['quantity'].sum() if not sells.empty else 0
        
        shares_held = total_bought - total_sold
        
        # Only include if we still hold shares
        if shares_held > 0:
            # Calculate average cost basis (important for performance!)
            # This uses weighted average cost method
            total_cost = (buys['total_amount'] + buys['fees']).sum()
            avg_cost_per_share = total_cost / total_bought if total_bought > 0 else 0
            
            positions.append({
                'stock_id': stock_id,
                'symbol': stock_txns.iloc[0]['stocks']['symbol'],
                'company_name': stock_txns.iloc[0]['stocks']['company_name'],
                'shares_held': shares_held,
                'avg_cost_per_share': avg_cost_per_share,
                'total_cost_basis': shares_held * avg_cost_per_share,
                'first_purchase_date': buys['transaction_date'].min()
            })
    
    return pd.DataFrame(positions)