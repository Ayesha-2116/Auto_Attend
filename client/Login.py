import streamlit as st
from pymongo import MongoClient
import time

# MongoDB connection details
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def connect_to_mongodb(uri):
    """
    Establishes a connection to MongoDB and returns the database and required collections.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db, db['admins']

def apply_custom_css():
    custom_css = """
    <style>
    body {
        background-color: LightGray;
    }
    .appview-container {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        margin-top: 1%;
    }
    #autoattend-tracker {
        margin-left: 30%;
        color:DodgerBlue;
        padding: inherit;
      
    }
    [data-testid="stAppViewBlockContainer"] {
        border: 2px solid #9e9e9e;  /* gray border color */
        padding: 20px;              /* Padding inside the section */
        border-radius: 10px;        /* Rounded corners */
        margin-bottom: 20px;        /* Space below the section */
        margin-top: 6%;           /* Set your desired height */
        width: 60%;                /* Set the width as needed */
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
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def user_registration():
    apply_custom_css()
    st.title("AutoAttend Tracker")
    st.header('User Registration')
    fName = st.text_input('First Name', placeholder='Enter first name.')
    lName = st.text_input('Last Name', placeholder='Enter last name.')
    email = st.text_input('Email Address', placeholder='Enter email.')
    password = st.text_input('Password', type='password', placeholder='Enter password.')
    confirmPassword = st.text_input('Confirm Password', type='password', placeholder='Confirm password.')
    registerButton = st.button('Register')

    if registerButton:
        if email.strip() == '' or password.strip() == '' or confirmPassword.strip() == '':
            st.error('Please fill in all required fields.')
        elif password.strip() != confirmPassword.strip():
            st.error('Password mismatch. Please check.')
        else:
            # Connect to MongoDB
            db, users_collection = connect_to_mongodb(URI)

            #client = get_mongo_client()
            #db = client['Attendence']  # Replace with your database name
            #users_collection = db['Users']  # Replace with your collection name
            
            # Check if the user already exists
            if users_collection.find_one({'email': email}):
                st.error('User already exists.')
            else:
                # Insert new user
                user_data = {
                    'first_name': fName,
                    'last_name': lName,
                    'email': email,
                    'password': password  # For security, hash the password before storing
                }
                users_collection.insert_one(user_data)
                st.success('Registration successful! Redirecting to Login...')
                st.session_state.show_login = True
                st.session_state.registered = False
                time.sleep(2)
                st.rerun()

def login():
    apply_custom_css()
    st.title("AutoAttend Tracker")
    st.header('Login')
    email = st.text_input('Email Address', placeholder='Enter email.')
    password = st.text_input('Password', type='password', placeholder='Enter password.')
    loginButton = st.button('Login')
     # Validate login credentials
    if loginButton:
        if email.strip() == '' or password.strip() == '':
            st.error('Please fill in all required fields.')
        else:
            db, users_collection = connect_to_mongodb(URI)
            #client = get_mongo_client()
            #db = client['Attendence']  # Replace with your database name
            #users_collection = db['Users']  # Replace with your collection name
            
            # Perform login authentication here
            user = users_collection.find_one({'email': email})
            if user:
                if user['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.show_login = False
                    st.success('Login successful!')
                    time.sleep(1)
                    st.rerun()    # Force rerun the script
                else:
                    st.error('Invalid password. Please try again.')
            else:
                st.error('User not found. Please try again.')

    if st.button("New User? Register here"):
        st.session_state.show_login = False
        st.session_state.registered = True
        st.rerun()
    
