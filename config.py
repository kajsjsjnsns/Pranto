import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bhaux-topup-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN') or '8274073586:AAFaliUj83rAjBi9TDXqJk_iKdLrMcHTUn0'
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') or '5985580179'