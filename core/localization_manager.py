
import json
from pathlib import Path


class LocalizationManager:
    def __init__(self, language="en"):
        self.locales_path = (
            Path(__file__).resolve().parent.parent / "locales"
        )
        self.language = None
        self.translations = {}

        self.set_language(language)

    def set_language(self, language):
        if language not in ("en", "pt_BR"):
            raise ValueError(f"Unsupported language: {language}")

        file_path = self.locales_path / f"{language}.json"

        with open(file_path, "r", encoding="utf-8") as file:
            self.translations = json.load(file)

        self.language = language

    def get(self, key):
        value = self.translations

        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return f"[{key}]"

            value = value[part]

        return value
