# import streamlit as st
# from datetime import time, date
#
# # Apply custom CSS style
# st.markdown("""
#     <style>
#         body {
#             background-color: LightGray;
#         }
#         .stRadio > div {
#             background-color: white;
#             border: 1px solid #ccc;
#             border-radius: 5px;
#             padding: 8px;
#             width: 100%;
#         }
#         .stRadio > div > label {
#             color: DodgerBlue;
#         }
#         .stRadio > div > div > label {
#             background-color: white;
#             color: black;
#             padding: 8px;
#             border-radius: 5px;
#         }
#         .stRadio > div > div > label:hover {
#             background-color: DodgerBlue;
#             color: white;
#         }
#         .stButton button {
#             background-color: DodgerBlue;
#             color: white;
#             padding: 10px 24px;
#             border: none;
#             border-radius: 5px;
#             cursor: pointer;
#             width: 100%;
#             transition: background-color 0.3s, color 0.3s;
#         }
#         .stButton button:hover {
#             background-color: #1e90ff;
#             color: white;
#         }
#         .stButton button:active {
#             background-color: #104e8b;
#             color: white;
#         }
#         .stButton button:focus {
#             outline: none;
#             color: white;
#             box-shadow: 0 0 0 2px rgba(30, 144, 255, 0.5);
#         }
#     </style>
# """, unsafe_allow_html=True)
#
# # Streamlit interface
# st.title('Schedule Email')
#
# # Dropdown or radio button for scheduling options
# options = ["Weekly", "Bi-weekly", "Monthly"]
# schedule = st.radio("Select your email schedule:", options, index=0)
#
# # Day selection
# days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
# selected_day = st.selectbox("Select the day of the week", days_of_week)
#
# # Date and time input
# start_date = st.date_input("Select the start date", date.today())
# selected_time = st.time_input("Select the time", time(9, 0))
#
# # Submit button
# if st.button('Submit'):
#     st.write(f"Scheduled: {schedule}")
#     st.write(f"Start Date: {start_date}")
#     st.write(f"Day: {selected_day}")
#     st.write(f"Time: {selected_time}")
#     st.success('Email schedule submitted successfully!')
