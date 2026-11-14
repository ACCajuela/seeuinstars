
import math
import random
import wave
from pathlib import Path

SAMPLE_RATE = 22050
OUTPUT = Path(__file__).resolve().parent

rng = random.Random(42)


def save_wav(filename, samples):
    path = OUTPUT / filename

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)

        data = bytearray()

        for sample in samples:
            sample = max(-1.0, min(1.0, sample))
            value = int(sample * 32767)
            data.extend(value.to_bytes(
                2, "little", signed=True
            ))

        wav.writeframes(data)

    print(f"Generated: {path.name}")


def generate_static(duration=3.0):
    """Radio noise with occasional crackles."""

    samples = []
    total = int(duration * SAMPLE_RATE)
    crackle = 0.0

    for i in range(total):
        t = i / SAMPLE_RATE

        noise = rng.uniform(-1, 1)

        if rng.random() < 0.0007:
            crackle = rng.uniform(-0.8, 0.8)

        crackle *= 0.91

        flutter = (
            0.75
            + 0.15 * math.sin(2 * math.pi * 2.3 * t)
        )

        sample = (
            noise * 0.20 * flutter
            + crackle * 0.35
        )

        samples.append(sample)

    save_wav("radio_static.wav", samples)


def generate_breathing(duration=6.0):
    """
    Soft synthetic breathing-like sound.

    Filtered noise with a slow inhale/exhale
    envelope, not a human voice recording.
    """

    samples = []
    total = int(duration * SAMPLE_RATE)

    filtered = 0.0

    for i in range(total):
        t = i / SAMPLE_RATE

        # Approximately one breathing cycle
        # every three seconds.
        phase = (t % 3.0) / 3.0

        if phase < 0.38:
            envelope = math.sin(
                math.pi * phase / 0.38
            ) ** 2

        elif phase < 0.50:
            envelope = 0.0

        else:
            exhale_phase = (phase - 0.50) / 0.50
            envelope = (
                0.7
                * math.sin(math.pi * exhale_phase) ** 2
            )

        noise = rng.uniform(-1, 1)

        # Simple low-pass filter.
        filtered = (
            0.22 * noise
            + 0.78 * filtered
        )

        # Faint radio noise remains.
        background = rng.uniform(-1, 1) * 0.018

        sample = (
            filtered * envelope * 0.42
            + background
        )

        # Fade at beginning and end.
        fade = min(
            1.0,
            t / 0.3,
            (duration - t) / 0.3
        )

        samples.append(sample * max(0.0, fade))

    save_wav("radio_breathing.wav", samples)


if __name__ == "__main__":
    generate_static()
    generate_breathing()
    print("Radio audio generation complete!")
