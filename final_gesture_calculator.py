#!/usr/bin/env python3
"""
Final Hand Gesture Calculator - Working with MediaPipe Tasks API
Uses the newer MediaPipe tasks API for reliable hand detection.

Installation requirements:
pip install opencv-python mediapipe

Author: AI Assistant
License: MIT
"""

import cv2
import time
import numpy as np
import urllib.request
import os

# ==================== CONSTANTS ====================
HOLD_TIME = 1.0
RESULT_DISPLAY_TIME = 2.0
ERROR_DISPLAY_TIME = 2.0

# UI Constants
FONT_SCALE = 1.5
FONT_THICKNESS = 3
LARGE_FONT_SCALE = 2.5
LARGE_FONT_THICKNESS = 4
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 80
BUTTON_MARGIN = 20

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GREEN = (144, 238, 144)

# States
STATE_FIRST_NUMBER = 0
STATE_OPERATOR = 1
STATE_SECOND_NUMBER = 2
STATE_SHOW_RESULT = 3


class FinalGestureCalculator:
    """Final gesture calculator with working hand detection."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.state = STATE_FIRST_NUMBER
        self.first_number = None
        self.operator = None
        self.second_number = None
        self.result = None
        self.error_message = ""
        
        # Gesture confirmation
        self.current_finger_count = None
        self.gesture_start_time = 0
        self.confirmation_progress = 0.0
        
        # Display timing
        self.result_start_time = 0
        self.error_start_time = 0
        
        # Button states
        self.buttons = {}
        self.hovered_button = None
        self.clicked_button = None
        self.button_click_time = 0
        
        # Mouse position
        self.mouse_x = 0
        self.mouse_y = 0
        
        # Hand detection
        self.hand_detector = None
        self.use_hand_detection = False
        
        # Try to initialize MediaPipe
        self.initialize_hand_detection()
    
    def download_hand_model(self):
        """Download the hand landmarker model if not present."""
        model_path = "hand_landmarker.task"
        if not os.path.exists(model_path):
            print("Downloading hand detection model...")
            try:
                url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
                urllib.request.urlretrieve(url, model_path)
                print("Model downloaded successfully!")
                return True
            except Exception as e:
                print(f"Failed to download model: {e}")
                return False
        return True
    
    def initialize_hand_detection(self):
        """Initialize MediaPipe hand detection."""
        try:
            import mediapipe as mp
            from mediapipe import tasks
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            # Download model if needed
            if not self.download_hand_model():
                print("Using keyboard fallback mode")
                return
            
            # Create hand landmarker
            base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=2,
                min_hand_detection_confidence=0.7,
                min_hand_presence_confidence=0.5
            )
            self.hand_detector = vision.HandLandmarker.create_from_options(options)
            self.use_hand_detection = True
            print("Hand detection initialized successfully!")
            
        except Exception as e:
            print(f"Hand detection initialization failed: {e}")
            print("Using keyboard fallback mode")
            self.use_hand_detection = False
    
    def detect_hands(self, frame):
        """Detect hands and count fingers."""
        if not self.use_hand_detection or not self.hand_detector:
            return None, []
        
        try:
            import mediapipe as mp
            
            # Convert frame to MediaPipe format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect hands
            results = self.hand_detector.detect(mp_image)
            
            if results.hand_landmarks and results.handedness:
                # Look for right hand
                for i, handedness in enumerate(results.handedness):
                    if handedness[0].category_name == "Right":
                        landmarks = results.hand_landmarks[i]
                        
                        # Count fingers
                        finger_count = self.count_fingers(landmarks)
                        
                        # Convert landmarks for drawing
                        h, w = frame.shape[:2]
                        landmark_points = []
                        for lm in landmarks:
                            x = int(lm.x * w)
                            y = int(lm.y * h)
                            landmark_points.append([x, y])
                        
                        return finger_count, landmark_points
            
        except Exception as e:
            print(f"Hand detection error: {e}")
        
        return None, []
    
    def count_fingers(self, landmarks):
        """Count raised fingers from landmarks."""
        if not landmarks or len(landmarks) < 21:
            return None
        
        # Finger tip and joint indices
        tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        pip_ids = [3, 6, 10, 14, 18]
        
        fingers_up = []
        
        # Thumb (special case)
        if landmarks[tip_ids[0]].x > landmarks[pip_ids[0]].x:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        # Other fingers
        for i in range(1, 5):
            if landmarks[tip_ids[i]].y < landmarks[pip_ids[i]].y:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        return sum(fingers_up)
    
    def draw_hand_landmarks(self, frame, landmarks):
        """Draw hand landmarks and connections."""
        if not landmarks:
            return
        
        # Draw fingertips
        fingertip_ids = [4, 8, 12, 16, 20]
        for tip_id in fingertip_ids:
            if tip_id < len(landmarks):
                x, y = landmarks[tip_id]
                cv2.circle(frame, (x, y), 8, COLOR_YELLOW, -1)
                cv2.circle(frame, (x, y), 10, COLOR_BLACK, 2)
        
        # Draw connections
        connections = [
            [0, 1], [1, 2], [2, 3], [3, 4],  # Thumb
            [0, 5], [5, 6], [6, 7], [7, 8],  # Index
            [0, 9], [9, 10], [10, 11], [11, 12],  # Middle
            [0, 13], [13, 14], [14, 15], [15, 16],  # Ring
            [0, 17], [17, 18], [18, 19], [19, 20],  # Pinky
            [5, 9], [9, 13], [13, 17]  # Palm
        ]
        
        for connection in connections:
            start_idx, end_idx = connection
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start_point = tuple(landmarks[start_idx])
                end_point = tuple(landmarks[end_idx])
                cv2.line(frame, start_point, end_point, COLOR_YELLOW, 2)
    
    def initialize_buttons(self, width, height):
        """Initialize operator buttons."""
        operators = ['+', '−', '×', '÷']
        button_start_y = (height - (len(operators) * BUTTON_HEIGHT + (len(operators) - 1) * BUTTON_MARGIN)) // 2
        button_x = width - BUTTON_WIDTH - BUTTON_MARGIN
        
        for i, op in enumerate(operators):
            button_y = button_start_y + i * (BUTTON_HEIGHT + BUTTON_MARGIN)
            self.buttons[op] = {
                'rect': (button_x, button_y, button_x + BUTTON_WIDTH, button_y + BUTTON_HEIGHT),
                'operator': op
            }
    
    def draw_buttons(self, frame):
        """Draw operator buttons."""
        for op, button_data in self.buttons.items():
            x1, y1, x2, y2 = button_data['rect']
            
            # Button color logic
            if self.clicked_button == op and time.time() - self.button_click_time < 0.3:
                button_color = COLOR_GREEN
                text_color = COLOR_BLACK
            elif self.hovered_button == op:
                button_color = COLOR_LIGHT_GREEN
                text_color = COLOR_BLACK
            elif self.state == STATE_OPERATOR:
                button_color = COLOR_BLUE
                text_color = COLOR_WHITE
            else:
                button_color = COLOR_GRAY
                text_color = COLOR_WHITE
            
            # Draw button
            cv2.rectangle(frame, (x1, y1), (x2, y2), button_color, -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_WHITE, 3)
            
            # Draw text
            text_size = cv2.getTextSize(op, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS)[0]
            text_x = x1 + (BUTTON_WIDTH - text_size[0]) // 2
            text_y = y1 + (BUTTON_HEIGHT + text_size[1]) // 2
            cv2.putText(frame, op, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, text_color, FONT_THICKNESS)
    
    def draw_equation_display(self, frame):
        """Draw equation at top."""
        height, width = frame.shape[:2]
        
        # Build equation
        parts = []
        parts.append(str(self.first_number) if self.first_number is not None else "?")
        parts.append(self.operator if self.operator is not None else "?")
        parts.append(str(self.second_number) if self.second_number is not None else "?")
        parts.append("=")
        parts.append(str(self.result) if self.result is not None else "?")
        
        equation_text = " ".join(parts)
        
        # Draw background
        cv2.rectangle(frame, (0, 0), (width, 100), COLOR_BLACK, -1)
        
        # Draw text
        text_size = cv2.getTextSize(equation_text, cv2.FONT_HERSHEY_SIMPLEX, LARGE_FONT_SCALE, LARGE_FONT_THICKNESS)[0]
        text_x = (width - text_size[0]) // 2
        text_y = 60
        
        cv2.putText(frame, equation_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, LARGE_FONT_SCALE, COLOR_WHITE, LARGE_FONT_THICKNESS)
    
    def draw_progress_bar(self, frame):
        """Draw confirmation progress bar."""
        if self.confirmation_progress <= 0:
            return
        
        height, width = frame.shape[:2]
        bar_width = 200
        bar_height = 15
        
        bar_x = (width - bar_width) // 2
        bar_y = 120
        
        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), COLOR_GRAY, -1)
        
        # Progress
        fill_width = int(self.confirmation_progress * bar_width)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), COLOR_GREEN, -1)
        
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), COLOR_WHITE, 2)
        
        # Percentage
        percentage = int(self.confirmation_progress * 100)
        percent_text = f"{percentage}%"
        text_size = cv2.getTextSize(percent_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        text_x = bar_x + (bar_width - text_size[0]) // 2
        text_y = bar_y + bar_height + 25
        cv2.putText(frame, percent_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_WHITE, 2)
    
    def draw_status_messages(self, frame):
        """Draw status and instructions."""
        height, width = frame.shape[:2]
        
        # Instructions
        if self.use_hand_detection:
            instructions = {
                STATE_FIRST_NUMBER: "Show 0-5 fingers on RIGHT hand, hold for 1 second",
                STATE_OPERATOR: "Click an operator button (+, −, ×, ÷)",
                STATE_SECOND_NUMBER: "Show 0-5 fingers on RIGHT hand, hold for 1 second",
                STATE_SHOW_RESULT: "Result displayed - auto-reset in progress"
            }
        else:
            instructions = {
                STATE_FIRST_NUMBER: "Press 0-5 keys for first number",
                STATE_OPERATOR: "Click an operator button (+, −, ×, ÷)",
                STATE_SECOND_NUMBER: "Press 0-5 keys for second number",
                STATE_SHOW_RESULT: "Result displayed - auto-reset in progress"
            }
        
        instruction = instructions.get(self.state, "")
        if instruction:
            text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            text_x = (width - text_size[0]) // 2
            cv2.putText(frame, instruction, (text_x, height - 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_WHITE, 2)
        
        # Error message
        if self.error_message:
            text_size = cv2.getTextSize(self.error_message, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS)[0]
            text_x = (width - text_size[0]) // 2
            cv2.putText(frame, self.error_message, (text_x, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, COLOR_RED, FONT_THICKNESS)
        
        # Detection status
        if self.use_hand_detection:
            if self.current_finger_count is not None:
                count_text = f"Detected: {self.current_finger_count} fingers"
                cv2.putText(frame, count_text, (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_YELLOW, 2)
            
            status_text = "Hand detection: ACTIVE"
            cv2.putText(frame, status_text, (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_GREEN, 2)
        else:
            status_text = "Hand detection: UNAVAILABLE (use keyboard 0-5)"
            cv2.putText(frame, status_text, (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_RED, 2)
        
        # Controls
        controls = "Q = quit | R = reset | 0-5 keys = numbers | Mouse = operators"
        text_size = cv2.getTextSize(controls, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(frame, controls, (text_x, height - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_GRAY, 1)
    
    def handle_mouse_event(self, event, x, y, flags, param):
        """Handle mouse events."""
        self.mouse_x = x
        self.mouse_y = y
        
        # Check hover
        self.hovered_button = None
        for op, button_data in self.buttons.items():
            x1, y1, x2, y2 = button_data['rect']
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.hovered_button = op
                break
        
        # Handle click
        if event == cv2.EVENT_LBUTTONDOWN and self.state == STATE_OPERATOR:
            for op, button_data in self.buttons.items():
                x1, y1, x2, y2 = button_data['rect']
                if x1 <= x <= x2 and y1 <= y <= y2:
                    self.operator = op
                    self.clicked_button = op
                    self.button_click_time = time.time()
                    self.state = STATE_SECOND_NUMBER
                    break
    
    def process_gesture_confirmation(self, finger_count):
        """Handle gesture confirmation."""
        current_time = time.time()
        
        if finger_count is not None:
            if self.current_finger_count == finger_count:
                elapsed = current_time - self.gesture_start_time
                self.confirmation_progress = min(elapsed / HOLD_TIME, 1.0)
                
                if elapsed >= HOLD_TIME:
                    self.current_finger_count = None
                    self.gesture_start_time = 0
                    self.confirmation_progress = 0.0
                    return True
            else:
                self.current_finger_count = finger_count
                self.gesture_start_time = current_time
                self.confirmation_progress = 0.0
        else:
            self.current_finger_count = None
            self.gesture_start_time = 0
            self.confirmation_progress = 0.0
        
        return False
    
    def calculate_result(self, num1, operator, num2):
        """Perform calculation."""
        try:
            if operator == "+":
                return num1 + num2, ""
            elif operator == "−":
                return num1 - num2, ""
            elif operator == "×":
                return num1 * num2, ""
            elif operator == "÷":
                if num2 == 0:
                    return None, "Error: Divide by zero"
                return round(num1 / num2, 2), ""
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def reset_calculator(self):
        """Reset calculator."""
        self.state = STATE_FIRST_NUMBER
        self.first_number = None
        self.operator = None
        self.second_number = None
        self.result = None
        self.error_message = ""
        self.current_finger_count = None
        self.gesture_start_time = 0
        self.confirmation_progress = 0.0
        self.result_start_time = 0
        self.error_start_time = 0
        self.clicked_button = None
    
    def run(self):
        """Main loop."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Cannot access webcam.")
                return
            
            cv2.namedWindow("Final Hand Gesture Calculator")
            cv2.setMouseCallback("Final Hand Gesture Calculator", self.handle_mouse_event)
            
            print("Final Hand Gesture Calculator Started!")
            if self.use_hand_detection:
                print("Hand detection is ACTIVE - show your RIGHT hand to the camera")
            else:
                print("Hand detection unavailable - use keyboard 0-5 for numbers")
            
            while True:
                success, frame = cap.read()
                if not success:
                    break
                
                frame = cv2.flip(frame, 1)
                height, width = frame.shape[:2]
                
                if not self.buttons:
                    self.initialize_buttons(width, height)
                
                # Detect hands
                finger_count, landmarks = self.detect_hands(frame)
                
                current_time = time.time()
                
                # Handle states
                if self.state == STATE_FIRST_NUMBER:
                    if self.use_hand_detection:
                        if self.process_gesture_confirmation(finger_count):
                            self.first_number = finger_count
                            self.state = STATE_OPERATOR
                elif self.state == STATE_SECOND_NUMBER:
                    if self.use_hand_detection:
                        if self.process_gesture_confirmation(finger_count):
                            self.second_number = finger_count
                            
                            # Calculate
                            self.result, self.error_message = self.calculate_result(
                                self.first_number, self.operator, self.second_number)
                            
                            if self.error_message:
                                self.error_start_time = current_time
                            
                            self.result_start_time = current_time
                            self.state = STATE_SHOW_RESULT
                elif self.state == STATE_SHOW_RESULT:
                    display_time = RESULT_DISPLAY_TIME if not self.error_message else ERROR_DISPLAY_TIME
                    if current_time - self.result_start_time > display_time:
                        self.reset_calculator()
                
                # Handle error timeout
                if self.error_message and current_time - self.error_start_time > ERROR_DISPLAY_TIME:
                    self.error_message = ""
                
                # Draw everything
                self.draw_equation_display(frame)
                if landmarks:
                    self.draw_hand_landmarks(frame, landmarks)
                self.draw_buttons(frame)
                self.draw_progress_bar(frame)
                self.draw_status_messages(frame)
                
                cv2.imshow("Final Hand Gesture Calculator", frame)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('r') or key == ord('R'):
                    self.reset_calculator()
                elif key in [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
                    number = int(chr(key))
                    
                    if self.state == STATE_FIRST_NUMBER:
                        self.first_number = number
                        self.state = STATE_OPERATOR
                    elif self.state == STATE_SECOND_NUMBER:
                        self.second_number = number
                        
                        self.result, self.error_message = self.calculate_result(
                            self.first_number, self.operator, self.second_number)
                        
                        if self.error_message:
                            self.error_start_time = current_time
                        
                        self.result_start_time = current_time
                        self.state = STATE_SHOW_RESULT
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            print("Calculator closed.")


if __name__ == "__main__":
    calculator = FinalGestureCalculator()
    calculator.run()