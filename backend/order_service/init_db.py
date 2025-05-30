from .database import engine
from .models import Base

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    logger.info("Initializing database...")
    Base.metadata.drop_all(bind=engine)  # 清除舊的表
    Base.metadata.create_all(bind=engine)