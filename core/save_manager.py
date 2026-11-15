
import json
from pathlib import Path

from core.mission import MissionState


class SaveManager:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.save_path = project_root / "save.json"

    def save_game(self, engine, localization):
        data = {
            "language": localization.language,
            "chapter": engine.chapter,
            "scene": self.get_scene_id(engine),
            "dialogue_index": engine.dialogue_index,
            "choices": engine.choices,
            "completed_puzzles": list(engine.completed_puzzles),
            "pending_puzzle": engine.pending_puzzle,
            # Recursos da nave (energia, oxigênio, radiação...)
            "mission": engine.mission.to_dict()
        }

        with open(self.save_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Game saved successfully!")

    def load_game(self, engine, localization):
        if not self.save_path.exists():
            print("No saved game found.")
            return False

        with open(self.save_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        localization.set_language(data["language"])

        # O capítulo precisa ser carregado antes da cena.
        # (Saves antigos não têm "chapter": eram do capítulo 0.)
        chapter = data.get("chapter", 0)
        if chapter != engine.chapter:
            engine.load_chapter(chapter)

        engine.change_scene(data["scene"])
        engine.dialogue_index = data["dialogue_index"]
        engine.choices = data["choices"]
        engine.completed_puzzles = set(data["completed_puzzles"])
        engine.pending_puzzle = data["pending_puzzle"]
        engine.mission = MissionState.from_dict(data.get("mission"))

        print("Game loaded successfully!")
        return True

    def has_save(self):
        return self.save_path.exists()

    def get_scene_id(self, engine):
        if getattr(engine, "scene_id", None):
            return engine.scene_id

        for scene_id, scene_data in engine.story["scenes"].items():
            if scene_data is engine.scene:
                return scene_id

        return engine.story["start_scene"]
