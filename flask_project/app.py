from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from threading import Thread
import dlib
from scipy.spatial import distance
from imutils import face_utils
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://vikasinigokulakrishnan:VeXkTMqqSkKqkhaL@cluster0.tatpwb4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["cat_db"]
collection = db["operator_tasks"]
status_collection = db["task_status"]  # For tracking status separately

@app.route("/api/machine-data", methods=["GET"])
def get_machine_data():
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)
@app.route("/api/update-task-status", methods=["POST"])
def update_task_status():
    data = request.json
    required_fields = {"operator_id", "machine_id", "task", "status", "timestamp"}
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    machine = collection.find_one({
        "operator_id": data["operator_id"],
        "machine_id": data["machine_id"]
    })

    if not machine:
        return jsonify({"error": "Machine entry not found"}), 404

    # Initialize task_logs if it doesn't exist
    task_logs = machine.get("task_logs", [])

    # Try to find the task log entry
    updated = False
    for task in task_logs:
        if task["task"] == data["task"]:
            if data["status"] == "in_progress":
                task["status"] = "in_progress"
                task["started_at"] = data["timestamp"]
            elif data["status"] == "completed":
                task["status"] = "completed"
                task["ended_at"] = data["timestamp"]
            updated = True
            break

    # If task not found in logs, add new
    if not updated:
        new_entry = {
            "task": data["task"],
            "status": data["status"],
            "started_at": data["timestamp"] if data["status"] == "in_progress" else None,
            "ended_at": data["timestamp"] if data["status"] == "completed" else None
        }
        task_logs.append(new_entry)

    # Update the document
    collection.update_one(
        {"_id": machine["_id"]},
        {"$set": {"task_logs": task_logs}}
    )

    return jsonify({"message": "Task status updated", "task_logs": task_logs})

@app.route("/api/task-status", methods=["GET"])
def get_all_status():
    tasks = list(status_collection.find({}, {"_id": 0}))
    return jsonify(tasks)


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    data = list(collection.find())

    total_machines = len(set(d["machine_id"] for d in data if "machine_id" in d))
    total_fuel = sum(float(d.get("fuel_used", 0)) for d in data)
    avg_engine_hours = (
        sum(float(d.get("engine_hours", 0)) for d in data) / len(data)
        if data else 0
    )

    completed_tasks = 0
    in_progress_tasks = 0

    for doc in data:
        if isinstance(doc.get("task_logs"), list):
            for log in doc["task_logs"]:
                if log.get("status") == "completed":
                    completed_tasks += 1
                elif log.get("status") == "in_progress":
                    in_progress_tasks += 1

    return jsonify({
        "total_machines": total_machines,
        "total_fuel": round(total_fuel, 2),
        "average_engine_hours": round(avg_engine_hours, 2),
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks
    })


# Load face detector for helmet logic
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


@app.route('/detect_seatbelt', methods=['POST'])
def detect_seatbelt():
    data = request.json
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Simulate chest area (adjust depending on camera position)
    chest_area = img[150:300, 200:450]
    gray = cv2.cvtColor(chest_area, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=40, maxLineGap=5)

    seatbelt_detected = False
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if 25 < abs(angle) < 65:
                seatbelt_detected = True
                break

    return jsonify({'seatbelt_detected': seatbelt_detected})


@app.route('/detect_helmet', methods=['POST'])
def detect_helmet_api():
    data = request.json
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    helmet_detected = detect_helmet_from_image(img)

    return jsonify({'helmet_detected': helmet_detected})


def detect_helmet_from_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        head = img[y:y + h, x:x + w]
        if detect_helmet(head):
            return True
    return False


def detect_helmet(head_img):
    if head_img.size == 0:
        return False

    hsv = cv2.cvtColor(head_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.equalizeHist(v)
    hsv = cv2.merge([h, s, v])

    brightness_mask = v > 80
    saturation_mask = s > 50

    mask_yellow = cv2.inRange(hsv, (20, 100, 100), (35, 255, 255))
    mask_red1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
    mask_red2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
    mask_white = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))

    combined_mask = mask_yellow | mask_red1 | mask_red2 | mask_white
    combined_mask = cv2.bitwise_and(combined_mask, combined_mask, mask=brightness_mask.astype(np.uint8))
    combined_mask = cv2.bitwise_and(combined_mask, combined_mask, mask=saturation_mask.astype(np.uint8))

    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

    color_ratio = np.sum(combined_mask > 0) / (combined_mask.shape[0] * combined_mask.shape[1])
    return color_ratio > 0.06


drowsy_status = "Not started"
EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 20

def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def start_drowsiness_monitoring():
    global drowsy_status
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    cap = cv2.VideoCapture(0)
    counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            drowsy_status = "Camera error"
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            if ear < EAR_THRESHOLD:
                counter += 1
                if counter >= CONSEC_FRAMES:
                    drowsy_status = "Drowsy 😴"
            else:
                counter = 0
                drowsy_status = "Awake 😊"

@app.route("/start-drowsiness", methods=["GET"])
def start_drowsiness():
    global drowsy_status
    drowsy_status = "Starting..."
    thread = Thread(target=start_drowsiness_monitoring)
    thread.daemon = True
    thread.start()
    return jsonify({"started": True})

@app.route("/drowsiness-status", methods=["GET"])
def get_drowsiness_status():
    return jsonify({"status": drowsy_status})

if __name__ == '__main__':
    app.run(debug=True)


