"""
Configuration file with bot settings and API keys from third-party services
"""
import os
from dotenv import load_dotenv

# Loading env variables from .env file
load_dotenv('.env')

APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
APP_PORT = os.environ.get('APP_PORT', 3000)
