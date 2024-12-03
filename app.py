import face_recognition
import pandas as pd  # type: ignore
from datetime import datetime
import cv2  # type: ignore
import os
import tkinter as tk
from tkinter import messagebox, filedialog

# Load known faces
known_faces_dir = 'C:/Users/BP/Downloads/face_detection_project'
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

# Function to capture image
def capture_image():
    cam = cv2.VideoCapture(0)
    messagebox.showinfo("Instructions", "Press SPACE to capture an image. Press ESC to cancel.")
    while True:
        ret, frame = cam.read()
        if not ret:
            messagebox.showerror("Error", "Failed to grab frame")
            break
        cv2.imshow('Press SPACE to Capture', frame)
        key = cv2.waitKey(1)
        if key == 32:  # SPACE key
            cam.release()
            cv2.destroyAllWindows()
            return frame
        elif key == 27:  # ESC key
            cam.release()
            cv2.destroyAllWindows()
            return None

# Function to recognize face
def recognize_face(captured_image):
    face_encodings = face_recognition.face_encodings(captured_image)
    if len(face_encodings) == 0:
        messagebox.showwarning("No Face Detected", "No faces detected in the image.")
        return None
    captured_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_faces, captured_encoding)
    if True in matches:
        first_match_index = matches.index(True)
        return known_names[first_match_index]
    return None

# Function to mark attendance
def mark_attendance(student_name, file='attendance.xlsx'):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    try:
        df = pd.read_excel(file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    if not df[(df["Name"] == student_name) & (df["Date"] == current_date)].empty:
        messagebox.showinfo("Attendance", f"Attendance already marked for {student_name}.")
        return
    new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
    df = pd.concat([df, new_record_df], ignore_index=True)
    try:
        df.to_excel(file, index=False)
        messagebox.showinfo("Success", f"Attendance marked for {student_name}.")
    except PermissionError:
        messagebox.showerror("Error", "Permission denied. Close the file and try again.")

# Tkinter GUI
def start_gui():
    def start_capture():
        image = capture_image()
        if image is None:
            return
        student_name = recognize_face(image)
        if student_name is None:
            messagebox.showinfo("Unrecognized", "Student not recognized!")
            return
        mark_attendance(student_name)

    def exit_application():
        root.destroy()

    # Main window
    root = tk.Tk()
    root.title("Face Recognition Attendance")
    root.geometry("400x300")

    # Add buttons
    tk.Label(root, text="Face Recognition Attendance System", font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="Capture & Mark Attendance", command=start_capture, font=("Arial", 12), width=25).pack(pady=10)
    tk.Button(root, text="Exit", command=exit_application, font=("Arial", 12), width=25).pack(pady=10)

    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    start_gui()
