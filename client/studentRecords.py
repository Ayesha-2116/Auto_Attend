import streamlit as st
import pandas as pd
from pymongo import MongoClient
from collections import defaultdict
import applyCss

URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def connect_to_mongodb(uri):
    client = MongoClient(uri)
    db = client[DB_NAME]

    students_collection = db['students']
    attendance_collection = db['attendance']
    workshops_collection = db['workshops']

    workshops_cursor = workshops_collection.find({}, {'_id': 0, 'workshopId': 1, 'workshopName': 1})
    workshops = {workshop['workshopId']: workshop['workshopName'] for workshop in workshops_cursor}
    workshop_names = list(workshops.values())

    attendance_info = defaultdict(lambda: {workshop_name: None for workshop_name in workshop_names})

    students = students_collection.find({}, {'studentID': 1, 'firstName': 1, 'lastName': 1})

    for student in students:
        student_id = student['studentID']
        student_name = f"{student['firstName']} {student['lastName']}"

        attendances = attendance_collection.find({'username': student_id, 'present': True})

        for attendance in attendances:
            workshop_id = attendance['workshopId']
            workshop_name = workshops.get(workshop_id, 'Unknown')

            attendance_info[student_name][workshop_name] = 1

    return attendance_info

def getStudentRecords():
    applyCss.apply_custom_css()
    st.markdown('<div class="header-section">AutoAttend Tracker</div>', unsafe_allow_html=True)
    
    attendance_info = connect_to_mongodb(URI)

    df_attendance = pd.DataFrame.from_dict(attendance_info, orient='index')
    df_attendance['Total Count'] = df_attendance.count(axis=1)

    columns = ['Total Count'] + [col for col in df_attendance.columns if col != 'Total Count']
    df_attendance = df_attendance[columns]
    st.markdown('### Students Workshop Attendance Record')
    st.dataframe(df_attendance)

getStudentRecords()
