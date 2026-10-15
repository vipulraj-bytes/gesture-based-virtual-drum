#!/usr/bin/env python3
"""
Working Virtual Drum System - Simplified Version
Uses OpenCV for hand detection and keyboard for voice commands
"""

import cv2
import pygame
import pyttsx3
import numpy as np
import time
import threading
import json
import os
from datetime import datetime

class WorkingDrumSystem:
    def __init__(self):
        # Initialize pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
            self.tts_available = True
        except:
            self.tts_available = False
            print("TTS not available, using text output only")
        
        # Current state
        self.current_style = "tamil_nadu"
        self.is_recording = False
        self.running = True
        
        # Create directories
        os.makedirs("recordings", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        # Create drum sounds
        self.drum_sounds = self.create_drum_sounds()
        
        # Gesture detection
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5
        
        print("Virtual Drum System initialized!")
        self.speak("Virtual Drum System ready")
    
    def create_drum_sounds(self):
        """Create drum sounds for all styles"""
        sounds = {}
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        
        for style in styles:
            sounds[style] = {}
            base_freq = {"tamil_nadu": 150, "karnataka": 120, "kerala": 180, "punjab": 100}[style]
            
            sounds[style]["drum_hit"] = self.generate_sound(base_freq, 0.3)
            sounds[style]["cymbal"] = self.generate_sound(base_freq * 4, 0.2)
            sounds[style]["heavy_drum"] = self.generate_sound(base_freq * 0.7, 0.5)
            sounds[style]["bass_drum"] = self.generate_sound(base_freq * 0.5, 0.4)
        
        return sounds
    
    def generate_sound(self, frequency, duration):
        """Generate drum sound"""
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 8)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t) * np.exp(-t * 10)
        noise = np.random.normal(0, 0.1, len(wave))
        wave = np.clip(wave + noise * 0.2, -1, 1)
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
    
    def detect_hand_gesture(self, frame):
        """Simple hand gesture detection"""
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define skin color range
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask for skin color
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area > 3000:  # Minimum hand area
                # Draw contour
                cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                
                # Simple gesture classification based on area
                if area > 12000:
                    return "open_palm"
                elif area > 8000:
                    return "two_fingers"
                elif area > 5000:
                    return "index_tap"
                else:
                    return "fist"
        
        return None
    
    def play_drum(self, sound_type):
        """Play drum sound"""
        if sound_type in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][sound_type].play()
            print(f"Playing {sound_type} ({self.current_style})")
    
    def process_gesture(self, gesture):
        """Process detected gesture"""
        if not gesture or time.time() - self.last_gesture_time < self.gesture_cooldown:
            return
        
        sound_map = {
            "index_tap": "drum_hit",
            "two_fingers": "cymbal", 
            "open_palm": "heavy_drum",
            "fist": "bass_drum"
        }
        
        if gesture in sound_map:
            self.play_drum(sound_map[gesture])
            self.last_gesture_time = time.time()
    
    def change_style(self, style_key):
        """Change drum style"""
        styles = {"1": "tamil_nadu", "2": "karnataka", "3": "kerala", "4": "punjab"}
        if style_key in styles:
            self.current_style = styles[style_key]
            style_name = self.current_style.replace('_', ' ').title()
            self.speak(f"{style_name} style selected")
    
    def show_instructions(self):
        """Show instructions"""
        print("\n" + "="*50)
        print("VIRTUAL DRUM SYSTEM - CONTROLS")
        print("="*50)
        print("HAND GESTURES (show to camera):")
        print("  Point finger -> Basic drum")
        print("  Two fingers -> Cymbal")
        print("  Open palm -> Heavy drum") 
        print("  Fist -> Bass drum")
        print("\nKEYBOARD COMMANDS:")
        print("  1-4: Change drum style")
        print("  R: Start/Stop recording")
        print("  H: Show help")
        print("  Q: Quit")
        print("="*50)
    
    def run(self):
        """Main application loop"""
        self.show_instructions()
        
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot open camera!")
            return
        
        print("\nStarting Virtual Drum System...")
        print("Show hand gestures to camera or press keys for commands")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect hand gesture
                gesture = self.detect_hand_gesture(frame)
                if gesture:
                    self.process_gesture(gesture)
                    # Show gesture on screen
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show current style
                cv2.putText(frame, f"Style: {self.current_style}", (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                # Show frame
                cv2.imshow('Virtual Drum System', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('h'):
                    self.show_instructions()
                elif key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                    self.change_style(chr(key))
                elif key == ord('r'):
                    self.is_recording = not self.is_recording
                    status = "started" if self.is_recording else "stopped"
                    self.speak(f"Recording {status}")
                    
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.speak("Goodbye")
            print("System stopped")

if __name__ == "__main__":
    system = WorkingDrumSystem()
    system.run()