import face_recognition
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId
from gridfs import GridFS
import cv2
import streamlit as st
from datetime import datetime, timedelta, timezone
from SurveyEmailSender import send_survey_email
import applyCss
import pytz

# MongoDB connection details
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'


def connect_to_mongodb(uri):
    """
    Establishes a connection to MongoDB and returns the database and required collections.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db, db['students'], db['workshops'], db['attendance'], db['presenters'], GridFS(db)


def get_todays_workshops(workshop_collection):
    """
    Fetches workshops scheduled for today from the database.
    """
    # Set the timezone for Windsor, Canada
    eastern = pytz.timezone('America/Toronto')  # Windsor follows the Toronto timezone (Eastern Time)

    # Get the current date and time in Eastern Time
    now = datetime.now(eastern)

    # Calculate the start and end of today in Eastern Time
    today_start = eastern.localize(datetime(now.year, now.month, now.day, 0, 0, 0))
    today_end = today_start + timedelta(days=1)

    # Convert the start and end times to UTC for the query
    today_start_utc = today_start.astimezone(pytz.utc)
    today_end_utc = today_end.astimezone(pytz.utc)

    # Query the database for today's workshops in UTC
    workshops = workshop_collection.find({
        'date': {
            '$gte': today_start_utc,
            '$lt': today_end_utc
        }
    })

    # Print workshop dates for debugging
    workshop_dict = {}
    for workshop in workshops:
        workshop_dict[workshop['workshopName']] = workshop['workshopId']
    return workshop_dict


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


def generate_google_form_url(student_id, workshop_id, presenter_id):
    base_url = "https://docs.google.com/forms/d/e/1FAIpQLSdfcY45SUCkQuREJQMR-M3E059hN-6f8ZG3t34A0CxHRWX3pA/viewform?usp=pp_url"
    filled_url = f"{base_url}&entry.1303033761={student_id}&entry.1899121104={workshop_id}&entry.569468511={presenter_id}"
    return filled_url


def process_attendance(image, known_face_encodings, student_ids, student_names, workshop_id, attendance_collection,
                       students_collection, presenter_id):
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
                    "inTime": datetime.now(timezone.utc),
                    "present": True
                }}
            )
            student_details = students_collection.find_one({"studentID": student_id})
            if student_details:
                student_email = student_details.get('email')
                student_name = f"{student_details.get('firstName')} {student_details.get('lastName')}"
                form_url = generate_google_form_url(student_id, workshop_id, presenter_id)
                send_survey_email(student_email, student_name, form_url)
            return f"Attendance marked for {student_name}"

    return "Face not recognized or student not registered for this workshop"


def main():
    applyCss.apply_custom_css()
    st.markdown('<div class="header-section">AutoAttend Tracker</div>', unsafe_allow_html=True)
    st.markdown('### Workshop Attendance System')
    # st.title("Workshop Attendance System")

    # Connect to MongoDB
    db, student_collection, workshop_collection, attendance_collection, presenters_collection, fs = connect_to_mongodb(
        URI)

    # Get today's workshops
    workshop_list = get_todays_workshops(workshop_collection)
    if not workshop_list:
        st.warning("No workshops scheduled for today.")
        return

    workshop_name = st.selectbox("Select Workshop", list(workshop_list.keys()))
    workshop_id = workshop_list[workshop_name]

    # Fetch the presenter ID for the selected workshop
    workshop = workshop_collection.find_one({"workshopId": workshop_id})
    presenter_object_id = workshop.get("presenter_id")

    if presenter_object_id:
        presenter = presenters_collection.find_one({"_id": presenter_object_id})
        presenter_id = presenter.get("presenterID")
    else:
        st.warning("Presenter details not found.")
        return

    # Load registered students
    known_face_encodings, student_ids, student_names = load_registered_students(
        workshop_id, DB_NAME, URI
    )

    if not student_ids:
        st.warning("No registered students found for the selected workshop.")
        return

    placeholder_camera = st.empty()
    # Capture photo
    img_file_buffer = placeholder_camera.camera_input("Capture Photo", key='1')

    if img_file_buffer:
        image = cv2.imdecode(np.frombuffer(img_file_buffer.read(), dtype=np.uint8), cv2.IMREAD_COLOR)
        result = process_attendance(image, known_face_encodings, student_ids, student_names, workshop_id,
                                    attendance_collection, student_collection, presenter_id)
        st.success(result)
        img_file_buffer = placeholder_camera.camera_input("Capture Photo", key='2')


if __name__ == "__main__":
    main()
