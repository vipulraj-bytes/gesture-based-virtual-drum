"""
Audio Engine Module
Handles drum sound playback (8 instruments) and text-to-speech functionality.

Instruments:
  Right Hand (Rhythm): Hi-Hat, Snare, Tom, Cymbal
  Left Hand  (Power):  Bass Drum, Crash, Ride, Effect
"""

import pygame
import pyttsx3
import numpy as np
import threading


class AudioEngine:
    def __init__(self):
        # Initialise pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Initialise text-to-speech
        self.tts_available = False
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
            self.tts_available = True
        except Exception:
            print("TTS not available, using text output only")

        # Build per-style sound banks
        self.drum_sounds = {}
        self._build_all_styles()

    # ------------------------------------------------------------------
    # Sound generation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_sound(wave):
        """Convert a mono float32 wave (-1..1) to a pygame stereo Sound."""
        wave = np.clip(wave, -1, 1).astype(np.float32)
        pcm = (wave * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.column_stack([pcm, pcm]))
        return pygame.sndarray.make_sound(stereo)

    # --- Individual instrument synthesisers ---

    @staticmethod
    def _gen_hihat(base_freq_mult=1.0):
        """Hi-hat: short burst of filtered noise."""
        sr, dur = 44100, 0.12
        t = np.linspace(0, dur, int(sr * dur))
        noise = np.random.normal(0, 1, len(t))
        # Band-pass feel via high-freq modulation
        env = np.exp(-t * 45)
        wave = noise * env * 0.7
        # Add a tiny tonal ping
        wave += 0.15 * np.sin(2 * np.pi * 6000 * base_freq_mult * t) * env
        return wave

    @staticmethod
    def _gen_snare(base_freq_mult=1.0):
        """Snare: mid-tone body + noise rattle."""
        sr, dur = 44100, 0.22
        t = np.linspace(0, dur, int(sr * dur))
        body = np.sin(2 * np.pi * 185 * base_freq_mult * t) * np.exp(-t * 20)
        noise = np.random.normal(0, 1, len(t)) * np.exp(-t * 15) * 0.5
        wave = body + noise
        return wave

    @staticmethod
    def _gen_tom(base_freq_mult=1.0):
        """Tom: mid-low sine with moderate decay."""
        sr, dur = 44100, 0.35
        t = np.linspace(0, dur, int(sr * dur))
        freq = 110 * base_freq_mult
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-t * 8)
        wave += 0.4 * np.sin(2 * np.pi * freq * 1.5 * t) * np.exp(-t * 12)
        # Slight noise
        wave += np.random.normal(0, 0.05, len(t)) * np.exp(-t * 10)
        return wave

    @staticmethod
    def _gen_cymbal(base_freq_mult=1.0):
        """Cymbal: metallic noise with slow decay."""
        sr, dur = 44100, 0.5
        t = np.linspace(0, dur, int(sr * dur))
        noise = np.random.normal(0, 1, len(t))
        env = np.exp(-t * 5)
        wave = noise * env * 0.5
        # Metallic overtones
        wave += 0.2 * np.sin(2 * np.pi * 3500 * base_freq_mult * t) * env
        wave += 0.15 * np.sin(2 * np.pi * 5200 * base_freq_mult * t) * env
        return wave

    @staticmethod
    def _gen_bass_drum(base_freq_mult=1.0):
        """Bass drum: deep sine sweep down, short punch."""
        sr, dur = 44100, 0.3
        t = np.linspace(0, dur, int(sr * dur))
        freq_sweep = 150 * base_freq_mult * np.exp(-t * 10) + 40 * base_freq_mult
        phase = 2 * np.pi * np.cumsum(freq_sweep) / sr
        wave = np.sin(phase) * np.exp(-t * 8)
        # Sub-bass thump
        wave += 0.5 * np.sin(2 * np.pi * 45 * base_freq_mult * t) * np.exp(-t * 12)
        return wave

    @staticmethod
    def _gen_crash(base_freq_mult=1.0):
        """Crash: wide-band noise with long sustain."""
        sr, dur = 44100, 0.7
        t = np.linspace(0, dur, int(sr * dur))
        noise = np.random.normal(0, 1, len(t))
        env = np.exp(-t * 3)
        wave = noise * env * 0.55
        # Shimmer
        wave += 0.2 * np.sin(2 * np.pi * 4800 * base_freq_mult * t) * env
        wave += 0.1 * np.sin(2 * np.pi * 7200 * base_freq_mult * t) * env
        return wave

    @staticmethod
    def _gen_ride(base_freq_mult=1.0):
        """Ride: bell-like tone + light noise."""
        sr, dur = 44100, 0.45
        t = np.linspace(0, dur, int(sr * dur))
        bell = np.sin(2 * np.pi * 2800 * base_freq_mult * t) * np.exp(-t * 6)
        bell += 0.5 * np.sin(2 * np.pi * 5600 * base_freq_mult * t) * np.exp(-t * 8)
        noise = np.random.normal(0, 0.15, len(t)) * np.exp(-t * 10)
        wave = bell * 0.6 + noise
        return wave

    @staticmethod
    def _gen_effect(base_freq_mult=1.0):
        """Effect / special percussion: frequency sweep with resonance."""
        sr, dur = 44100, 0.4
        t = np.linspace(0, dur, int(sr * dur))
        sweep = np.sin(2 * np.pi * (300 + 2000 * t) * base_freq_mult * t) * np.exp(-t * 7)
        click = np.random.normal(0, 0.5, len(t)) * np.exp(-t * 35) * 0.4
        wave = sweep * 0.7 + click
        return wave

    # ------------------------------------------------------------------
    # Style builder
    # ------------------------------------------------------------------

    _GENERATORS = {
        "hihat":     _gen_hihat.__func__,
        "snare":     _gen_snare.__func__,
        "tom":       _gen_tom.__func__,
        "cymbal":    _gen_cymbal.__func__,
        "bass_drum": _gen_bass_drum.__func__,
        "crash":     _gen_crash.__func__,
        "ride":      _gen_ride.__func__,
        "effect":    _gen_effect.__func__,
    }

    # Per-style frequency multiplier so each state sounds slightly different
    _STYLE_FREQ_MULT = {
        "tamil_nadu":  1.0,
        "karnataka":   0.92,
        "kerala":      1.08,
        "punjab":      0.85,
    }

    def _build_all_styles(self):
        for style, mult in self._STYLE_FREQ_MULT.items():
            self.drum_sounds[style] = {}
            for name, gen in self._GENERATORS.items():
                wave = gen(mult)
                self.drum_sounds[style][name] = self._to_sound(wave)

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def play_drum_sound(self, instrument, style):
        """Play the given instrument for the given style.

        Parameters
        ----------
        instrument : str
            One of: hihat, snare, tom, cymbal, bass_drum, crash, ride, effect
        style : str
            One of: tamil_nadu, karnataka, kerala, punjab
        """
        if style in self.drum_sounds and instrument in self.drum_sounds[style]:
            self.drum_sounds[style][instrument].play()

    # ------------------------------------------------------------------
    # Text-to-speech
    # ------------------------------------------------------------------

    def speak(self, text):
        """Convert text to speech (non-blocking)."""
        print(f"SYSTEM: {text}")
        if self.tts_available:
            def _speak():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception:
                    pass
            threading.Thread(target=_speak, daemon=True).start()

    # ------------------------------------------------------------------
    # File playback (for playlist)
    # ------------------------------------------------------------------

    def play_audio_file(self, filepath):
        """Play an audio file."""
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
        except pygame.error:
            self.speak("Error playing audio file")