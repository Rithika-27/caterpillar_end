import cv2
import dlib
import time
import pyttsx3
from scipy.spatial import distance
from imutils import face_utils

# Voice assistant setup
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speech speed

def speak_alert(message):
    engine.say(message)
    engine.runAndWait()

# Eye aspect ratio calculation
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Constants
EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 20
COUNTER = 0
last_alert_time = 0
alert_interval = 5  # seconds

# Load detectors
print("[INFO] Loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# Start video stream
print("[INFO] Starting video stream...")
cap = cv2.VideoCapture(0)
time.sleep(1.0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0

        current_time = time.time()

        if ear < EAR_THRESHOLD:
            COUNTER += 1
            if COUNTER >= CONSEC_FRAMES:
                if current_time - last_alert_time >= alert_interval:
                    print("[ALERT] Drowsiness Detected!")
                    speak_alert("Warning! You are feeling sleepy. Please take a break!")
                    last_alert_time = current_time
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            COUNTER = 0  # Reset if no drowsiness

        cv2.putText(frame, f"EAR: {ear:.2f}", (480, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Driver Drowsiness Detection", frame)
    if cv2.waitKey(1) == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
