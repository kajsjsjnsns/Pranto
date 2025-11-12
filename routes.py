from flask import render_template, request, redirect, url_for, session, jsonify
from app.orders import orders_bp
from app import db
from app.models import TopupCategory, TopupItem, Order
from app.services.telegram import send_order_notification

@orders_bp.route('/')
def index():
    categories = TopupCategory.query.all()
    return render_template('index.html', categories=categories)

@orders_bp.route('/uidtopup')
def uid_topup():
    category = TopupCategory.query.filter_by(name='Free Fire UID Topup').first_or_404()
    items = TopupItem.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template('category_page.html', category=category, items=items)

@orders_bp.route('/weeklymonthly')
def weekly_monthly():
    category = TopupCategory.query.filter_by(name='Weekly Monthly Offer').first_or_404()
    items = TopupItem.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template('category_page.html', category=category, items=items)

@orders_bp.route('/leveluppass')
def level_up_pass():
    category = TopupCategory.query.filter_by(name='Level Up Pass').first_or_404()
    items = TopupItem.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template('category_page.html', category=category, items=items)

@orders_bp.route('/weeklylite')
def weekly_lite():
    category = TopupCategory.query.filter_by(name='Weekly Lite').first_or_404()
    items = TopupItem.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template('category_page.html', category=category, items=items)

@orders_bp.route('/evoaccess')
def evo_access():
    category = TopupCategory.query.filter_by(name='Evo Access/E-Badge').first_or_404()
    items = TopupItem.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template('category_page.html', category=category, items=items)

@orders_bp.route('/autolike')
def auto_like():
    category = TopupCategory.query.filter_by(name='Free Fire Auto Like').first_or_404()
    items = TopupItem.query.filter_by(category_id=category.id, is_active=True).all()
    return render_template('category_page.html', category=category, items=items)

@orders_bp.route('/category/<int:category_id>')
def category_items(category_id):
    category = TopupCategory.query.get_or_404(category_id)
    items = TopupItem.query.filter_by(category_id=category_id, is_active=True).all()
    return jsonify({
        'category': {
            'id': category.id,
            'name': category.name,
            'description': category.description
        },
        'items': [{
            'id': item.id,
            'title': item.title,
            'price_bdt': item.price_bdt,
            'diamond_amount': item.diamond_amount
        } for item in items]
    })

@orders_bp.route('/order', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request'}), 400
    
    item_id = data.get('item_id')
    player_uid = data.get('player_uid', '').strip()
    quantity = data.get('quantity', 1)
    
    if not player_uid:
        return jsonify({'success': False, 'message': 'Player UID is required'}), 400
    
    if not item_id:
        return jsonify({'success': False, 'message': 'Item ID is required'}), 400
    
    try:
        quantity = int(quantity)
        if quantity < 1 or quantity > 10:
            return jsonify({'success': False, 'message': 'Quantity must be between 1 and 10'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    
    item = TopupItem.query.get_or_404(item_id)
    total_price = item.price_bdt * quantity
    
    order = Order(
        user_id=session['user_id'],
        topup_item_id=item_id,
        player_uid=player_uid,
        quantity=quantity,
        total_price=total_price
    )
    db.session.add(order)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Order created successfully. Redirecting to payment...',
        'order_id': order.id,
        'redirect_url': url_for('orders.payment_page', order_id=order.id)
    })

@orders_bp.route('/payment/<int:order_id>')
def payment_page(order_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id']:
        return redirect(url_for('orders.index'))
    
    if order.transaction_id:
        return redirect(url_for('orders.my_orders'))
    
    return render_template('payment.html', order=order)

@orders_bp.route('/payment/verify/<int:order_id>', methods=['POST'])
def verify_payment(order_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    transaction_id = data.get('transaction_id', '').strip()
    payment_method = data.get('payment_method', '').strip()
    
    if not transaction_id:
        return jsonify({'success': False, 'message': 'Transaction ID is required'}), 400
    
    if not payment_method:
        return jsonify({'success': False, 'message': 'Payment method is required'}), 400
    
    order.transaction_id = transaction_id
    order.payment_method = payment_method
    order.status = 'processing'
    db.session.commit()
    
    send_order_notification(order)
    
    return jsonify({
        'success': True,
        'message': 'Payment verified successfully'
    })

@orders_bp.route('/my-orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=orders)
