
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

    def next_dialogue(self):
        dialogues = self.scene["dialogues"]

        if self.dialogue_index >= len(dialogues):
            return None

        dialogue = dialogues[self.dialogue_index]
        self.dialogue_index += 1

        return dialogue
