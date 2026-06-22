#!/usr/bin/env python3
"""
Complete Working Virtual Drum System
With improved hand gesture detection for reliable drum playing
"""

import cv2
import pygame
import pyttsx3
import numpy as np
import time
import threading
import os

class VirtualDrumSystem:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_available = True
        except:
            self.tts_available = False
        
        # System state
        self.current_style = "tamil_nadu"
        self.running = True
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5
        
        # Create drum sounds
        self.drum_sounds = self.create_drum_sounds()
        
        print("Virtual Drum System initialized!")
        self.speak("Virtual Drum System ready. Show hand gestures to play drums!")
    
    def create_drum_sounds(self):
        """Create synthetic drum sounds for all Indian styles"""
        sounds = {}
        styles = {
            "tamil_nadu": 150,    # Parai/Thavil frequency
            "karnataka": 120,     # Chande/Dollu frequency
            "kerala": 180,        # Chenda frequency
            "punjab": 100         # Dhol frequency
        }
        
        for style, base_freq in styles.items():
            sounds[style] = {
                "drum_hit": self.generate_drum_sound(base_freq, 0.3),
                "cymbal": self.generate_drum_sound(base_freq * 4, 0.2),
                "heavy_drum": self.generate_drum_sound(base_freq * 0.7, 0.5),
                "bass_drum": self.generate_drum_sound(base_freq * 0.5, 0.4)
            }
        
        return sounds
    
    def generate_drum_sound(self, frequency, duration):
        """Generate realistic drum sound"""
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create drum sound with harmonics and decay
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 8)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t) * np.exp(-t * 10)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t) * np.exp(-t * 12)
        
        # Add noise for realistic drum sound
        noise = np.random.normal(0, 0.1, len(wave))
        wave = np.clip(wave + noise * 0.2, -1, 1)
        
        # Convert to pygame sound
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo_wave)
    
    def speak(self, text):
        """Text to speech with fallback to print"""
        print(f"🔊 {text}")
        if self.tts_available:
            def speak_async():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except:
                    pass
            threading.Thread(target=speak_async, daemon=True).start()
    
    def detect_hand_gesture(self, frame):
        """Improved hand gesture detection"""
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Skin color range (adjust for different skin tones)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create skin mask
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour (hand)
            hand_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(hand_contour)
            
            if area > 8000:  # Minimum hand size
                # Draw hand outline
                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 2)
                
                # Classify gesture based on hand properties
                return self.classify_hand_gesture(hand_contour)
        
        return None
    
    def classify_hand_gesture(self, contour):
        """Classify hand gesture using contour analysis"""
        # Get contour properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return None
        
        # Calculate shape properties
        compactness = (4 * np.pi * area) / (perimeter * perimeter)
        
        # Get convex hull for finger detection
        hull = cv2.convexHull(contour, returnPoints=False)
        
        if len(hull) > 3:
            defects = cv2.convexityDefects(contour, hull)
            finger_count = 0
            
            if defects is not None:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(contour[s][0])
                    end = tuple(contour[e][0])
                    far = tuple(contour[f][0])
                    
                    # Calculate angle between fingers
                    a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                    b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                    c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                    
                    if b != 0 and c != 0:
                        angle = np.arccos(min(1.0, (b**2 + c**2 - a**2) / (2 * b * c)))
                        
                        # Count as finger if angle is acute
                        if angle <= np.pi / 2:
                            finger_count += 1
            
            # Gesture classification
            if finger_count == 0 and compactness > 0.4:
                return "fist"
            elif finger_count == 1:
                return "index_tap"
            elif finger_count == 2:
                return "two_fingers"
            elif finger_count >= 3 and area > 15000:
                return "open_palm"
        
        return None
    
    def play_drum_sound(self, sound_type):
        """Play drum sound for current style"""
        if sound_type in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][sound_type].play()
            style_name = self.current_style.replace('_', ' ').title()
            print(f"🥁 {sound_type} - {style_name} style")
    
    def process_gesture(self, gesture):
        """Process detected gesture and play corresponding drum"""
        if not gesture or time.time() - self.last_gesture_time < self.gesture_cooldown:
            return
        
        # Map gestures to drum sounds
        gesture_map = {
            "index_tap": "drum_hit",      # Point finger = Basic drum
            "two_fingers": "cymbal",      # Two fingers = Cymbal
            "open_palm": "heavy_drum",    # Open hand = Heavy drum
            "fist": "bass_drum"           # Fist = Bass drum
        }
        
        if gesture in gesture_map:
            self.play_drum_sound(gesture_map[gesture])
            self.last_gesture_time = time.time()
    
    def change_style(self, style_num):
        """Change drum style"""
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        if 0 <= style_num < len(styles):
            self.current_style = styles[style_num]
            style_name = self.current_style.replace('_', ' ').title()
            self.speak(f"{style_name} drum style selected")
    
    def draw_ui(self, frame):
        """Draw user interface on frame"""
        # Current style
        style_name = self.current_style.replace('_', ' ').title()
        cv2.putText(frame, f"Style: {style_name}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Instructions
        instructions = [
            "Hand Gestures:",
            "Point finger = Basic drum",
            "Two fingers = Cymbal",
            "Open palm = Heavy drum", 
            "Fist = Bass drum",
            "",
            "Keys: 1-4 = Change style, Q = Quit"
        ]
        
        y_start = frame.shape[0] - 200
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_start + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("🥁 VIRTUAL DRUM SYSTEM - HAND GESTURE CONTROLS")
        print("="*60)
        print("GESTURES:")
        print("  👆 Point finger → Basic drum hit")
        print("  ✌️  Two fingers → Cymbal sound")
        print("  🖐️  Open palm → Heavy drum")
        print("  ✊ Fist → Bass drum")
        print("\nKEYBOARD:")
        print("  1 = Tamil Nadu style    2 = Karnataka style")
        print("  3 = Kerala style        4 = Punjab style")
        print("  Q = Quit")
        print("="*60)
        
        # Open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ ERROR: Cannot access camera!")
            return
        
        print("✅ Camera ready! Show hand gestures to play drums...")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect and process gesture
                gesture = self.detect_hand_gesture(frame)
                if gesture:
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    self.process_gesture(gesture)
                
                # Draw UI
                self.draw_ui(frame)
                
                # Show frame
                cv2.imshow('Virtual Drum System', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                    self.change_style(int(chr(key)) - 1)
                    
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.speak("Goodbye!")
            print("👋 Virtual Drum System stopped")

if __name__ == "__main__":
    system = VirtualDrumSystem()
    system.run()