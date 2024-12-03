import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
import face_recognition
import cv2
import pandas as pd
from datetime import datetime

# Flask app setup
app = Flask(__name__)

# Directory containing known faces
known_faces_dir = 'C:/Users/BP/Downloads/face_detection_project'
attendance_file = 'attendance.xlsx'

# Load known faces
known_faces = []
known_names = []

for filename in os.listdir(known_faces_dir):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image = face_recognition.load_image_file(f"{known_faces_dir}/{filename}")
        encodings = face_recognition.face_encodings(image)
        if encodings:
            encoding = encodings[0]
            known_faces.append(encoding)
            known_names.append(filename.split('.')[0])

# Function to recognize a face
def recognize_face(captured_image):
    face_encodings = face_recognition.face_encodings(captured_image)
    if len(face_encodings) == 0:
        return None
    captured_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_faces, captured_encoding)
    if True in matches:
        first_match_index = matches.index(True)
        return known_names[first_match_index]
    return None

# Function to mark attendance
def mark_attendance(student_name):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    try:
        df = pd.read_excel(attendance_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    if not df[(df["Name"] == student_name) & (df["Date"] == current_date)].empty:
        return f"Attendance already marked for {student_name}."
    new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
    df = pd.concat([df, new_record_df], ignore_index=True)
    df.to_excel(attendance_file, index=False)
    return f"Attendance marked for {student_name}."

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        return jsonify({"status": "error", "message": "Failed to capture image"})
    cam.release()
    cv2.destroyAllWindows()

    student_name = recognize_face(frame)
    if not student_name:
        return jsonify({"status": "error", "message": "Student not recognized"})
    message = mark_attendance(student_name)
    return jsonify({"status": "success", "message": message})

@app.route('/attendance')
def attendance():
    try:
        df = pd.read_excel(attendance_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    return df.to_html(index=False)

if __name__ == "__main__":
    app.run(debug=True)
