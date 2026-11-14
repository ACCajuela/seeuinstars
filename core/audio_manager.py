
from pathlib import Path
import pygame


class AudioManager:
    def __init__(self):
        self.audio_path = (
            Path(__file__).resolve().parent.parent
            / "shared_assets" / "audio"
        )

        pygame.mixer.init()

        self.enabled = True
        self.music_volume = 0.25
        self.effects_volume = 0.65
        self.effects = {}

    def play_effect(self, filename):
        if not self.enabled:
            return

        file_path = self.audio_path / filename

        if not file_path.exists():
            print(f"Audio file not found: {file_path}")
            return

        if filename not in self.effects:
            self.effects[filename] = pygame.mixer.Sound(
                str(file_path)
            )

        sound = self.effects[filename]
        sound.set_volume(self.effects_volume)
        sound.play()

    def play_music(self, filename="background.wav"):
        file_path = self.audio_path / filename

        if not file_path.exists():
            print(f"Music file not found: {file_path}")
            return

        pygame.mixer.music.load(str(file_path))
        pygame.mixer.music.set_volume(
            self.music_volume if self.enabled else 0
        )
        pygame.mixer.music.play(-1)

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(
            self.music_volume if self.enabled else 0
        )

    def set_effects_volume(self, volume):
        self.effects_volume = max(0.0, min(1.0, volume))

        for sound in self.effects.values():
            sound.set_volume(
                self.effects_volume if self.enabled else 0
            )

    def stop_audio(self):
        pygame.mixer.music.set_volume(0)
        pygame.mixer.stop()

    def set_enabled(self, enabled):
        self.enabled = enabled

        if enabled:
            pygame.mixer.music.set_volume(self.music_volume)
        else:
            self.stop_audio()

    def toggle_audio(self):
        self.set_enabled(not self.enabled)
        return self.enabled
