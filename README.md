# Facial Biometric Attendance & Productivity Monitor

A real-time, contactless attendance system that verifies identity via facial recognition and infers productivity from emotion detection - all running locally in the browser.

## Overview

Traditional attendance systems — manual registers, RFID cards — verify presence but tell you nothing about the person behind the check-in. This system goes further: when someone checks in, it recognises their face, detects their emotional state, computes a productivity score, and logs everything to a daily Excel file. The full pipeline runs in ~1.3 seconds per user.

---

## Features

- **Face Recognition** — real-time identity verification against a registered user database using `face_recognition` + dlib
- **Emotion Detection** — 7-class classification (Happy, Neutral, Sad, Angry, Fear, Disgust, Surprise) powered by DeepFace
- **Productivity Scoring** — weighted emotion-to-productivity formula, normalised to 0–100%
- **Daily Excel Logging** — auto-generated `log_YYYY-MM-DD.xlsx` with name, timestamp, dominant emotion, and score
- **Analytics Dashboard** — per-user weekly emotion pie chart and daily productivity trend line chart via Chart.js
- **Unknown Face Blocking** — unregistered faces are flagged and denied check-in

---

## Architecture

```
┌────────────────────────────────────────────┐
│              Flask Web Application          │
│  Home · Mark Attendance · Dashboard · Logs  │
└───────────────────┬────────────────────────┘
                    │
       ┌────────────▼────────────┐
       │       Core Modules       │
       │                         │
       │  FaceRecognizer         │
       │    └─ User Database     │
       │  EmotionAnalyzer        │
       │    └─ DeepFace          │
       │  ProductivityCalculator │
       └────────────┬────────────┘
                    │
       ┌────────────▼────────────┐
       │         Storage          │
       │  ExcelLogger            │
       │    └─ log_YYYY-MM-DD    │
       └─────────────────────────┘
```

## Productivity Formula

Each emotion is assigned a weight reflecting its estimated impact on work readiness:

| Emotion | Weight |
|---|---|
| Happy | +2 |
| Neutral | +1 |
| Surprise | 0 |
| Sad | -1 |
| Angry | -2 |
| Fear | -2 |
| Disgust | -2 |

```
Raw Score        = Σ (weight_i × emotion_intensity_i)
Normalized Score = Raw Score / (2 × Σ emotion_intensities)
Productivity (%) = ((Normalized Score + 1) / 2) × 100
```

Output is bounded between 0% and 100%. A neutral emotional state yields approximately 50–70% depending on the full emotion distribution.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Backend | Python, Flask |
| Face Recognition | `face_recognition` (dlib), OpenCV |
| Emotion Detection | DeepFace (VGG-Face, Facenet, OpenFace) |
| Data Storage | OpenPyXL, Pandas |
| Frontend | HTML, CSS, JavaScript |
| Visualisation | Chart.js |

---

## Setup

```bash
# Clone
git clone https://github.com/ommhatre/Facial-Attendance-System.git
cd Facial-Attendance-System

# Install dependencies
pip install flask opencv-python face_recognition deepface openpyxl pandas

# Register users
# Add one image per person to /users, named after them (e.g. Om.jpg)
mkdir users

# Run
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### Project Structure

```
Facial-Attendance-System/
├── app.py
├── users/                   # Registered face images (name.jpg)
├── log_YYYY-MM-DD.xlsx      # Auto-generated daily logs
└── templates/
    ├── index.html
    ├── mark_attendance.html
    ├── display_attendance.html
    └── productivity.html
```
