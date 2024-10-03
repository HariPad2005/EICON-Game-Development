import cv2
import mediapipe as mp

# Initialize MediaPipe Hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize video capture globally
cap = cv2.VideoCapture(0)

# Variables to track hand movement
prev_x = None
movement_threshold = 15  # Adjust this to make hand movement detection more or less sensitive

# Function to get hand gesture direction
def get_gesture_direction():
    global prev_x

    ret, frame = cap.read()
    if not ret:
        return None

    # Flip the frame horizontally for natural hand movement
    frame = cv2.flip(frame, 1)

    # Convert the image to RGB as MediaPipe processes RGB images
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image and detect hands
    result = hands.process(rgb_image)

    direction = None
    # Extract hand landmarks if a hand is detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get coordinates of the index finger tip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[8]

            # Convert normalized coordinates to pixel values
            h, w, _ = frame.shape
            cx = int(index_finger_tip.x * w)

            # Detect horizontal movement based on the threshold
            if prev_x is not None:
                if cx - prev_x > movement_threshold:
                    direction = "right"
                elif prev_x - cx > movement_threshold:
                    direction = "left"

            # Update previous x-coordinate
            prev_x = cx

            # Draw landmarks and hand connections on the frame for visual feedback
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    # Show the frame for hand tracking feedback (optional)
    cv2.imshow('Hand Tracking', frame)

    # Exit camera display when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        release_camera()

    return direction

# Function to release the camera resource
def release_camera():
    cap.release()
    cv2.destroyAllWindows()
