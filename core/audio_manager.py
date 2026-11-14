
import winsound
from pathlib import Path


class AudioManager:
    def __init__(self):
        # Pasta onde ficam os arquivos de áudio
        project_root = Path(__file__).resolve().parent.parent
        self.audio_path = project_root / "shared_assets" / "audio"

        # Controle de áudio
        self.enabled = True

    def play_effect(self, filename):
        """Reproduz um efeito sonoro WAV."""
        if not self.enabled:
            return

        file_path = self.audio_path / filename

        if not file_path.exists():
            print(f"Audio file not found: {file_path}")
            return

        winsound.PlaySound(
            str(file_path),
            winsound.SND_FILENAME | winsound.SND_ASYNC
        )

    def stop_audio(self):
        """Interrompe o áudio atual."""
        winsound.PlaySound(None, 0)

    def set_enabled(self, enabled):
        """Ativa ou desativa os efeitos sonoros."""
        self.enabled = enabled

        if not enabled:
            self.stop_audio()
