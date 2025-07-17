import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize for performance
    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Simulate chest area (hardcoded for now — adjust if needed)
    chest_area = gray[150:300, 200:450]
    color_crop = frame[150:300, 200:450].copy()

    # Detect edges in the chest region
    edges = cv2.Canny(chest_area, 50, 150, apertureSize=3)

    # Hough Line Transform to detect diagonal lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=40, maxLineGap=5)

    seatbelt_detected = False
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            # Check for diagonal-ish lines (25° to 65°)
            if 25 < abs(angle) < 65:
                seatbelt_detected = True
                cv2.line(frame, (x1 + 200, y1 + 150), (x2 + 200, y2 + 150), (0, 255, 0), 2)

    label = "Seatbelt: YES" if seatbelt_detected else "Seatbelt: NO"
    color = (0, 255, 0) if seatbelt_detected else (0, 0, 255)
    cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

    # Draw rectangle showing where we're checking
    cv2.rectangle(frame, (200, 150), (450, 300), (255, 255, 0), 2)

    # Show the result
    cv2.imshow("Seatbelt Detection", frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
