
import json
from pathlib import Path


class LocalizationManager:
    def __init__(self, language="en"):
        self.project_root = Path(__file__).resolve().parent.parent

        self.locales_path = self.project_root / "locales"
        self.settings_file = self.project_root / "settings.json"

        self.language = None
        self.translations = {}

        # Recupera o idioma salvo, se existir.
        saved_language = self.load_language()

        self.set_language(
            saved_language or language,
            save=False
        )

    # ========================================================
    # PERSISTÊNCIA DO IDIOMA
    # ========================================================

    def load_language(self):
        if not self.settings_file.exists():
            return None

        try:
            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as file:
                settings = json.load(file)

            language = settings.get("language")

            if language in ("en", "pt_BR"):
                return language

        except (OSError, ValueError, TypeError) as error:
            print(f"Could not load language settings: {error}")

        return None

    def save_language(self):
        # Preserva as configurações de áudio já existentes.
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

        settings["language"] = self.language

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
            print(f"Could not save language settings: {error}")

    # ========================================================
    # TRADUÇÕES
    # ========================================================

    def set_language(self, language, save=True):
        if language not in ("en", "pt_BR"):
            raise ValueError(
                f"Unsupported language: {language}"
            )

        file_path = self.locales_path / f"{language}.json"

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            translations = json.load(file)

        self.translations = translations
        self.language = language

        if save:
            self.save_language()

    def get(self, key):
        value = self.translations

        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return f"[{key}]"

            value = value[part]

        return value
