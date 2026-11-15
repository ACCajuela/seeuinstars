# -*- mode: python ; coding: utf-8 -*-
# Receita do PyInstaller para gerar o ASTRA.exe (Windows).
# Para gerar: python tools/build_windows.py

from pathlib import Path

ROOT = Path(SPECPATH)

# Pastas com arquivos que não são código (imagens, fontes, textos...)
DATA_FOLDERS = ["assets", "chapters", "data", "locales"]

# Áudios: leva só os pequenos e as versões .ogg (os .wav grandes
# ficam de fora; o jogo usa o .ogg no lugar deles).
MAX_WAV_SIZE = 1_000_000

datas = []
for folder in DATA_FOLDERS:
    for file in (ROOT / folder).rglob("*"):
        if file.is_file():
            datas.append((str(file), str(file.parent.relative_to(ROOT))))

for file in (ROOT / "shared_assets").rglob("*"):
    if not file.is_file() or file.suffix == ".py":
        continue
    if file.suffix.lower() == ".wav" and file.stat().st_size > MAX_WAV_SIZE:
        continue
    datas.append((str(file), str(file.parent.relative_to(ROOT))))

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    datas=datas,
    hiddenimports=["pygame"],
    excludes=["numpy", "soundfile", "PyInstaller"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ASTRA",
    console=False,        # sem janela preta de terminal
    upx=False,
    icon=None,
)
