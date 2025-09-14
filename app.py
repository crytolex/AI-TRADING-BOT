from flask import Flask
import threading
from bot import main  # Import the main function from your bot.py

app = Flask(__name__)

def run_bot_in_background():
    main()

@app.route('/')
def home():
    return "Bot is alive! ✅", 200

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot_in_background)
    bot_thread.daemon = True
    bot_thread.start()
    app.run(host='0.0.0.0', port=10000)
