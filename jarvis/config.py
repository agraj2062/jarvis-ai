import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    base_url: str = os.getenv("JARVIS_BASE_URL", "http://localhost:11434/v1")
    api_key: str = os.getenv("JARVIS_API_KEY", "ollama")
    model: str = os.getenv("JARVIS_MODEL", "qwen2.5:7b")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    # Persona / voice
    address: str = os.getenv("JARVIS_ADDRESS", "sir")
    voice_model: str = os.getenv("JARVIS_VOICE_MODEL", "voices/en_GB-alan-medium.onnx")
    whisper_model: str = os.getenv("JARVIS_WHISPER_MODEL", "base.en")
    mic_level: int = int(os.getenv("JARVIS_MIC_LEVEL", "500"))
