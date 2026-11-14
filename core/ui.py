
import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from core.audio_manager import AudioManager


PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"

BACKGROUND_IMAGE = IMAGES_DIR / "fundo-home.png"
SAVE_FILE = PROJECT_ROOT / "save.json"

WIDTH, HEIGHT = 900, 600

# Menu positioning
MENU_X, MENU_Y, MENU_GAP = 650, 225, 65

# Title positioning
TITLE_FONT = "Sunborn Sans One"
TITLE_X, TITLE_Y = 250, 200
TITLE_SIZE, SUBTITLE_SIZE = 80, 16

SHADOW_COLOR = "#2B1208"
SHADOW_X, SHADOW_Y = 1, 1

# Color palette
BG = "#101827"
TITLE = "#FFFFFF"
ACCENT = "#8BD3FF"
BUTTON_BG = "#1E2A44"
BUTTON_HOVER = "#2C3E66"
BUTTON_BORDER = "#8BD3FF"
BUTTON_DISABLED = "#4A5568"

audio_manager = AudioManager()


def load_project_fonts():
    """Register project fonts on Windows."""
    if sys.platform != "win32" or not FONTS_DIR.exists():
        return

    import ctypes

    FR_PRIVATE = 0x10

    font_files = (
        list(FONTS_DIR.glob("*.ttf"))
        + list(FONTS_DIR.glob("*.otf"))
    )

    for font_file in font_files:
        ctypes.windll.gdi32.AddFontResourceExW(
            str(font_file), FR_PRIVATE, 0
        )


def font_or_fallback(family, fallback="Arial"):
    if family in tkfont.families():
        return family
    return fallback


class MenuButton:
    """Rounded Canvas button with hover and sound."""

    def __init__(
        self, canvas, x, y, text, command,
        width=260, height=52, enabled=True
    ):
        self.canvas = canvas
        self.command = command
        self.enabled = enabled

        tag = f"btn_{id(self)}"

        x0 = x - width // 2
        y0 = y - height // 2
        x1 = x + width // 2
        y1 = y + height // 2

        self.shape = self._rounded_rect(
            x0, y0, x1, y1, r=18, tag=tag
        )

        self.label = canvas.create_text(
            x, y,
            text=text,
            font=("Arial", 15, "bold"),
            tags=tag
        )

        self._paint(BUTTON_BG)

        if enabled:
            canvas.tag_bind(
                tag, "<Enter>",
                lambda event: self._hover(True)
            )

            canvas.tag_bind(
                tag, "<Leave>",
                lambda event: self._hover(False)
            )

            canvas.tag_bind(
                tag, "<Button-1>",
                lambda event: self._click()
            )

    def _rounded_rect(self, x0, y0, x1, y1, r, tag):
        points = [
            x0 + r, y0,
            x1 - r, y0,
            x1, y0,
            x1, y0 + r,
            x1, y1 - r,
            x1, y1,
            x1 - r, y1,
            x0 + r, y1,
            x0, y1,
            x0, y1 - r,
            x0, y0 + r,
            x0, y0
        ]

        return self.canvas.create_polygon(
            points,
            smooth=True,
            width=2,
            tags=tag
        )

    def _paint(self, fill):
        border = (
            BUTTON_BORDER if self.enabled
            else BUTTON_DISABLED
        )

        text_color = (
            TITLE if self.enabled
            else BUTTON_DISABLED
        )

        self.canvas.itemconfigure(
            self.shape,
            fill=fill,
            outline=border
        )

        self.canvas.itemconfigure(
            self.label,
            fill=text_color
        )

    def _hover(self, inside):
        self._paint(
            BUTTON_HOVER if inside else BUTTON_BG
        )

        self.canvas.configure(
            cursor="hand2" if inside else ""
        )

    def _click(self):
        if not self.enabled:
            return

        audio_manager.play_effect("click.wav")
        self.command()


class TitleScreen(tk.Frame):
    """Base screen with background and title."""

    def __init__(self, master):
        super().__init__(master, bg=BG)

        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self._draw_background()
        self._draw_title()

    def _draw_title(self):
        family = font_or_fallback(TITLE_FONT)

        lines = [
            ("ASTRA", TITLE_SIZE, TITLE_Y),
            (
                "A JOURNEY BEYOND EARTH",
                SUBTITLE_SIZE,
                TITLE_Y + TITLE_SIZE // 2 + 30
            )
        ]

        for text, size, y in lines:
            if SHADOW_X or SHADOW_Y:
                self.canvas.create_text(
                    TITLE_X + SHADOW_X,
                    y + SHADOW_Y,
                    text=text,
                    font=(family, size),
                    fill=SHADOW_COLOR
                )

            self.canvas.create_text(
                TITLE_X,
                y,
                text=text,
                font=(family, size),
                fill=TITLE
            )

    def _draw_background(self):
        if not BACKGROUND_IMAGE.exists():
            return

        img = tk.PhotoImage(
            file=str(BACKGROUND_IMAGE)
        )

        factor = max(
            1,
            img.width() // WIDTH,
            img.height() // HEIGHT
        )

        if factor > 1:
            img = img.subsample(factor)

        self.background_img = img

        self.canvas.create_image(
            WIDTH // 2,
            HEIGHT // 2,
            image=img
        )


class HomeScreen(TitleScreen):
    """Main menu with bilingual sound control."""

    def __init__(
        self, master, t,
        on_new_game, on_continue,
        on_options, on_quit
    ):
        super().__init__(master)

        x, y, gap = MENU_X, MENU_Y, MENU_GAP

        has_save = SAVE_FILE.exists()

        MenuButton(
            self.canvas,
            x, y,
            t("ui.new_game"),
            on_new_game
        )

        MenuButton(
            self.canvas,
            x, y + gap,
            t("ui.continue"),
            on_continue,
            enabled=has_save
        )

        MenuButton(
            self.canvas,
            x, y + gap * 2,
            t("ui.options"),
            on_options
        )

        MenuButton(
            self.canvas,
            x, y + gap * 3,
            t("ui.quit"),
            on_quit
        )

        # Bilingual sound button
        sound_key = (
            "ui.sound_on"
            if audio_manager.enabled
            else "ui.sound_off"
        )

        sound_button = MenuButton(
            self.canvas,
            x,
            y + gap * 4,
            t(sound_key),
            lambda: None
        )

        def toggle_and_update():
            audio_manager.toggle_audio()

            key = (
                "ui.sound_on"
                if audio_manager.enabled
                else "ui.sound_off"
            )

            self.canvas.itemconfigure(
                sound_button.label,
                text=t(key)
            )

        sound_button.command = toggle_and_update


class LanguageScreen(TitleScreen):
    """Language selection screen."""

    def __init__(self, master, on_choose):
        super().__init__(master)

        x, y = MENU_X, MENU_Y

        self.canvas.create_text(
            x,
            y - 60,
            text="Choose your language\nEscolha seu idioma",
            font=("Arial", 14, "bold"),
            fill=TITLE,
            justify="center"
        )

        MenuButton(
            self.canvas,
            x,
            y + 20,
            "Português (Brasil)",
            lambda: on_choose("pt_BR")
        )

        MenuButton(
            self.canvas,
            x,
            y + 20 + MENU_GAP,
            "English",
            lambda: on_choose("en")
        )


def _flat_button(master, text, command):
    """Standard button with click sound."""

    def play_and_execute():
        audio_manager.play_effect("click.wav")
        command()

    return tk.Button(
        master,
        text=text,
        command=play_and_execute,
        font=("Arial", 13),
        bg=BUTTON_BG,
        fg="white",
        activebackground=BUTTON_HOVER,
        activeforeground="white",
        relief="flat",
        padx=20,
        pady=6,
        cursor="hand2"
    )


class DialogueScreen(tk.Frame):
    """Dialogue, choices and puzzle interface."""

    def __init__(
        self, master, engine, t,
        on_end, on_save
    ):
        super().__init__(master, bg=BG)

        self.engine = engine
        self.t = t
        self.on_end = on_end
        self.on_save = on_save

        # Bottom toolbar
        bar = tk.Frame(self, bg=BG)
        bar.pack(side="bottom", pady=20)

        _flat_button(
            bar,
            t("ui.save"),
            self.save
        ).pack(side="left", padx=8)

        _flat_button(
            bar,
            t("ui.menu"),
            on_end
        ).pack(side="left", padx=8)

        # Character name
        self.speaker = tk.Label(
            self,
            font=("Arial", 16, "bold"),
            fg=ACCENT,
            bg=BG
        )

        self.speaker.pack(pady=(40, 10))

        # Dialogue text
        self.text = tk.Label(
            self,
            font=("Arial", 15),
            fg="white",
            bg=BG,
            wraplength=750,
            justify="center"
        )

        self.text.pack(pady=20)

        # Choice buttons
        self.choices_frame = tk.Frame(
            self,
            bg=BG
        )

        self.choices_frame.pack(pady=10)

        # Puzzle feedback
        self.feedback = tk.Label(
            self,
            font=("Arial", 13),
            fg="#FFD166",
            bg=BG,
            wraplength=750
        )

        self.feedback.pack(pady=10)

        # Continue button
        self.next_button = _flat_button(
            self,
            t("ui.continue"),
            self.next_dialogue
        )

        # Restore pending puzzle directly
        if self.engine.pending_puzzle:
            self.show_puzzle(
                self.engine.pending_puzzle
            )
        else:
            self.next_dialogue()

    def save(self):
        self.on_save(self.engine)

        self.feedback.config(
            text=self.t("ui.saved")
        )

    def _clear_choices(self):
        for widget in self.choices_frame.winfo_children():
            widget.destroy()

    def next_dialogue(self):
        self._clear_choices()
        self.feedback.config(text="")

        data = self.engine.next_dialogue()

        # End of chapter
        if data is None:
            self.speaker.config(text="")

            self.text.config(
                text=self.t("ui.chapter_end")
            )

            self.next_button.config(
                text=self.t("ui.back_to_menu"),
                command=self.on_end
            )

            self.next_button.pack(pady=20)
            return

        # Puzzle
        if data.get("type") == "puzzle":
            self.show_puzzle(data["id"])
            return

        # Dialogue
        self.speaker.config(
            text=data["speaker"]
        )

        self.text.config(
            text=self.t(data["text_key"])
        )

        if "choices" in data:
            self.next_button.pack_forget()

            for choice in data["choices"]:
                _flat_button(
                    self.choices_frame,
                    self.t(choice["text_key"]),
                    lambda choice_id=choice["id"]:
                        self.select_choice(choice_id)
                ).pack(pady=5)

        else:
            self.next_button.pack(pady=20)

    def select_choice(self, choice_id):
        self.engine.make_choice(choice_id)
        self.next_dialogue()

    def show_puzzle(self, puzzle_id):
        self._clear_choices()

        puzzle = self.engine.get_puzzle(puzzle_id)

        self.speaker.config(
            text=self.t("ui.challenge")
        )

        self.text.config(
            text=self.t(puzzle["question_key"])
        )

        self.next_button.pack_forget()

        for index, option in enumerate(puzzle["options"]):
            _flat_button(
                self.choices_frame,
                self.t(option["text_key"]),
                lambda i=index:
                    self.answer_puzzle(puzzle_id, i)
            ).pack(pady=5)

    def answer_puzzle(self, puzzle_id, option_index):
        correct, message_key = self.engine.answer_puzzle(
            puzzle_id,
            option_index
        )

        if correct:
            audio_manager.play_effect("correct.wav")
        else:
            audio_manager.play_effect("wrong.wav")

        self.feedback.config(
            text=self.t(message_key)
        )

        if correct:
            self._clear_choices()
            self.next_button.pack(pady=20)
