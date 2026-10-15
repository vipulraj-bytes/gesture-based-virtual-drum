"""
Audio-Guided Learning System Module (ML Feature 2)
Provides an interactive teacher mode with spoken instructions,
performance tracking, and adaptive difficulty (RL-inspired).

Designed for visually impaired users.
"""

import time
import random

# Pre-defined lesson patterns (instrument sequence)
LESSONS = {
    "beginner": [
        ("hihat", "Pinch your right index finger for the hi-hat."),
        ("snare", "Pinch your right middle finger for the snare."),
        ("hihat", "Right index again."),
        ("snare", "Right middle again."),
    ],
    "intermediate": [
        ("hihat", "Right index."),
        ("hihat", "Right index."),
        ("snare", "Right middle."),
        ("custom_1", "Left index for your custom sound."),
    ],
    "advanced": [
        ("custom_1", "Left index."),
        ("hihat", "Right index."),
        ("snare", "Right middle."),
        ("custom_5", "Make a left fist."),
        ("cymbal", "Right pinky for cymbal crash!"),
    ]
}


class LearningSystem:
    """Manages audio-guided drum lessons with adaptive difficulty."""

    def __init__(self, audio_engine):
        self.audio_engine = audio_engine
        self.is_active = False
        self.current_level = "beginner"
        self.lesson_sequence = []
        self.current_step = 0
        
        # Adaptive tracking
        self.accuracy_history = []  # List of 1 (correct) or 0 (incorrect)
        self.step_start_time = 0
        self.time_limit = 4.0  # seconds to hit the right drum

    def start_lesson(self):
        """Start or resume a learning session."""
        self.is_active = True
        self.audio_engine.speak(f"Starting {self.current_level} lesson.")
        self._load_current_lesson()
        self._play_current_instruction()

    def stop_lesson(self):
        """Stop the learning session."""
        if self.is_active:
            self.is_active = False
            self.audio_engine.speak("Lesson stopped.")

    def _load_current_lesson(self):
        self.lesson_sequence = LESSONS[self.current_level]
        self.current_step = 0
        self.step_start_time = time.time()

    def _play_current_instruction(self):
        if self.current_step < len(self.lesson_sequence):
            target, instruction = self.lesson_sequence[self.current_step]
            self.audio_engine.speak(instruction)
            self.step_start_time = time.time()
        else:
            self._finish_lesson()

    def check_hit(self, hit_instrument):
        """Called by main loop when an instrument is played."""
        if not self.is_active:
            return

        target_instrument, _ = self.lesson_sequence[self.current_step]
        
        if hit_instrument == target_instrument:
            # Correct hit! Give positive reinforcement occasionally
            if random.random() < 0.3:
                self.audio_engine.speak(random.choice(["Good!", "Perfect!", "Nice!"]))
            
            self.accuracy_history.append(1)
            self.current_step += 1
            time.sleep(0.5)  # Brief pause before next instruction
            self._play_current_instruction()
            
        else:
            # Wrong hit!
            self.accuracy_history.append(0)
            self.audio_engine.speak("Not quite. Let's try again. " + self.lesson_sequence[self.current_step][1])
            self.step_start_time = time.time()

    def update(self):
        """Called every frame to check for timeouts."""
        if not self.is_active:
            return
            
        if self.current_step < len(self.lesson_sequence):
            elapsed = time.time() - self.step_start_time
            if elapsed > self.time_limit:
                # User took too long
                self.accuracy_history.append(0)
                self.audio_engine.speak("Are you still there? Try again. " + self.lesson_sequence[self.current_step][1])
                self.step_start_time = time.time()

    def _finish_lesson(self):
        """Lesson complete, calculate score and adapt difficulty."""
        if not self.accuracy_history:
            self.is_active = False
            return
            
        # RL-inspired scoring: recent attempts matter more
        # Simple implementation: basic average for now
        score = sum(self.accuracy_history) / len(self.accuracy_history)
        
        if score >= 0.8:
            self.audio_engine.speak("Excellent work! You passed.")
            self._adapt_difficulty(up=True)
        elif score < 0.5:
            self.audio_engine.speak("That was tough. Let's practice that again.")
            self._adapt_difficulty(up=False)
        else:
            self.audio_engine.speak("Good job! Let's review this level once more to get perfect.")
            
        # Reset and wait for user to say "start lesson" again
        self.is_active = False
        self.accuracy_history = []

    def _adapt_difficulty(self, up):
        """Adapt to next or previous level based on performance."""
        levels = ["beginner", "intermediate", "advanced"]
        current_idx = levels.index(self.current_level)
        
        if up and current_idx < len(levels) - 1:
            self.current_level = levels[current_idx + 1]
            self.audio_engine.speak(f"You've been promoted to {self.current_level} level.")
        elif not up and current_idx > 0:
            self.current_level = levels[current_idx - 1]
            self.audio_engine.speak(f"We'll review the {self.current_level} level.")
