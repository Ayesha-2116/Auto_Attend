import streamlit as st
import face_recognition
import numpy as np
from pymongo import MongoClient
from gridfs import GridFS
import cv2
from datetime import datetime, timedelta

# MongoDB connection details
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def connect_to_mongodb(uri):
    """
    Establishes a connection to MongoDB and returns the database and required collections.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db, db['students'], db['workshops'], db['attendance'], GridFS(db)

def get_todays_workshops(workshop_collection):
    """
    Fetches workshops scheduled for today from the database.
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    workshops = workshop_collection.find({
        'date': {
            '$gte': today_start,
            '$lt': today_end
        }
    })
    return {w['workshopName']: w['workshopId'] for w in workshops}

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_registered_students(workshop_id, db_name, uri):
    """
    Loads registered students for the selected workshop who haven't been marked present.
    """
    client = MongoClient(uri)
    db = client[db_name]
    attendance_collection = db['attendance']
    student_collection = db['students']
    fs = GridFS(db)

    registered_students = attendance_collection.find({
        "workshopId": workshop_id,
        "present": False
    })
    
    known_face_encodings, student_ids, student_names = [], [], []

    for registered_student in registered_students:
        student_id = registered_student['username']
        student = student_collection.find_one({"studentID": student_id})
        
        if student and 'profile_image_id' in student:
            profile_image_id = student['profile_image_id']
            face_encoding = get_face_encoding(profile_image_id, fs)
            if face_encoding is not None:
                known_face_encodings.append(face_encoding)
                student_ids.append(student_id)
                student_names.append(f"{student['firstName']} {student['lastName']}")
            else:
                print(f"No face found in the photo for student ID {student_id}")
        else:
            print(f"Student with ID {student_id} not found or has no profile image")

    client.close()
    return known_face_encodings, student_ids, student_names

def get_face_encoding(profile_image_id, fs):
    """
    Retrieves and processes a student's profile image to get face encoding.
    """
    profile_image_data = fs.get(profile_image_id).read()
    image = cv2.imdecode(np.frombuffer(profile_image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings[0] if face_encodings else None

def process_attendance(image, known_face_encodings, student_ids, student_names, workshop_id, attendance_collection):
    """
    Processes the captured image for face recognition and marks attendance.
    """
    small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
    face_locations = face_recognition.face_locations(small_frame)
    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

    if not face_encodings:
        return "No face detected in the captured photo."

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            student_id = student_ids[best_match_index]
            student_name = student_names[best_match_index]

            attendance_collection.update_one(
                {"username": student_id, "workshopId": workshop_id},
                {"$set": {
                    "inTime": datetime.utcnow(),
                    "present": True
                }}
            )
            return f"Attendance marked for {student_name}"

    return "Face not recognized or student not registered for this workshop"

def main():
    st.title("Workshop Attendance System")

    # Connect to MongoDB
    db, student_collection, workshop_collection, attendance_collection, fs = connect_to_mongodb(URI)

    # Get today's workshops
    workshop_list = get_todays_workshops(workshop_collection)
    workshop_name = st.selectbox("Select Workshop", list(workshop_list.keys()))
    workshop_id = workshop_list[workshop_name]

    # Load registered students
    known_face_encodings, student_ids, student_names = load_registered_students(
        workshop_id, DB_NAME, URI
    )

    placeholder_camera = st.empty()

    # Capture photo
    img_file_buffer = placeholder_camera.camera_input("Capture Photo", key='1')

    if img_file_buffer:
        image = cv2.imdecode(np.frombuffer(img_file_buffer.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
        result = process_attendance(image, known_face_encodings, student_ids, student_names, workshop_id, attendance_collection)
        st.success(result)
        img_file_buffer = placeholder_camera.camera_input("Capture Photo", key='2')


if _name_ == "_main_":
    main()
