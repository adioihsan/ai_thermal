import cv2

# Load the pre-trained face detection cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the OpenCV video capture
cap = cv2.VideoCapture(1)

# Initialize the face tracker
face_tracker = cv2.legacy.TrackerMOSSE_create()

# Read the first frame from the camera
ret, frame = cap.read()

# Detect the face in the first frame
faces = face_cascade.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

if len(faces) > 0:
    x, y, w, h = faces[0]
    bbox = (x, y, w, h)
    face_tracker.init(frame, bbox)
else:
    print("No face detected!")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Update the face tracker
    ret, bbox = face_tracker.update(frame)

    if ret:
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Tracking failure", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    cv2.imshow("Face Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the resources
cap.release()
cv2.destroyAllWindows()
