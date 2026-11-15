
import json
from pathlib import Path

from core.mission import LEGS, MissionState


class StoryEngine:

    KNOWLEDGE_ASSESSMENT = "knowledge_assessment"
    ORBITAL_LAUNCH = "orbital_launch"

    # Minigames com tela própria. Se uma cena do story.json pedir um
    # destes ids em "puzzle", ele é registrado automaticamente.
    STANDALONE_PUZZLES = {
        "orbital_launch": "puzzles.orbital_launch_ui",
        "mars_gravity": "puzzles.mars_gravity_ui",
        "mission_report": "screens.mission_report",
    }

    def __init__(self, chapter=0):
        self.project_root = Path(__file__).resolve().parent.parent

        # Estado da nave (energia, oxigênio, blindagem, radiação).
        # Dura o jogo inteiro: não é reiniciado ao trocar de capítulo.
        self.mission = MissionState()

        self.chapter = chapter
        self.story = {}
        self.puzzles = {}

        self.scene = None
        self.scene_id = None
        self.dialogue_index = 0
        self.choices = {}

        self.pending_puzzle = None
        self.completed_puzzles = set()
        self.puzzle_results = {}

        self.load_chapter(chapter)

    # ========================================================
    # CHAPTERS
    # ========================================================

    def chapter_folder(self, chapter):
        return (
            self.project_root
            / "chapters"
            / f"chapter_{chapter:02d}"
        )

    def chapter_exists(self, chapter):
        return (
            self.chapter_folder(chapter) / "story.json"
        ).exists()

    def load_chapter(self, chapter):
        folder = self.chapter_folder(chapter)

        story_path = folder / "story.json"
        puzzles_path = folder / "puzzles.json"

        if not story_path.exists():
            raise FileNotFoundError(
                f"Story file not found: {story_path}"
            )

        with open(
            story_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.story = json.load(file)

        if puzzles_path.exists():
            with open(
                puzzles_path,
                "r",
                encoding="utf-8"
            ) as file:
                puzzle_data = json.load(file)

            self.puzzles = puzzle_data.get("puzzles", {})
        else:
            self.puzzles = {}

        self.chapter = chapter

        # Chapter 0: standalone knowledge assessment.
        if chapter == 0:
            self.puzzles[self.KNOWLEDGE_ASSESSMENT] = {
                "type": "knowledge_quiz",
                "module": "puzzles.quiz_screen"
            }

            assessment = self.story["scenes"].get("assessment")

            if assessment is not None:
                assessment["puzzle"] = (
                    self.KNOWLEDGE_ASSESSMENT
                )

        # Chapter 1: standalone orbital launch simulation.
        if chapter == 1:
            self.puzzles[self.ORBITAL_LAUNCH] = {
                "type": "orbital_launch",
                "module": "puzzles.orbital_launch_ui"
            }

            launch_scene = self.story["scenes"].get("launch")

            if launch_scene is not None:
                launch_scene["puzzle"] = (
                    self.ORBITAL_LAUNCH
                )

        # Registra os minigames com tela própria pedidos pelas cenas
        # (ex.: "puzzle": "mars_gravity" no capítulo 2).
        for scene in self.story["scenes"].values():
            puzzle_id = scene.get("puzzle")
            if (
                puzzle_id in self.STANDALONE_PUZZLES
                and puzzle_id not in self.puzzles
            ):
                self.puzzles[puzzle_id] = {
                    "type": puzzle_id,
                    "module": self.STANDALONE_PUZZLES[puzzle_id]
                }

            # Trechos de viagem (Diário de Bordo), ex.: travel_earth_mars
            if puzzle_id in LEGS and puzzle_id not in self.puzzles:
                self.puzzles[puzzle_id] = {
                    "type": "mission_leg",
                    "module": "screens.mission_log"
                }

        start_scene = self.story["start_scene"]

        self.scene_id = start_scene
        self.scene = self.story["scenes"][start_scene]

        self.dialogue_index = 0
        self.choices = {}
        self.pending_puzzle = None
        self.completed_puzzles = set()
        self.puzzle_results = {}

        print(f"[ENGINE] Chapter loaded: {chapter}")
        print(f"[ENGINE] Start scene: {start_scene}")
        print(f"[ENGINE] Puzzles loaded: {len(self.puzzles)}")

    # ========================================================
    # DIALOGUES
    # ========================================================

    def next_dialogue(self):
        # A pending puzzle must be completed before
        # advancing the story.
        if self.pending_puzzle:
            return {
                "type": "puzzle",
                "id": self.pending_puzzle
            }

        dialogues = self.scene.get("dialogues", [])

        if self.dialogue_index < len(dialogues):
            dialogue = dialogues[self.dialogue_index]
            self.dialogue_index += 1
            return dialogue

        puzzle_id = self.scene.get("puzzle")

        if (
            puzzle_id
            and puzzle_id not in self.completed_puzzles
        ):
            if puzzle_id not in self.puzzles:
                raise KeyError(
                    f"Puzzle not found: {puzzle_id}"
                )

            self.pending_puzzle = puzzle_id

            print(f"[ENGINE] Puzzle triggered: {puzzle_id}")

            return {
                "type": "puzzle",
                "id": puzzle_id
            }

        next_scene = self.scene.get("next_scene")

        if next_scene:
            self.change_scene(next_scene)
            return self.next_dialogue()

        # Chapter finished. Continue to the next chapter
        # if its story file exists.
        next_chapter = self.chapter + 1

        if self.chapter_exists(next_chapter):
            print(
                f"[ENGINE] Chapter {self.chapter} completed."
            )

            self.load_chapter(next_chapter)
            return self.next_dialogue()

        print(
            f"[ENGINE] End of available story: "
            f"chapter {self.chapter}"
        )

        return None

    # ========================================================
    # CHOICES
    # ========================================================

    def make_choice(self, choice_id):
        self.choices["route"] = choice_id
        self.change_scene(choice_id)

        print(f"[ENGINE] Choice registered: {choice_id}")

    # ========================================================
    # SCENES
    # ========================================================

    def change_scene(self, scene_id):
        if scene_id not in self.story["scenes"]:
            raise KeyError(
                f"Scene not found: {scene_id}"
            )

        self.scene_id = scene_id
        self.scene = self.story["scenes"][scene_id]

        self.dialogue_index = 0
        self.pending_puzzle = None

        print(f"[ENGINE] Scene changed: {scene_id}")

    # ========================================================
    # PUZZLES
    # ========================================================

    def get_puzzle(self, puzzle_id):
        if puzzle_id not in self.puzzles:
            raise KeyError(
                f"Puzzle not found: {puzzle_id}"
            )

        return self.puzzles[puzzle_id]

    def complete_puzzle(self, puzzle_id, result=None):
        if puzzle_id not in self.puzzles:
            raise KeyError(
                f"Puzzle not found: {puzzle_id}"
            )

        self.completed_puzzles.add(puzzle_id)
        self.pending_puzzle = None

        if result is not None:
            self.puzzle_results[puzzle_id] = result

            # Consequências do minigame nos recursos da nave,
            # ex.: {"effects": {"energy": -1, "oxygen": +2}}
            self.mission.apply_effects(result.get("effects"))
            if "effects" in result:
                self.mission.record_minigame(puzzle_id, result["effects"])

        print(f"[ENGINE] Puzzle completed: {puzzle_id}")

        if result is not None:
            print(f"[ENGINE] Result: {result}")

    def answer_puzzle(self, puzzle_id, option_index):
        puzzle = self.get_puzzle(puzzle_id)

        if puzzle.get("type") in (
            "knowledge_quiz",
            "orbital_launch"
        ):
            raise ValueError(
                "This puzzle must be completed "
                "through its dedicated interface."
            )

        options = puzzle.get("options", [])

        if not 0 <= option_index < len(options):
            raise IndexError(
                f"Invalid option index: {option_index}"
            )

        option = options[option_index]

        if option["correct"]:
            self.complete_puzzle(puzzle_id)
            return True, puzzle["success_key"]

        return False, puzzle["failure_key"]
