import os
import logging
import pymysql
import pymysql.cursors
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection(db_name=None):
    """
    Establishes connection to the MySQL server using PyMySQL.
    Raises RuntimeError if connection fails.
    """
    if db_name is None:
        db_name = Config.MYSQL_DB
        
    try:
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
            charset='utf8mb4'
        )
        return connection
    except pymysql.Error as e:
        logger.error(f"MySQL connection error: {e}")
        raise RuntimeError(
            f"Could not connect to MySQL database '{db_name}' on {Config.MYSQL_HOST}:{Config.MYSQL_PORT}. "
            f"Please verify MySQL service is running and credentials in config.py are correct. Error: {e}"
        ) from e

def init_db():
    """
    Ensures the MySQL database and all 6 core tables exist on application startup.
    Executes schema.sql using PyMySQL.
    """
    try:
        # Step 1: Connect to MySQL server (without database context) to create lifepilot_db if missing
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()

        # Step 2: Connect to lifepilot_db and execute table creation from schema.sql
        conn = get_db_connection()
        schema_path = os.path.join(Config.BASE_DIR, 'schema.sql')
        
        with conn.cursor() as cursor:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                for stmt in statements:
                    if stmt.upper().startswith("USE ") or stmt.upper().startswith("CREATE DATABASE"):
                        continue
                    cursor.execute(stmt)
                    
        conn.commit()
        conn.close()
        logger.info("MySQL database and schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize MySQL database schema: {e}")
        raise RuntimeError(f"MySQL database initialization failed: {e}") from e

def execute_query(sql, args=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Executes a SQL query safely using PyMySQL with parameterized placeholders (%s).
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, args or ())
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            elif commit:
                result = cursor.lastrowid
                
        if commit:
            conn.commit()
            
        return result
    except Exception as e:
        if commit:
            conn.rollback()
        logger.error(f"Error executing MySQL query: {sql} | Error: {e}")
        raise e
    finally:
        conn.close()
