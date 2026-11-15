
from core.ui import DialogueScreen


class StoryDialogueScreen(DialogueScreen):
    """
    Extends the existing dialogue screen without
    modifying its animations or visual components.

    Standalone puzzles are delegated to the App.
    Legacy puzzles continue using DialogueScreen.
    """

    STANDALONE_PUZZLE_TYPES = {
        "knowledge_quiz",
        "orbital_launch",
        "mars_gravity",
        "mission_leg",
    }

    def __init__(
        self,
        master,
        engine,
        translate,
        on_end,
        on_save,
        on_open_puzzle
    ):
        self.on_open_puzzle = on_open_puzzle

        super().__init__(
            master,
            engine,
            translate,
            on_end=on_end,
            on_save=on_save
        )

    def _show_puzzle(self, puzzle_id):
        puzzle = self.engine.get_puzzle(puzzle_id)

        puzzle_type = puzzle.get("type")

        # Tela própria: tipos conhecidos ou qualquer puzzle com "module"
        # (registrado pelo motor, ex.: Diário de Bordo, Gravidade Marciana)
        if (
            puzzle_type in self.STANDALONE_PUZZLE_TYPES
            or "module" in puzzle
        ):
            self.state = "busy"

            # Schedule the transition after the dialogue
            # screen has finished initializing.
            self.after_idle(
                lambda: self._open_standalone_puzzle(
                    puzzle_id
                )
            )

            return

        # Preserve existing dialogue-based puzzles.
        super()._show_puzzle(puzzle_id)

    def _open_standalone_puzzle(self, puzzle_id):
        if not self.winfo_exists():
            return

        print(
            f"[STORY] Opening standalone puzzle: "
            f"{puzzle_id}"
        )

        self.on_open_puzzle(
            self.engine,
            puzzle_id
        )
