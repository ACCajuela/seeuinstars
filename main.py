
import tkinter as tk

from core.audio_manager import AudioManager
from core.engine import StoryEngine
from core.localization_manager import LocalizationManager
from core.save_manager import SaveManager

from core.ui import (
    BG,
    HEIGHT,
    WIDTH,
    AudioSettingsScreen,
    HomeScreen,
    LanguageScreen,
    OptionsScreen,
    load_project_fonts,
)

from screens.intro_screen import IntroScreen
from screens.story_dialogue import StoryDialogueScreen

from puzzles.quiz_screen import QuizScreen
from puzzles.knowledge_quiz import KnowledgeQuiz
from puzzles.orbital_launch_ui import OrbitalLaunchUI
from puzzles.mars_gravity_ui import MarsGravityUI


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        load_project_fonts()

        self.title("ASTRA - A Journey Beyond Earth")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG)

        # ====================================================
        # MANAGERS
        # ====================================================

        self.localization = LocalizationManager("en")
        self.save_manager = SaveManager()
        self.audio_manager = AudioManager()

        self.current = None
        self.active_engine = None

        if self.localization.load_language() is not None:
            self.show_home()
        else:
            self.show_language()

    # ========================================================
    # LOCALIZATION
    # ========================================================

    def t(self, key):
        return self.localization.get(key)

    def current_language(self):
        language = getattr(
            self.localization,
            "current_language",
            None
        )

        if language is None:
            language = getattr(
                self.localization,
                "language",
                "en"
            )

        if language not in ("en", "pt_BR"):
            language = "en"

        return language

    # ========================================================
    # SCREEN MANAGEMENT
    # ========================================================

    def _switch(self, screen):
        if self.current is not None:
            self.current.destroy()

        self.current = screen
        self.current.pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # LANGUAGE
    # ========================================================

    def show_language(self):
        self._switch(
            LanguageScreen(
                self,
                on_choose=self.choose_language
            )
        )

    def choose_language(self, language):
        self.localization.set_language(language)
        self.show_home()

    # ========================================================
    # HOME
    # ========================================================

    def show_home(self):
        self.audio_manager.resume_music()

        self._switch(
            HomeScreen(
                self,
                self.t,
                on_new_game=self.new_game,
                on_continue=self.continue_game,
                on_options=self.show_options,
                on_quit=self.destroy
            )
        )

    # ========================================================
    # OPTIONS
    # ========================================================

    def show_options(self):
        self._switch(
            OptionsScreen(
                self,
                self.t,
                on_audio=self.show_audio_settings,
                on_language=self.show_language,
                on_back=self.show_home
            )
        )

    def show_audio_settings(self):
        self._switch(
            AudioSettingsScreen(
                self,
                self.t,
                on_back=self.show_options
            )
        )

    # ========================================================
    # STORY
    # ========================================================

    def _start(self, engine):
        self.active_engine = engine

        screen = StoryDialogueScreen(
            self,
            engine,
            self.t,
            on_end=self.show_home,
            on_save=self.save_game,
            on_open_puzzle=self.open_puzzle
        )

        self._switch(screen)

    # ========================================================
    # NEW GAME
    # ========================================================

    def new_game(self):
        self.active_engine = None
        self.show_intro()

    # ========================================================
    # INTRODUCTION
    # ========================================================

    def show_intro(self):
        self.audio_manager.pause_music()

        self._switch(
            IntroScreen(
                self,
                on_finish=self.finish_intro
            )
        )

    def finish_intro(self):
        print("[GAME] Introduction finished.")

        engine = StoryEngine(chapter=0)

        self._start(engine)

        self.audio_manager.play_music(
            "background.wav"
        )

        print("[GAME] Chapter 0 started.")

    # ========================================================
    # STANDALONE PUZZLES
    # ========================================================

    def open_puzzle(self, engine, puzzle_id):
        puzzle = engine.get_puzzle(puzzle_id)

        puzzle_type = puzzle.get("type")

        if puzzle_type == "knowledge_quiz":
            self.open_knowledge_quiz(
                engine,
                puzzle_id
            )
            return

        if puzzle_type == "orbital_launch":
            self.open_orbital_launch(
                engine,
                puzzle_id
            )
            return

        if puzzle_type == "mars_gravity":
            self.open_mars_gravity(
                engine,
                puzzle_id
            )
            return

        raise ValueError(
            f"Unsupported standalone puzzle: {puzzle_id}"
        )

    # ========================================================
    # KNOWLEDGE QUIZ
    # ========================================================

    def open_knowledge_quiz(self, engine, puzzle_id):
        print("[GAME] Opening knowledge assessment.")

        quiz = KnowledgeQuiz()

        screen = QuizScreen(
            self,
            quiz=quiz,
            language=self.current_language(),
            on_finish=lambda result: self.finish_puzzle(
                engine,
                puzzle_id,
                result
            )
        )

        self._switch(screen)

    # ========================================================
    # ORBITAL LAUNCH
    # ========================================================

    def open_orbital_launch(self, engine, puzzle_id):
        print("[GAME] Opening orbital launch.")

        screen = OrbitalLaunchUI(
            self,
            language=self.current_language(),
            on_complete=lambda: self.finish_puzzle(
                engine,
                puzzle_id,
                {
                    "completed": True,
                    "status": "stable_orbit"
                }
            ),
            on_back=lambda: self.return_from_puzzle(engine)
        )

        self._switch(screen)

    # ========================================================
    # MARS GRAVITY — CHAPTER 02
    # ========================================================

    def open_mars_gravity(self, engine, puzzle_id):
        print("[GAME] Opening Mars gravity puzzle.")

        screen = MarsGravityUI(
            self,
            language=self.current_language(),
            on_complete=lambda: self.finish_puzzle(
                engine,
                puzzle_id,
                {
                    "completed": True,
                    "status": "rover_reached"
                }
            ),
            on_back=lambda: self.return_from_puzzle(engine)
        )

        self._switch(screen)

    # ========================================================
    # RETURN FROM PUZZLE
    # ========================================================

    def return_from_puzzle(self, engine):
        print("[GAME] Returning to story from puzzle.")

        # The puzzle remains pending.
        # Reopening the story will trigger it again.
        self._start(engine)

    # ========================================================
    # PUZZLE COMPLETION
    # ========================================================

    def finish_puzzle(self, engine, puzzle_id, result):
        print(f"[GAME] Puzzle finished: {puzzle_id}")

        engine.complete_puzzle(
            puzzle_id,
            result=result
        )

        # Return to the same engine, preserving progress.
        self._start(engine)

        print("[GAME] Story resumed.")

    # ========================================================
    # SAVE GAME
    # ========================================================

    def save_game(self, engine):
        self.save_manager.save_game(
            engine,
            self.localization
        )

        print("[GAME] Progress saved.")

    # ========================================================
    # CONTINUE GAME
    # ========================================================

    def continue_game(self):
        engine = StoryEngine(chapter=0)

        loaded = self.save_manager.load_game(
            engine,
            self.localization
        )

        if not loaded:
            print("[GAME] No save available.")
            return

        if (
            not engine.pending_puzzle
            and engine.dialogue_index > 0
        ):
            engine.dialogue_index -= 1

        self._start(engine)

        self.audio_manager.play_music(
            "background.wav"
        )

        print("[GAME] Saved game loaded.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
