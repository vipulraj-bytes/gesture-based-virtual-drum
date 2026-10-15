"""
Improved Gesture Detection Module
Uses skin color detection and finger counting for reliable hand gesture recognition
"""

import cv2
import numpy as np
import time

class GestureDetector:
    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # Increased cooldown for better control
        
    def process_frame(self, frame, style):
        """Process video frame and detect hand gestures"""
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Create hand mask using skin color detection
        hand_mask = self.create_hand_mask(frame)
        
        # Find hand contour
        contours, _ = cv2.findContours(hand_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour (hand)
            hand_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(hand_contour)
            
            if area > 8000:  # Minimum hand area
                # Draw hand contour
                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 2)
                
                # Detect gesture
                gesture = self.detect_gesture(hand_contour, frame)
                
                if gesture:
                    # Display gesture on screen
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Trigger drum sound with cooldown
                    if time.time() - self.last_gesture_time > self.gesture_cooldown:
                        self.trigger_drum_sound(gesture, style)
                        self.last_gesture_time = time.time()
        
        # Show instructions on frame
        self.draw_instructions(frame)
        return frame
    
    def create_hand_mask(self, frame):
        """Create mask for hand detection using skin color"""
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations to clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Apply Gaussian blur
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        return mask
    
    def detect_gesture(self, contour, frame):
        """Detect gesture based on hand contour analysis"""
        # Get convex hull and defects
        hull = cv2.convexHull(contour, returnPoints=False)
        
        if len(hull) > 3:
            defects = cv2.convexityDefects(contour, hull)
            
            if defects is not None:
                # Count fingers based on convexity defects
                finger_count = self.count_fingers(contour, defects)
                
                # Get hand area and perimeter for additional classification
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                # Classify gesture based on finger count and hand properties
                return self.classify_gesture(finger_count, area, perimeter)
        
        return None
    
    def count_fingers(self, contour, defects):
        """Count extended fingers using convexity defects"""
        count = 0
        
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])
            
            # Calculate angle between fingers
            a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            
            # Calculate angle using cosine rule
            angle = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
            
            # If angle is less than 90 degrees, count as finger
            if angle <= np.pi / 2:
                count += 1
        
        return count + 1  # Add 1 for thumb
    
    def classify_gesture(self, finger_count, area, perimeter):
        """Classify gesture based on finger count and hand properties"""
        # Calculate compactness
        if perimeter > 0:
            compactness = (4 * np.pi * area) / (perimeter * perimeter)
        else:
            compactness = 0
        
        # Gesture classification logic
        if finger_count == 1:
            return "index_tap"  # One finger pointing
        elif finger_count == 2:
            return "two_fingers"  # Peace sign or two fingers
        elif finger_count >= 4 and compactness > 0.3:
            return "open_palm"  # Open hand
        elif finger_count == 0 or (area > 10000 and compactness > 0.5):
            return "fist"  # Closed fist
        
        return None
    
    def trigger_drum_sound(self, gesture, style):
        """Trigger drum sound based on gesture"""
        sound_map = {
            "index_tap": "drum_hit",      # Basic drum sound
            "two_fingers": "cymbal",      # Cymbal sound
            "open_palm": "heavy_drum",    # Heavy drum sound
            "fist": "bass_drum"           # Bass drum sound
        }
        
        if gesture in sound_map:
            print(f"🥁 Playing {sound_map[gesture]} with {gesture} gesture ({style} style)")
            self.audio_engine.play_drum_sound(sound_map[gesture], style)
    
    def draw_instructions(self, frame):
        """Draw gesture instructions on frame"""
        instructions = [
            "Hand Gestures:",
            "1 finger = Basic drum",
            "2 fingers = Cymbal", 
            "Open palm = Heavy drum",
            "Fist = Bass drum"
        ]
        
        y_offset = frame.shape[0] - 150
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)