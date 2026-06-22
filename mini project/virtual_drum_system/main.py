#!/usr/bin/env python3
"""
Voice Controlled Gesture-Based Virtual Drum System for the Visually Impaired
Main application entry point

Two-hand finger-thumb pinch mapping:
  Right Hand (Rhythm): Index→Hi-Hat, Middle→Snare, Ring→Tom, Pinky→Cymbal
  Left Hand  (Power):  Index→Bass Drum, Middle→Crash, Ring→Ride, Pinky→Effect
"""

import cv2
import threading
import time
from gesture_detection import GestureDetector, INSTRUMENT_NAMES
from voice_control import VoiceController
from audio_engine import AudioEngine
from recording_manager import RecordingManager
from playlist_manager import PlaylistManager


class VirtualDrumSystem:
    def __init__(self):
        self.audio_engine = AudioEngine()
        self.gesture_detector = GestureDetector()
        self.voice_controller = VoiceController(self)
        self.recording_manager = RecordingManager()
        self.playlist_manager = PlaylistManager()

        self.current_style = "tamil_nadu"
        self.is_recording = False
        self.running = True

        # Initialise TTS greeting
        self.audio_engine.speak(
            "Virtual Drum System initialized. "
            "Use finger-thumb pinches to play drums. Say 'help' for commands."
        )

    def start(self):
        """Start the main application loop."""
        self._print_banner()

        # Start voice control in a background thread
        voice_thread = threading.Thread(
            target=self.voice_controller.listen_continuously
        )
        voice_thread.daemon = True
        voice_thread.start()

        # Open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Cannot access camera!")
            self.audio_engine.speak("Error: cannot access camera.")
            return

        print("Camera ready! Pinch fingers to thumb to play drums...\n")

        try:
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    continue

                # Flip horizontally for mirror effect
                frame = cv2.flip(frame, 1)

                # Detect pinch gestures → list of triggered instrument names
                frame, triggered = self.gesture_detector.process_frame(
                    frame, self.current_style
                )

                # Play every triggered instrument
                for instrument in triggered:
                    self.audio_engine.play_drum_sound(instrument, self.current_style)
                    name = INSTRUMENT_NAMES.get(instrument, instrument)
                    print(f"[DRUM] {name}  ({self.current_style.replace('_', ' ').title()})")

                    # Record event if recording
                    if self.is_recording:
                        self.recording_manager.record_event(instrument)

                # Draw on-screen HUD
                self._draw_hud(frame)

                cv2.imshow("Virtual Drum System", frame)

                # Keyboard shortcuts
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key in (ord("1"), ord("2"), ord("3"), ord("4")):
                    style_idx = int(chr(key)) - 1
                    styles = ["tamil_nadu", "karnataka", "kerala", "punjab"]
                    self.change_style(styles[style_idx])
                elif key == ord("r"):
                    if self.is_recording:
                        self.stop_recording()
                    else:
                        self.start_recording()

        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.gesture_detector.release()
            self.stop()

    # ------------------------------------------------------------------
    # Commands (also called from voice controller)
    # ------------------------------------------------------------------

    def change_style(self, style):
        """Change drum style."""
        if style in ("tamil_nadu", "karnataka", "kerala", "punjab"):
            self.current_style = style
            self.audio_engine.speak(
                f"{style.replace('_', ' ').title()} drum style selected"
            )
        else:
            self.audio_engine.speak("Invalid drum style")

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.recording_manager.start_recording()
            self.audio_engine.speak("Recording started")

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            filename = self.recording_manager.stop_recording()
            self.playlist_manager.add_track(filename, self.current_style)
            self.audio_engine.speak("Recording saved to playlist")

    def play_playlist(self):
        self.playlist_manager.play_next()

    def stop(self):
        self.running = False
        self.audio_engine.speak("Goodbye")

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _draw_hud(self, frame):
        """Draw a heads-up display with current style and mapping info."""
        h, w, _ = frame.shape
        style_name = self.current_style.replace("_", " ").title()

        # Style label (top-left)
        cv2.putText(
            frame,
            f"Style: {style_name}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2,
        )

        # Recording indicator
        if self.is_recording:
            cv2.circle(frame, (w - 30, 30), 12, (0, 0, 255), -1)
            cv2.putText(
                frame, "REC", (w - 70, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2,
            )

        # Mapping legend (bottom-left)
        legend = [
            "RIGHT HAND (Rhythm):",
            "  Index+Thumb = Hi-Hat",
            "  Middle+Thumb = Snare",
            "  Ring+Thumb = Tom",
            "  Pinky+Thumb = Cymbal",
            "",
            "LEFT HAND (Power):",
            "  Index+Thumb = Bass Drum",
            "  Middle+Thumb = Crash",
            "  Ring+Thumb = Ride",
            "  Pinky+Thumb = Effect",
            "",
            "Keys: 1-4=Style  R=Record  Q=Quit",
        ]

        y = h - len(legend) * 22 - 10
        for line in legend:
            is_header = "HAND" in line
            color = (0, 255, 255) if is_header else (255, 255, 255)
            thickness = 2 if is_header else 1
            cv2.putText(
                frame, line, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, thickness,
            )
            y += 22

    @staticmethod
    def _print_banner():
        print("\n" + "=" * 62)
        print("  VIRTUAL DRUM SYSTEM — FINGER-THUMB PINCH CONTROLS")
        print("=" * 62)
        print()
        print("  RIGHT HAND (Rhythm Layer):")
        print("    Index  + Thumb  ->  Hi-Hat    (Time Keeping)")
        print("    Middle + Thumb  ->  Snare     (Main Beat)")
        print("    Ring   + Thumb  ->  Tom       (Fills)")
        print("    Pinky  + Thumb  ->  Cymbal    (Accents)")
        print()
        print("  LEFT HAND (Power Layer):")
        print("    Index  + Thumb  ->  Bass Drum (Foundation)")
        print("    Middle + Thumb  ->  Crash     (Impact)")
        print("    Ring   + Thumb  ->  Ride      (Ride Rhythm)")
        print("    Pinky  + Thumb  ->  Effect    (Percussion)")
        print()
        print("  KEYBOARD:  1-4 = Style   R = Record   Q = Quit")
        print("=" * 62)
        print()


if __name__ == "__main__":
    system = VirtualDrumSystem()
    system.start()