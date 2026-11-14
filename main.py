
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

    # Remove escolhas anteriores
    for widget in choices_frame.winfo_children():
        widget.destroy()

    # Verifica se o diálogo possui escolhas
    if "choices" in dialogue_data:
        next_button.pack_forget()

        for choice in dialogue_data["choices"]:
            ttk.Button(
                choices_frame,
                text=choice["text"],
                command=lambda choice_id=choice["id"]: select_choice(choice_id)
            ).pack(pady=5)
    else:
        next_button.pack(pady=20)


def select_choice(choice_id):
    engine.make_choice(choice_id)
    next_button.pack(pady=20)
    next_dialogue()



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

choices_frame = tk.Frame(root, bg="#101827")
choices_frame.pack(pady=10)

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
