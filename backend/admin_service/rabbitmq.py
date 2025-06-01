import pika
import json
from datetime import datetime
import os
# RabbitMQ configuration
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
NOTIFICATION_EXCHANGE = "notifications"
NOTIFICATION_ROUTING_KEY = "billing.notification"
MENU_NOTIFICATION_QOUTING_KEY = "menu.notification"

def get_rabbitmq_channel():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declare exchange
    channel.exchange_declare(
        exchange=NOTIFICATION_EXCHANGE,
        exchange_type='topic',
        durable=True
    )
    
    return channel, connection

def send_notification(user_data):
    """
    Send a notification to RabbitMQ for a single user
    """
    channel, connection = get_rabbitmq_channel()
    
    notification = {
        "user_id": user_data["user_id"],
        "user_name": user_data["user_name"],
        "unpaid_amount": user_data["unpaidAmount"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publish notification to RabbitMQ
    channel.basic_publish(
        exchange=NOTIFICATION_EXCHANGE,
        routing_key=NOTIFICATION_ROUTING_KEY,
        body=json.dumps(notification),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json'
        )
    )
    
    # Close RabbitMQ connection
    connection.close()

def send_notifications_to_users(unpaid_users):
    """
    Send notifications to multiple users
    """
    if not isinstance(unpaid_users, list):
        raise ValueError("unpaid_users must be a list")
    
    for user in unpaid_users:
        if not isinstance(user, dict):
            raise ValueError("Each user must be a dictionary")
        if not all(key in user for key in ["user_id", "user_name", "unpaidAmount"]):
            raise ValueError("Each user must have user_id, user_name, and unpaidAmount fields")
        send_notification(user)
    
    return len(unpaid_users)

def send_menu_notification(menu_item):
    """
    Send a menu item notification to RabbitMQ
    """
    channel, connection = get_rabbitmq_channel()
    
    notification = {
        "zh_name": menu_item["zh_name"],
        "en_name": menu_item["en_name"],
        "price": menu_item["price"],
        "url": menu_item["url"],
        "is_available": menu_item.get("is_available", True),
    }

    if "id" in menu_item:
        notification["id"] = menu_item["id"]
    
    # Publish notification to RabbitMQ
    channel.basic_publish(
        exchange=NOTIFICATION_EXCHANGE,
        routing_key=MENU_NOTIFICATION_QOUTING_KEY,
        body=json.dumps(notification),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json'
        )
    )
    
    # Close RabbitMQ connection
    connection.close()