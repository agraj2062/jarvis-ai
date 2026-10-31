"""Voice loop: wake word -> speech-to-text -> brain -> text-to-speech.
Requires the optional extras: pip install -e ".[voice]"
"""
import os
import shutil
import subprocess
import tempfile
import wave

import numpy as np
import sounddevice as sd

from .config import Config

RATE = 16000
FRAME = 1280  # 80 ms, what openWakeWord expects


class Ears:
    def __init__(self, cfg: Config, threshold: float = 0.5):
        from faster_whisper import WhisperModel
        from openwakeword.model import Model
        from openwakeword.utils import download_models

        try:
            download_models()
        except Exception:
            pass  # already downloaded or offline
        self.oww = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        self.stt = WhisperModel(cfg.whisper_model, compute_type="int8")
        self.threshold = threshold
        self.level = cfg.mic_level

    def wait_for_wake(self) -> None:
        self.oww.reset()
        with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=FRAME) as s:
            while True:
                frame, _ = s.read(FRAME)
                scores = self.oww.predict(frame[:, 0])
                if max(scores.values(), default=0.0) > self.threshold:
                    return

    def listen(self, max_s: float = 12, silence_s: float = 1.0, start_timeout: float = 5) -> str:
        chunks, heard, quiet = [], False, 0.0
        with sd.InputStream(samplerate=RATE, channels=1, dtype="int16", blocksize=FRAME) as s:
            while True:
                frame, _ = s.read(FRAME)
                mono = frame[:, 0]
                chunks.append(mono)
                rms = float(np.sqrt(np.mean(mono.astype(np.float32) ** 2)))
                elapsed = len(chunks) * FRAME / RATE
                if rms > self.level:
                    heard, quiet = True, 0.0
                else:
                    quiet += FRAME / RATE
                if heard and quiet >= silence_s:
                    break
                if not heard and elapsed >= start_timeout:
                    return ""
                if elapsed >= max_s:
                    break
        audio = np.concatenate(chunks).astype(np.float32) / 32768.0
        segments, _ = self.stt.transcribe(audio, language="en", vad_filter=True)
        return " ".join(seg.text.strip() for seg in segments).strip()


class Mouth:
    def __init__(self, cfg: Config):
        self.voice = cfg.voice_model
        self.piper = shutil.which("piper")
        if not (self.piper and os.path.exists(self.voice)):
            print("[voice] Piper or voice model not found; replies will be text only.")

    def say(self, text: str) -> None:
        print(f"\njarvis > {text}")
        if not (self.piper and os.path.exists(self.voice)):
            return
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            subprocess.run(
                [self.piper, "--model", self.voice, "--output_file", path],
                input=text.encode(), check=True, capture_output=True,
            )
            with wave.open(path) as w:
                rate = w.getframerate()
                data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
            sd.play(data, rate)
            sd.wait()
        finally:
            os.remove(path)


def run_voice() -> None:
    from .brain import Brain

    cfg = Config()
    ears, mouth = Ears(cfg), Mouth(cfg)

    def confirm(action: str) -> bool:
        name = action.split("(")[0].replace("_", " ")
        mouth.say(f"I'd like to run {name}. Shall I proceed, {cfg.address}?")
        reply = ears.listen(max_s=6).lower()
        return any(w in reply for w in ("yes", "proceed", "go ahead", "do it", "confirm"))

    brain = Brain(cfg, confirm=confirm)
    mouth.say(
        f"Good day, {cfg.address}. All systems are online. "
        "Say 'hey Jarvis' whenever you need me."
    )
    while True:
        ears.wait_for_wake()
        mouth.say(f"Yes, {cfg.address}?")
        text = ears.listen()
        if not text:
            continue
        print(f"you    > {text}")
        if any(p in text.lower() for p in ("power down", "shut down", "goodbye jarvis")):
            mouth.say(f"Very good, {cfg.address}. Powering down.")
            break
        mouth.say(brain.ask(text))
