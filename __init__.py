from flask import Blueprint

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')

from app.webhook import routes
