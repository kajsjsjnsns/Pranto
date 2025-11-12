import requests
from config import Config

def send_order_notification(order):
    try:
        payment_info = ""
        if order.payment_method and order.transaction_id:
            payment_info = f"""
💳 Payment Method: {order.payment_method.upper()}
🔢 Transaction ID: {order.transaction_id}
"""
        
        message = f"""
🔔 New Order Received - BhauXTopup

📦 Order ID: #{order.id}
👤 Username: {order.user.username}
🎮 Player UID: {order.player_uid}
💎 Item: {order.topup_item.title}
💰 Price: {order.total_price} BDT
📊 Quantity: {order.quantity}{payment_info}
⏰ Time: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Status: {order.status.upper()}
"""
        
        # Create inline keyboard with Complete and Reject buttons
        inline_keyboard = {
            'inline_keyboard': [[
                {
                    'text': '✅ Complete Order',
                    'callback_data': f'complete_order_{order.id}'
                },
                {
                    'text': '❌ Reject',
                    'callback_data': f'reject_order_{order.id}'
                }
            ]]
        }
        
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': Config.TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': inline_keyboard
        }
        
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")
        return False

def update_telegram_message(chat_id, message_id, text):
    """Update existing Telegram message"""
    try:
        url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/editMessageText"
        payload = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to update Telegram message: {e}")
        return False
