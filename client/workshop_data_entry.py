import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
 
# MongoDB connection
client = MongoClient("mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['attendance_system']
 
def apply_customCss():
    # Define your custom CSS
    custom_css = """
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
        /*
        [data-testid="stAppViewBlockContainer"] {
            border: 2px solid #9e9e9e;  /* gray border color */
            padding: 20px;              /* Padding inside the section */
            border-radius: 10px;        /* Rounded corners */
            margin-bottom: 20px;        /* Space below the section */
            margin-top: 90px;           /* Set your desired height */
            width: 100%;                /* Set the width as needed */
        }*/
    </style>
    """
 
    # Inject the custom CSS into the app
    st.markdown(custom_css, unsafe_allow_html=True)
 
# Function to insert attendance
def insert_attendance(username, workshop_id, in_time, present):
    attendance_record = {
        "username": username,
        "workshopId": workshop_id,
        "inTime": in_time,
        "present": present
    }
    db.attendance.insert_one(attendance_record)
 
def insert_workshop(workshop_details, presenter_details):
    # Check if presenter already exists
    presenter = db.presenters.find_one({"username": presenter_details['username']})
    
    if not presenter:
        # Insert presenter details into presenters collection
        presenter_record = {
            "presenterID": presenter_details['presenterID'],
            "username": presenter_details['username'],
            "email": presenter_details['email'],
            "firstName": presenter_details['firstName'],
            "lastName": presenter_details['lastName'],
            "qualification": presenter_details.get('qualification', ''),
        }
        presenter_id = db.presenters.insert_one(presenter_record).inserted_id
    else:
        presenter_id = presenter['_id']

    # Create workshop document with reference to presenter
    combined_datetime = datetime.combine(workshop_details['date'], workshop_details['time'])
    workshop_record = {
        "workshopId": workshop_details['workshopId'],
        "workshopName": workshop_details['workshopName'],
        "date": combined_datetime,
        "location": workshop_details['location'],
        "presenter_id": presenter_id,  # Reference to presenter
    }
    db.workshops.insert_one(workshop_record)
    st.success("Workshop added successfully.")

# Helper functions to get presenter details
def get_presenter_id_by_username(username):
    presenter = db.presenters.find_one({"username": username}, {"_id": 1})
    return presenter['_id'] if presenter else None
 
def get_presenter_email_by_username(username):
    presenter = db.presenters.find_one({"username": username}, {"email": 1})
    return presenter['email'] if presenter else None
 
def get_presenter_firstName_by_username(username):
    presenter = db.presenters.find_one({"username": username}, {"firstName": 1})
    return presenter['firstName'] if presenter else None
 
def get_presenter_lastName_by_username(username):
    presenter = db.presenters.find_one({"username": username}, {"lastName": 1})
    return presenter['lastName'] if presenter else None
 
def get_presenter_usernames():
    presenters = db.presenters.find({}, {"username": 1})
    presenter_usernames = [presenter['username'] for presenter in presenters]
    return presenter_usernames
 
# Streamlit app
def main():
    apply_customCss()
    st.markdown('<div class="header-section">AutoAttend Tracker</div>', unsafe_allow_html=True)
    st.markdown('### Workshop and Attendance Management')
 
    # Tabs for different sections
    tab1, tab2 = st.tabs(["Upload Attendance", "Add Workshop"])
 
    with tab1:
        st.subheader("Attendance Upload")
       
        # File upload and validation
        uploaded_file = st.file_uploader("Upload Excel file", type=["xls", "xlsx"])
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
 
                # Check if required columns are present
                required_columns = ['Student_ID', 'Student Name', 'Workshop Name']
                if not set(required_columns).issubset(df.columns):
                    st.error("Excel file must contain columns: 'Student_ID', 'Student Name', 'Workshop Name'.")
                    return
 
                # Check if all rows have these columns filled
                if df[required_columns].isnull().values.any():
                    st.error("All rows must have 'Student_ID', 'Student Name', 'Workshop Name' filled.")
                    return
 
                # Check if all student IDs exist in the student table
                student_ids = df['Student_ID'].astype(str).tolist()
                existing_students = db.students.find({'studentID': {'$in': student_ids}})
                existing_student_ids = {student['studentID'] for student in existing_students}
 
                missing_student_ids = [sid for sid in student_ids if sid not in existing_student_ids]
                if missing_student_ids:
                    st.error(f"Student IDs not found in database: {', '.join(map(str, missing_student_ids))}")
                else:                    # Insert attendance records
                    for index, row in df.iterrows():
                        student_id = str(row['Student_ID'])
                        student_name = row['Student Name']
                        workshop_name = row['Workshop Name']
    
                        # Fetch workshop ID based on workshop_name
                        workshop = db.workshops.find_one({'workshopName': workshop_name})
                        if workshop:
                            workshop_id = workshop['workshopId']
                            in_time = workshop['date'] + timedelta(hours=7)  # Adjust as per timezone
                            present = False  # Assuming default is not present
    
                            # Fetch username from students table based on student_id
                            student = db.students.find_one({'studentID': student_id})
                            if student:
                                insert_attendance(student_id, workshop_id, in_time, present)
                                st.success(f"Attendance recorded for {student_name} at {workshop_name}.")
                        else:
                            st.warning(f"Workshop '{workshop_name}' not found in database.")
            except Exception as e:
                st.error(f"Error processing file: {e}")
 
    with tab2:
        st.subheader("Add Workshop and Presenter")
 
        presenter_names = get_presenter_usernames()
        selected_presenter = st.selectbox("Select Presenter", options=presenter_names + ["Add New Presenter"])
 
        if selected_presenter == "Add New Presenter" or st.session_state.get('add_presenter_mode', False):
            st.session_state.add_presenter_mode = True
            with st.form(key='add_presenter_form'):
                st.subheader("Add New Presenter")
                presenter_id = st.text_input("Presenter ID")
                username = st.text_input("Username")
                email = st.text_input("Email")
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                qualification = st.text_input("Qualification")
                workshop_id = st.text_input("Workshop ID")
                workshop_name = st.text_input("Workshop Name")
                date = st.date_input("Date", min_value=datetime.today())
                time = st.time_input("Time")
                location = st.text_input("Location")
                submit_button = st.form_submit_button("Submit")
                st.session_state.add_presenter_mode = False

 
                if submit_button:
                    presenter_details = {
                        "presenterID": presenter_id,
                        "username": username,
                        "email": email,
                        "firstName": first_name,
                        "lastName": last_name,
                        "qualification": qualification
                    }
                    workshop_details = {
                        "workshopId": workshop_id,
                        "workshopName": workshop_name,
                        "date": date,
                        "time": time,
                        "location": location,
                    }
                    insert_workshop(workshop_details, presenter_details)
                    st.session_state.add_presenter_mode = False
 
        if not st.session_state.get('add_presenter_mode', False):
            if selected_presenter != "Add New Presenter":
                presenter_id = get_presenter_id_by_username(selected_presenter)
                presenter_email = get_presenter_email_by_username(selected_presenter)
                presenter_fn = get_presenter_firstName_by_username(selected_presenter)
                presenter_ln = get_presenter_lastName_by_username(selected_presenter)
                presenter_details = {
                    "presenterID": presenter_id,
                    "username": selected_presenter,
                    "email": presenter_email,
                    "firstName": presenter_fn,
                    "lastName": presenter_ln
                }
                if presenter_id:
                    st.subheader("Enter Workshop Details")
                    workshop_id = st.text_input("Workshop ID")
                    workshop_name = st.text_input("Workshop Name")
                    date = st.date_input("Date", min_value=datetime.today())
                    time = st.time_input("Time")
                    location = st.text_input("Location")
 
                    if st.button("Add Workshop"):
                        workshop_details = {
                            "workshopId": workshop_id,
                            "workshopName": workshop_name,
                            "date": date,
                            "time": time,
                            "location": location,
                        }
                        insert_workshop(workshop_details, presenter_details)
 
if __name__ == "__main__":
    main()