
import json
from pathlib import Path


class StoryEngine:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent

        story_path = (
            project_root / "chapters" / "chapter_01" / "story.json"
        )

        puzzles_path = story_path.parent / "puzzles.json"

        # Load story
        with open(story_path, "r", encoding="utf-8") as file:
            self.story = json.load(file)

        # Load puzzles
        with open(puzzles_path, "r", encoding="utf-8") as file:
            self.puzzles = json.load(file)["puzzles"]

        # Story state
        self.scene = self.story["scenes"][self.story["start_scene"]]
        self.dialogue_index = 0
        self.choices = {}

        # Puzzle state
        self.pending_puzzle = None
        self.completed_puzzles = set()

    def next_dialogue(self):
        dialogues = self.scene["dialogues"]

        if self.dialogue_index >= len(dialogues):

            puzzle_id = self.scene.get("puzzle")

            # Block progression until puzzle is completed
            if puzzle_id and puzzle_id not in self.completed_puzzles:
                self.pending_puzzle = puzzle_id

                return {
                    "type": "puzzle",
                    "id": puzzle_id
                }

            # Move to next scene
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

        print(f"Choice registered: {choice_id}")

    def change_scene(self, scene_id):
        self.scene = self.story["scenes"][scene_id]
        self.dialogue_index = 0
        self.pending_puzzle = None

    def get_puzzle(self, puzzle_id):
        return self.puzzles[puzzle_id]

    def answer_puzzle(self, puzzle_id, option_index):
        puzzle = self.get_puzzle(puzzle_id)
        option = puzzle["options"][option_index]

        if option["correct"]:
            self.completed_puzzles.add(puzzle_id)
            self.pending_puzzle = None

            return True, puzzle["success_key"]

        return False, puzzle["failure_key"]
