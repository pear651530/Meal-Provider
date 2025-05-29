import pika
import json
from datetime import datetime
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
MAX_RETRIES = 5
RETRY_DELAY = 5  # seconds

# Exchange and queue names
NOTIFICATION_EXCHANGE = "notifications"
NOTIFICATION_ROUTING_KEY = "billing.notification"
NOTIFICATION_QUEUE = "billing_notifications"
ORDER_NOTIFICATION_ROUTING_KEY = "order.notification"
ORDER_NOTIFICATION_QUEUE = "order_notifications"

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

            #declare queue to receive message sent from order_service
            channel.queue_declare(
                queue=ORDER_NOTIFICATION_QUEUE,
                durable=True
            )
            channel.queue_bind(
                exchange=NOTIFICATION_EXCHANGE,
                queue=ORDER_NOTIFICATION_QUEUE,
                routing_key=ORDER_NOTIFICATION_ROUTING_KEY
            )

            connection.close()
            logger.info("Successfully set up RabbitMQ")
            return
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed to set up RabbitMQ after {MAX_RETRIES} attempts: {str(e)}")
                raise
            logger.warning(f"Failed to set up RabbitMQ, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

def send_notification(notification_data):
    """Send a notification to RabbitMQ"""
    connection = get_connection()
    channel = connection.channel()

    # Publish message
    channel.basic_publish(
        exchange=NOTIFICATION_EXCHANGE,
        routing_key=NOTIFICATION_ROUTING_KEY,
        body=json.dumps(notification_data),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
            content_type='application/json'
        )
    )

    connection.close()

def process_notification(ch, method, properties, body, db: Session):
    """Process a notification message"""
    try:
        data = json.loads(body)
        
        # Validate required fields
        required_fields = ['user_id', 'user_name', 'unpaid_amount']
        if not all(field in data for field in required_fields):
            print(f"Invalid notification format: {data}")
            return

        # Create notification in database
        notification = models.Notification(
            user_id=data['user_id'],
            message=f"Payment reminder: You have an unpaid amount of ${data['unpaid_amount']}",
            notification_type="billing",
            is_read=False
        )
        db.add(notification)
        db.commit()

    except json.JSONDecodeError:
        print(f"Invalid JSON format: {body}")
    except Exception as e:
        print(f"Error processing notification: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def consume_notifications(db: Session):
    """Start consuming notifications from RabbitMQ"""
    connection = get_connection()
    channel = connection.channel()

    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=NOTIFICATION_QUEUE,
        on_message_callback=lambda ch, method, properties, body: process_notification(ch, method, properties, body, db)
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

def start_consumer_thread(db: Session):
    """Start the RabbitMQ consumer in a background thread"""
    consumer_thread = threading.Thread(
        target=consume_notifications,
        args=(db,),
        daemon=True
    )
    consumer_thread.start()
    return consumer_thread 

def consume_order_notifications(db: Session):
    """Consume order notifications from RabbitMQ"""
    connection = get_connection()
    channel = connection.channel()

    # Set up consumer for order notifications
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=ORDER_NOTIFICATION_QUEUE,
        on_message_callback=lambda ch, method, properties, body: process_order_notification(ch, method, properties, body, db)
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

def process_order_notification(ch, method, properties, body, db: Session):
    """Process an order notification and create a dining record"""
    try:
        data = json.loads(body)
        logger.info(f"Received order notification: {data}")
        
        # Validate required fields
        required_fields = ['user_id', 'order_id', 'menu_item_id', 'menu_item_name', 'total_amount', 'payment_status']
        if not all(field in data for field in required_fields):
            logger.error(f"Invalid order notification format: {data}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        # Create dining record
        dining_record = models.DiningRecord(
            user_id=data['user_id'],
            order_id=data['order_id'],
            menu_item_id=data['menu_item_id'],
            menu_item_name=data['menu_item_name'],
            total_amount=data['total_amount'],
            payment_status=data['payment_status']
        )
        
        db.add(dining_record)
        db.commit()
        logger.info(f"Created dining record for order {data['order_id']}")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format: {body}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing order notification: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)
        db.rollback()

def start_order_consumer_thread(db: Session):
    """Start the order notification consumer in a background thread"""
    consumer_thread = threading.Thread(
        target=consume_order_notifications,
        args=(db,),
        daemon=True
    )
    consumer_thread.start()
    return consumer_thread