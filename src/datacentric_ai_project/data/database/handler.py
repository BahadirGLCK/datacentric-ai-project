import psycopg2
import uuid
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import os


class DatabaseManager:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()

        # Initialize database connection settings
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_port = os.getenv('DB_PORT')

    def connect(self):
        """Establishes a connection to the database."""
        try:
            connection = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                port=self.db_port
            )
            return connection
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

    ### Insert into Companies
    def insert_company(self, company_name, contact_person, contact_email):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO companies (company_id, company_name, contact_person, contact_email)
                VALUES (%s, %s, %s, %s) RETURNING company_id;
                """
                company_id = uuid.uuid4()

                cursor.execute(insert_query, (
                    company_id,
                    company_name,
                    contact_person,
                    contact_email
                ))
                connection.commit()
                print(f"Company {company_id} inserted successfully.")
                return company_id  # Returning the company_id for further relationships
        
        except Exception as e:
            print(f"Failed to insert company: {e}")
        
        finally:
            connection.close()

    ### Insert into Factories
    def insert_factory(self, company_id, factory_name, factory_country, factory_city):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO factories (factory_id, company_id, factory_name, factory_country, factory_city)
                VALUES (%s, %s, %s, %s, %s) RETURNING factory_id;
                """
                factory_id = uuid.uuid4()

                cursor.execute(insert_query, (
                    factory_id,
                    company_id,
                    factory_name,
                    factory_country,
                    factory_city
                ))
                connection.commit()
                print(f"Factory {factory_id} inserted successfully.")
                return factory_id  # Returning the factory_id for further relationships
        
        except Exception as e:
            print(f"Failed to insert factory: {e}")
        
        finally:
            connection.close()

    ### Insert into Device Types
    def insert_device_type(self, device_type):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO device_types (device_type_id, device_type)
                VALUES (%s, %s) RETURNING device_type_id;
                """
                device_type_id = uuid.uuid4()

                cursor.execute(insert_query, (
                    device_type_id,
                    device_type
                ))
                connection.commit()
                print(f"Device type {device_type_id} inserted successfully.")
                return device_type_id  # Returning the device_type_id for further relationships
        
        except Exception as e:
            print(f"Failed to insert device type: {e}")
        
        finally:
            connection.close()

    ### Insert into Devices
    def insert_device(self, device_type_id, factory_id, is_test_device, is_installed, is_data_collector, installation_date):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO devices (device_id, device_type_id, factory_id, is_test_device, is_installed, is_data_collector, installation_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING device_id;
                """
                device_id = uuid.uuid4()

                cursor.execute(insert_query, (
                    device_id,
                    device_type_id,
                    factory_id,
                    is_test_device,
                    is_installed,
                    is_data_collector,
                    installation_date
                ))
                connection.commit()
                print(f"Device {device_id} inserted successfully.")
                return device_id  # Returning the device_id for further relationships
        
        except Exception as e:
            print(f"Failed to insert device: {e}")
        
        finally:
            connection.close()

    ### Insert into Images
    def insert_image(self, device_id, image_url, is_trainable, image_resolution, augmentation, timestamp=None):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO images (image_id, device_id, image_url, capture_timestamp, is_trainable, image_resolution, augmentation)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING image_id;
                """
                image_id = uuid.uuid4()
                capture_timestamp = datetime.now() if not timestamp else timestamp

                cursor.execute(insert_query, (
                    image_id,
                    device_id,
                    image_url,
                    capture_timestamp,
                    is_trainable,
                    image_resolution,
                    augmentation
                ))
                connection.commit()
                print(f"Image {image_id} inserted successfully.")
                return image_id  # Returning the image_id for further relationships
        
        except Exception as e:
            print(f"Failed to insert image: {e}")
        
        finally:
            connection.close()

    ### Insert into Detections
    def insert_detection(self, image_id, label_id, confidence_score, bbox_file_url, timestamp=None):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO detections (detection_id, image_id, label_id, confidence_score, bbox_file_url, detection_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING detection_id;
                """
                detection_id = uuid.uuid4()
                detection_timestamp = datetime.now() if not timestamp else timestamp

                cursor.execute(insert_query, (
                    detection_id,
                    image_id,
                    label_id,
                    confidence_score,
                    bbox_file_url,
                    detection_timestamp
                ))
                connection.commit()
                print(f"Detection {detection_id} inserted successfully.")
                return detection_id  # Returning the detection_id for further relationships
        
        except Exception as e:
            print(f"Failed to insert detection: {e}")
        
        finally:
            connection.close()
    
    ### Insert into labels
    def insert_labels(self, label_id, label_name):
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO labels (label_id, label_name)
                VALUES (%s, %s) RETURNING label_id;
                """

                label_id = uuid.uuid4()
                cursor.execute(insert_query, (
                    label_id,
                    label_name
                ))
                connection.commit()
                print(f"Label {label_id} inserted successfully.")
                return label_id
        except Exception as e:
            print(f"Failed to insert label: {e}")
        
        finally:
            connection.close()

    ### Fetch detection summary
    def fetch_detection_summary(self):
        """
        Fetch data from the 'detection_summary' view and return it as a pandas DataFrame.
        """
        connection = self.connect()
        if connection is None:
            return

        try:
            with connection.cursor() as cursor:
                fetch_query = """
                SELECT image_id, capture_timestamp, label_name, confidence_score, factory_name, device_type, is_trainable, is_data_collector, bbox_file_url
                FROM detection_summary;
                """
                cursor.execute(fetch_query)

                records =cursor.fetchall()

                # Define column names for the DataFrame
                columns = ['image_id', 'capture_timestamp', 'label_name', 'confidence_score', 'factory_name', 'device_type', 'is_trainable', 'is_data_collector', 'bbox_file_url']
            
                # Convert the records into a pandas DataFrame
                df = pd.DataFrame(records, columns=columns)

                # Return the DataFrame
                return df
        
        except Exception as e:
            print(f"Failed to fetch detection summary: {e}")
        
        finally:
            connection.close()
