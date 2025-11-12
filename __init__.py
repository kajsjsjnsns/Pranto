from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

def setup_telegram_webhook(app):
    """Automatically set up Telegram webhook on app start"""
    try:
        # Get the Repl URL from environment or use the provided URL
        repl_url = os.environ.get('REPL_URL', 'এনে তোমার webhook link, i mean website link)
        webhook_url = f"{repl_url}/webhook/telegram"
        
        bot_token = app.config['TELEGRAM_BOT_TOKEN']
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        payload = {'url': webhook_url}
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Telegram webhook set successfully: {webhook_url}")
            else:
                print(f"❌ Failed to set webhook: {result}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not set Telegram webhook: {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    bcrypt.init_app(app)
    
    with app.app_context():
        from app.auth import auth_bp
        from app.orders import orders_bp
        from app.webhook import webhook_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(orders_bp)
        app.register_blueprint(webhook_bp)
        
        db.create_all()
        
        from app.models import seed_data
        seed_data()
        
        # Set up Telegram webhook automatically
        setup_telegram_webhook(app)
    
    return app
