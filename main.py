import cv2
import time
import math
from cvzone.HandTrackingModule import HandDetector

# --- States ---
ENTER_FIRST_NUMBER = 0
SELECT_OPERATOR = 1
ENTER_SECOND_NUMBER = 2
SHOW_RESULT = 3
RESET = 4

state_names = {
    ENTER_FIRST_NUMBER: "Enter First Number",
    SELECT_OPERATOR: "Select Operator",
    ENTER_SECOND_NUMBER: "Enter Second Number",
    SHOW_RESULT: "Result",
    RESET: "Reset"
}

def get_number_from_hand(hand, detector):
    """
    Returns the number based on the hand type and fingers up.
    Right hand: 1-5
    Left hand: 6-10
    Fist (both/either): 0
    Returns None if not clearly a number.
    """
    fingers = detector.fingersUp(hand)
    count = sum(fingers)

    if count == 0:
        return 0

    hand_type = hand["type"]
    if hand_type == "Right":
        return count
    elif hand_type == "Left":
        return count + 5

    return None

def get_operator_from_hand(hand, detector):
    """
    Returns the operator based on the gesture.
    ✌️ Peace sign (index + middle finger) = Addition (+)
    👍 Thumbs up only = Subtraction (-)
    ☝️ Index finger only = Multiplication (*)
    🤙 Pinky finger only = Division (/)
    """
    fingers = detector.fingersUp(hand)

    # [thumb, index, middle, ring, pinky]
    if fingers == [0, 1, 1, 0, 0]:
        return "+"
    elif fingers == [1, 0, 0, 0, 0]:
        return "-"
    elif fingers == [0, 1, 0, 0, 0]:
        return "*"
    elif fingers == [0, 0, 0, 0, 1] or fingers == [1, 0, 0, 0, 1]:
        # Thumbs up + pinky is sometimes detected for shaka (pinky only). We can check for pinky only [0,0,0,0,1]
        # but MediaPipe's Shaka/Call me is usually thumb+pinky [1,0,0,0,1]. Let's support both just in case,
        # but the spec says "Pinky finger only".
        return "/"
    return None

def draw_ui(img, current_gesture, equation, state, progress, final_result, error_msg):
    """
    Draws the UI elements on the image.
    Top left: current gesture being detected
    Top center: equation so far
    Top right: current state
    Center bottom: final result
    Progress bar: mid-screen (bottom-ish)
    """
    height, width, _ = img.shape

    # Top Left: Current Gesture
    cv2.putText(img, f"Gesture: {current_gesture}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Top Center: Equation
    # Calculate text size to center it
    eq_text = f"Eq: {equation}"
    text_size = cv2.getTextSize(eq_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    eq_x = (width - text_size[0]) // 2
    cv2.putText(img, eq_text, (eq_x, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Top Right: Current State
    state_text = f"State: {state_names.get(state, '')}"
    text_size = cv2.getTextSize(state_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    state_x = width - text_size[0] - 20
    cv2.putText(img, state_text, (state_x, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Progress Bar
    if progress > 0:
        bar_width = 400
        bar_height = 30
        x1 = (width - bar_width) // 2
        y1 = height - 150
        x2 = x1 + bar_width
        y2 = y1 + bar_height

        cv2.rectangle(img, (x1, y1), (x2, y2), (200, 200, 200), 2)

        fill_width = int((progress / 2.0) * bar_width) # 2.0 is the hold time
        if fill_width > bar_width:
            fill_width = bar_width

        cv2.rectangle(img, (x1, y1), (x1 + fill_width, y2), (0, 255, 0), cv2.FILLED)

    # Final Result
    if state == SHOW_RESULT:
        if error_msg:
            res_text = error_msg
            color = (0, 0, 255)
        else:
            res_text = f"Result: {final_result}"
            color = (255, 0, 255)

        text_size = cv2.getTextSize(res_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
        res_x = (width - text_size[0]) // 2
        cv2.putText(img, res_text, (res_x, height - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)

    # Error overlay logic
    if error_msg and state != SHOW_RESULT:
         text_size = cv2.getTextSize(error_msg, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
         err_x = (width - text_size[0]) // 2
         cv2.putText(img, error_msg, (err_x, height - 50),
                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=2)

    state = ENTER_FIRST_NUMBER

    first_num = None
    operator = None
    second_num = None
    final_result = None
    error_msg = ""

    current_gesture_val = None
    gesture_start_time = 0

    while True:
        success, img = cap.read()
        if not success:
            continue

        img = cv2.flip(img, 1) # Mirror image for user convenience
        hands, img = detector.findHands(img, draw=True, flipType=True)

        # State logic variables
        detected_val = None
        is_reset_gesture = False
        is_calc_gesture = False
        progress = 0.0

        # Determine gestures
        if hands:
            if state != SHOW_RESULT:
                error_msg = ""

            # Check for reset (open palm facing camera - 5 fingers up on both hands)
            if len(hands) == 2:
                fingers1 = detector.fingersUp(hands[0])
                fingers2 = detector.fingersUp(hands[1])
                if sum(fingers1) == 5 and sum(fingers2) == 5:
                    is_reset_gesture = True
                # Check for calc (fist on both hands)
                elif sum(fingers1) == 0 and sum(fingers2) == 0:
                    is_calc_gesture = True

            if not is_reset_gesture and not is_calc_gesture:
                # Process single hand for numbers/operators
                hand = hands[0] # Priority to the first detected hand
                if state in [ENTER_FIRST_NUMBER, ENTER_SECOND_NUMBER]:
                    detected_val = get_number_from_hand(hand, detector)
                elif state == SELECT_OPERATOR:
                    detected_val = get_operator_from_hand(hand, detector)
        else:
            error_msg = "No hand detected"
            current_gesture_val = None
            gesture_start_time = 0

        # Handle Reset Gesture
        if is_reset_gesture:
            state = ENTER_FIRST_NUMBER
            first_num = None
            operator = None
            second_num = None
            final_result = None
            error_msg = ""
            current_gesture_val = None
            gesture_start_time = 0

        # Handle Calculate Gesture
        elif is_calc_gesture and state == ENTER_SECOND_NUMBER and second_num is not None:
            if operator == '/' and second_num == 0:
                error_msg = "Error: Div by 0"
                final_result = None
            else:
                try:
                    if operator == '+':
                        final_result = first_num + second_num
                    elif operator == '-':
                        final_result = first_num - second_num
                    elif operator == '*':
                        final_result = first_num * second_num
                    elif operator == '/':
                        final_result = first_num / second_num
                except Exception as e:
                    error_msg = f"Error: {str(e)}"

            state = SHOW_RESULT

        # Handle state transitions based on timer
        elif detected_val is not None and state != SHOW_RESULT:
            if detected_val == current_gesture_val:
                # Same gesture held
                elapsed = time.time() - gesture_start_time
                progress = elapsed
                if elapsed >= 2.0:
                    # Confirm gesture
                    if state == ENTER_FIRST_NUMBER:
                        first_num = detected_val
                        state = SELECT_OPERATOR
                    elif state == SELECT_OPERATOR:
                        operator = detected_val
                        state = ENTER_SECOND_NUMBER
                    elif state == ENTER_SECOND_NUMBER:
                        second_num = detected_val
                        # Wait for calculate gesture now

                    # Reset timer for next state
                    current_gesture_val = None
                    gesture_start_time = 0
            else:
                # New gesture detected
                current_gesture_val = detected_val
                gesture_start_time = time.time()

        # Build equation string
        eq_str = ""
        if first_num is not None:
            eq_str += str(first_num)
        if operator is not None:
            eq_str += f" {operator}"
        if second_num is not None:
            eq_str += f" {second_num}"
        if state == SHOW_RESULT:
            eq_str += " ="

        # Draw UI
        draw_ui(img, str(detected_val) if detected_val is not None else "None", eq_str, state, progress, final_result, error_msg)

        cv2.imshow("Gesture Calculator", img)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
