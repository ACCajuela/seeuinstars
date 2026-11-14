import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"
BACKGROUND_IMAGE = IMAGES_DIR / "fundo-home.png"
SAVE_FILE = PROJECT_ROOT / "saves" / "save.json"

WIDTH, HEIGHT = 900, 600

# Posição dos botões na home (centro do primeiro botão e espaço entre eles)
MENU_X, MENU_Y, MENU_GAP = 650, 250, 72

# Título do jogo (centro do texto "ASTRA"; o subtítulo fica logo abaixo)
TITLE_FONT = "Sunborn Sans One"
TITLE_X, TITLE_Y = 250, 200
TITLE_SIZE, SUBTITLE_SIZE = 80, 16

# Sombra do título: cor e deslocamento em pixels (x para a direita, y para baixo)
# Use SHADOW_X, SHADOW_Y = 0, 0 para tirar a sombra
SHADOW_COLOR = "#2B1208"
SHADOW_X, SHADOW_Y = 1, 1


def load_project_fonts():
    """Registra as fontes .ttf/.otf de assets/fonts só para o jogo (Windows),
    sem precisar instalar no computador. Chamar antes de criar a janela."""
    if sys.platform != "win32" or not FONTS_DIR.exists():
        return
    import ctypes
    FR_PRIVATE = 0x10
    for font_file in list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf")):
        ctypes.windll.gdi32.AddFontResourceExW(str(font_file), FR_PRIVATE, 0)


def font_or_fallback(family, fallback="Arial"):
    """Usa a fonte pedida se ela existir; senão, usa a fonte reserva."""
    return family if family in tkfont.families() else fallback

# Paleta
BG = "#101827"
TITLE = "#FFFFFF"
ACCENT = "#8BD3FF"
BUTTON_BG = "#1E2A44"
BUTTON_HOVER = "#2C3E66"
BUTTON_BORDER = "#8BD3FF"
BUTTON_DISABLED = "#4A5568"


class MenuButton:
    """Botão arredondado desenhado no Canvas, com efeito de hover."""

    def __init__(self, canvas, x, y, text, command, width=260, height=52, enabled=True):
        self.canvas = canvas
        self.command = command
        self.enabled = enabled
        tag = f"btn_{id(self)}"

        x0, y0 = x - width // 2, y - height // 2
        x1, y1 = x + width // 2, y + height // 2
        self.shape = self._rounded_rect(x0, y0, x1, y1, r=18, tag=tag)
        self.label = canvas.create_text(
            x, y, text=text, font=("Arial", 15, "bold"), tags=tag
        )
        self._paint(BUTTON_BG)

        if enabled:
            canvas.tag_bind(tag, "<Enter>", lambda e: self._hover(True))
            canvas.tag_bind(tag, "<Leave>", lambda e: self._hover(False))
            canvas.tag_bind(tag, "<Button-1>", lambda e: self.command())

    def _rounded_rect(self, x0, y0, x1, y1, r, tag):
        points = [
            x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
            x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
            x0, y1, x0, y1 - r, x0, y0 + r, x0, y0,
        ]
        return self.canvas.create_polygon(points, smooth=True, width=2, tags=tag)

    def _paint(self, fill):
        border = BUTTON_BORDER if self.enabled else BUTTON_DISABLED
        text = TITLE if self.enabled else BUTTON_DISABLED
        self.canvas.itemconfigure(self.shape, fill=fill, outline=border)
        self.canvas.itemconfigure(self.label, fill=text)

    def _hover(self, inside):
        self._paint(BUTTON_HOVER if inside else BUTTON_BG)
        self.canvas.configure(cursor="hand2" if inside else "")


class HomeScreen(tk.Frame):
    """Tela inicial: imagem de fundo com os botões do menu por cima."""

    def __init__(self, master, on_new_game, on_continue, on_options, on_quit):
        super().__init__(master, bg=BG)
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._draw_background()
        self._draw_title()
        self._draw_menu(on_new_game, on_continue, on_options, on_quit)

    def _draw_title(self):
        family = font_or_fallback(TITLE_FONT)
        lines = [
            ("ASTRA", TITLE_SIZE, TITLE_Y),
            ("A JOURNEY BEYOND EARTH", SUBTITLE_SIZE, TITLE_Y + TITLE_SIZE // 2 + 30),
        ]
        for text, size, y in lines:
            # sombra (desenhada primeiro, fica atrás do texto)
            if SHADOW_X or SHADOW_Y:
                self.canvas.create_text(
                    TITLE_X + SHADOW_X, y + SHADOW_Y,
                    text=text, font=(family, size), fill=SHADOW_COLOR,
                )
            self.canvas.create_text(TITLE_X, y, text=text, font=(family, size), fill=TITLE)

    def _draw_background(self):
        if not BACKGROUND_IMAGE.exists():
            return  # sem imagem: fica só a cor de fundo
        img = tk.PhotoImage(file=str(BACKGROUND_IMAGE))
        # PhotoImage só reduz por fatores inteiros; o ideal é a imagem ter 900x600
        factor = max(1, img.width() // WIDTH, img.height() // HEIGHT)
        if factor > 1:
            img = img.subsample(factor)
        self.background_img = img  # manter referência, senão a imagem some
        self.canvas.create_image(WIDTH // 2, HEIGHT // 2, image=img)

    def _draw_menu(self, on_new_game, on_continue, on_options, on_quit):
        x, y, gap = MENU_X, MENU_Y, MENU_GAP
        has_save = SAVE_FILE.exists()
        MenuButton(self.canvas, x, y, "Novo Jogo", on_new_game)
        MenuButton(self.canvas, x, y + gap, "Continuar", on_continue, enabled=has_save)
        MenuButton(self.canvas, x, y + gap * 2, "Opções", on_options)
        MenuButton(self.canvas, x, y + gap * 3, "Sair", on_quit)


def _flat_button(master, text, command):
    return tk.Button(
        master, text=text, command=command, font=("Arial", 13),
        bg=BUTTON_BG, fg="white", activebackground=BUTTON_HOVER,
        activeforeground="white", relief="flat", padx=20, pady=6, cursor="hand2",
    )


class DialogueScreen(tk.Frame):
    """Tela de diálogo: mostra as falas do StoryEngine e os botões de escolha."""

    def __init__(self, master, engine, on_end):
        super().__init__(master, bg=BG)
        self.engine = engine
        self.on_end = on_end

        self.speaker = tk.Label(self, font=("Arial", 16, "bold"), fg=ACCENT, bg=BG)
        self.speaker.pack(pady=(40, 10))
        self.text = tk.Label(
            self, font=("Arial", 15), fg="white", bg=BG,
            wraplength=750, justify="center",
        )
        self.text.pack(pady=20)

        self.choices_frame = tk.Frame(self, bg=BG)
        self.choices_frame.pack(pady=10)
        self.next_button = _flat_button(self, "Continuar", self.next_dialogue)

        self.next_dialogue()

    def next_dialogue(self):
        for widget in self.choices_frame.winfo_children():
            widget.destroy()

        data = self.engine.next_dialogue()

        if data is None:
            self.speaker.config(text="")
            self.text.config(text="Fim do capítulo 1!")
            self.next_button.config(text="Voltar ao menu", command=self.on_end)
            self.next_button.pack(pady=20)
            return

        self.speaker.config(text=data["speaker"])
        self.text.config(text=data["text"])

        if "choices" in data:
            self.next_button.pack_forget()
            for choice in data["choices"]:
                _flat_button(
                    self.choices_frame, choice["text"],
                    lambda choice_id=choice["id"]: self.select_choice(choice_id),
                ).pack(pady=5)
        else:
            self.next_button.pack(pady=20)

    def select_choice(self, choice_id):
        self.engine.make_choice(choice_id)
        self.next_dialogue()
