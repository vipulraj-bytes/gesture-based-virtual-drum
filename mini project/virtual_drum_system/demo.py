#!/usr/bin/env python3
"""
Simplified Virtual Drum System Demo
Works with basic dependencies and keyboard input for testing
"""

import pygame
import pyttsx3
import time
import threading
import json
import os
from datetime import datetime

class SimpleDrumSystem:
    def __init__(self):
        # Initialize pygame for audio
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
        
        # Current state
        self.current_style = "tamil_nadu"
        self.is_recording = False
        self.running = True
        
        # Create drum sounds
        self.drum_sounds = self.create_drum_sounds()
        
        # Playlist
        self.playlist = []
        self.current_track = 0
        
        # Ensure directories exist
        os.makedirs("recordings", exist_ok=True)
        os.makedirs("data", exist_ok=True)
        
        self.speak("Virtual Drum System initialized. Press keys to play drums!")
        self.show_instructions()
    
    def create_drum_sounds(self):
        """Create synthetic drum sounds for all styles"""
        import numpy as np
        
        sounds = {}
        styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
        
        for style in styles:
            sounds[style] = {}
            
            # Different base frequencies for each style
            base_freq = {
                "tamil_nadu": 150,    # Parai/Thavil
                "karnataka": 120,     # Chande/Dollu  
                "kerala": 180,        # Chenda
                "punjab": 100         # Dhol
            }[style]
            
            # Create different drum sounds
            sounds[style]["drum_hit"] = self.generate_drum_sound(base_freq, 0.3)
            sounds[style]["cymbal"] = self.generate_drum_sound(base_freq * 4, 0.2)
            sounds[style]["heavy_drum"] = self.generate_drum_sound(base_freq * 0.7, 0.5)
            sounds[style]["bass_drum"] = self.generate_drum_sound(base_freq * 0.5, 0.4)
        
        return sounds
    
    def generate_drum_sound(self, frequency, duration):
        """Generate a drum sound with given frequency and duration"""
        import numpy as np
        
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create drum sound with decay
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 8)
        
        # Add harmonics for richer sound
        wave += 0.3 * np.sin(2 * np.pi * frequency * 2 * t) * np.exp(-t * 10)
        wave += 0.1 * np.sin(2 * np.pi * frequency * 3 * t) * np.exp(-t * 12)
        
        # Add noise for realistic drum sound
        noise = np.random.normal(0, 0.1, len(wave))
        wave = wave + noise * 0.2
        
        # Normalize and convert to int16
        wave = np.clip(wave, -1, 1)
        wave = (wave * 32767).astype(np.int16)
        
        # Create stereo
        stereo_wave = np.array([wave, wave]).T
        stereo_wave = np.ascontiguousarray(stereo_wave)
        
        return pygame.sndarray.make_sound(stereo_wave)
    
    def speak(self, text):
        """Text to speech"""
        def speak_async():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        thread = threading.Thread(target=speak_async)
        thread.daemon = True
        thread.start()
    
    def show_instructions(self):
        """Show keyboard instructions"""
        print("\n" + "="*60)
        print("🥁 VIRTUAL DRUM SYSTEM - KEYBOARD CONTROLS")
        print("="*60)
        print("DRUM SOUNDS:")
        print("  [1] - Basic drum hit")
        print("  [2] - Cymbal sound") 
        print("  [3] - Heavy drum")
        print("  [4] - Bass drum")
        print("\nSTYLE SELECTION:")
        print("  [T] - Tamil Nadu style (Parai/Thavil)")
        print("  [K] - Karnataka style (Chande/Dollu)")
        print("  [L] - Kerala style (Chenda)")
        print("  [P] - Punjab style (Dhol)")
        print("\nRECORDING:")
        print("  [R] - Start/Stop recording")
        print("  [SPACE] - Play playlist")
        print("  [N] - Next track")
        print("\nSYSTEM:")
        print("  [H] - Show this help")
        print("  [Q] - Quit")
        print("="*60)
    
    def play_drum(self, sound_type):
        """Play drum sound"""
        if sound_type in self.drum_sounds[self.current_style]:
            self.drum_sounds[self.current_style][sound_type].play()
            print(f"🥁 Playing {sound_type} ({self.current_style})")
    
    def change_style(self, style):
        """Change drum style"""
        styles = {
            "t": "tamil_nadu",
            "k": "karnataka", 
            "l": "kerala",
            "p": "punjab"
        }
        
        if style in styles:
            self.current_style = styles[style]
            style_name = self.current_style.replace('_', ' ').title()
            print(f"🎵 Style changed to: {style_name}")
            self.speak(f"{style_name} drum style selected")
    
    def toggle_recording(self):
        """Toggle recording state"""
        self.is_recording = not self.is_recording
        if self.is_recording:
            print("🔴 Recording started...")
            self.speak("Recording started")
            self.recording_start_time = time.time()
        else:
            print("⏹️ Recording stopped")
            self.speak("Recording saved to playlist")
            # Simulate saving recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/drum_performance_{timestamp}.wav"
            
            # Add to playlist
            track = {
                "filename": filename,
                "style": self.current_style,
                "date_created": datetime.now().isoformat(),
                "title": f"Performance_{timestamp}",
                "duration": time.time() - self.recording_start_time
            }
            self.playlist.append(track)
            self.save_playlist()
    
    def save_playlist(self):
        """Save playlist to JSON"""
        try:
            with open("data/playlist.json", 'w') as f:
                json.dump(self.playlist, f, indent=2)
        except Exception as e:
            print(f"Error saving playlist: {e}")
    
    def play_playlist(self):
        """Play next track in playlist"""
        if not self.playlist:
            print("📭 Playlist is empty")
            self.speak("Playlist is empty")
            return
        
        if self.current_track >= len(self.playlist):
            self.current_track = 0
        
        track = self.playlist[self.current_track]
        print(f"🎵 Playing: {track['title']} ({track['style']} style)")
        self.speak(f"Playing {track['title']}")
        
        # Simulate playing track by playing a drum sound
        self.play_drum("drum_hit")
        self.current_track += 1
    
    def run(self):
        """Main application loop"""
        print("\n🎵 Virtual Drum System is running!")
        print("Press 'H' for help, 'Q' to quit")
        
        try:
            while self.running:
                key = input("\nPress key: ").lower().strip()
                
                if key == 'q':
                    self.running = False
                    self.speak("Goodbye")
                    print("👋 Goodbye!")
                    
                elif key == 'h':
                    self.show_instructions()
                    
                elif key == '1':
                    self.play_drum("drum_hit")
                elif key == '2':
                    self.play_drum("cymbal")
                elif key == '3':
                    self.play_drum("heavy_drum")
                elif key == '4':
                    self.play_drum("bass_drum")
                    
                elif key in ['t', 'k', 'l', 'p']:
                    self.change_style(key)
                    
                elif key == 'r':
                    self.toggle_recording()
                    
                elif key == ' ' or key == 'space':
                    self.play_playlist()
                    
                elif key == 'n':
                    self.play_playlist()
                    
                else:
                    print("❓ Unknown command. Press 'H' for help.")
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    system = SimpleDrumSystem()
    system.run()