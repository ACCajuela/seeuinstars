"""Gera o ASTRA.exe e o ASTRA-windows.zip para o GitHub Release.

Precisa de: python -m pip install pyinstaller soundfile
Uso:        python tools/build_windows.py

Resultado:
    dist/ASTRA.exe            o jogo (um arquivo só)
    dist/ASTRA-windows.zip    o .exe + COMO-JOGAR.txt (para o Release)
"""
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

HOW_TO_PLAY = """ASTRA - A Journey Beyond Earth / Uma Jornada Alem da Terra
=========================================================

PORTUGUES
1. Clique duas vezes em ASTRA.exe.
2. Se aparecer "O Windows protegeu o computador", clique em
   "Mais informacoes" e depois em "Executar assim mesmo".
   (O aviso aparece porque o jogo nao tem assinatura digital paga.)
3. O progresso e as configuracoes ficam em %APPDATA%\\ASTRA.

ENGLISH
1. Double-click ASTRA.exe.
2. If you see "Windows protected your PC", click "More info"
   and then "Run anyway".
   (The warning appears because the game has no paid digital signature.)
3. Progress and settings are saved in %APPDATA%\\ASTRA.
"""


def main():
    # 1) áudios grandes -> .ogg
    subprocess.run([sys.executable, str(ROOT / "tools" / "convert_audio.py")],
                   check=True, cwd=ROOT)

    # 2) PyInstaller
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm",
                    "--clean", str(ROOT / "astra.spec")],
                   check=True, cwd=ROOT)

    exe = DIST / "ASTRA.exe"
    print(f"\nASTRA.exe: {exe.stat().st_size / 1e6:.1f} MB")

    # 3) .zip para o Release
    archive = DIST / "ASTRA-windows.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe, "ASTRA/ASTRA.exe")
        zf.writestr("ASTRA/COMO-JOGAR.txt", HOW_TO_PLAY)
    print(f"ASTRA-windows.zip: {archive.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
