from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import logging
import os
from datetime import datetime

# Load environment variables (if you're using a .env file)
from dotenv import load_dotenv
load_dotenv()

# Basic Logging Configuration
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask App
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model for Stock
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Create the database tables
db.create_all()

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# Function to fetch stock price
def get_stock_price(ticker):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            return float(data['Global Quote']['05. price'])
        else:
            return None
    except Exception as e:
        app.logger.error('Error fetching price for %s: %s', ticker, e)
        return None

# Function to update stock data in the database
def fetch_stock_data():
    symbols = ['TSLA', 'GOOGL', 'AMZN', 'AAPL', 'CSCO', 'NOK']
    for symbol in symbols:
        price = get_stock_price(symbol)
        if price is not None:
            stock = Stock.query.filter_by(symbol=symbol).first()
            if stock:
                stock.price = price
                stock.last_updated = datetime.utcnow()
            else:
                new_stock = Stock(symbol=symbol, price=price)
                db.session.add(new_stock)
            db.session.commit()

# Scheduler to fetch stock data
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_stock_data, trigger='cron', hour=0, minute=1)
scheduler.start()

# Fetch initial data
fetch_stock_data()

# Route to display stock prices
@app.route('/get-stock-prices')
def get_stock_prices():
    stocks = Stock.query.all()
    stock_data = {stock.symbol: {'price': stock.price, 'last_updated': stock.last_updated.strftime('%Y-%m-%d %H:%M:%S')} for stock in stocks}
    return jsonify(stock_data)

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error('Internal Server Error: %s', e)
    return jsonify(error=str(e)), 500

# Logging to a File in Production
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)