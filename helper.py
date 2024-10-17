import yfinance as yf

def lookup(symbol):
    symbol = symbol.upper()
    
    ticker = yf.Ticker(symbol)

    try:
        price = ticker.history(period='1d')['Close'].iloc[-1]  
        price = float(price)
        name = ticker.info.get('ShortName', symbol)  


        return {
            'name': name,
            'price': price
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None