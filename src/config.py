# project/config.py

import logging
import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOGGING_LOCATION = 'flask-base.log'
    LOGGING_LEVEL = logging.DEBUG
    GOOGLE_CLOUD_PROJECT = os.environ.get('PUBSUB_PROJECT_ID')


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    ENV = 'Developement'
    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    ENV = 'Production'
    DEBUG = False
