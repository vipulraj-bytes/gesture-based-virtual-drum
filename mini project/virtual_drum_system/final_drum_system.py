#!/usr/bin/env python3
"""
FINAL WORKING Virtual Drum System
Hand gesture controlled drums with Indian state styles
"""

import cv2
import pygame
import numpy as np
import time
import threading

class VirtualDrumSystem:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Initialize TTS (optional)
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
        self.gesture_cooldown = 0.5
        
        # Create drum sounds
        self.drum_sounds = self.create_drum_sounds()
        
        print("Virtual Drum System initialized!")
        self.speak("Virtual Drum System ready. Show hand gestures to play drums!")
    
    def create_drum_sounds(self):
        """Create drum sounds for all Indian styles"""
        sounds = {}
        styles = {
            "tamil_nadu": 150,    # Parai/Thavil
            "karnataka": 120,     # Chande/Dollu
            "kerala": 180,        # Chenda
            "punjab": 100         # Dhol
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
        
        # Add noise for realistic drum sound
        noise = np.random.normal(0, 0.1, len(wave))
        wave = np.clip(wave + noise * 0.2, -1, 1)
        
        # Convert to pygame sound
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo_wave)
    
    def speak(self, text):
        """Text to speech with fallback to print"""
        print(f"SYSTEM: {text}")
        if self.tts_available:
            def speak_async():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except:
                    pass
            threading.Thread(target=speak_async, daemon=True).start()
    
    def detect_hand_gesture(self, frame):
        """Detect hand gesture using skin color and contour analysis"""
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define skin color range (works for most skin tones)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create skin mask
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour (assumed to be the hand)
            hand_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(hand_contour)
            
            if area > 8000:  # Minimum hand size threshold
                # Draw hand outline for visual feedback
                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 2)
                
                # Classify the gesture
                return self.classify_gesture(hand_contour)
        
        return None
    
    def classify_gesture(self, contour):
        """Classify hand gesture based on contour properties"""
        # Calculate contour properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return None
        
        # Calculate compactness (how circular the shape is)
        compactness = (4 * np.pi * area) / (perimeter * perimeter)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Simple gesture classification based on area and shape
        if area > 20000 and compactness > 0.3:
            return "open_palm"  # Large, relatively circular = open palm
        elif area > 15000 and aspect_ratio > 1.2:
            return "two_fingers"  # Medium area, elongated = two fingers
        elif area > 10000 and compactness < 0.4:
            return "index_tap"  # Medium area, not circular = pointing finger
        elif area > 8000 and compactness > 0.5:
            return "fist"  # Smaller, compact = fist
        
        return None
    
    def play_drum_sound(self, sound_type):
        """Play drum sound for current style"""
        if sound_type in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][sound_type].play()
            style_name = self.current_style.replace('_', ' ').title()
            print(f"DRUM: {sound_type} - {style_name} style")
    
    def process_gesture(self, gesture):
        """Process detected gesture and play corresponding drum"""
        if not gesture or time.time() - self.last_gesture_time < self.gesture_cooldown:
            return
        
        # Map gestures to drum sounds
        gesture_map = {
            "index_tap": "drum_hit",      # Pointing finger = Basic drum
            "two_fingers": "cymbal",      # Two fingers = Cymbal
            "open_palm": "heavy_drum",    # Open hand = Heavy drum
            "fist": "bass_drum"           # Fist = Bass drum
        }
        
        if gesture in gesture_map:
            self.play_drum_sound(gesture_map[gesture])
            self.last_gesture_time = time.time()
    
    def change_style(self, style_num):
        """Change drum style (0=Tamil Nadu, 1=Karnataka, 2=Kerala, 3=Punjab)"""
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        style_names = ["Tamil Nadu", "Karnataka", "Kerala", "Punjab"]
        
        if 0 <= style_num < len(styles):
            self.current_style = styles[style_num]
            self.speak(f"{style_names[style_num]} drum style selected")
    
    def draw_interface(self, frame):
        """Draw user interface on the frame"""
        # Current style display
        style_name = self.current_style.replace('_', ' ').title()
        cv2.putText(frame, f"Style: {style_name}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Gesture instructions
        instructions = [
            "HAND GESTURES:",
            "Point finger = Basic drum",
            "Two fingers = Cymbal",
            "Open palm = Heavy drum", 
            "Fist = Bass drum",
            "",
            "KEYBOARD:",
            "1=Tamil Nadu  2=Karnataka",
            "3=Kerala      4=Punjab",
            "Q=Quit"
        ]
        
        # Draw instructions on the bottom left
        y_start = frame.shape[0] - 250
        for i, text in enumerate(instructions):
            color = (0, 255, 255) if "GESTURES:" in text or "KEYBOARD:" in text else (255, 255, 255)
            cv2.putText(frame, text, (10, y_start + i * 22), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("VIRTUAL DRUM SYSTEM - HAND GESTURE CONTROLS")
        print("="*60)
        print("HAND GESTURES:")
        print("  Point finger -> Basic drum hit")
        print("  Two fingers  -> Cymbal sound")
        print("  Open palm    -> Heavy drum")
        print("  Fist         -> Bass drum")
        print("\nKEYBOARD CONTROLS:")
        print("  1 = Tamil Nadu style (Parai/Thavil)")
        print("  2 = Karnataka style (Chande/Dollu)")
        print("  3 = Kerala style (Chenda)")
        print("  4 = Punjab style (Dhol)")
        print("  Q = Quit")
        print("="*60)
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot access camera!")
            return
        
        print("Camera ready! Show hand gestures to play drums...")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand gesture
                gesture = self.detect_hand_gesture(frame)
                
                # Display detected gesture
                if gesture:
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    self.process_gesture(gesture)
                
                # Draw user interface
                self.draw_interface(frame)
                
                # Show the frame
                cv2.imshow('Virtual Drum System', frame)
                
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
            print("Virtual Drum System stopped")

if __name__ == "__main__":
    system = VirtualDrumSystem()
    system.run()