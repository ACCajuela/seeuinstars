
import json
from pathlib import Path

import pygame


class AudioManager:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent

        self.audio_path = (
            self.project_root / "shared_assets" / "audio"
        )

        self.settings_file = self.project_root / "settings.json"

        # Configurações padrão
        self.enabled = True
        self.music_volume = 0.25
        self.effects_volume = 0.65

        # Cache dos efeitos sonoros
        self.effects = {}

        # Recupera as configurações salvas
        self.load_settings()

        # Inicializa o sistema de áudio apenas se necessário
        if not pygame.mixer.get_init():
            pygame.mixer.init()

    # ========================================================
    # PERSISTÊNCIA
    # ========================================================

    def load_settings(self):
        if not self.settings_file.exists():
            return

        try:
            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as file:
                settings = json.load(file)

            if not isinstance(settings, dict):
                return

            self.music_volume = self._valid_volume(
                settings.get("music_volume", 0.25),
                0.25
            )

            self.effects_volume = self._valid_volume(
                settings.get("effects_volume", 0.65),
                0.65
            )

            enabled = settings.get("enabled", True)

            self.enabled = (
                enabled
                if isinstance(enabled, bool)
                else True
            )

        except (OSError, ValueError, TypeError) as error:
            print(f"Could not load audio settings: {error}")

    def save_settings(self):
        # Preserva outras preferências, como idioma
        settings = {}

        if self.settings_file.exists():
            try:
                with open(
                    self.settings_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    data = json.load(file)

                if isinstance(data, dict):
                    settings = data

            except (OSError, ValueError, TypeError) as error:
                print(f"Could not read settings: {error}")
                return

        settings.update({
            "music_volume": self.music_volume,
            "effects_volume": self.effects_volume,
            "enabled": self.enabled
        })

        try:
            with open(
                self.settings_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    settings,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except OSError as error:
            print(f"Could not save audio settings: {error}")

    @staticmethod
    def _valid_volume(value, default):
        if isinstance(value, bool):
            return default

        try:
            return max(
                0.0,
                min(1.0, float(value))
            )

        except (TypeError, ValueError):
            return default

    # ========================================================
    # EFEITOS SONOROS
    # ========================================================

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

    # ========================================================
    # MÚSICA DE FUNDO
    # ========================================================

    def play_music(self, filename="background.wav"):
        """
        Inicia uma música em loop.

        Respeita as configurações de volume e áudio.
        """

        file_path = self.audio_path / filename

        if not file_path.exists():
            print(f"Music file not found: {file_path}")
            return

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        pygame.mixer.music.load(str(file_path))

        pygame.mixer.music.set_volume(
            self.music_volume
            if self.enabled
            else 0
        )

        # -1 = reprodução em loop
        pygame.mixer.music.play(-1)

        print(f"[AUDIO] Playing music: {filename}")

    def pause_music(self):
        """
        Pausa a música sem perder a posição.
        """
        if pygame.mixer.get_init():
            pygame.mixer.music.pause()

    def resume_music(self):
        """
        Retoma a música pausada.
        """
        if pygame.mixer.get_init():
            pygame.mixer.music.unpause()

    def stop_music(self):
        """
        Para somente a música de fundo.
        """
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    # ========================================================
    # CONTROLE DO VOLUME DA MÚSICA
    # ========================================================

    def set_music_volume(self, volume):
        self.music_volume = self._valid_volume(
            volume,
            self.music_volume
        )

        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(
                self.music_volume
                if self.enabled
                else 0
            )

        self.save_settings()

    # ========================================================
    # CONTROLE DO VOLUME DOS EFEITOS
    # ========================================================

    def set_effects_volume(self, volume):
        self.effects_volume = self._valid_volume(
            volume,
            self.effects_volume
        )

        for sound in self.effects.values():
            sound.set_volume(
                self.effects_volume
                if self.enabled
                else 0
            )

        self.save_settings()

    # ========================================================
    # DESLIGAR O ÁUDIO
    # ========================================================

    def stop_audio(self):
        if not pygame.mixer.get_init():
            return

        pygame.mixer.music.set_volume(0)
        pygame.mixer.stop()

    # ========================================================
    # LIGAR / DESLIGAR O ÁUDIO
    # ========================================================

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        if self.enabled:
            pygame.mixer.music.set_volume(
                self.music_volume
            )

            for sound in self.effects.values():
                sound.set_volume(
                    self.effects_volume
                )

        else:
            self.stop_audio()

        self.save_settings()

    def toggle_audio(self):
        self.set_enabled(not self.enabled)
        return self.enabled
