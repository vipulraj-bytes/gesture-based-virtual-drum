"""
Adaptive Gesture Calibration Module (ML Feature 1)
Learns each user's unique hand size and gesture patterns to auto-tune
pinch/fist detection thresholds using scikit-learn.

Designed for visually impaired users — all guidance is via TTS.
"""

import os
import json
import time
import math
import numpy as np
from sklearn.mixture import GaussianMixture

# Calibration data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROFILE_PATH = os.path.join(DATA_DIR, "calibration_profile.json")

# Landmark indices
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

FINGER_TIPS = [INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
FINGER_NAMES = {
    INDEX_TIP: "index",
    MIDDLE_TIP: "middle",
    RING_TIP: "ring",
    PINKY_TIP: "pinky",
}


class CalibrationManager:
    """Manages per-user gesture calibration using ML."""

    def __init__(self):
        self.samples = {tip: {"pinched": [], "released": []} for tip in FINGER_TIPS}
        self.fist_samples = {"closed": [], "open": []}
        self.thresholds = None
        self.is_calibrating = False
        self.calibration_step = 0
        self.current_state = "idle"  # idle, collecting_pinch, collecting_release, etc.
        self._current_finger = None
        self._collection_start = 0
        self._collect_duration = 2.0  # seconds per gesture

        # Try to load existing profile
        self._load_profile()

    # ------------------------------------------------------------------
    # Calibration Session (TTS-guided)
    # ------------------------------------------------------------------

    def start_calibration(self, audio_engine):
        """Begin the calibration session with TTS guidance."""
        self.is_calibrating = True
        self.calibration_step = 0
        self.samples = {tip: {"pinched": [], "released": []} for tip in FINGER_TIPS}
        self.fist_samples = {"closed": [], "open": []}
        audio_engine.speak(
            "Starting calibration. I will guide you through a series of "
            "hand gestures. Please follow my instructions carefully."
        )
        time.sleep(0.5)
        self._advance_step(audio_engine)

    def _advance_step(self, audio_engine):
        """Move to the next calibration step."""
        # Steps: For each finger (4 fingers × 2 states = 8 steps) + fist (2 steps) = 10
        steps = []
        for tip in FINGER_TIPS:
            name = FINGER_NAMES[tip]
            steps.append(("pinch", tip, f"Please pinch your {name} finger and thumb together. Hold it."))
            steps.append(("release", tip, f"Now relax your {name} finger. Keep it open."))
        steps.append(("fist_close", None, "Now make a fist. Close all your fingers tightly."))
        steps.append(("fist_open", None, "Now open your hand completely. Spread your fingers."))

        if self.calibration_step >= len(steps):
            self._finish_calibration(audio_engine)
            return

        action, finger, instruction = steps[self.calibration_step]
        self.current_state = action
        self._current_finger = finger
        self._collection_start = time.time()

        audio_engine.speak(instruction)

    def collect_frame_data(self, hand_landmarks, audio_engine):
        """Collect calibration data from a single frame."""
        if not self.is_calibrating:
            return

        elapsed = time.time() - self._collection_start
        if elapsed < 0.8:
            # Wait for user to get into position
            return
        if elapsed > self._collect_duration + 0.8:
            # Time's up, advance to next step
            self.calibration_step += 1
            self._advance_step(audio_engine)
            return

        thumb = hand_landmarks[THUMB_TIP]

        if self.current_state == "pinch":
            finger = hand_landmarks[self._current_finger]
            dist = math.hypot(thumb.x - finger.x, thumb.y - finger.y)
            self.samples[self._current_finger]["pinched"].append(dist)

        elif self.current_state == "release":
            finger = hand_landmarks[self._current_finger]
            dist = math.hypot(thumb.x - finger.x, thumb.y - finger.y)
            self.samples[self._current_finger]["released"].append(dist)

        elif self.current_state == "fist_close":
            palm_cx = (hand_landmarks[0].x + hand_landmarks[9].x) / 2
            palm_cy = (hand_landmarks[0].y + hand_landmarks[9].y) / 2
            avg_dist = np.mean([
                math.hypot(hand_landmarks[tip].x - palm_cx,
                           hand_landmarks[tip].y - palm_cy)
                for tip in FINGER_TIPS
            ])
            self.fist_samples["closed"].append(avg_dist)

        elif self.current_state == "fist_open":
            palm_cx = (hand_landmarks[0].x + hand_landmarks[9].x) / 2
            palm_cy = (hand_landmarks[0].y + hand_landmarks[9].y) / 2
            avg_dist = np.mean([
                math.hypot(hand_landmarks[tip].x - palm_cx,
                           hand_landmarks[tip].y - palm_cy)
                for tip in FINGER_TIPS
            ])
            self.fist_samples["open"].append(avg_dist)

    def _finish_calibration(self, audio_engine):
        """Compute optimal thresholds using ML and save profile."""
        self.is_calibrating = False
        self.current_state = "idle"

        audio_engine.speak("Calibration data collected. Computing your personal thresholds.")

        thresholds = self._compute_thresholds()
        if thresholds:
            self.thresholds = thresholds
            self._save_profile()
            audio_engine.speak(
                "Calibration complete! Your personal gesture thresholds have been "
                "saved. The system is now tuned to your hand."
            )
        else:
            audio_engine.speak(
                "Calibration could not be completed. Not enough data was collected. "
                "Please try again."
            )

    # ------------------------------------------------------------------
    # ML Threshold Computation
    # ------------------------------------------------------------------

    def _compute_thresholds(self):
        """Use Gaussian Mixture Model to find optimal pinch/release boundaries."""
        thresholds = {}

        for tip in FINGER_TIPS:
            pinched = self.samples[tip]["pinched"]
            released = self.samples[tip]["released"]

            if len(pinched) < 3 or len(released) < 3:
                # Not enough data, use defaults
                thresholds[str(tip)] = {
                    "pinch": 0.045,
                    "release": 0.070,
                }
                continue

            # Combine data and fit a 2-component GMM
            all_data = np.array(pinched + released).reshape(-1, 1)
            labels = [0] * len(pinched) + [1] * len(released)

            gmm = GaussianMixture(n_components=2, random_state=42)
            gmm.fit(all_data)

            # Identify which component is pinched (lower mean) vs released (higher)
            means = gmm.means_.flatten()
            if means[0] < means[1]:
                pinch_mean, release_mean = means[0], means[1]
                pinch_std = np.sqrt(gmm.covariances_.flatten()[0])
                release_std = np.sqrt(gmm.covariances_.flatten()[1])
            else:
                pinch_mean, release_mean = means[1], means[0]
                pinch_std = np.sqrt(gmm.covariances_.flatten()[1])
                release_std = np.sqrt(gmm.covariances_.flatten()[0])

            # Set thresholds at the boundary between the two distributions
            # Pinch threshold: pinch_mean + 2 * pinch_std
            # Release threshold: release_mean - 2 * release_std
            pinch_threshold = pinch_mean + 2 * pinch_std
            release_threshold = max(
                pinch_threshold + 0.01,
                release_mean - 2 * release_std
            )

            thresholds[str(tip)] = {
                "pinch": float(round(pinch_threshold, 4)),
                "release": float(round(release_threshold, 4)),
            }

        # Fist threshold
        closed = self.fist_samples["closed"]
        opened = self.fist_samples["open"]
        if len(closed) >= 3 and len(opened) >= 3:
            closed_mean = np.mean(closed)
            opened_mean = np.mean(opened)
            # Threshold at midpoint between closed and open
            fist_threshold = (closed_mean + opened_mean) / 2
            thresholds["fist"] = float(round(fist_threshold, 4))
        else:
            thresholds["fist"] = 0.08

        return thresholds

    # ------------------------------------------------------------------
    # Profile Persistence
    # ------------------------------------------------------------------

    def _save_profile(self):
        """Save calibration profile to JSON."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(PROFILE_PATH, "w") as f:
            json.dump(self.thresholds, f, indent=2)
        print(f"Calibration profile saved to {PROFILE_PATH}")

    def _load_profile(self):
        """Load calibration profile from JSON if it exists."""
        if os.path.exists(PROFILE_PATH):
            try:
                with open(PROFILE_PATH, "r") as f:
                    self.thresholds = json.load(f)
                print(f"Loaded calibration profile from {PROFILE_PATH}")
            except (json.JSONDecodeError, IOError):
                self.thresholds = None
        else:
            self.thresholds = None

    def reset_calibration(self, audio_engine):
        """Reset calibration to defaults."""
        self.thresholds = None
        if os.path.exists(PROFILE_PATH):
            os.remove(PROFILE_PATH)
        audio_engine.speak("Calibration has been reset to default thresholds.")

    # ------------------------------------------------------------------
    # Threshold Access
    # ------------------------------------------------------------------

    def get_pinch_threshold(self, finger_tip_id):
        """Get the pinch threshold for a specific finger."""
        if self.thresholds and str(finger_tip_id) in self.thresholds:
            return self.thresholds[str(finger_tip_id)]["pinch"]
        return 0.045  # default

    def get_release_threshold(self, finger_tip_id):
        """Get the release threshold for a specific finger."""
        if self.thresholds and str(finger_tip_id) in self.thresholds:
            return self.thresholds[str(finger_tip_id)]["release"]
        return 0.070  # default

    def get_fist_threshold(self):
        """Get the fist detection threshold."""
        if self.thresholds and "fist" in self.thresholds:
            return self.thresholds["fist"]
        return 0.08  # default
