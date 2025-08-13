import streamlit as st
from pymongo import MongoClient
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# MongoDB setup
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def connect_to_mongodb(uri):
    """
    Establishes a connection to MongoDB and returns the database and required collections.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db, db['ratings'], db['students']

def get_student_details(student_id, students_collection):
    """
    Fetch student details from the students collection.
    """
    return students_collection.find_one({"studentID": student_id})

def main():
    st.title("Workshop Feedback Survey")
    st.header("We value your feedback!")

    # Connect to MongoDB
    db, feedback_collection, students_collection = connect_to_mongodb(URI)

    # Get URL parameters
    query_params = st.experimental_get_query_params()
    workshop_id = query_params.get("workshopId", [None])[0]
    presenter_id = query_params.get("presenterID", [None])[0]
    student_id = query_params.get("studentID", [None])[0]

    # Ensure required parameters are present
    if not workshop_id or not presenter_id or not student_id:
        st.error("Missing required parameters in the URL.")
        return

    # Validate student
    student_details = get_student_details(student_id, students_collection)
    if not student_details:
        st.error("Invalid student ID.")
        return

    # Survey form
    with st.form("feedback_form"):
        st.text_input("Name", value=student_details['firstName'] + " " + student_details['lastName'], disabled=True)
        st.text_input("Student ID", value=student_id, disabled=True)
        st.text_input("Workshop ID", value=workshop_id, disabled=True)
        st.text_input("Presenter ID", value=presenter_id, disabled=True)
        comments = st.text_area("Comments on the workshop content")

        st.markdown("### Rate the workshop and presenter")
        workshop_rating = st.slider("Workshop Rating", 1, 5, 3)
        presenter_rating = st.slider("Presenter Rating", 1, 5, 3)

        # Submit button
        submitted = st.form_submit_button("Submit")

    if submitted:
        # Prepare the rating details
        rating_details = {
            "studentID": student_id,
            "workshopId": workshop_id,
            "presenterID": presenter_id,
            "workshop_rating": workshop_rating,
            "presenter_rating": presenter_rating,
            "comments": comments,
            "date": datetime.utcnow()
        }

        # Insert the rating details into MongoDB
        feedback_collection.insert_one(rating_details)

        st.success("Thank you for your feedback!")
        st.balloons()

    # Display the form details (optional, for debugging or review purposes)
    if submitted:
        st.write("### Submitted Feedback")
        #st.json(rating_details)

if __name__ == "__main__":
    main()
