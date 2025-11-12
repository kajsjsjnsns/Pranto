from flask import request, jsonify
from app.webhook import webhook_bp
from app import db
from app.models import Order
from app.services.telegram import update_telegram_message
from config import Config

@webhook_bp.route('/telegram', methods=['POST'])
def telegram_webhook():
    """Handle Telegram bot callbacks (button clicks)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'ok': False}), 400
        
        # Handle callback query (button click)
        if 'callback_query' in data:
            callback_query = data['callback_query']
            callback_data = callback_query.get('data', '')
            message = callback_query.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            message_id = message.get('message_id')
            
            # Check if it's a complete order action
            if callback_data.startswith('complete_order_'):
                order_id = int(callback_data.replace('complete_order_', ''))
                
                # Update order status
                order = Order.query.get(order_id)
                if order:
                    order.status = 'completed'
                    db.session.commit()
                    
                    # Update the Telegram message
                    payment_info = ""
                    if order.payment_method and order.transaction_id:
                        payment_info = f"""
💳 Payment Method: {order.payment_method.upper()}
🔢 Transaction ID: {order.transaction_id}
"""
                    
                    updated_message = f"""
✅ <b>ORDER COMPLETED</b> - BhauXTopup

📦 Order ID: #{order.id}
👤 Username: {order.user.username}
🎮 Player UID: {order.player_uid}
💎 Item: {order.topup_item.title}
💰 Price: {order.total_price} BDT
📊 Quantity: {order.quantity}{payment_info}
⏰ Time: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Status: ✅ <b>COMPLETED</b>
"""
                    
                    update_telegram_message(chat_id, message_id, updated_message)
                    
                    # Answer callback query
                    answer_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
                    answer_payload = {
                        'callback_query_id': callback_query.get('id'),
                        'text': f'✅ Order #{order_id} marked as completed!',
                        'show_alert': True
                    }
                    import requests
                    requests.post(answer_url, json=answer_payload, timeout=10)
            
            # Check if it's a reject order action
            elif callback_data.startswith('reject_order_'):
                order_id = int(callback_data.replace('reject_order_', ''))
                
                # Update order status
                order = Order.query.get(order_id)
                if order:
                    order.status = 'rejected'
                    db.session.commit()
                    
                    # Update the Telegram message
                    payment_info = ""
                    if order.payment_method and order.transaction_id:
                        payment_info = f"""
💳 Payment Method: {order.payment_method.upper()}
🔢 Transaction ID: {order.transaction_id}
"""
                    
                    updated_message = f"""
❌ <b>ORDER REJECTED</b> - BhauXTopup

📦 Order ID: #{order.id}
👤 Username: {order.user.username}
🎮 Player UID: {order.player_uid}
💎 Item: {order.topup_item.title}
💰 Price: {order.total_price} BDT
📊 Quantity: {order.quantity}{payment_info}
⏰ Time: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Status: ❌ <b>REJECTED</b>
"""
                    
                    update_telegram_message(chat_id, message_id, updated_message)
                    
                    # Answer callback query
                    answer_url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
                    answer_payload = {
                        'callback_query_id': callback_query.get('id'),
                        'text': f'❌ Order #{order_id} has been rejected!',
                        'show_alert': True
                    }
                    import requests
                    requests.post(answer_url, json=answer_payload, timeout=10)
        
        return jsonify({'ok': True})
    
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'ok': False, 'error': str(e)}), 500
