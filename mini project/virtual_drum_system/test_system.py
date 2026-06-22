#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
"""

def test_imports():
    """Test all required imports"""
    try:
        import cv2
        print("[OK] OpenCV imported successfully")
    except ImportError:
        print("[ERROR] OpenCV import failed")
        return False
    
    try:
        import mediapipe as mp
        print("[OK] MediaPipe imported successfully")
    except ImportError:
        print("[ERROR] MediaPipe import failed")
        return False
    
    try:
        import pygame
        print("[OK] Pygame imported successfully")
    except ImportError:
        print("[ERROR] Pygame import failed")
        return False
    
    try:
        import pyttsx3
        print("[OK] pyttsx3 imported successfully")
    except ImportError:
        print("[ERROR] pyttsx3 import failed")
        return False
    
    try:
        import speech_recognition as sr
        print("[OK] SpeechRecognition imported successfully")
    except ImportError:
        print("[ERROR] SpeechRecognition import failed")
        return False
    
    try:
        import sounddevice as sd
        print("[OK] sounddevice imported successfully")
    except ImportError:
        print("[ERROR] sounddevice import failed")
        return False
    
    try:
        import scipy
        print("[OK] scipy imported successfully")
    except ImportError:
        print("[ERROR] scipy import failed")
        return False
    
    try:
        import numpy as np
        print("[OK] numpy imported successfully")
    except ImportError:
        print("[ERROR] numpy import failed")
        return False
    
    return True

def test_camera():
    """Test camera access"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("[OK] Camera access successful")
            cap.release()
            return True
        else:
            print("[ERROR] Camera access failed")
            return False
    except Exception as e:
        print(f"[ERROR] Camera test error: {e}")
        return False

def test_audio():
    """Test audio system"""
    try:
        import pygame
        pygame.mixer.init()
        print("[OK] Audio system initialized successfully")
        pygame.mixer.quit()
        return True
    except Exception as e:
        print(f"[ERROR] Audio system error: {e}")
        return False

def test_tts():
    """Test text-to-speech"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("[OK] Text-to-speech initialized successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Text-to-speech error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Virtual Drum System Dependencies...")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test imports
    if not test_imports():
        all_tests_passed = False
    
    print("\nTesting Hardware Access...")
    print("-" * 30)
    
    # Test camera
    if not test_camera():
        all_tests_passed = False
    
    # Test audio
    if not test_audio():
        all_tests_passed = False
    
    # Test TTS
    if not test_tts():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("[OK] All tests passed! System is ready to run.")
        print("Run 'python main.py' to start the Virtual Drum System.")
    else:
        print("[ERROR] Some tests failed. Please check the installation.")
        print("Refer to README.md for troubleshooting steps.")