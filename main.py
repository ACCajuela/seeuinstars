
import tkinter as tk
from tkinter import ttk

from core.engine import StoryEngine

# Inicializa o motor narrativo
engine = StoryEngine()

# Configuração da janela
root = tk.Tk()
root.title("See U in Stars")
root.geometry("900x600")
root.configure(bg="#101827")


def next_dialogue():
    dialogue_data = engine.next_dialogue()

    if dialogue_data is None:
        character_name.config(text="")
        dialogue.config(text="Fim do capítulo 1!")
        next_button.config(state="disabled")
        return

    character_name.config(text=dialogue_data["speaker"])
    dialogue.config(text=dialogue_data["text"])


# Nome do personagem
character_name = tk.Label(
    root,
    text="",
    font=("Arial", 16, "bold"),
    fg="#8BD3FF",
    bg="#101827"
)
character_name.pack(pady=(40, 10))

# Área de diálogo
dialogue = tk.Label(
    root,
    text="",
    font=("Arial", 15),
    fg="white",
    bg="#101827",
    wraplength=750,
    justify="center"
)
dialogue.pack(pady=20)

# Botão de avançar
next_button = ttk.Button(
    root,
    text="Continuar",
    command=next_dialogue
)
next_button.pack(pady=20)

# Exibe o primeiro diálogo automaticamente
next_dialogue()

root.mainloop()
