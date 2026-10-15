"""
Gesture Detection Module
Two-hand finger-thumb pinch detection using MediaPipe HandLandmarker (Tasks API).

Right Hand (Rhythm Layer):
    Index + Thumb  → Hi-Hat   (Time Keeping)
    Middle + Thumb → Snare    (Main Beat)
    Ring + Thumb   → Tom      (Fills)
    Pinky + Thumb  → Cymbal   (Accents)

Left Hand (Power Layer):
    Index + Thumb  → Bass Drum (Foundation)
    Middle + Thumb → Crash     (Impact)
    Ring + Thumb   → Ride      (Ride Rhythm)
    Pinky + Thumb  → Effect    (Percussion)
"""

import cv2
import mediapipe as mp
import numpy as np
import math
import time
import os

from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarkerResult,
    RunningMode,
)

# MediaPipe hand landmark indices
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

# Pinch thresholds (normalised coordinate distance — 0..1 range)
PINCH_THRESHOLD = 0.045      # Below this = pinch detected
RELEASE_THRESHOLD = 0.070    # Above this = released

# Right hand finger→instrument mapping (Rhythm Layer)
RIGHT_HAND_MAP = {
    INDEX_TIP:  "hihat",
    MIDDLE_TIP: "snare",
    RING_TIP:   "tom",
    PINKY_TIP:  "cymbal",
}

# Left hand finger→instrument mapping (Power Layer)
LEFT_HAND_MAP = {
    INDEX_TIP:  "bass_drum",
    MIDDLE_TIP: "crash",
    RING_TIP:   "ride",
    PINKY_TIP:  "effect",
}

# Human-readable names for display
INSTRUMENT_NAMES = {
    "hihat":     "Hi-Hat",
    "snare":     "Snare",
    "tom":       "Tom",
    "cymbal":    "Cymbal",
    "bass_drum": "Bass Drum",
    "crash":     "Crash",
    "ride":      "Ride",
    "effect":    "Effect",
}

# Finger display names
FINGER_NAMES = {
    INDEX_TIP:  "Index",
    MIDDLE_TIP: "Middle",
    RING_TIP:   "Ring",
    PINKY_TIP:  "Pinky",
}

# Colours for each finger (BGR)
FINGER_COLORS = {
    INDEX_TIP:  (0, 255, 0),    # Green
    MIDDLE_TIP: (255, 165, 0),  # Orange
    RING_TIP:   (255, 0, 255),  # Magenta
    PINKY_TIP:  (0, 255, 255),  # Yellow
}

# Hand landmark connections for drawing (same as MediaPipe HAND_CONNECTIONS)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),       # Index
    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
    (0, 13), (13, 14), (14, 15), (15, 16), # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17),             # Palm
]


class GestureDetector:
    """Detects finger-thumb pinch gestures on both hands using MediaPipe HandLandmarker."""

    def __init__(self):
        # Locate model file
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"HandLandmarker model not found at {model_path}. "
                "Download from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
            )

        # Create HandLandmarker in VIDEO mode (synchronous, frame-by-frame)
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

        # Per-hand, per-finger pinch state: True = currently pinched
        self.pinch_state = {}

        # Cooldown per instrument to avoid rapid re-triggers
        self.last_trigger_time = {}
        self.cooldown = 0.25  # seconds

        # Frame timestamp counter (milliseconds) — must be monotonically increasing
        self._timestamp_ms = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_frame(self, frame, style):
        """Process a BGR video frame.

        Parameters
        ----------
        frame : np.ndarray
            BGR image (already flipped horizontally for mirror effect).
        style : str
            Current drum style name (unused here but kept for interface).

        Returns
        -------
        (annotated_frame, list_of_triggered_instruments)
        """
        # Convert BGR → RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Advance timestamp
        self._timestamp_ms += 33  # ~30 fps

        # Run detection
        result: HandLandmarkerResult = self.landmarker.detect_for_video(mp_image, self._timestamp_ms)

        triggered = []
        h, w, _ = frame.shape

        if result.hand_landmarks and result.handedness:
            for hand_landmarks, handedness_list in zip(result.hand_landmarks, result.handedness):
                # handedness_list is a list of Category; take highest-score one
                label = handedness_list[0].category_name  # "Left" or "Right"

                # MediaPipe reports handedness from the camera's POV (un-mirrored).
                # Since we already flipped the frame, swap labels:
                user_hand = "Right" if label == "Left" else "Left"
                instrument_map = RIGHT_HAND_MAP if user_hand == "Right" else LEFT_HAND_MAP

                # Draw the hand skeleton
                self._draw_hand(frame, hand_landmarks, w, h)

                # Get thumb tip in normalised coords
                thumb = hand_landmarks[THUMB_TIP]

                for finger_tip_id, instrument in instrument_map.items():
                    finger = hand_landmarks[finger_tip_id]

                    # Euclidean distance in normalised space
                    dist = math.hypot(thumb.x - finger.x, thumb.y - finger.y)

                    state_key = (user_hand, finger_tip_id)
                    was_pinched = self.pinch_state.get(state_key, False)

                    if dist < PINCH_THRESHOLD and not was_pinched:
                        # New pinch detected
                        self.pinch_state[state_key] = True
                        now = time.time()
                        if now - self.last_trigger_time.get(instrument, 0) > self.cooldown:
                            triggered.append(instrument)
                            self.last_trigger_time[instrument] = now

                        # Visual feedback: filled circle at the midpoint
                        mid_x = int((thumb.x + finger.x) / 2 * w)
                        mid_y = int((thumb.y + finger.y) / 2 * h)
                        cv2.circle(frame, (mid_x, mid_y), 18, (0, 0, 255), -1)
                        cv2.putText(
                            frame,
                            INSTRUMENT_NAMES[instrument],
                            (mid_x - 30, mid_y - 25),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 0, 255),
                            2,
                        )

                    elif dist > RELEASE_THRESHOLD and was_pinched:
                        self.pinch_state[state_key] = False

                    # Draw line between thumb and fingertip
                    thumb_px = (int(thumb.x * w), int(thumb.y * h))
                    finger_px = (int(finger.x * w), int(finger.y * h))
                    color = FINGER_COLORS.get(finger_tip_id, (255, 255, 255))
                    thickness = 3 if self.pinch_state.get(state_key, False) else 1
                    cv2.line(frame, thumb_px, finger_px, color, thickness)

                # Label the hand
                wrist = hand_landmarks[0]
                wrist_px = (int(wrist.x * w), int(wrist.y * h) - 20)
                layer = "Rhythm" if user_hand == "Right" else "Power"
                cv2.putText(
                    frame,
                    f"{user_hand} Hand ({layer})",
                    wrist_px,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 0),
                    2,
                )

        return frame, triggered

    def release(self):
        """Release MediaPipe resources."""
        self.landmarker.close()

    # ------------------------------------------------------------------
    # Internal drawing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _draw_hand(frame, landmarks, w, h):
        """Draw hand skeleton given a list of NormalizedLandmark."""
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

        for start_idx, end_idx in HAND_CONNECTIONS:
            cv2.line(frame, points[start_idx], points[end_idx], (200, 200, 200), 1)

        for pt in points:
            cv2.circle(frame, pt, 3, (255, 255, 255), -1)