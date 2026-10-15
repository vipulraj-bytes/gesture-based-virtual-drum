#!/usr/bin/env python3
"""
Enhanced Virtual Drum System with More Indian Music
Includes traditional instruments from multiple Indian states with rich musical variety
"""

import cv2
import pygame
import numpy as np
import time
import threading

class EnhancedVirtualDrumSystem:
    def __init__(self):
        # Initialize pygame mixer with higher quality
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        
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
        self.gesture_cooldown = 0.4
        
        # Create enhanced drum sounds with more instruments
        self.drum_sounds = self.create_enhanced_drum_sounds()
        
        print("Enhanced Virtual Drum System with Rich Indian Music initialized!")
        self.speak("Enhanced Virtual Drum System ready with traditional Indian instruments!")
    
    def create_enhanced_drum_sounds(self):
        """Create rich drum sounds for all Indian styles with multiple instruments"""
        sounds = {}
        
        # Enhanced instrument configurations for each state
        instrument_configs = {
            "tamil_nadu": {
                "base_freq": 150,
                "instruments": {
                    "parai": {"freq": 150, "decay": 6, "harmonics": [1, 0.5, 0.3, 0.2]},
                    "thavil": {"freq": 200, "decay": 8, "harmonics": [1, 0.7, 0.4, 0.2]},
                    "kanjira": {"freq": 300, "decay": 4, "harmonics": [1, 0.3, 0.1]},
                    "ghatam": {"freq": 120, "decay": 10, "harmonics": [1, 0.6, 0.3]}
                }
            },
            "karnataka": {
                "base_freq": 120,
                "instruments": {
                    "chande": {"freq": 120, "decay": 7, "harmonics": [1, 0.6, 0.4, 0.2]},
                    "dollu": {"freq": 80, "decay": 12, "harmonics": [1, 0.8, 0.5, 0.3]},
                    "tabla": {"freq": 180, "decay": 5, "harmonics": [1, 0.4, 0.2]},
                    "mridangam": {"freq": 140, "decay": 9, "harmonics": [1, 0.7, 0.4, 0.2]}
                }
            },
            "kerala": {
                "base_freq": 180,
                "instruments": {
                    "chenda": {"freq": 180, "decay": 6, "harmonics": [1, 0.5, 0.3]},
                    "timila": {"freq": 160, "decay": 8, "harmonics": [1, 0.6, 0.4, 0.2]},
                    "edakka": {"freq": 200, "decay": 5, "harmonics": [1, 0.4, 0.2]},
                    "mizhavu": {"freq": 100, "decay": 15, "harmonics": [1, 0.8, 0.6, 0.4]}
                }
            },
            "punjab": {
                "base_freq": 100,
                "instruments": {
                    "dhol": {"freq": 100, "decay": 10, "harmonics": [1, 0.7, 0.5, 0.3]},
                    "tabla": {"freq": 150, "decay": 6, "harmonics": [1, 0.5, 0.3]},
                    "dholak": {"freq": 120, "decay": 8, "harmonics": [1, 0.6, 0.4]},
                    "nagara": {"freq": 80, "decay": 12, "harmonics": [1, 0.8, 0.6]}
                }
            },
            "rajasthan": {
                "base_freq": 130,
                "instruments": {
                    "dhol": {"freq": 130, "decay": 9, "harmonics": [1, 0.6, 0.4]},
                    "nagada": {"freq": 90, "decay": 11, "harmonics": [1, 0.7, 0.5, 0.3]},
                    "manjeera": {"freq": 400, "decay": 3, "harmonics": [1, 0.3, 0.1]},
                    "khartal": {"freq": 350, "decay": 2, "harmonics": [1, 0.2]}
                }
            },
            "bengal": {
                "base_freq": 140,
                "instruments": {
                    "dhak": {"freq": 140, "decay": 7, "harmonics": [1, 0.5, 0.3]},
                    "tabla": {"freq": 170, "decay": 6, "harmonics": [1, 0.4, 0.2]},
                    "khol": {"freq": 160, "decay": 8, "harmonics": [1, 0.6, 0.4]},
                    "kartal": {"freq": 380, "decay": 2, "harmonics": [1, 0.2]}
                }
            }
        }
        
        for state, config in instrument_configs.items():
            sounds[state] = {}
            instruments = list(config["instruments"].keys())
            
            # Map gestures to different instruments
            sounds[state]["drum_hit"] = self.generate_instrument_sound(
                config["instruments"][instruments[0]], 0.4)  # Primary drum
            sounds[state]["cymbal"] = self.generate_instrument_sound(
                config["instruments"][instruments[-1]], 0.3)  # Metallic instrument
            sounds[state]["heavy_drum"] = self.generate_instrument_sound(
                config["instruments"][instruments[1] if len(instruments) > 1 else instruments[0]], 0.6)  # Secondary drum
            sounds[state]["bass_drum"] = self.generate_instrument_sound(
                config["instruments"][instruments[-2] if len(instruments) > 2 else instruments[0]], 0.5)  # Bass instrument
        
        return sounds
    
    def generate_instrument_sound(self, instrument_config, duration):
        """Generate realistic instrument sound with harmonics"""
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        frequency = instrument_config["freq"]
        decay_rate = instrument_config["decay"]
        harmonics = instrument_config["harmonics"]
        
        # Create base wave with harmonics
        wave = np.zeros_like(t)
        for i, amplitude in enumerate(harmonics):
            harmonic_freq = frequency * (i + 1)
            wave += amplitude * np.sin(2 * np.pi * harmonic_freq * t) * np.exp(-t * decay_rate)
        
        # Add attack envelope for realistic drum sound
        attack_time = 0.01  # 10ms attack
        attack_samples = int(attack_time * sample_rate)
        if len(wave) > attack_samples:
            attack_envelope = np.linspace(0, 1, attack_samples)
            wave[:attack_samples] *= attack_envelope
        
        # Add subtle noise for realism
        noise = np.random.normal(0, 0.05, len(wave))
        wave = wave + noise * 0.1
        
        # Add slight pitch bend for natural sound
        pitch_bend = 1 + 0.1 * np.exp(-t * 20)
        wave = wave * pitch_bend
        
        # Normalize and convert to pygame sound
        wave = np.clip(wave, -1, 1)
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
        """Enhanced hand gesture detection"""
        # Convert to HSV for better skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Enhanced skin color range for better detection
        lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)
        lower_skin2 = np.array([170, 20, 70], dtype=np.uint8)
        upper_skin2 = np.array([180, 255, 255], dtype=np.uint8)
        
        # Create skin masks
        mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
        mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Enhanced mask cleaning
        kernel = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, (7, 7), 0)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour (hand)
            hand_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(hand_contour)
            
            if area > 6000:  # Adjusted threshold
                # Enhanced visual feedback
                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 3)
                
                # Get convex hull for better gesture detection
                hull = cv2.convexHull(hand_contour)
                cv2.drawContours(frame, [hull], -1, (255, 0, 0), 2)
                
                return self.classify_enhanced_gesture(hand_contour, hull)
        
        return None
    
    def classify_enhanced_gesture(self, contour, hull):
        """Enhanced gesture classification with better accuracy"""
        # Calculate properties
        area = cv2.contourArea(contour)
        hull_area = cv2.contourArea(hull)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return None
        
        # Calculate shape metrics
        compactness = (4 * np.pi * area) / (perimeter * perimeter)
        solidity = area / hull_area if hull_area > 0 else 0
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        extent = area / (w * h)
        
        # Enhanced gesture classification
        if area > 25000 and solidity > 0.8 and compactness > 0.4:
            return "open_palm"  # Large, solid, circular = open palm
        elif area > 18000 and aspect_ratio > 1.3 and solidity > 0.7:
            return "two_fingers"  # Medium, elongated, solid = two fingers
        elif area > 12000 and solidity < 0.8 and extent < 0.7:
            return "index_tap"  # Medium, not solid = pointing finger
        elif area > 8000 and compactness > 0.6 and solidity > 0.85:
            return "fist"  # Compact, very solid = fist
        
        return None
    
    def play_drum_sound(self, sound_type):
        """Play drum sound with enhanced feedback"""
        if sound_type in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][sound_type].play()
            
            # Get instrument names for each state
            instrument_names = {
                "tamil_nadu": {"drum_hit": "Parai", "cymbal": "Kanjira", "heavy_drum": "Thavil", "bass_drum": "Ghatam"},
                "karnataka": {"drum_hit": "Chande", "cymbal": "Tabla", "heavy_drum": "Dollu", "bass_drum": "Mridangam"},
                "kerala": {"drum_hit": "Chenda", "cymbal": "Edakka", "heavy_drum": "Timila", "bass_drum": "Mizhavu"},
                "punjab": {"drum_hit": "Dhol", "cymbal": "Tabla", "heavy_drum": "Dholak", "bass_drum": "Nagara"},
                "rajasthan": {"drum_hit": "Dhol", "cymbal": "Manjeera", "heavy_drum": "Nagada", "bass_drum": "Khartal"},
                "bengal": {"drum_hit": "Dhak", "cymbal": "Kartal", "heavy_drum": "Tabla", "bass_drum": "Khol"}
            }
            
            instrument = instrument_names[self.current_style][sound_type]
            style_name = self.current_style.replace('_', ' ').title()
            print(f"PLAYING: {instrument} ({style_name} style)")
    
    def process_gesture(self, gesture):
        """Process gesture with enhanced timing"""
        if not gesture or time.time() - self.last_gesture_time < self.gesture_cooldown:
            return
        
        # Enhanced gesture mapping
        gesture_map = {
            "index_tap": "drum_hit",      # Pointing = Primary drum
            "two_fingers": "cymbal",      # Two fingers = Metallic sound
            "open_palm": "heavy_drum",    # Open hand = Heavy drum
            "fist": "bass_drum"           # Fist = Bass drum
        }
        
        if gesture in gesture_map:
            self.play_drum_sound(gesture_map[gesture])
            self.last_gesture_time = time.time()
    
    def change_style(self, style_num):
        """Change to different Indian musical styles"""
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab", "rajasthan", "bengal"]
        style_names = ["Tamil Nadu", "Karnataka", "Kerala", "Punjab", "Rajasthan", "Bengal"]
        
        if 0 <= style_num < len(styles):
            self.current_style = styles[style_num]
            self.speak(f"{style_names[style_num]} traditional music style selected")
    
    def draw_enhanced_interface(self, frame):
        """Draw enhanced user interface"""
        # Current style with instrument info
        style_name = self.current_style.replace('_', ' ').title()
        cv2.putText(frame, f"Style: {style_name} Traditional Music", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Instrument mapping for current style
        instrument_info = {
            "tamil_nadu": ["Parai", "Kanjira", "Thavil", "Ghatam"],
            "karnataka": ["Chande", "Tabla", "Dollu", "Mridangam"],
            "kerala": ["Chenda", "Edakka", "Timila", "Mizhavu"],
            "punjab": ["Dhol", "Tabla", "Dholak", "Nagara"],
            "rajasthan": ["Dhol", "Manjeera", "Nagada", "Khartal"],
            "bengal": ["Dhak", "Kartal", "Tabla", "Khol"]
        }
        
        instruments = instrument_info[self.current_style]
        
        # Enhanced instructions
        instructions = [
            "HAND GESTURES & INSTRUMENTS:",
            f"Point finger = {instruments[0]}",
            f"Two fingers = {instruments[1]}",
            f"Open palm = {instruments[2]}", 
            f"Fist = {instruments[3]}",
            "",
            "MUSICAL STYLES (1-6):",
            "1=Tamil Nadu  2=Karnataka  3=Kerala",
            "4=Punjab      5=Rajasthan  6=Bengal",
            "Q=Quit"
        ]
        
        # Draw instructions with better formatting
        y_start = frame.shape[0] - 280
        for i, text in enumerate(instructions):
            if "GESTURES" in text or "STYLES" in text:
                color = (0, 255, 255)
                thickness = 2
            elif any(char.isdigit() for char in text) and "=" in text:
                color = (255, 200, 100)
                thickness = 1
            else:
                color = (255, 255, 255)
                thickness = 1
            
            cv2.putText(frame, text, (10, y_start + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
    
    def run(self):
        """Main application loop with enhanced features"""
        print("\n" + "="*70)
        print("ENHANCED VIRTUAL DRUM SYSTEM - RICH INDIAN MUSIC")
        print("="*70)
        print("TRADITIONAL INSTRUMENTS BY STATE:")
        print("  Tamil Nadu: Parai, Thavil, Kanjira, Ghatam")
        print("  Karnataka:  Chande, Dollu, Tabla, Mridangam")
        print("  Kerala:     Chenda, Timila, Edakka, Mizhavu")
        print("  Punjab:     Dhol, Dholak, Tabla, Nagara")
        print("  Rajasthan:  Dhol, Nagada, Manjeera, Khartal")
        print("  Bengal:     Dhak, Khol, Tabla, Kartal")
        print("\nHAND GESTURES:")
        print("  Point finger -> Primary drum")
        print("  Two fingers  -> Metallic instrument")
        print("  Open palm    -> Heavy drum")
        print("  Fist         -> Bass instrument")
        print("\nKEYBOARD: 1-6 = Change style, Q = Quit")
        print("="*70)
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot access camera!")
            return
        
        print("Camera ready! Experience rich Indian traditional music...")
        
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
                
                # Draw enhanced interface
                self.draw_enhanced_interface(frame)
                
                # Show frame
                cv2.imshow('Enhanced Virtual Drum System', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6')]:
                    self.change_style(int(chr(key)) - 1)
                    
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.speak("Thank you for experiencing Indian traditional music!")
            print("Enhanced Virtual Drum System stopped")

if __name__ == "__main__":
    system = EnhancedVirtualDrumSystem()
    system.run()