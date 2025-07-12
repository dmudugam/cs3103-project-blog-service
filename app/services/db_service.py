import psycopg2
from psycopg2.extras import RealDictCursor
from config.settings import DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWD

def get_connection():
    """Get a PostgreSQL database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWD
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