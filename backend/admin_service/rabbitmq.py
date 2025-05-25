import pika
import json
from datetime import datetime

# RabbitMQ configuration
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"
NOTIFICATION_EXCHANGE = "notifications"
NOTIFICATION_ROUTING_KEY = "billing.notification"

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
    for user in unpaid_users:
        send_notification(user)
    
    return len(unpaid_users) 