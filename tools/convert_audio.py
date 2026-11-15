"""Converte os áudios .wav grandes para .ogg (bem menores).

O jogo usa o .ogg automaticamente quando ele existe (core/paths.py).
Precisa de: python -m pip install soundfile
Uso:        python tools/convert_audio.py
"""
from pathlib import Path

import soundfile

AUDIO = Path(__file__).resolve().parent.parent / "shared_assets" / "audio"
MIN_SIZE = 1_000_000  # só converte arquivos acima de ~1 MB

for wav in sorted(AUDIO.rglob("*.wav")):
    if wav.stat().st_size < MIN_SIZE:
        continue
    ogg = wav.with_suffix(".ogg")
    info = soundfile.info(str(wav))
    # Grava em pedaços: gravar tudo de uma vez estoura a memória
    # da biblioteca de áudio com arquivos grandes.
    with soundfile.SoundFile(str(ogg), "w", samplerate=info.samplerate,
                             channels=info.channels, format="OGG",
                             subtype="VORBIS") as out:
        for block in soundfile.blocks(str(wav), blocksize=8192):
            out.write(block)
    print(f"{wav.name}: {wav.stat().st_size / 1e6:.1f} MB -> "
          f"{ogg.name}: {ogg.stat().st_size / 1e6:.1f} MB")
