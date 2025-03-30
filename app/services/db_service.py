import pymysql.cursors
from flask import current_app, abort, request
import sys

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWD'],
            database=current_app.config['DB_DATABASE'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        abort(500)

def sql_call_fetch_all(proc_name, args=None):
    cursor = None
    db_connection = None
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        if args is not None:
            cursor.callproc(proc_name, args)
        else:
            cursor.callproc(proc_name)
            
        rows = cursor.fetchall()
        db_connection.commit()
        return rows
    except Exception as e:
        print(f"Database error: {e}", file=sys.stderr)
        if request:
            abort(500)
        raise e
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()

def sql_call_fetch_one(proc_name, args=None):
    cursor = None
    db_connection = None
    try:
        db_connection = get_db_connection()
        cursor = db_connection.cursor()
        
        if args is not None:
            cursor.callproc(proc_name, args)
        else:
            cursor.callproc(proc_name)
            
        row = cursor.fetchone()
        db_connection.commit()
        return row
    except pymysql.err.IntegrityError as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        print(f"Database integrity error: {error_code}, {error_msg}", file=sys.stderr)
        raise e
    except Exception as e:
        print(f"Database error: {e}", file=sys.stderr)
        if request:
            abort(500)
        raise e
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()