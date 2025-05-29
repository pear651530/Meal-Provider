import pika
import json
from sqlalchemy.orm import Session
from . import models
import threading
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ configuration
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"
MAX_RETRIES = 1
RETRY_DELAY = 5  # seconds

# Exchange and queue names
NOTIFICATION_EXCHANGE = "notifications"
NOTIFICATION_ROUTING_KEY = "menu.notification"
NOTIFICATION_QUEUE = "menu_notifications"
ORDER_NOTIFICATION_ROUTING_KEY = "order.notification"
ORDER_NOTIFICATION_QUEUE = "order_notifications"

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

def get_connection():
    """Create a connection to RabbitMQ with retries"""
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        connection_attempts=MAX_RETRIES,
        retry_delay=RETRY_DELAY,
        socket_timeout=5
    )
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{MAX_RETRIES})")
            connection = pika.BlockingConnection(parameters)
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to connect to RabbitMQ after {MAX_RETRIES} attempts")
                raise
            logger.warning(f"Failed to connect to RabbitMQ, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

def setup_rabbitmq():
    """Set up RabbitMQ exchange and queue with retries"""
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Setting up RabbitMQ (attempt {attempt + 1}/{MAX_RETRIES})")
            connection = get_connection()
            channel = connection.channel()

            # Declare exchange
            channel.exchange_declare(
                exchange=NOTIFICATION_EXCHANGE,
                exchange_type='topic',
                durable=True
            )

            # Declare queue
            channel.queue_declare(
                queue=NOTIFICATION_QUEUE, 
                durable=True
            )

            # Bind queue to exchange
            channel.queue_bind(
                exchange=NOTIFICATION_EXCHANGE,
                queue=NOTIFICATION_QUEUE,
                routing_key=NOTIFICATION_ROUTING_KEY
            )

            channel.queue_declare(queue=ORDER_NOTIFICATION_QUEUE, durable=True)
            channel.queue_bind(
                exchange=NOTIFICATION_EXCHANGE,
                queue=ORDER_NOTIFICATION_QUEUE,
                routing_key=ORDER_NOTIFICATION_ROUTING_KEY
            )

            connection.close()  # Close the connection after setup
            logger.info("RabbitMQ setup completed successfully")
            return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to set up RabbitMQ after {MAX_RETRIES} attempts: {e}")
                raise
            logger.warning(f"Failed to set up RabbitMQ, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

def process_notification_menu(ch, method, properties, body, db: Session):
    try:
        data = json.loads(body)
        required_fields = ["zh_name", "en_name", "price", "url", "is_available"]
        optional_fields = ["id"]
        if not all(field in data for field in required_fields):
            logger.error("Notification data is missing required fields")
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return
        current_menu_id = data.get("id", -1)
        #if not exists, add
        if db.query(models.MenuItem).filter(models.MenuItem.id == current_menu_id).first() is None:
            menu_item = models.MenuItem(
                zh_name=data["zh_name"],
                en_name=data["en_name"],
                price=data["price"],
                url=data["url"],
                is_available=data.get("is_available", True)
            )
            db.add(menu_item)
            db.commit()
        else:
            #already exists, update
            menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == current_menu_id).first()
            if menu_item:
                menu_item.zh_name = data["zh_name"]
                menu_item.en_name = data["en_name"]
                menu_item.price = data["price"]
                menu_item.url = data["url"]
                menu_item.is_available = data.get("is_available", True)
                db.commit()

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Unexpected error processing notification: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    else:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_notifications(db: Session):
    connection = get_connection()
    channel = connection.channel()

    channel.basic_qos(prefetch_count=1)  # Fair dispatch
    channel.basic_consume(
        queue=NOTIFICATION_QUEUE,
        on_message_callback=lambda ch, method, properties, body: process_notification_menu(ch, method, properties, body, db),
        auto_ack=False
    )

    try: 
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Stopping RabbitMQ consumer")
        channel.stop_consuming()
    finally:
        connection.close()
        logger.info("RabbitMQ connection closed")

def start_consumer_thread(db: Session):
    consumer_thread = threading.Thread(
        target=consume_notifications, 
        args=(db,), 
        daemon=True)
    consumer_thread.start()

    return consumer_thread

def send_order_notification(dining_record_item):
    """
    Send a menu item notification to RabbitMQ
    """
    channel, connection = get_rabbitmq_channel()
    
    notification = {
        "user_id": dining_record_item["user_id"],
        "order_id": dining_record_item["order_id"],
        "menu_item_id": dining_record_item["menu_item_id"],
        "menu_item_name": dining_record_item["menu_item_name"],
        "total_amount": dining_record_item["total_amount"],
        "payment_status": dining_record_item["payment_status"]
    }
    
    # Publish notification to RabbitMQ
    channel.basic_publish(
        exchange=NOTIFICATION_EXCHANGE,
        routing_key=ORDER_NOTIFICATION_ROUTING_KEY,
        body=json.dumps(notification),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            content_type='application/json'
        )
    )
    
    # Close RabbitMQ connection
    connection.close()