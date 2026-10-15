# Voice Controlled Gesture-Based Virtual Drum System Setup Instructions

## Prerequisites
- Python 3.8 or higher
- Webcam
- Microphone
- Speakers/Headphones

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Additional Windows Setup (if needed)
If you encounter issues with PyAudio on Windows:
```bash
pip install pipwin
pipwin install pyaudio
```

### 3. Test Microphone and Camera
Ensure your microphone and camera are working and accessible by Python.

## Running the Application

### Start the System
```bash
python main.py
```

### Voice Commands
- **Style Selection:**
  - "Select Tamil Nadu style"
  - "Select Karnataka style" 
  - "Select Kerala style"
  - "Select Punjab style"

- **Recording:**
  - "Start recording"
  - "Stop recording"

- **Playback:**
  - "Play playlist"
  - "Next track"
  - "Delete track"

- **System:**
  - "Help" - Get list of commands
  - "Exit" - Close application

### Hand Gestures
- **Index Finger Tap:** Basic drum hit
- **Two Fingers (Peace Sign):** Cymbal sound
- **Open Palm:** Heavy drum sound
- **Fist:** Bass drum sound

## Troubleshooting

### Common Issues:
1. **Microphone not working:** Check Windows privacy settings for microphone access
2. **Camera not detected:** Ensure no other applications are using the camera
3. **Audio issues:** Check speaker/headphone connections
4. **Speech recognition errors:** Speak clearly and ensure good microphone quality

### Performance Tips:
- Use good lighting for better gesture detection
- Keep hands within camera frame
- Speak clearly for voice commands
- Minimize background noise

## Project Structure
```
virtual_drum_system/
├── main.py                 # Main application
├── gesture_detection.py    # Hand gesture recognition
├── voice_control.py        # Speech recognition and commands
├── audio_engine.py         # Sound playback and TTS
├── recording_manager.py    # Audio recording functionality
├── playlist_manager.py     # Playlist management
├── requirements.txt        # Python dependencies
├── audio_samples/          # Drum sound files (organized by state)
│   ├── tamil_nadu/
│   ├── karnataka/
│   ├── kerala/
│   └── punjab/
├── recordings/             # Saved drum performances
└── data/                   # Application data (playlist.json)
```