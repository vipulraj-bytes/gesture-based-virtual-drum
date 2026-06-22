#!/usr/bin/env python3
"""
Finger-Counting Virtual Drum System
1 finger = Drum 1, 2 fingers = Drum 2, ..., 5 fingers = Drum 5
"""

import cv2
import pygame
import numpy as np
import time
import threading

class FingerCountDrumSystem:
    def __init__(self):
        # Initialize pygame
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Initialize TTS
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_available = True
        except:
            self.tts_available = False
        
        # System state
        self.current_style = "tamil_nadu"
        self.running = True
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.4
        
        # Create 5 different drum sounds
        self.drum_sounds = self.create_finger_drum_sounds()
        
        print("Finger-Count Drum System initialized!")
        self.speak("Show 1 to 5 fingers to play different drums!")
    
    def create_finger_drum_sounds(self):
        """Create 5 different drum sounds for each finger count"""
        sounds = {}
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        
        for style in styles:
            sounds[style] = {}
            base_freq = {"tamil_nadu": 150, "karnataka": 120, "kerala": 180, "punjab": 100}[style]
            
            # Create 5 different drums with varying frequencies
            sounds[style]["1_finger"] = self.generate_drum_sound(base_freq, 0.3, [1, 0.5])
            sounds[style]["2_fingers"] = self.generate_drum_sound(base_freq * 1.5, 0.25, [1, 0.3, 0.1])
            sounds[style]["3_fingers"] = self.generate_drum_sound(base_freq * 2, 0.2, [1, 0.4])
            sounds[style]["4_fingers"] = self.generate_drum_sound(base_freq * 0.7, 0.4, [1, 0.6, 0.3])
            sounds[style]["5_fingers"] = self.generate_drum_sound(base_freq * 0.5, 0.5, [1, 0.8, 0.4, 0.2])
        
        return sounds
    
    def generate_drum_sound(self, frequency, duration, harmonics):
        """Generate drum sound with harmonics"""
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create wave with harmonics
        wave = np.zeros_like(t)
        for i, amp in enumerate(harmonics):
            wave += amp * np.sin(2 * np.pi * frequency * (i + 1) * t) * np.exp(-t * 8)
        
        # Add noise for realism
        noise = np.random.normal(0, 0.1, len(wave))
        wave = np.clip(wave + noise * 0.1, -1, 1)
        
        # Convert to pygame sound
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo_wave)
    
    def speak(self, text):
        """Text to speech"""
        print(f"SYSTEM: {text}")
        if self.tts_available:
            def speak_async():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except:
                    pass
            threading.Thread(target=speak_async, daemon=True).start()
    
    def count_fingers(self, frame):
        """Count extended fingers using contour analysis"""
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Skin color detection
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Clean mask
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
                # Draw hand contour
                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 2)
                
                # Get convex hull and defects for finger counting
                hull = cv2.convexHull(hand_contour, returnPoints=False)
                
                if len(hull) > 3:
                    defects = cv2.convexityDefects(hand_contour, hull)
                    
                    if defects is not None:
                        finger_count = self.analyze_defects(hand_contour, defects, frame)
                        return finger_count
        
        return 0
    
    def analyze_defects(self, contour, defects, frame):
        """Analyze convexity defects to count fingers"""
        finger_count = 0
        
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])
            
            # Calculate distances
            a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            
            # Calculate angle using cosine rule
            if b != 0 and c != 0:
                angle = np.arccos(min(1.0, (b**2 + c**2 - a**2) / (2 * b * c)))
                
                # If angle is less than 90 degrees and defect is deep enough, count as finger
                if angle <= np.pi / 2 and d > 10000:
                    finger_count += 1
                    # Draw finger detection points
                    cv2.circle(frame, far, 5, (0, 0, 255), -1)
        
        # Add 1 for thumb (usually not detected in defects)
        return min(finger_count + 1, 5)
    
    def play_finger_drum(self, finger_count):
        """Play drum based on finger count"""
        if finger_count == 0:
            return
        
        drum_key = f"{finger_count}_finger{'s' if finger_count > 1 else ''}"
        
        if drum_key in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][drum_key].play()
            
            # Get drum names
            drum_names = {
                "1_finger": "Tabla",
                "2_fingers": "Dholak", 
                "3_fingers": "Mridangam",
                "4_fingers": "Chenda",
                "5_fingers": "Dhol"
            }
            
            drum_name = drum_names.get(drum_key, "Drum")
            style_name = self.current_style.replace('_', ' ').title()
            print(f"PLAYING: {drum_name} ({finger_count} finger{'s' if finger_count > 1 else ''}) - {style_name} style")
    
    def process_finger_count(self, finger_count):
        """Process finger count and play drum"""
        if finger_count > 0 and time.time() - self.last_gesture_time > self.gesture_cooldown:
            self.play_finger_drum(finger_count)
            self.last_gesture_time = time.time()
    
    def change_style(self, style_num):
        """Change drum style"""
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        style_names = ["Tamil Nadu", "Karnataka", "Kerala", "Punjab"]
        
        if 0 <= style_num < len(styles):
            self.current_style = styles[style_num]
            self.speak(f"{style_names[style_num]} style selected")
    
    def draw_interface(self, frame, finger_count):
        """Draw user interface"""
        # Current style
        style_name = self.current_style.replace('_', ' ').title()
        cv2.putText(frame, f"Style: {style_name}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Finger count display
        if finger_count > 0:
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Instructions
        instructions = [
            "FINGER COUNT DRUMS:",
            "1 finger = Tabla",
            "2 fingers = Dholak",
            "3 fingers = Mridangam",
            "4 fingers = Chenda", 
            "5 fingers = Dhol",
            "",
            "Keys: 1-4 = Change style, Q = Quit"
        ]
        
        y_start = frame.shape[0] - 220
        for i, text in enumerate(instructions):
            color = (0, 255, 255) if "DRUMS:" in text else (255, 255, 255)
            cv2.putText(frame, text, (10, y_start + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("FINGER-COUNT VIRTUAL DRUM SYSTEM")
        print("="*60)
        print("FINGER GESTURES:")
        print("  1 finger  -> Tabla (light drum)")
        print("  2 fingers -> Dholak (medium drum)")
        print("  3 fingers -> Mridangam (classical drum)")
        print("  4 fingers -> Chenda (heavy drum)")
        print("  5 fingers -> Dhol (bass drum)")
        print("\nKEYBOARD:")
        print("  1 = Tamil Nadu    2 = Karnataka")
        print("  3 = Kerala        4 = Punjab")
        print("  Q = Quit")
        print("="*60)
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot access camera!")
            return
        
        print("Camera ready! Show 1-5 fingers to play different drums...")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Count fingers and process
                finger_count = self.count_fingers(frame)
                self.process_finger_count(finger_count)
                
                # Draw interface
                self.draw_interface(frame, finger_count)
                
                # Show frame
                cv2.imshow('Finger-Count Drum System', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                    self.change_style(int(chr(key)) - 1)
                    
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.speak("Goodbye!")
            print("Finger-Count Drum System stopped")

if __name__ == "__main__":
    system = FingerCountDrumSystem()
    system.run()