from app import db
from datetime import datetime
import json
import os

def load_prices_from_json():
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'diamond_prices.json')
    
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Using default prices.")
        return
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            prices_data = json.load(f)
        
        category_mapping = {
            'uid_topup': 'Free Fire UID Topup',
            'weekly_monthly': 'Weekly Monthly Offer',
            'level_up': 'Level Up Pass',
            'weekly_lite': 'Weekly Lite',
            'evo_access': 'Evo Access/E-Badge',
            'auto_like': 'Free Fire Auto Like'
        }
        
        for key, category_name in category_mapping.items():
            category = TopupCategory.query.filter_by(name=category_name).first()
            if not category or key not in prices_data:
                continue
            
            TopupItem.query.filter_by(category_id=category.id).delete()
            
            for item_data in prices_data[key]:
                item = TopupItem(category_id=category.id, **item_data)
                db.session.add(item)
        
        db.session.commit()
        print("Prices loaded successfully from diamond_prices.json")
    except Exception as e:
        print(f"Error loading prices from JSON: {e}")
        db.session.rollback()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

class TopupCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200))
    items = db.relationship('TopupItem', backref='category', lazy=True)

class TopupItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('topup_category.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    price_bdt = db.Column(db.Integer, nullable=False)
    diamond_amount = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topup_item_id = db.Column(db.Integer, db.ForeignKey('topup_item.id'), nullable=False)
    player_uid = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), nullable=True)
    transaction_id = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topup_item = db.relationship('TopupItem')

def update_categories():
    categories_data = [
        {'name': 'Free Fire UID Topup', 'image_url': 'https://i.ibb.co/WWvZPzw8/images-1751280542704.png', 'description': 'Get Free Fire Diamonds instantly'},
        {'name': 'Weekly Monthly Offer', 'image_url': 'https://i.ibb.co/fVqJM3B8/images-1751530838868.png', 'description': 'Special weekly and monthly packages'},
        {'name': 'Level Up Pass', 'image_url': 'https://i.ibb.co/sdrF18TB/images-1751280861154.png', 'description': 'Level up your account'},
        {'name': 'Weekly Lite', 'image_url': 'https://i.ibb.co/fVqJM3B8/images-1751530838868.png', 'description': 'Lite version of weekly pass'},
        {'name': 'Evo Access/E-Badge', 'image_url': 'https://i.ibb.co/Q3kJK0Wc/images-1751281589305.png', 'description': 'Get exclusive Evo Access'},
        {'name': 'Free Fire Auto Like', 'image_url': 'https://i.ibb.co/HfCjMD8Y/images-1751281878198.jpg', 'description': 'Get daily 100 auto likes'}
    ]
    
    for cat_data in categories_data:
        category = TopupCategory.query.filter_by(name=cat_data['name']).first()
        if category:
            category.image_url = cat_data['image_url']
            category.description = cat_data['description']
        else:
            category = TopupCategory(**cat_data)
            db.session.add(category)
    
    db.session.commit()

def seed_data():
    update_categories()
    load_prices_from_json()
