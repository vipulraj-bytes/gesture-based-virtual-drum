"""
Recording Manager Module
Handles recording of drum performances and saving to files
"""

import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import datetime
import os
import threading

class RecordingManager:
    def __init__(self):
        self.sample_rate = 44100
        self.channels = 2
        self.recording_data = []
        self.is_recording = False
        self.recording_thread = None
        
        # Ensure recordings directory exists
        os.makedirs("recordings", exist_ok=True)
    
    def start_recording(self):
        """Start recording audio"""
        if not self.is_recording:
            self.is_recording = True
            self.recording_data = []
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
    
    def stop_recording(self):
        """Stop recording and save to file"""
        if self.is_recording:
            self.is_recording = False
            if self.recording_thread:
                self.recording_thread.join()
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/drum_performance_{timestamp}.wav"
            
            # Save recording
            if self.recording_data:
                audio_data = np.concatenate(self.recording_data, axis=0)
                wav.write(filename, self.sample_rate, audio_data)
                return filename
        
        return None
    
    def _record_audio(self):
        """Internal method to record audio"""
        def audio_callback(indata, frames, time, status):
            if self.is_recording:
                self.recording_data.append(indata.copy())
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback
            ):
                while self.is_recording:
                    sd.sleep(100)  # Sleep for 100ms
        except Exception as e:
            print(f"Recording error: {e}")
            self.is_recording = False