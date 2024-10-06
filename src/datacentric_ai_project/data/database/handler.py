import psycopg2
from psycopg2 import sql
import pandas as pd
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

# Load environment variables (if needed)
load_dotenv()

# Database connection settings (from environment variables or hardcoded for simplicity)
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

def connect():
    """
    Create a connection to the PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    

def insert_image_data(device_id, image_url, is_trainable, image_resolution, augmentation, timestamp=None):
    """
    Insert a new image record into the 'images' table.
    """
    connection = connect()
    if connection is None:
        return

    try:
        with connection.cursor() as cursor:
            insert_query = """
            INSERT INTO images (image_id, device_id, image_url, capture_timestamp, is_trainable, image_resolution, augmentation)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            image_id = uuid.uuid4()  # Generate a new UUID for the image_id
            capture_timestamp = datetime.now() if not timestamp else timestamp 
            
            # Execute the query
            cursor.execute(insert_query, (
                image_id,
                device_id,
                image_url,
                capture_timestamp,
                is_trainable,
                image_resolution,
                augmentation
            ))
            
            # Commit the transaction
            connection.commit()
            print(f"Image {image_id} inserted successfully.")
    
    except Exception as e:
        print(f"Failed to insert data: {e}")
    
    finally:
        # Close the connection
        connection.close()

def fetch_image_data():
    """
    Fetch image data from the 'images' table and return it as a pandas DataFrame.
    """
    connection = connect()  # Assuming connect() is your function for creating the DB connection
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            # SQL query to fetch image data
            fetch_query = """
            SELECT image_id, device_id, image_url, capture_timestamp, trainable, image_resolution, augmentation
            FROM images;
            """
            
            # Execute the query
            cursor.execute(fetch_query)
            
            # Fetch the data
            records = cursor.fetchall()
            
            # Define column names for the DataFrame
            columns = ['image_id', 'device_id', 'image_url', 'capture_timestamp', 'trainable', 'image_resolution', 'augmentation']
            
            # Convert the records into a pandas DataFrame
            df = pd.DataFrame(records, columns=columns)

            # Return the DataFrame
            return df
    
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return None
    
    finally:
        # Close the connection
        connection.close()

def fetch_detection_summary():
    """
    Fetch data from the 'detection_summary' view and return it as a pandas DataFrame.
    """
    connection = connect()  # Assuming connect() is your function for creating the DB connection
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            # SQL query to fetch data from the 'detection_summary' view
            fetch_query = """
            SELECT image_id, capture_timestamp, label_name, confidence_score, factory_name, device_type, is_trainable, is_data_collector, bbox_file_url
            FROM detection_summary;
            """
            
            # Execute the query
            cursor.execute(fetch_query)
            
            # Fetch the data
            records = cursor.fetchall()
            
            # Define column names for the DataFrame
            columns = ['image_id', 'capture_timestamp', 'label_name', 'confidence_score', 'factory_name', 'device_type', 'is_trainable', 'is_data_collector', 'bbox_file_url']
            
            # Convert the records into a pandas DataFrame
            df = pd.DataFrame(records, columns=columns)

            # Return the DataFrame
            return df
    
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return None
    
    finally:
        # Close the connection
        connection.close()