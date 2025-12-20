"""
Database connection and utilities for MySQL
"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from config import Config

def get_connection():
    """Create a new database connection"""
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=DictCursor,
        autocommit=False
    )

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database operations
    
    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO ...")
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()

def execute_query(query, params=None, commit=False, fetch_one=False):
    """
    Execute a SQL query with optional parameters
    
    Args:
        query: SQL query string
        params: Tuple of parameters for parameterized queries
        commit: Whether to commit the transaction (INSERT/UPDATE/DELETE)
        fetch_one: Return single row instead of list
    
    Returns:
        For SELECT: List of dictionaries or single dictionary
        For INSERT: Last inserted row ID
        For UPDATE/DELETE: Number of affected rows
    """
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())
        
        if commit:
            # INSERT/UPDATE/DELETE
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        else:
            # SELECT
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
