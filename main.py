import requests
from twilio.rest import Client
from datetime import datetime, timedelta
import time

# stock market api key

ALPHA_VANTAGE_API_KEY = 'MBJR35REMKHSXB49'

# Twilio account setup (sms messaging api)

TWILIO_ACCOUNT_SID = 'ACCOUNT SID' 
TWILIO_AUTH_TOKEN = 'AUTH TOKEN'
TWILIO_PHONE_NUMBER = 'TWILIO PHONE NUMBER'
USER_PHONE_NUMBER = 'USER PHONE NUMBER'

# User-customized list of stock symbols to be notified of

USER_WATCHLIST = []

# fuction to retrieve current stock price
def get_stock_price(symbol):
    base_url = 'https://www.alphavantage.co/query'
    function = 'GLOBAL_QUOTE'
    params = {
        'function': function,
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if 'Global Quote' in data:
        return data['Global Quote']['05. price']
    else:
        return None
    
# function to send SMS using twilio API
    
def send_message(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Use the messages.create method to send a message
    message = client.messages.create(
        to=USER_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=message
    )

# Function to check and send stock price alerts of each stock in the user's customized watchlist
    
def check_stock_prices():
    while True:
        now = datetime.now()

        # Market open time (9:30 AM)

        market_open_time = datetime(now.year, now.month, now.day, 9, 30) 

        # Noon (12:00 PM)
         
        market_noon_time = datetime(now.year, now.month, now.day, 12, 0) 

        # Market close time (4:00 PM)

        market_close_time = datetime(now.year, now.month, now.day, 16, 00)  

        # retrieves and sends stock prices with customized notification depending on time of day
        if now.time() == market_open_time.time():
            send_message("Market is open! Here is the status of your watchlist: ")
            for symbol in USER_WATCHLIST:
                stock_price = get_stock_price(symbol)
                if stock_price:
                    send_message(f"{symbol} is @ {stock_price}/share.")

        elif now.time() == market_noon_time.time():
            send_message("Good afternoon! Here is the status of your watchlist: ")
            for symbol in USER_WATCHLIST:
                stock_price = get_stock_price(symbol)
                if stock_price:
                    send_message(f"{symbol} is @ {stock_price}/share.")

        elif now.time() == market_close_time.time():
            send_message("Market is closing! Here is the status of your watchlist: ")
            for symbol in USER_WATCHLIST:
                stock_price = get_stock_price(symbol)
                if stock_price:
                    send_message(f"{symbol} is @ {stock_price}/share.")

        # checks the time in one minute intervals

        time.sleep(60)

if __name__ == "__main__":
    check_stock_prices()