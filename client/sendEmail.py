import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
import threading
import streamlit as st
from pymongo import MongoClient
from collections import defaultdict
import applyCss

URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def sendEmailMain():
    applyCss.apply_custom_css()
    st.markdown('<div class="header-section">AutoAttend Tracker</div>', unsafe_allow_html=True)
    st.markdown('### Schedule Email (Weekly)')
    #st.title("Schedule Email (Weekly)")

    user_selected_day = st.selectbox("Day:",
                                     ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    task_hour = st.number_input("Hour:", min_value=0, max_value=23, value=9)
    task_minute = st.number_input("Minute:", min_value=0, max_value=59, value=0)
    selected_time = f"{task_hour:02d}:{task_minute:02d}"
    if task_hour >= 12:
        selected_time += " PM"
    else:
        selected_time += " AM"

    st.write(f"Selected day: {user_selected_day}")
    st.write(f"Selected time: {selected_time}")

    if st.button("Schedule"):
        scheduler_thread = threading.Thread(target=run_scheduler, args=(user_selected_day, task_hour, task_minute), daemon=True)
        scheduler_thread.start()
        st.success("Schedule has been triggered!")


    st.markdown('### Email now')
    #st.title("Email now")
    if st.button("Send Email"):
        job()
        st.success("Email sent!")

def connect_to_mongodb(uri):
    client = MongoClient(uri)
    db = client[DB_NAME]

    students_collection = db['students']
    attendance_collection = db['attendance']
    workshops_collection = db['workshops']

    students = students_collection.find({}, {'studentID': 1, 'firstName': 1, 'lastName': 1, 'email': 1})
    attendance_count = defaultdict(lambda: {'count': 0, 'email': ''})

    for student in students:
        student_id = student['studentID']
        student_name = f"{student['firstName']} {student['lastName']}"
        count = attendance_collection.count_documents({'username': student_id})
        attended_workshops_ids = attendance_collection.distinct('workshopId', {'username': student_id})
        workshops = workshops_collection.find({'workshopId': {'$in': attended_workshops_ids}}, {'workshopName': 1})
        workshops_names = [workshop['workshopName'] for workshop in workshops]

        attendance_count[student_name] = {
            'count': count,
            'email': student['email'],
            'workshopsAttended': workshops_names
        }

    attendance_count = dict(attendance_count)
    return attendance_count


def send_email(subject, body, to_email, from_email, password):
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject

    message.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(message)
        server.quit()
        print(f"Email sent successfully to {to_email}!")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")

def job():
    from_email = "bivektest97@gmail.com"
    password = "ypxt tsbh okvx qali"

    attendance_count = connect_to_mongodb(URI)

    for student_name, info in attendance_count.items():
        subject = "Workshop Count"
        count = info['count']
        workshops_attended = ', '.join(info['workshopsAttended']) if info['workshopsAttended'] else 'None'
        body = (
            f"Hello {student_name},\n\n"
            f"Your current workshop count is {count}.\n"
            f"Workshops attended: {workshops_attended}\n\n"
            f"Best regards,\n"
            f"AutoAttend Team"
        )
        to_email = info['email']

        send_email(subject, body, to_email, from_email, password)



def schedule_task(user_selected_day, task_hour, task_minute):
    if user_selected_day == "Monday":
        schedule.every().monday.at(f"{task_hour:02}:{task_minute:02}").do(job)
    elif user_selected_day == "Tuesday":
        schedule.every().tuesday.at(f"{task_hour:02}:{task_minute:02}").do(job)
    elif user_selected_day == "Wednesday":
        schedule.every().wednesday.at(f"{task_hour:02}:{task_minute:02}").do(job)
    elif user_selected_day == "Thursday":
        schedule.every().thursday.at(f"{task_hour:02}:{task_minute:02}").do(job)
    elif user_selected_day == "Friday":
        schedule.every().friday.at(f"{task_hour:02}:{task_minute:02}").do(job)
    elif user_selected_day == "Saturday":
        schedule.every().saturday.at(f"{task_hour:02}:{task_minute:02}").do(job)
    elif user_selected_day == "Sunday":
        schedule.every().sunday.at(f"{task_hour:02}:{task_minute:02}").do(job)


def run_scheduler(user_selected_day, task_hour, task_minute):
    schedule_task(user_selected_day, task_hour, task_minute)
    # schedule.every().saturday.at("09:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)









