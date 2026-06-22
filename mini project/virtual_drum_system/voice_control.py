"""
Voice Control Module
Handles speech recognition and voice commands for blind users.
"""

import speech_recognition as sr
import time


class VoiceController:
    def __init__(self, drum_system):
        self.drum_system = drum_system
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
        except Exception:
            pass

    def listen_continuously(self):
        """Continuously listen for voice commands."""
        while self.drum_system.running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(
                        source, timeout=1, phrase_time_limit=3
                    )

                try:
                    command = self.recognizer.recognize_google(audio).lower()
                    self.process_command(command)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass

            except sr.WaitTimeoutError:
                pass
            except Exception:
                time.sleep(0.1)

    def process_command(self, command):
        """Process a recognised voice command."""
        print(f"Voice command: {command}")

        # Style selection
        if "tamil nadu" in command or "tamil" in command:
            self.drum_system.change_style("tamil_nadu")
        elif "karnataka" in command:
            self.drum_system.change_style("karnataka")
        elif "kerala" in command:
            self.drum_system.change_style("kerala")
        elif "punjab" in command or "dhol" in command:
            self.drum_system.change_style("punjab")

        # Recording
        elif "start recording" in command or "record" in command:
            self.drum_system.start_recording()
        elif "stop recording" in command or "stop" in command:
            self.drum_system.stop_recording()

        # Playlist
        elif "play playlist" in command or "play" in command:
            self.drum_system.play_playlist()
        elif "next track" in command or "next" in command:
            self.drum_system.playlist_manager.play_next()
        elif "delete track" in command or "delete" in command:
            self.drum_system.playlist_manager.delete_current()

        # Help
        elif "help" in command:
            self.provide_help()

        # Exit
        elif "exit" in command or "quit" in command or "goodbye" in command:
            self.drum_system.stop()

        else:
            self.drum_system.audio_engine.speak(
                "Command not recognized. Say 'help' for available commands."
            )

    def provide_help(self):
        """Provide help information via TTS."""
        help_lines = [
            "Finger-thumb pinch mapping:",
            "Right hand, rhythm layer:",
            "Index and thumb for hi-hat.",
            "Middle and thumb for snare.",
            "Ring and thumb for tom.",
            "Pinky and thumb for cymbal.",
            "Left hand, power layer:",
            "Index and thumb for bass drum.",
            "Middle and thumb for crash.",
            "Ring and thumb for ride.",
            "Pinky and thumb for effect.",
            "Voice commands: select Tamil Nadu, Karnataka, Kerala, or Punjab style.",
            "Start recording, stop recording, play playlist, next track, "
            "delete track, help, or exit.",
        ]
        self.drum_system.audio_engine.speak(" ".join(help_lines))