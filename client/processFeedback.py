import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import pytz
import requests
import os

# MongoDB connection details
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'
COLLECTION_NAME = 'ratings'  # Ensure this is the correct collection name

# URL to download the CSV file
CSV_URL = "https://docs.google.com/spreadsheets/d/1JJ1wJgF7YmLXeJFrMDgQaKuxRXsuri7zkL5HdcKSCd8/export?format=csv"

# Path to save the downloaded CSV file
CSV_FILE_PATH = r'C:\Users\Admin\Downloads\WorkshopFeedbackResponse - Form responses 1.csv'


def connect_to_mongodb(uri):
    try:
        client = MongoClient(uri)
        db = client[DB_NAME]
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


def download_csv(csv_url, file_path):
    try:
        response = requests.get(csv_url)
        response.raise_for_status()  # Check if the request was successful
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded CSV file to {file_path}")
    except Exception as e:
        print(f"Error downloading CSV file: {e}")
        raise


def validate_file(file_path):
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return False
    if os.path.getsize(file_path) == 0:
        print(f"File is empty: {file_path}")
        return False
    return True


def upload_csv_to_mongodb(csv_file_path, db, collection_name):
    if not validate_file(csv_file_path):
        print(f"File validation failed: {csv_file_path}")
        return

    try:
        # Read CSV file into a DataFrame, skip bad lines
        df = pd.read_csv(csv_file_path, on_bad_lines='skip')

        # Define mappings from CSV columns to MongoDB fields
        field_mapping = {
            'Timestamp': 'timestamp',
            'Student ID': 'studentID',
            'Workshop ID': 'workshopId',
            'Presenter ID': 'presenterID',
            'Workshop Rating': 'workshop_rating',
            'Presenter Rating': 'presenter_rating',
            'Comments': 'comments'
        }

        # Convert DataFrame to dictionary with appropriate MongoDB structure
        data = []
        collection = db[collection_name]

        for index, row in df.iterrows():
            try:
                print(f"Processing row {index}: {row.to_dict()}")  # Print row data for debugging

                # Ensure all required fields are present
                required_fields = ['Timestamp', 'Student ID', 'Workshop ID', 'Presenter ID', 'Workshop Rating',
                                   'Presenter Rating']
                if any(pd.isnull(row[field]) for field in required_fields):
                    print(f"Skipping row {index} due to missing required fields.")
                    continue

                document = {
                    'timestamp': datetime.strptime(row['Timestamp'], '%m/%d/%Y %H:%M:%S'),  # Adjusted format
                    'studentID': row['Student ID'],
                    'workshopId': row['Workshop ID'],
                    'presenterID': row['Presenter ID'],
                    'workshop_rating': int(row['Workshop Rating']),
                    'presenter_rating': int(row['Presenter Rating']),
                    'comments': row['Comments'],
                    'date': datetime.now(pytz.UTC)  # Use timezone-aware UTC datetime
                }

                # Check for duplicates based on unique fields
                query = {
                    'timestamp': document['timestamp'],
                    'studentID': document['studentID'],
                    'workshopId': document['workshopId'],
                    'presenterID': document['presenterID']
                }

                if collection.find_one(query):
                    print(f"Duplicate record found, skipping row {index}.")
                else:
                    data.append(document)
            except Exception as e:
                print(f"Error processing row {index}: {e}")

        if data:
            # Insert data into MongoDB collection
            if data:
                result = collection.insert_many(data)
            print(f"Inserted {len(result.inserted_ids)} documents into the '{collection_name}' collection.")
        else:
            print("No valid documents to insert into MongoDB.")
    except Exception as e:
        print(f"Error uploading CSV data to MongoDB: {e}")


def main():
    # Download the CSV file
    download_csv(CSV_URL, CSV_FILE_PATH)

    # Connect to MongoDB
    db = connect_to_mongodb(URI)

    # Upload CSV data to MongoDB
    upload_csv_to_mongodb(CSV_FILE_PATH, db, COLLECTION_NAME)


if __name__ == "__main__":
    main()
