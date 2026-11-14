
import math
import wave
import struct
from pathlib import Path

audio_dir = Path("shared_assets/audio")
audio_dir.mkdir(parents=True, exist_ok=True)

sample_rate = 44100
duration = 0.12
frequency = 660
volume = 0.18

samples = int(sample_rate * duration)

with wave.open(str(audio_dir / "click.wav"), "w") as audio:
    audio.setnchannels(1)
    audio.setsampwidth(2)
    audio.setframerate(sample_rate)

    for i in range(samples):
        time = i / sample_rate

        # Fade-out para evitar estalos
        fade = (1 - i / samples) ** 2

        value = math.sin(2 * math.pi * frequency * time)
        value *= volume * fade

        audio.writeframes(
            struct.pack("<h", int(value * 32767))
        )

print("Created assets/audio/click.wav")
