
import json
from pathlib import Path


class SaveManager:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.save_path = project_root / "save.json"

    def save_game(self, engine):
        data = {
            "scene": self.get_scene_id(engine),
            "dialogue_index": engine.dialogue_index,
            "choices": engine.choices,
            "completed_puzzles": list(engine.completed_puzzles),
            "pending_puzzle": engine.pending_puzzle
        }

        with open(self.save_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("Jogo salvo com sucesso!")

    def load_game(self, engine):
        if not self.save_path.exists():
            print("Nenhum jogo salvo encontrado.")
            return False

        with open(self.save_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        engine.change_scene(data["scene"])
        engine.dialogue_index = data["dialogue_index"]
        engine.choices = data["choices"]
        engine.completed_puzzles = set(data["completed_puzzles"])
        engine.pending_puzzle = data["pending_puzzle"]

        print("Jogo carregado com sucesso!")
        return True

    def get_scene_id(self, engine):
        for scene_id, scene_data in engine.story["scenes"].items():
            if scene_data is engine.scene:
                return scene_id

        return engine.story["start_scene"]
