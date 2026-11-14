
import tkinter as tk
from tkinter import ttk

from core.engine import StoryEngine
from core.localization_manager import LocalizationManager
from core.save_manager import SaveManager


# Initialize game systems
engine = StoryEngine()
localization = LocalizationManager("en")
save_manager = SaveManager()


# Main window
root = tk.Tk()
root.title("See U in Stars")
root.geometry("900x600")
root.configure(bg="#101827")


def clear_choices():
    for widget in choices_frame.winfo_children():
        widget.destroy()


def choose_language(language):
    localization.set_language(language)

    language_frame.pack_forget()
    game_frame.pack(fill="both", expand=True)

    next_button.config(
        text=localization.get("ui.continue")
    )

    next_dialogue()


def next_dialogue():
    clear_choices()
    feedback.config(text="")

    dialogue_data = engine.next_dialogue()

    # End of chapter
    if dialogue_data is None:
        character_name.config(text="")
        dialogue.config(
            text=localization.get("ui.chapter_end")
        )
        next_button.pack_forget()
        return

    # Puzzle event
    if dialogue_data.get("type") == "puzzle":
        show_puzzle(dialogue_data["id"])
        return

    # Display dialogue
    character_name.config(
        text=dialogue_data["speaker"]
    )

    dialogue.config(
        text=localization.get(dialogue_data["text_key"])
    )

    # Display choices
    if "choices" in dialogue_data:
        next_button.pack_forget()

        for choice in dialogue_data["choices"]:
            ttk.Button(
                choices_frame,
                text=localization.get(choice["text_key"]),
                command=lambda choice_id=choice["id"]: select_choice(choice_id)
            ).pack(pady=5)

    else:
        next_button.pack(pady=20)


def select_choice(choice_id):
    engine.make_choice(choice_id)
    next_dialogue()


def show_puzzle(puzzle_id):
    puzzle = engine.get_puzzle(puzzle_id)

    character_name.config(
        text=localization.get("ui.challenge")
    )

    dialogue.config(
        text=localization.get(puzzle["question_key"])
    )

    next_button.pack_forget()

    for index, option in enumerate(puzzle["options"]):
        ttk.Button(
            choices_frame,
            text=localization.get(option["text_key"]),
            command=lambda i=index: answer_puzzle(puzzle_id, i)
        ).pack(pady=5)


def answer_puzzle(puzzle_id, option_index):
    correct, message_key = engine.answer_puzzle(
        puzzle_id,
        option_index
    )

    feedback.config(
        text=localization.get(message_key)
    )

    if correct:
        clear_choices()
        next_button.pack(pady=20)


def save_game():
    save_manager.save_game(engine, localization)
    print("Progress saved!")


def load_game():
    if not save_manager.load_game(engine, localization):
        return

    language_frame.pack_forget()
    game_frame.pack(fill="both", expand=True)

    next_button.config(text=localization.get("ui.continue"))

    clear_choices()
    feedback.config(text="")

    if engine.pending_puzzle:
        show_puzzle(engine.pending_puzzle)
    else:
        # Restore the current scene without advancing
        if engine.dialogue_index > 0:
            engine.dialogue_index -= 1

        next_dialogue()



# ==========================================
# LANGUAGE SELECTION SCREEN
# ==========================================

language_frame = tk.Frame(
    root,
    bg="#101827"
)

language_frame.pack(
    fill="both",
    expand=True
)

tk.Label(
    language_frame,
    text="SEE U IN STARS",
    font=("Arial", 28, "bold"),
    fg="#8BD3FF",
    bg="#101827"
).pack(pady=(110, 25))

tk.Label(
    language_frame,
    text="Choose your language / Escolha seu idioma",
    font=("Arial", 15),
    fg="white",
    bg="#101827"
).pack(pady=15)

ttk.Button(
    language_frame,
    text="Português (Brasil)",
    command=lambda: choose_language("pt_BR")
).pack(pady=10)

ttk.Button(
    language_frame,
    text="English",
    command=lambda: choose_language("en")
).pack(pady=10)

if save_manager.has_save():
    ttk.Button(
        language_frame,
        text="Continue Game / Continuar jogo",
        command=load_game
    ).pack(pady=20)


# ==========================================
# GAME SCREEN
# ==========================================

game_frame = tk.Frame(
    root,
    bg="#101827"
)

# Character name
character_name = tk.Label(
    game_frame,
    text="",
    font=("Arial", 16, "bold"),
    fg="#8BD3FF",
    bg="#101827"
)

character_name.pack(pady=(40, 10))


# Dialogue text
dialogue = tk.Label(
    game_frame,
    text="",
    font=("Arial", 15),
    fg="white",
    bg="#101827",
    wraplength=750,
    justify="center"
)

dialogue.pack(pady=20)


# Choices container
choices_frame = tk.Frame(
    game_frame,
    bg="#101827"
)

choices_frame.pack(pady=10)


# Puzzle feedback
feedback = tk.Label(
    game_frame,
    text="",
    font=("Arial", 13),
    fg="#FFD166",
    bg="#101827",
    wraplength=750
)

feedback.pack(pady=10)


# Save and load buttons
save_frame = tk.Frame(game_frame, bg="#101827")
save_frame.pack(pady=15)

ttk.Button(
    save_frame,
    text="Save Game / Salvar jogo",
    command=save_game
).pack(side="left", padx=10)

ttk.Button(
    save_frame,
    text="Load Game / Carregar jogo",
    command=load_game
).pack(side="left", padx=10)


# Continue button
next_button = ttk.Button(
    game_frame,
    text="Continue",
    command=next_dialogue
)


# Start application
root.mainloop()
