import psycopg2
import psycopg2.extras
from flask import current_app, abort, request
import sys
import os

def get_db_connection():
    try:
        # Use DATABASE_URL from Render if available
        if os.environ.get('DATABASE_URL'):
            connection = psycopg2.connect(
                os.environ.get('DATABASE_URL'),
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        else:
            connection = psycopg2.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWD'],
                dbname=current_app.config['DB_DATABASE'],
                port=current_app.config['DB_PORT'],
                cursor_factory=psycopg2.extras.RealDictCursor
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
    except psycopg2.IntegrityError as e:
        error_code = e.pgcode
        error_msg = e.pgerror
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