import streamlit as st
from streamlit_option_menu import option_menu
import Dashboard
import registerStudent
import studentSearch
import face_recognition_script, workshop_data_entry, studentRecords
from Login import login, user_registration
import sendEmail

st.set_page_config(
    page_title="AutoAttend Tracker",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

class AutoAttendApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title='Menu',
                options=[app['title'] for app in self.apps],
                icons=['house', 'person-plus', 'camera', 'book', 'briefcase','file-text'],
                menu_icon='menu-app-fill',
                default_index=0,
                styles={
                    "container": {"padding": "0!important", "background-color": "#f0f2f6"},
                    "icon": {"color": "orange", "font-size": "25px"},
                    "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                    "nav-link-selected": {"background-color": "#007BFF"},
                }
            )
            if st.button('Logout'):
                logout()

        for app_dict in self.apps:
            if app_dict['title'] == app:
                app_dict['function']()
                break

def display_dashboard():
    Dashboard.displayDashboard()

def register_student():
    registerStudent.runRegisterStudent()

def face_recognition():
    face_recognition_script.main()

def search_student():
    studentSearch.main()

def workshopData():
    workshop_data_entry.main()

def schedule_email():
    sendEmail.sendEmailMain()

def student_record():
    studentRecords.getStudentRecords()

def logout():
    st.session_state.logged_in = False
    st.session_state.show_login = True
    st.session_state.registered = False
    st.experimental_rerun()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'show_login' not in st.session_state:
        st.session_state.show_login = True
    if 'registered' not in st.session_state:
        st.session_state.registered = False

    if st.session_state.logged_in:
        app = AutoAttendApp()
        app.add_app('Dashboard', display_dashboard)
        app.add_app('Register Student', register_student)
        app.add_app('Attendance', face_recognition)
        app.add_app('Student Attendance Record', search_student)
        app.add_app('Workshop Record', workshopData)
        app.add_app('Student Record', student_record)
        app.add_app('Schedule Email', schedule_email)
        app.run()
    else:
        if st.session_state.show_login and not st.session_state.registered:
            login()
        elif st.session_state.registered:
            user_registration()
            if st.button("Already registered? Login here"):
                st.session_state.show_login = True
                st.session_state.registered = False
                st.experimental_rerun()

if __name__ == "__main__":
    main()
