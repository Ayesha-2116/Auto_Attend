import streamlit as st
import pandas as pd
import plotly.express as px
import applyCss
from pymongo import MongoClient
from datetime import timedelta

# MongoDB connection details
URI = "mongodb+srv://AutoAttendNew:AutoAttendNew@cluster0.vlu3rze.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = 'attendance_system'

def connect_to_mongodb(uri):
    """
    Establishes a connection to MongoDB and returns the database and required collections.
    """
    client = MongoClient(uri)
    db = client[DB_NAME]
    return db, db['attendance'], db['workshops'], db['students'], db['ratings'], db['presenters']

#st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

def fetch_workshop_data(db, attendance_collection, workshops_collection):
    # db, attendance_collection, workshops_collection, _, _, _ = connect_to_mongodb(URI)

    # Fetch attendance data
    attendance = list(attendance_collection.find())

    # Get the list of workshop IDs present in the attendance data
    attended_workshop_ids = set(a['workshopId'] for a in attendance)

    # Fetch only the workshops that have entries in the attendance data
    workshops = list(workshops_collection.find({"workshopId": {"$in": list(attended_workshop_ids)}}))

    workshop_data = []
    for workshop in workshops:
        workshop_id = workshop['workshopId']
        present_count = sum(1 for a in attendance if a['workshopId'] == workshop_id and a['present'] == True)
        absent_count = sum(1 for a in attendance if a['workshopId'] == workshop_id and a['present'] == False)

        workshop_data.append({
            "Workshop Title": workshop['workshopName'],
            "Present": present_count,
            "Absent": absent_count
        })

    return pd.DataFrame(workshop_data)

def fetch_late_arrival_data(db, attendance_collection, workshops_collection):
    # db, attendance_collection, workshops_collection, _, _, _ = connect_to_mongodb(URI)

    # Fetch attendance data
    attendance = list(attendance_collection.find())

    # Get the list of workshop IDs present in the attendance data
    attended_workshop_ids = set(a['workshopId'] for a in attendance)

    # Fetch only the workshops that have entries in the attendance data
    workshops = list(workshops_collection.find({"workshopId": {"$in": list(attended_workshop_ids)}}))

    # Prepare data for late arrivals
    late_arrival_data = []
    for workshop in workshops:
        workshop_id = workshop['workshopId']
        workshop_datetime = workshop['date']

        late_count = 0
        for record in attendance:
            if record['workshopId'] == workshop_id:
                arrival_datetime = record['inTime']

                # Check if the student arrived more than 5 minutes late
                if arrival_datetime > (workshop_datetime + timedelta(minutes=5)):
                    late_count += 1

        late_arrival_data.append({
            "Workshop Title": workshop['workshopName'],
            "Late Arrival": late_count
        })

    return pd.DataFrame(late_arrival_data)


def fetch_presenter_data(db, ratings_collection, presenters_collection):
    ratings = list(ratings_collection.find())

    # Calculate the average rating for each presenter
    presenter_ratings = {}
    for rating in ratings:
        presenter_id = rating['presenterID']
        if presenter_id in presenter_ratings:
            presenter_ratings[presenter_id].append(rating['presenter_rating'])
        else:
            presenter_ratings[presenter_id] = [rating['presenter_rating']]

    average_ratings = {presenter_id: sum(ratings) / len(ratings) for presenter_id, ratings in presenter_ratings.items()}

    # Join with presenters collection to get the full names
    presenter_data = []
    for presenter_id, avg_rating in average_ratings.items():
        presenter = presenters_collection.find_one({"presenterID": presenter_id})
        if presenter:
            full_name = f"{presenter['firstName']} {presenter['lastName']}"
            presenter_data.append({
                "Presenter": full_name,
                "Rating": avg_rating
            })

    return pd.DataFrame(presenter_data)



def fetch_workshop_rating_data(db, ratings_collection, workshops_collection):
    ratings = list(ratings_collection.find())

    workshop_ratings = {}
    for rating in ratings:
        workshop_id = rating['workshopId']
        if workshop_id in workshop_ratings:
            workshop_ratings[workshop_id].append(rating['workshop_rating'])
        else:
            workshop_ratings[workshop_id] = [rating['workshop_rating']]

    average_ratings = {workshop_id: sum(ratings) / len(ratings) for workshop_id, ratings in workshop_ratings.items()}

    workshop_data = []
    for workshop_id, avg_rating in average_ratings.items():
        workshop = workshops_collection.find_one({"workshopId": workshop_id})

        if workshop:
            workshop_name = workshop['workshopName']
            workshop_data.append({
                "Workshop": workshop_name,
                "Rating": avg_rating
            })
        else:
            print(f"Workshop with ID {workshop_id} not found in workshops collection.")

    return pd.DataFrame(workshop_data)




# Function to Display the Dashboard Charts :
def displayDashboard():
    
    applyCss.apply_custom_css()
    # Top section with background color
    st.markdown('<div cl="header-section">AutoAttend Tracker</div>', unsafe_allow_html=True)
    st.markdown('### Dashboard')

    db, attendance_collection, workshops_collection, students_collection, ratings_collection, presenters_collection = connect_to_mongodb(
        URI)
    #CHART No.1 : ---------------------------------
    # Fetch workshop data from MongoDB
    df_workshops = fetch_workshop_data(db, attendance_collection, workshops_collection)

    #CHART No.2 : ---------------------------------
    df_late_arrivals = fetch_late_arrival_data(db, attendance_collection, workshops_collection)

    # CHART No.3 : ---------------------------------
    df_presenters = fetch_presenter_data(db, ratings_collection, presenters_collection)

    # CHART No.4 : ---------------------------------
    df_workshop_ratings = fetch_workshop_rating_data(db, ratings_collection, workshops_collection)

 # Create and display the chart in columns
    col1, col2 = st.columns(2)

    # Chart 1: Student attendance in workshops
    with col1:
        # st.subheader("Number of Students Present and Absent in Each Workshop (Current Week)")
        fig_workshops = px.bar(df_workshops, x='Workshop Title', y=['Present', 'Absent'], barmode='group',
                                labels={'value': 'Number of Students', 'variable': 'Attendance'},
                                title="Student's Attendance in Workshops")
        fig_workshops.update_layout(xaxis_tickangle=90) # Change to 90 degrees to make titles vertical
        st.plotly_chart(fig_workshops)

    # Chart 2: Late arrivals in the past three weeks
    with col2:
        # st.subheader("Number of Students that Arrived Late in the Past Three Weeks")
        fig_late_arrivals = px.bar(df_late_arrivals, x='Workshop Title', y='Late Arrival',
                                   labels={'Late Arrival': 'Number of Students', 'Workshop Title': 'Workshop Title'},
                                   title='Late Arrivals')
        fig_late_arrivals.update_traces(marker_color='orange')
        fig_late_arrivals.update_layout(xaxis_tickangle=90) # Change to 90 degrees to make titles vertical
        st.plotly_chart(fig_late_arrivals)

    # Chart 3: Top presenters of last week
    with col1:
        fig_presenters = px.pie(
            df_presenters,
            names='Presenter',
            values='Rating',
            labels={'Rating': 'Rating', 'Presenter': 'Presenter'},
            title='Top Presenters of Last Week'
        )
        st.plotly_chart(fig_presenters)

    # Chart 4: Top workshops of last week
    with col2:
        fig_workshop_ratings = px.pie(
            df_workshop_ratings,
            names='Workshop',
            values='Rating',
            labels={'Rating': 'Rating', 'Workshop': 'Workshop'},
            title='Top Workshops of Last Week',
            color_discrete_sequence=px.colors.qualitative.Light24
        )
        st.plotly_chart(fig_workshop_ratings)

displayDashboard()