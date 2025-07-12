import pymysql
from pymysql.cursors import DictCursor
from config.settings import DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWD

def get_connection():
    """Get a MySQL database connection"""
    return pymysql.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        db=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWD,
        charset='utf8mb4',
        cursorclass=DictCursor
    )

def sql_call_fetch_one(sql, params=()):
    """Execute SQL query and fetch one result"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc(sql, params)  # MySQL uses callproc for stored procedures
            result = cursor.fetchone()
            return result
    finally:
        connection.close()

def sql_call_fetch_all(sql, params=()):
    """Execute SQL query and fetch all results"""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.callproc(sql, params)  # MySQL uses callproc for stored procedures
            result = cursor.fetchall()
            return result
    finally:
        connection.close()