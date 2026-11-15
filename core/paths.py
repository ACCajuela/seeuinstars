
"""Onde o jogo lê e grava arquivos.

- RESOURCE_ROOT: de onde vêm imagens, fontes, áudios, textos e capítulos.
  No desenvolvimento é a pasta do projeto. No ASTRA.exe (PyInstaller),
  é a pasta temporária onde o executável se descompacta.

- USER_DATA_DIR: onde ficam o save e as configurações (idioma, volume).
  No desenvolvimento continua sendo a pasta do projeto (como sempre foi).
  No ASTRA.exe vai para %APPDATA%\\ASTRA, porque a pasta temporária do
  executável é apagada quando o jogo fecha.
"""

import os
import sys
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT))

if FROZEN:
    USER_DATA_DIR = Path(
        os.environ.get("APPDATA", Path.home())
    ) / "ASTRA"
else:
    USER_DATA_DIR = PROJECT_ROOT

USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = USER_DATA_DIR / "settings.json"
SAVE_FILE = USER_DATA_DIR / "save.json"


def audio_file(folder, filename):
    """Prefere a versão .ogg (bem menor) se ela existir; senão, a original.
    Ex.: audio_file(pasta, "background.wav") -> background.ogg"""
    path = Path(folder) / filename
    ogg = path.with_suffix(".ogg")
    if path.suffix.lower() == ".wav" and ogg.exists():
        return ogg
    return path
