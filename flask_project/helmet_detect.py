import cv2
import numpy as np
import sys

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_helmet(head_img):
    if head_img.size == 0:
        return False

    # Apply histogram equalization to normalize brightness
    hsv = cv2.cvtColor(head_img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.equalizeHist(v)
    hsv = cv2.merge([h, s, v])

    # Filter low brightness (shadows) and low saturation (dull regions)
    brightness_mask = v > 80
    saturation_mask = s > 50

    # Create color masks
    mask_yellow = cv2.inRange(hsv, (20, 100, 100), (35, 255, 255))
    mask_red1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
    mask_red2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
    mask_white = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))

    # Combine and clean masks
    combined_mask = mask_yellow | mask_red1 | mask_red2 | mask_white

    # Apply shadow rejection
    combined_mask = cv2.bitwise_and(combined_mask, combined_mask, mask=brightness_mask.astype(np.uint8))
    combined_mask = cv2.bitwise_and(combined_mask, combined_mask, mask=saturation_mask.astype(np.uint8))

    # Morphological cleanup
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

    # Helmet presence based on mask area
    color_ratio = np.sum(combined_mask > 0) / (combined_mask.shape[0] * combined_mask.shape[1])
    return color_ratio > 0.06  # Adjusted slightly from 0.05

def analyze_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        head = frame[y:y + h, x:x + w]
        helmet = detect_helmet(head)

        label = "Helmet" if helmet else "No Helmet"
        color = (0, 255, 0) if helmet else (0, 0, 255)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    return frame

def run_image(path):
    frame = cv2.imread(path)
    if frame is None:
        print(f"Could not load image: {path}")
        return

    processed = analyze_frame(frame)
    cv2.imshow("Helmet Detection (Image)", processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_webcam():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = analyze_frame(frame)
        cv2.imshow("Helmet Detection", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_image(sys.argv[1])
    else:
        run_webcam()
