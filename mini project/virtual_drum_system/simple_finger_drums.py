#!/usr/bin/env python3
"""
Simple Finger Drum System - Reliable Version
Press keys 1-5 to simulate finger counts and hear different drums
"""

import pygame
import numpy as np
import time

class SimpleFingerDrums:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.current_style = "tamil_nadu"
        self.running = True
        self.last_play_time = 0
        self.cooldown = 0.3
        
        # Create 5 VERY different drum sounds
        self.create_distinct_drums()
        
        print("Simple Finger Drum System Ready!")
        print("Press keys 1-5 to hear different drums")
    
    def create_distinct_drums(self):
        """Create 5 completely different sounding drums"""
        self.drums = {}
        
        # Drum 1: High pitched tabla
        self.drums[1] = self.make_tabla()
        
        # Drum 2: Medium dholak  
        self.drums[2] = self.make_dholak()
        
        # Drum 3: Complex mridangam
        self.drums[3] = self.make_mridangam()
        
        # Drum 4: Heavy chenda
        self.drums[4] = self.make_chenda()
        
        # Drum 5: Deep bass dhol
        self.drums[5] = self.make_dhol()
        
        print("Created 5 distinct drum sounds!")
    
    def make_tabla(self):
        """High pitched, sharp tabla sound"""
        duration = 0.15
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Very high frequency
        freq = 500
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 25)
        
        # Convert to sound
        wave = np.clip(wave, -1, 1) * 0.8
        wave = (wave * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo)
    
    def make_dholak(self):
        """Medium pitched dholak"""
        duration = 0.25
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Medium frequency
        freq = 200
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 10)
        wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t * 15)
        
        # Convert to sound
        wave = np.clip(wave, -1, 1) * 0.8
        wave = (wave * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo)
    
    def make_mridangam(self):
        """Complex harmonics mridangam"""
        duration = 0.35
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Multiple frequencies
        freq = 150
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)
        wave += 0.5 * np.sin(2 * np.pi * freq * 1.5 * t) * np.exp(-t * 10)
        wave += 0.3 * np.sin(2 * np.pi * freq * 2.5 * t) * np.exp(-t * 12)
        
        # Convert to sound
        wave = np.clip(wave, -1, 1) * 0.8
        wave = (wave * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo)
    
    def make_chenda(self):
        """Heavy chenda drum"""
        duration = 0.4
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Lower frequency, more noise
        freq = 100
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 6)
        
        # Add noise for heavy sound
        noise = np.random.normal(0, 0.2, len(wave))
        wave = wave + noise * 0.4
        
        # Convert to sound
        wave = np.clip(wave, -1, 1) * 0.8
        wave = (wave * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo)
    
    def make_dhol(self):
        """Deep bass dhol"""
        duration = 0.5
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Very low frequency
        freq = 50
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 4)
        wave += 0.7 * np.sin(2 * np.pi * freq * 0.5 * t) * np.exp(-t * 5)
        
        # Heavy bass noise
        noise = np.random.normal(0, 0.3, len(wave))
        wave = wave + noise * 0.3
        
        # Convert to sound
        wave = np.clip(wave, -1, 1) * 0.8
        wave = (wave * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.array([wave, wave]).T)
        return pygame.sndarray.make_sound(stereo)
    
    def play_drum(self, drum_number):
        """Play specific drum"""
        if time.time() - self.last_play_time < self.cooldown:
            return
        
        if drum_number in self.drums:
            self.drums[drum_number].play()
            
            drum_names = {
                1: "Tabla (High & Sharp)",
                2: "Dholak (Medium)",
                3: "Mridangam (Complex)",
                4: "Chenda (Heavy)",
                5: "Dhol (Deep Bass)"
            }
            
            print(f"PLAYING: {drum_names[drum_number]}")
            self.last_play_time = time.time()
    
    def run(self):
        """Main loop - keyboard controlled"""
        print("\n" + "="*50)
        print("SIMPLE FINGER DRUM SYSTEM")
        print("="*50)
        print("KEYBOARD CONTROLS:")
        print("  Press 1 = Tabla (High & Sharp)")
        print("  Press 2 = Dholak (Medium)")
        print("  Press 3 = Mridangam (Complex)")
        print("  Press 4 = Chenda (Heavy)")
        print("  Press 5 = Dhol (Deep Bass)")
        print("  Press Q = Quit")
        print("="*50)
        print("\nListening for key presses...")
        
        try:
            while self.running:
                key = input("Press 1-5 to play drums (q to quit): ").strip().lower()
                
                if key == 'q':
                    self.running = False
                    print("Goodbye!")
                elif key in ['1', '2', '3', '4', '5']:
                    drum_num = int(key)
                    self.play_drum(drum_num)
                else:
                    print("Invalid key. Press 1-5 for drums, q to quit")
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")

if __name__ == "__main__":
    system = SimpleFingerDrums()
    system.run()