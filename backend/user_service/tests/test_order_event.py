import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json
import pika
from unittest.mock import patch, MagicMock

from ..main import app, get_db
from ..models import Base, User, DiningRecord
from ..rabbitmq import (
    NOTIFICATION_EXCHANGE,
    ORDER_NOTIFICATION_ROUTING_KEY,
    process_order_notification,
    consume_order_notifications,
    ORDER_NOTIFICATION_QUEUE,
    setup_rabbitmq
)

# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = TestingSessionLocal()
    try:
        # Create a test user
        test_user = User(
            username="testuser",
            hashed_password="hashedpass",
            role="employee"
        )
        db.add(test_user)
        db.commit()
        yield db
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)

def test_process_order_notification(db):
    """Test processing a valid order notification"""
    # Mock channel and method
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1
    
    # Test data
    test_data = {
        "user_id": 1,
        "order_id": 123,
        "menu_item_id": 456,
        "menu_item_name": "Test Item",
        "total_amount": 10.99,
        "payment_status": "unpaid"
    }
    
    # Process the notification
    process_order_notification(
        mock_channel,
        mock_method,
        None,
        json.dumps(test_data).encode(),
        db
    )
    
    # Verify dining record was created
    dining_record = db.query(DiningRecord).filter(
        DiningRecord.order_id == test_data["order_id"]
    ).first()
    
    assert dining_record is not None
    assert dining_record.user_id == test_data["user_id"]
    assert dining_record.menu_item_id == test_data["menu_item_id"]
    assert dining_record.menu_item_name == test_data["menu_item_name"]
    assert dining_record.total_amount == test_data["total_amount"]
    assert dining_record.payment_status == test_data["payment_status"]
    
    # Verify message was acknowledged
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)

def test_process_invalid_order_notification(db):
    """Test processing an invalid order notification"""
    # Mock channel and method
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1
    
    # Test data with missing required field
    test_data = {
        "user_id": 1,
        "order_id": 123,
        # Missing menu_item_id
        "menu_item_name": "Test Item",
        "total_amount": 10.99,
        "payment_status": "unpaid"
    }
    
    # Process the notification
    process_order_notification(
        mock_channel,
        mock_method,
        None,
        json.dumps(test_data).encode(),
        db
    )
    
    # Verify no dining record was created
    dining_record = db.query(DiningRecord).filter(
        DiningRecord.order_id == test_data["order_id"]
    ).first()
    assert dining_record is None
    
    # Verify message was rejected
    mock_channel.basic_nack.assert_called_once_with(delivery_tag=1)

def test_process_invalid_json(db):
    """Test processing an invalid JSON message"""
    # Mock channel and method
    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 1
    
    # Invalid JSON data
    invalid_json = "invalid json data"
    
    # Process the notification
    process_order_notification(
        mock_channel,
        mock_method,
        None,
        invalid_json.encode(),
        db
    )
    
    # Verify message was rejected
    mock_channel.basic_nack.assert_called_once_with(delivery_tag=1)

@patch('pika.BlockingConnection')
def test_consume_order_notifications(mock_connection, db):
    """Test the order notification consumer setup"""
    # Mock channel
    mock_channel = MagicMock()
    mock_connection.return_value.channel.return_value = mock_channel
    
    # Test data
    test_data = {
        "user_id": 1,
        "order_id": 123,
        "menu_item_id": 456,
        "menu_item_name": "Test Item",
        "total_amount": 10.99,
        "payment_status": "unpaid"
    }
    
    # First set up RabbitMQ
    setup_rabbitmq()
    
    # Verify queue was declared and bound
    mock_channel.queue_declare.assert_called_with(
        queue=ORDER_NOTIFICATION_QUEUE,
        durable=True
    )
    mock_channel.queue_bind.assert_called_with(
        exchange=NOTIFICATION_EXCHANGE,
        queue=ORDER_NOTIFICATION_QUEUE,
        routing_key=ORDER_NOTIFICATION_ROUTING_KEY
    )
    
    # Set up the consumer
    consume_order_notifications(db)
    
    # Verify consumer was set up
    mock_channel.basic_consume.assert_called_once()
    mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)
    
    # Get the callback that was registered
    callback = mock_channel.basic_consume.call_args[1]['on_message_callback']
    
    # Simulate receiving a message
    callback(
        mock_channel,
        MagicMock(delivery_tag=1),
        None,
        json.dumps(test_data).encode()
    )
    
    # Verify dining record was created
    dining_record = db.query(DiningRecord).filter(
        DiningRecord.order_id == test_data["order_id"]
    ).first()
    assert dining_record is not None
    assert dining_record.user_id == test_data["user_id"] 