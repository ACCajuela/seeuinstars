
import json
from pathlib import Path


class StoryEngine:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        story_path = (
            project_root / "chapters" / "chapter_01" / "story.json"
        )

        with open(story_path, "r", encoding="utf-8") as file:
            self.story = json.load(file)

        self.scene = self.story["scenes"][self.story["start_scene"]]
        self.dialogue_index = 0
        self.choices = {}


    def next_dialogue(self):
        dialogues = self.scene["dialogues"]

        if self.dialogue_index >= len(dialogues):
            next_scene = self.scene.get("next_scene")

            if next_scene:
                self.change_scene(next_scene)
                return self.next_dialogue()

            return None

        dialogue = dialogues[self.dialogue_index]
        self.dialogue_index += 1

        return dialogue


    def make_choice(self, choice_id):
        self.choices["route"] = choice_id
        self.change_scene(choice_id)
        print(f"Escolha registrada: {choice_id}")


    def change_scene(self, scene_id):
        self.scene = self.story["scenes"][scene_id]
        self.dialogue_index = 0


