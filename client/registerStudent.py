import time
import streamlit as st
import cv2
import numpy as np
import base64
from pymongo import MongoClient
from io import BytesIO
import gridfs  # Import GridFS for handling image storage

# MongoDB connection details
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def connect_to_mongodb(uri):
    """
    Establishes a connection to MongoDB and returns the database and required collections.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db, db['students'], gridfs.GridFS(db)  # Return the GridFS instance

def runRegisterStudent():
    # Apply custom CSS style
    st.markdown("""
        <style>
            #autoattend-tracker {
                margin-left: auto;
                color:DodgerBlue;
                padding: inherit;
            
            }
            .header-section {
                background-color: #f0f2f6;
                /*padding: 20px;*/
                border-radius: 10px;
                color: DodgerBlue;
                text-align: center;
                margin-bottom: 20px;
                font-size: 2.5em;
                font-weight: bold;
                position: fixed;
                top: 7%;
                left: 0;
                width: 100%;
                z-index: 1000;
                margin-left: auto;
                margin-right: auto;
                
            }
           
            .stTextInput > div > div > input[type="text"],
            .stTextInput > div > div > input[type="password"] {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                width: 100%;
            }
            .stTextInput > div > div > input[type="text"]:hover,
            .stTextInput > div > div > input[type="password"]:hover {
                outline: DodgerBlue;
            }
            .stButton button {
                background-color: DodgerBlue;
                color: white;
                padding: 10px 24px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                width: 100%;
                transition: background-color 0.3s, color 0.3s;
            }
            .stButton button:hover {
                background-color: #1e90ff;
                color: white;
            }
            .stButton button:active {
                background-color: #104e8b;
                color: white;
            }
            .stButton button:focus {
                outline: none;
                color: white;
                box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.5);
            }
            .stButton button:hover,
            .stButton button:active,
            .stButton button:focus,
            .stButton button:visited {
                color: white;
            }
            
           
            [playsinline] {
                border-left: 2px solid DodgerBlue;
                border-right: 2px solid DodgerBlue;
                padding: 1px;
                border-radius: 10px;
                margin-bottom: 20px;
                margin-top: 10px;
                width: 100%;
            }
            [data-testid="stCameraInputButton"] {
                content: 'Capture Photo';
                font-weight: 400;
                background-color: DodgerBlue;
                color: white;
                height: 45px;
                border-radius: 6px;
            }
           /* [data-testid="stVerticalBlock"] {
                margin-top: -100px
            }
                */
                
            # [data-testid="stVerticalBlockBorderWrapper"]{ /* block content width*/
            #     width: 70%;
            # }
                }
        </style>
    """, unsafe_allow_html=True)
    # Streamlit interface
    st.markdown('<div class="header-section">AutoAttend Tracker</div>', unsafe_allow_html=True)
    st.markdown('### Register Student Records')
    #st.title('Register Student Records')

    # Placeholders for input fields
    placeholder_student_name = st.empty()
    placeholder_student_lname = st.empty()
    placeholder_student_id = st.empty()
    placeholder_student_email = st.empty()
    placeholder_student_username = st.empty()
    placeholder_camera = st.empty()

    # Input fields for student name and ID
    student_fname = placeholder_student_name.text_input('Enter First Name:', key='student_name_input')
    student_lname = placeholder_student_lname.text_input('Enter Last Name:', key='student_lname_input')
    student_id = placeholder_student_id.text_input('Enter Student ID:', key='student_id_input')
    student_username = placeholder_student_username.text_input('Enter Student Username:', key='student_username')
    student_email = placeholder_student_email.text_input('Enter Student Email:', key='placeholder_student_email')

    # Camera input
    img_file_buffer = placeholder_camera.camera_input("Capture Photo", key='camera_input')

    if img_file_buffer is not None:
        # To read image file buffer with OpenCV:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Save button to save data to MongoDB
    if st.button('Save Data'):
        if student_fname.strip() != '' and student_lname.strip()!='' and student_id.strip() != '' and student_email.strip() != '' and student_username.strip() != '' and img_file_buffer is not None:
            save_to_mongodb(student_fname,student_lname, student_id, student_email,student_username,cv2_img, placeholder_student_name,placeholder_student_lname, placeholder_student_id,placeholder_student_email,placeholder_student_username, placeholder_camera)
        else:
            st.warning('Please enter all fields, and capture a photo before saving.')

def save_to_mongodb(student_fname,student_lname, student_id, student_email,student_username,image, placeholder_student_name,placeholder_student_lname, placeholder_student_id,placeholder_student_email,placeholder_student_username, placeholder_camera):
    db, students_collection, fs = connect_to_mongodb(URI)
    existing_student = students_collection.find_one({'studentID': student_id})

    if existing_student:
        st.warning(f"Student with ID '{student_id}' already exists. Please use a different student ID.")
        return

    # Convert the image to bytes and store it using GridFS
    _, buffer = cv2.imencode('.jpg', image)
    image_id = fs.put(buffer.tobytes(), filename=f"{student_username}_profile.jpg")

    # Prepare and insert the document into the students collection
    document = {
        'firstName': student_fname,
        'lastName': student_lname,
        'studentID': student_id,
        'username': student_username,
        'email': student_email,
        'profile_image_id': image_id
    }

    # Insert document into MongoDB collection
    students_collection.insert_one(document)
    st.success('Data saved successfully!')
    # Refresh fields
    placeholder_student_name.text_input('Enter Student Name:', key='student_name_input2')
    placeholder_student_lname.text_input('Enter Last Name:', key='student_lname_input2')
    placeholder_student_id.text_input('Enter Student ID:', key='student_id_input2')
    placeholder_student_username.text_input('Enter Student Username:', key='student_username2')
    placeholder_student_email.text_input('Enter Student Email:', key='placeholder_student_email2')
    placeholder_camera.camera_input("Capture Photo", key='camera_input2')
