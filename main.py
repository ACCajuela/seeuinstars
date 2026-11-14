import tkinter as tk

from core.engine import StoryEngine
from core.localization_manager import LocalizationManager
from core.save_manager import SaveManager
from core.ui import (
    BG, HEIGHT, WIDTH,
    DialogueScreen, HomeScreen, LanguageScreen, load_project_fonts,
)


class App(tk.Tk):
    def __init__(self):
        load_project_fonts()
        super().__init__()
        self.title("See U in Stars")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.localization = LocalizationManager("en")
        self.save_manager = SaveManager()
        self.current = None

        # Fluxo: escolha de idioma -> home -> jogo
        self.show_language()

    def t(self, key):
        return self.localization.get(key)

    def _switch(self, screen):
        if self.current is not None:
            self.current.destroy()
        self.current = screen
        self.current.pack(fill="both", expand=True)

    def show_language(self):
        self._switch(LanguageScreen(self, on_choose=self.choose_language))

    def choose_language(self, language):
        self.localization.set_language(language)
        self.show_home()

    def show_home(self):
        self._switch(HomeScreen(
            self, self.t,
            on_new_game=self.new_game,
            on_continue=self.continue_game,
            on_options=self.show_language,
            on_quit=self.destroy,
        ))

    def _start(self, engine):
        self._switch(DialogueScreen(
            self, engine, self.t,
            on_end=self.show_home,
            on_save=self.save_game,
        ))

    def new_game(self):
        self._start(StoryEngine())

    def save_game(self, engine):
        self.save_manager.save_game(engine, self.localization)

    def continue_game(self):
        engine = StoryEngine()
        if not self.save_manager.load_game(engine, self.localization):
            return
        # Mostra de novo a fala em que o jogador parou (sem pular para a próxima).
        # Se havia um desafio pendente, o engine já volta direto para ele.
        if not engine.pending_puzzle and engine.dialogue_index > 0:
            engine.dialogue_index -= 1
        self._start(engine)


if __name__ == "__main__":
    App().mainloop()
