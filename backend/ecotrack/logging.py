"""
Centralized logging configuration for EcoTrack
"""
import os
import logging.config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "timestamp": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ecotrack.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'api_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'api.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'ecotrack.api': {
            'handlers': ['api_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'ecotrack.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'social': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'ai_recommendations': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    logs_dir = BASE_DIR / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Get logger and log setup completion
    logger = logging.getLogger('ecotrack')
    logger.info("Logging configuration initialized")