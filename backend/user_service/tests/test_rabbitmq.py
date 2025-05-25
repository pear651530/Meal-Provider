import pytest
import pika
import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from .. import models
from ..rabbitmq import (
    get_connection,
    setup_rabbitmq,
    send_notification,
    start_consumer_thread,
    NOTIFICATION_EXCHANGE,
    NOTIFICATION_ROUTING_KEY,
    NOTIFICATION_QUEUE
)

# Test RabbitMQ configuration
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
RABBITMQ_USER = "guest"
RABBITMQ_PASSWORD = "guest"

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        connection_attempts=3,
        retry_delay=1
    )
    return pika.BlockingConnection(parameters)

@pytest.fixture(scope="module")
def rabbitmq_connection():
    """Fixture to provide RabbitMQ connection"""
    connection = get_rabbitmq_connection()
    yield connection
    connection.close()

def test_rabbitmq_connection():
    """Test that we can connect to RabbitMQ"""
    connection = get_connection()
    assert connection.is_open
    connection.close()

def test_notification_publish_and_consume(db: Session):
    """Test that we can publish and consume notifications"""
    # Set up RabbitMQ
    setup_rabbitmq()

    # Create test user first
    test_user = models.User(
        username="testuser",
        hashed_password="password",
        role="employee"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Create test notification data
    test_notification = {
        "user_id": test_user.id,
        "user_name": test_user.username,
        "unpaid_amount": 150.0,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Start consumer thread
    consumer_thread = start_consumer_thread(db)

    # Send notification
    send_notification(test_notification)

    # Wait for message to be processed
    time.sleep(2)

    # Check if notification was stored in database
    db_notification = db.query(models.Notification).filter(
        models.Notification.user_id == test_user.id
    ).first()

    assert db_notification is not None
    assert db_notification.message == f"Payment reminder: You have an unpaid amount of ${test_notification['unpaid_amount']}"
    assert db_notification.notification_type == "billing"
    assert db_notification.is_read == False

def test_rabbitmq_error_handling():
    """Test RabbitMQ error handling"""
    # Try to connect with wrong credentials
    wrong_credentials = pika.PlainCredentials("wrong", "wrong")
    parameters = pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=wrong_credentials,
        connection_attempts=1
    )
    
    with pytest.raises(pika.exceptions.AMQPConnectionError):
        pika.BlockingConnection(parameters)

def test_notification_format(db: Session):
    """Test that notifications are properly formatted"""
    # Set up RabbitMQ
    setup_rabbitmq()

    # Create test user first
    test_user = models.User(
        username="testuser",
        hashed_password="password",
        role="employee"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Create test notification with invalid format
    invalid_notification = {
        "user_id": "not_an_integer",  # Invalid type
        "user_name": "testuser",
        "unpaid_amount": "not_a_float",  # Invalid type
        "timestamp": "invalid_timestamp"  # Invalid format
    }

    # Start consumer thread
    consumer_thread = start_consumer_thread(db)

    # Send invalid notification
    send_notification(invalid_notification)

    # Wait for message to be processed
    time.sleep(2)

    # Check that no notification was stored (due to error handling)
    db_notification = db.query(models.Notification).filter(
        models.Notification.user_id == test_user.id
    ).first()

    assert db_notification is None 