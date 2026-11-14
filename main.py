
import tkinter as tk

from core.engine import StoryEngine
from core.localization_manager import LocalizationManager
from core.save_manager import SaveManager

from core.ui import (
    BG,
    HEIGHT,
    WIDTH,
    AudioSettingsScreen,
    DialogueScreen,
    HomeScreen,
    LanguageScreen,
    OptionsScreen,
    load_project_fonts,
)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        load_project_fonts()

        self.title("See U in Stars")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Gerenciadores
        self.localization = LocalizationManager("en")
        self.save_manager = SaveManager()

        self.current = None

        # Se já existe idioma salvo, abre a Home.
        # Caso contrário, solicita a escolha do idioma.
        if self.localization.load_language() is not None:
            self.show_home()
        else:
            self.show_language()

    # ========================================================
    # TRADUÇÕES
    # ========================================================

    def t(self, key):
        return self.localization.get(key)

    # ========================================================
    # GERENCIAMENTO DE TELAS
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
    # IDIOMA
    # ========================================================

    def show_language(self):
        self._switch(
            LanguageScreen(
                self,
                on_choose=self.choose_language
            )
        )

    def choose_language(self, language):
        # set_language também salva o idioma no settings.json
        self.localization.set_language(language)

        self.show_home()

    # ========================================================
    # MENU PRINCIPAL
    # ========================================================

    def show_home(self):
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
    # OPÇÕES
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

    # ========================================================
    # CONFIGURAÇÕES DE ÁUDIO
    # ========================================================

    def show_audio_settings(self):
        self._switch(
            AudioSettingsScreen(
                self,
                self.t,
                on_back=self.show_options
            )
        )

    # ========================================================
    # INICIAR JOGO
    # ========================================================

    def _start(self, engine):
        self._switch(
            DialogueScreen(
                self,
                engine,
                self.t,
                on_end=self.show_home,
                on_save=self.save_game
            )
        )

    def new_game(self):
        self._start(StoryEngine())

    # ========================================================
    # SALVAR PROGRESSO
    # ========================================================

    def save_game(self, engine):
        self.save_manager.save_game(
            engine,
            self.localization
        )

    # ========================================================
    # CONTINUAR JOGO
    # ========================================================

    def continue_game(self):
        engine = StoryEngine()

        if not self.save_manager.load_game(
            engine,
            self.localization
        ):
            return

        # Restaura o diálogo atual
        if (
            not engine.pending_puzzle
            and engine.dialogue_index > 0
        ):
            engine.dialogue_index -= 1

        self._start(engine)


if __name__ == "__main__":
    app = App()
    app.mainloop()
