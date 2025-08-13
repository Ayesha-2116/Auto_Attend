# Server
# Workshop Attendance System

This project is a Streamlit-based web application designed to automate the attendance process for workshops. The system uses face recognition to mark attendance, making the process fast and efficient.

## Features
- Face recognition-based attendance marking.
- Integration with MongoDB for storing student and workshop data.
- Real-time photo capture for face recognition.

## Requirements
- Python 3.8 or higher
- MongoDB

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/kasajubivek/AutoAttend.git
    cd yourrepository
    ```

2. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

3. **MongoDB Setup:**
    Ensure you have a MongoDB instance running and update the `URI` in the code with your MongoDB connection details.

4. **Run the application:**
    ```bash
    streamlit run face_recognition_scripts.py
    ```

## Requirements.txt

```text
streamlit==1.18.1
face_recognition==1.3.0
numpy==1.23.5
opencv-python-headless==4.6.0.66
pymongo[srv]==4.3.3
