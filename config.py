import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get('SECRET_KEY', 'lifepilot-ai-secret-key-2026-secure-key')
    
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'lifepilot_db')
    
    # ML Models Directory
    ML_MODEL_DIR = os.path.join(BASE_DIR, 'app', 'ml', 'saved_models')
    
    # Static uploads / plots directory
    PLOT_OUTPUT_DIR = os.path.join(BASE_DIR, 'app', 'static', 'images', 'plots')
    
    # Pagination
    RECORDS_PER_PAGE = 10
