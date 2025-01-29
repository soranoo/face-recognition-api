from fastapi import HTTPException
import toml
from contextlib import contextmanager
import psycopg2
from typing import Generator

# Load configuration from config.toml
config = toml.load("config.toml")
DB_CONFIG = config["database"]
AUTH_TOKEN = config["auth"]["token"]

def get_db_connection() -> psycopg2.extensions.connection:
    """
    Establish a connection to the database using the configuration from config.toml.
    
    Returns:
        psycopg2.extensions.connection: Database connection object.
    """
    return psycopg2.connect(**DB_CONFIG)

def verify_token(token: str) -> None:
    """
    Verify the provided authentication token.
    
    Args:
        token (str): The authentication token to verify.
    
    Raises:
        HTTPException: If the token is invalid.
    """
    if token != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid authentication token")

@contextmanager
def db_transaction(token: str) -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Context manager for database transactions with token verification.
    
    Args:
        token (str): The authentication token to verify.
    
    Yields:
        psycopg2.extensions.cursor: Database cursor object.
    
    Raises:
        HTTPException: If an error occurs during the transaction.
    """
    verify_token(token)  # Verify the token here
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        yield cur  # Yield the cursor to the calling function
        conn.commit() # Commit transaction if needed
    except HTTPException as e:
        # If an HTTPException is raised, use the status code and detail from the exception
        conn.rollback()
        raise e
    except Exception as e:
        # If any other exception is raised, return a 500 error with the exception message
        conn.rollback() # Rollback transaction on error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
