from flask import Flask, render_template, Response
import cv2
import os
import face_recognition
from datetime import datetime
import openpyxl

app = Flask(__name__)

# Encodings and Name list
user_face_encodings = []
user_face_names = []

# Extract encodings and names from database and appending them to the main list
user_data = 'users'
for u in os.listdir(user_data):
    path = 'users/'+ u
    name = u.partition(".")[0]

    user_image = face_recognition.load_image_file(path)
    user_encoding = face_recognition.face_encodings(user_image)[0]
    
    user_face_encodings.append(user_encoding)
    user_face_names.append(name)

# Initialize Excel workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["Name", "Time"])

# Function to check if a name has already been logged
def is_name_logged(name):
    for row in ws.iter_rows(min_row=2, max_col=1):
        if row[0].value == name:
            return True
    return False

# Function to check if a name has already been marked present
def is_present(name):
    for row in ws.iter_rows(min_row=2, max_col=2):
        if len(row) >= 2 and row[0].value == name and row[1].value is not None:
            return True
    return False

def detect_faces():
    camera = cv2.VideoCapture(0)

    while True:
        ret, frame = camera.read()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(frame_rgb)
        face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(user_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = user_face_names[first_match_index]

                if not is_name_logged(name):
                    # Log the name and current time
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ws.append([name, current_time])
                    today_date = str(datetime.today()).partition(" ")[0]
                    log_name = "log_" + str(today_date) + ".xlsx"
                    wb.save(log_name)  # Save the workbook

                if is_present(name):
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name} (Present)", (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                else:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            else:
                # Draw a red rectangle and display "Unknown" for faces not recognized in the database
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    camera.release()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mark_attendance')
def mark_attendance():
    return render_template('mark_attendance.html')

@app.route('/video_feed')
def video_feed():
    return Response(detect_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/display_attendance')
def display_attendance():
    # Load attendance data from Excel file
    data = []
    for row in ws.iter_rows(min_row=2, max_col=2):
        name, time = row[0].value, row[1].value
        data.append((name, time))
    return render_template('display_attendance.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
