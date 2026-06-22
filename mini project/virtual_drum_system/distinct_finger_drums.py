#!/usr/bin/env python3
"""
Fixed Finger-Count Drum System
Each finger count (1-5) plays a distinctly different drum sound
"""

import cv2
import pygame
import numpy as np
import time

class FingerDrumSystem:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.current_style = "tamil_nadu"
        self.running = True
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.6
        
        # Create 5 distinctly different drum sounds
        self.drum_sounds = self.create_distinct_drums()
        
        print("Finger-Count Drum System with Distinct Sounds!")
    
    def create_distinct_drums(self):
        """Create 5 completely different drum sounds"""
        sounds = {}
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        
        for style in styles:
            sounds[style] = {}
            
            # Create 5 very different drum sounds
            sounds[style]["1_finger"] = self.generate_tabla_sound()      # High pitch, short
            sounds[style]["2_fingers"] = self.generate_dholak_sound()    # Medium pitch, medium
            sounds[style]["3_fingers"] = self.generate_mridangam_sound() # Complex harmonics
            sounds[style]["4_fingers"] = self.generate_chenda_sound()    # Heavy, deep
            sounds[style]["5_fingers"] = self.generate_dhol_sound()      # Very deep bass
        
        return sounds
    
    def generate_tabla_sound(self):
        """Generate high-pitched tabla sound"""
        sample_rate = 44100
        duration = 0.2
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # High frequency with sharp attack
        frequency = 400
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 15)
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t) * np.exp(-t * 20)
        
        # Sharp attack envelope
        attack = np.exp(-t * 50)
        wave = wave * attack
        
        return self.convert_to_sound(wave)
    
    def generate_dholak_sound(self):
        """Generate medium-pitched dholak sound"""
        sample_rate = 44100
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Medium frequency
        frequency = 250
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 8)
        wave += 0.5 * np.sin(2 * np.pi * frequency * 1.5 * t) * np.exp(-t * 10)
        
        # Add some noise for texture
        noise = np.random.normal(0, 0.1, len(wave))
        wave = wave + noise * 0.3
        
        return self.convert_to_sound(wave)
    
    def generate_mridangam_sound(self):
        """Generate complex mridangam sound"""
        sample_rate = 44100
        duration = 0.4
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Complex harmonics
        frequency = 180
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 6)
        wave += 0.6 * np.sin(2 * np.pi * frequency * 1.3 * t) * np.exp(-t * 8)
        wave += 0.4 * np.sin(2 * np.pi * frequency * 2.1 * t) * np.exp(-t * 12)
        wave += 0.2 * np.sin(2 * np.pi * frequency * 3.2 * t) * np.exp(-t * 15)
        
        return self.convert_to_sound(wave)
    
    def generate_chenda_sound(self):
        """Generate heavy chenda sound"""
        sample_rate = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Lower frequency, longer sustain
        frequency = 120
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 4)
        wave += 0.8 * np.sin(2 * np.pi * frequency * 0.7 * t) * np.exp(-t * 5)
        
        # Add heavy noise
        noise = np.random.normal(0, 0.15, len(wave))
        wave = wave + noise * 0.4
        
        return self.convert_to_sound(wave)
    
    def generate_dhol_sound(self):
        """Generate deep bass dhol sound"""
        sample_rate = 44100
        duration = 0.6
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Very low frequency, long sustain
        frequency = 60
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 3)
        wave += 0.9 * np.sin(2 * np.pi * frequency * 0.5 * t) * np.exp(-t * 4)
        wave += 0.7 * np.sin(2 * np.pi * frequency * 1.5 * t) * np.exp(-t * 6)
        
        # Heavy bass noise
        noise = np.random.normal(0, 0.2, len(wave))
        wave = wave + noise * 0.5
        
        return self.convert_to_sound(wave)
    
    def convert_to_sound(self, wave):
        """Convert wave to pygame sound"""
        wave = np.clip(wave, -1, 1)
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo_wave)
    
    def count_fingers_simple(self, frame):
        """Simple finger counting based on contour area"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Skin detection
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Clean mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            hand_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(hand_contour)
            
            if area > 8000:
                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 2)
                
                # Simple area-based finger counting
                if area > 35000:
                    return 5  # Open hand
                elif area > 28000:
                    return 4  # Four fingers
                elif area > 20000:
                    return 3  # Three fingers
                elif area > 15000:
                    return 2  # Two fingers
                elif area > 8000:
                    return 1  # One finger
        
        return 0
    
    def play_finger_drum(self, finger_count):
        """Play drum based on finger count"""
        if finger_count == 0:
            return
        
        drum_key = f"{finger_count}_finger{'s' if finger_count > 1 else ''}"
        
        if drum_key in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][drum_key].play()
            
            # Different drum names for each finger count
            drum_names = {
                1: "Tabla (High)",
                2: "Dholak (Medium)", 
                3: "Mridangam (Complex)",
                4: "Chenda (Heavy)",
                5: "Dhol (Bass)"
            }
            
            print(f"PLAYING: {drum_names[finger_count]} - {finger_count} finger{'s' if finger_count > 1 else ''}")
    
    def process_finger_count(self, finger_count):
        """Process finger count with cooldown"""
        if finger_count > 0 and time.time() - self.last_gesture_time > self.gesture_cooldown:
            self.play_finger_drum(finger_count)
            self.last_gesture_time = time.time()
    
    def change_style(self, style_num):
        """Change drum style"""
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        style_names = ["Tamil Nadu", "Karnataka", "Kerala", "Punjab"]
        
        if 0 <= style_num < len(styles):
            self.current_style = styles[style_num]
            print(f"Style changed to: {style_names[style_num]}")
    
    def draw_interface(self, frame, finger_count):
        """Draw interface"""
        style_name = self.current_style.replace('_', ' ').title()
        cv2.putText(frame, f"Style: {style_name}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        if finger_count > 0:
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Instructions
        instructions = [
            "FINGER DRUMS (DISTINCT SOUNDS):",
            "1 finger = Tabla (High pitch)",
            "2 fingers = Dholak (Medium)",
            "3 fingers = Mridangam (Complex)",
            "4 fingers = Chenda (Heavy)", 
            "5 fingers = Dhol (Deep bass)",
            "",
            "Keys: 1-4 = Style, Q = Quit"
        ]
        
        y_start = frame.shape[0] - 220
        for i, text in enumerate(instructions):
            color = (0, 255, 255) if "DISTINCT" in text else (255, 255, 255)
            cv2.putText(frame, text, (10, y_start + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    def run(self):
        """Main loop"""
        print("\n" + "="*60)
        print("FINGER-COUNT DRUM SYSTEM - DISTINCT SOUNDS")
        print("="*60)
        print("FINGER GESTURES (Each has DIFFERENT sound):")
        print("  1 finger  -> Tabla (High pitch, sharp)")
        print("  2 fingers -> Dholak (Medium pitch)")
        print("  3 fingers -> Mridangam (Complex harmonics)")
        print("  4 fingers -> Chenda (Heavy, deep)")
        print("  5 fingers -> Dhol (Very deep bass)")
        print("\nKEYBOARD: 1-4 = Change style, Q = Quit")
        print("="*60)
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot access camera!")
            return
        
        print("Camera ready! Show 1-5 fingers for DIFFERENT drum sounds...")
        
        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame = cv2.flip(frame, 1)
                
                # Count fingers and play drums
                finger_count = self.count_fingers_simple(frame)
                self.process_finger_count(finger_count)
                
                # Draw interface
                self.draw_interface(frame, finger_count)
                
                cv2.imshow('Finger-Count Drums - Distinct Sounds', frame)
                
                # Handle keys
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
            print("System stopped")

if __name__ == "__main__":
    system = FingerDrumSystem()
    system.run()