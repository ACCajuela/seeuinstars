
import tkinter as tk
from tkinter import ttk

# Configuração da janela
root = tk.Tk()
root.title("Junior Astronaut - Ada & COSMO")
root.geometry("900x600")
root.configure(bg="#101827")

# Nome do personagem
character_name = tk.Label(
    root,
    text="COSMO",
    font=("Arial", 16, "bold"),
    fg="#8BD3FF",
    bg="#101827"
)
character_name.pack(pady=(40, 10))

# Área de diálogo
dialogue = tk.Label(
    root,
    text="Olá, Ada! Pronta para nossa aventura espacial?",
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
    text="Continuar"
)
next_button.pack(pady=20)

root.mainloop()
