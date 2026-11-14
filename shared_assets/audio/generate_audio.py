
import math
import struct
import wave
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parent
SAMPLE_RATE = 44100


def generate_sound(filename, notes, duration=0.3, volume=0.18):
    samples = []
    total_samples = int(SAMPLE_RATE * duration)

    for i in range(total_samples):
        time = i / SAMPLE_RATE

        # Escolhe a nota conforme o momento do áudio
        note_index = min(
            int(time / duration * len(notes)),
            len(notes) - 1
        )

        frequency = notes[note_index]

        # Volume diminui suavemente até o final
        fade = (1 - i / total_samples) ** 2

        value = math.sin(2 * math.pi * frequency * time)
        value *= volume * fade

        samples.append(
            struct.pack("<h", int(value * 32767))
        )

    file_path = AUDIO_DIR / filename

    with wave.open(str(file_path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(b"".join(samples))

    print(f"Created: {file_path.name}")


# Clique curto
generate_sound("click.wav", [660], duration=0.12)

# Acerto: notas ascendentes
generate_sound("correct.wav", [523, 659, 784], duration=0.45)

# Erro: notas descendentes e suaves
generate_sound("wrong.wav", [440, 392], duration=0.3)
