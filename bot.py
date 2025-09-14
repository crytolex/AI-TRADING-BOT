import os
import time
import requests
import pandas as pd
import talib
from telegram import Bot
from telegram.error import TelegramError

# ----------------------------
# CONFIGURATION - Get these from your environment
# ----------------------------
MEXC_API_URL = 'https://api.mexc.com/api/v3/klines'
SYMBOL = 'BTCUSDT'  # MEXC Trading pair
INTERVAL = '5m'     # Check 5-minute candles
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') 
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
MEXC_API_KEY = os.environ.get('MEXC_API_KEY')

# ----------------------------
# 1. FETCH DATA FROM MEXC
# ----------------------------
def get_mexc_data(symbol, interval, limit=100):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    try:
        response = requests.get(MEXC_API_URL, params=params)
        data = response.json()
        df = pd.DataFrame(data)
        df = df.iloc[:, :5] 
        df.columns = ['time', 'open', 'high', 'low', 'close']
        df = df.astype({'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float'})
        return df
    except Exception as e:
        print(f"Error fetching data from MEXC: {e}")
        return None

# ----------------------------
# 2. CHECK FOR RSI SIGNALS
# ----------------------------
def check_rsi_signal(df):
    if df is None or len(df) < 15:
        return None, "Not enough data"

    rsi = talib.RSI(df['close'], timeperiod=14)
    current_rsi = rsi.iloc[-1]
    signal = None
    message = ""

    if current_rsi < 30:
        signal = "LONG"
        message = f"✅ **LONG SIGNAL (Oversold)** ✅\n"
        message += f"**Pair:** {SYMBOL}\n**Interval:** {INTERVAL}\n"
        message += f"**RSI:** {current_rsi:.2f}\n"
    elif current_rsi > 70:
        signal = "SHORT"
        message = f"🔻 **SHORT SIGNAL (Overbought)** 🔻\n"
        message += f"**Pair:** {SYMBOL}\n**Interval:** {INTERVAL}\n"
        message += f"**RSI:** {current_rsi:.2f}\n"

    return signal, message

# ----------------------------
# 3. SEND TELEGRAM ALERT
# ----------------------------
def send_telegram_alert(message):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        print("Signal sent to Telegram!")
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")

# ----------------------------
# MAIN LOOP - The bot's heart
# ----------------------------
def main():
    print("MEXC Signal Bot is running...")
    while True:
        try:
            data_df = get_mexc_data(SYMBOL, INTERVAL)
            signal, message = check_rsi_signal(data_df)
            if signal:
                print(f"New signal found: {signal}")
                send_telegram_alert(message)
                time.sleep(300)
            else:
                time.sleep(60)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)
