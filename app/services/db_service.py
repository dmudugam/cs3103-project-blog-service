import psycopg2
import os
from psycopg2.extras import RealDictCursor

# Get connection parameters from environment variables
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')

def get_connection():
    """Get a PostgreSQL database connection"""
    return psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )

def sql_call_fetch_one(sql, params=()):
    """Execute SQL query and fetch one result"""
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()

def sql_call_fetch_all(sql, params=()):
    """Execute SQL query and fetch all results"""
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()