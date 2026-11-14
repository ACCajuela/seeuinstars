import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

# Permite rodar tanto "python core/main.py" quanto "python -m core.main"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.ui import BG, HEIGHT, WIDTH, DialogueScreen, HomeScreen, load_project_fonts


class App(tk.Tk):
    def __init__(self):
        load_project_fonts()
        super().__init__()
        self.title("Junior Astronaut - Ada & COSMO")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.current = None
        self.show_home()

    def _switch(self, screen):
        if self.current is not None:
            self.current.destroy()
        self.current = screen
        self.current.pack(fill="both", expand=True)

    def show_home(self):
        self._switch(HomeScreen(
            self,
            on_new_game=self.new_game,
            on_continue=self.continue_game,
            on_options=self.options,
            on_quit=self.destroy,
        ))

    def new_game(self):
        self._switch(DialogueScreen(
            self, "COSMO", "Olá, Ada! Pronta para nossa aventura espacial?",
            on_next=self.show_home,
        ))

    def continue_game(self):
        messagebox.showinfo("Continuar", "Carregar jogo salvo: em breve!")

    def options(self):
        messagebox.showinfo("Opções", "Volume, idioma etc.: em breve!")


if __name__ == "__main__":
    App().mainloop()
