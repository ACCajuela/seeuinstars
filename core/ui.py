import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from core.audio_manager import AudioManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"
BACKGROUND_IMAGE = IMAGES_DIR / "fundo-home.png"
SAVE_FILE = PROJECT_ROOT / "save.json"  # mesmo caminho do SaveManager

WIDTH, HEIGHT = 900, 600

# Posição dos botões na home (centro do primeiro botão e espaço entre eles)
MENU_X, MENU_Y, MENU_GAP = 650, 225, 65

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

audio_manager = AudioManager()  # efeitos sonoros (clique, acerto, erro)

# Paleta
BG = "#101827"
TITLE = "#FFFFFF"
ACCENT = "#8BD3FF"
BUTTON_BG = "#1E2A44"
BUTTON_HOVER = "#2C3E66"
BUTTON_BORDER = "#8BD3FF"
BUTTON_DISABLED = "#4A5568"


def rounded_rect(canvas, x0, y0, x1, y1, r=18, **options):
    """Desenha um retângulo com cantos arredondados no Canvas."""
    points = [
        x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
        x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
        x0, y1, x0, y1 - r, x0, y0 + r, x0, y0,
    ]
    return canvas.create_polygon(points, smooth=True, **options)


def fit_image(path, max_w, max_h):
    """Abre um PNG e reduz (por fator inteiro) até caber em max_w x max_h."""
    img = tk.PhotoImage(file=str(path))
    factor = max(1, -(-img.width() // max_w), -(-img.height() // max_h))
    return img.subsample(factor) if factor > 1 else img


def draw_background(canvas, path):
    """Desenha a imagem de fundo centralizada. Devolve a imagem: guarde a
    referência, senão o Tkinter apaga a imagem da tela."""
    if not path.exists():
        return None  # sem imagem: fica só a cor de fundo
    img = tk.PhotoImage(file=str(path))
    # PhotoImage só reduz por fatores inteiros; o ideal é a imagem ter 900x600
    factor = max(1, img.width() // WIDTH, img.height() // HEIGHT)
    if factor > 1:
        img = img.subsample(factor)
    canvas.create_image(WIDTH // 2, HEIGHT // 2, image=img)
    return img


class MenuButton:
    """Botão arredondado desenhado no Canvas, com efeito de hover."""

    def __init__(self, canvas, x, y, text, command, width=260, height=52,
                 enabled=True, font_size=15):
        self.canvas = canvas
        self.command = command
        self.enabled = enabled
        self.tag = tag = f"btn_{id(self)}"

        x0, y0 = x - width // 2, y - height // 2
        x1, y1 = x + width // 2, y + height // 2
        self.shape = rounded_rect(canvas, x0, y0, x1, y1, r=18, width=2, tags=tag)
        self.label = canvas.create_text(
            x, y, text=text, font=("Arial", font_size, "bold"), tags=tag,
            width=width - 24, justify="center",
        )
        self._paint(BUTTON_BG)

        if enabled:
            canvas.tag_bind(tag, "<Enter>", lambda e: self._hover(True))
            canvas.tag_bind(tag, "<Leave>", lambda e: self._hover(False))
            canvas.tag_bind(tag, "<Button-1>", lambda e: self._click())

    def _paint(self, fill):
        border = BUTTON_BORDER if self.enabled else BUTTON_DISABLED
        text = TITLE if self.enabled else BUTTON_DISABLED
        self.canvas.itemconfigure(self.shape, fill=fill, outline=border)
        self.canvas.itemconfigure(self.label, fill=text)

    def _hover(self, inside):
        self._paint(BUTTON_HOVER if inside else BUTTON_BG)
        self.canvas.configure(cursor="hand2" if inside else "")

    def _click(self):
        if not self.enabled:
            return
        audio_manager.play_effect("click.wav")
        self.command()

    def destroy(self):
        self.canvas.delete(self.tag)
        self.canvas.configure(cursor="")


class TitleScreen(tk.Frame):
    """Base das telas de menu: imagem de fundo + título ASTRA."""

    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._draw_background()
        self._draw_title()

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
        self.background_img = draw_background(self.canvas, BACKGROUND_IMAGE)



class HomeScreen(TitleScreen):
    """Tela inicial: fundo, título e botões do menu. `t` traduz as chaves de texto."""

    def __init__(self, master, t, on_new_game, on_continue, on_options, on_quit):
        super().__init__(master)
        x, y, gap = MENU_X, MENU_Y, MENU_GAP
        has_save = SAVE_FILE.exists()
        MenuButton(self.canvas, x, y, t("ui.new_game"), on_new_game)
        MenuButton(self.canvas, x, y + gap, t("ui.continue"), on_continue, enabled=has_save)
        MenuButton(self.canvas, x, y + gap * 2, t("ui.options"), on_options)
        MenuButton(self.canvas, x, y + gap * 3, t("ui.quit"), on_quit)

        # Liga/desliga o som (o texto muda conforme o estado)
        def sound_text():
            return t("ui.sound_on" if audio_manager.enabled else "ui.sound_off")

        def toggle_sound():
            audio_manager.toggle_audio()
            self.canvas.itemconfigure(sound_button.label, text=sound_text())

        sound_button = MenuButton(self.canvas, x, y + gap * 4, sound_text(), toggle_sound)


class LanguageScreen(TitleScreen):
    """Escolha de idioma, com o mesmo visual da home."""

    def __init__(self, master, on_choose):
        super().__init__(master)
        x, y = MENU_X, MENU_Y
        self.canvas.create_text(
            x, y - 60, text="Choose your language\nEscolha seu idioma",
            font=("Arial", 14, "bold"), fill=TITLE, justify="center",
        )
        MenuButton(self.canvas, x, y + 20, "Português (Brasil)", lambda: on_choose("pt_BR"))
        MenuButton(self.canvas, x, y + 20 + MENU_GAP, "English", lambda: on_choose("en"))


# =====================================================================
# CENA DE DIÁLOGO
# =====================================================================

CHARACTERS_DIR = IMAGES_DIR / "characters"
DIALOGUE_BACKGROUND = IMAGES_DIR / "fundo-dialogo.png"

# Personagens: o nome tem que ser igual ao "speaker" do story.json.
# image: arquivo em assets/images/characters | side: lado da tela
# color: cor da silhueta usada enquanto não houver imagem
CHARACTERS = {
    "Ada":   {"image": "Ada.png",   "side": "left",  "color": "#F4A261"},
    "COSMO": {"image": "Cosmo.png", "side": "right", "color": "#8BD3FF"},
}
CHAR_MAX_W, CHAR_MAX_H = 360, 400  # tamanho máximo da imagem do personagem
CHAR_LEFT_X, CHAR_RIGHT_X = 220, 680  # centro do personagem em cada lado
CHAR_BASE_Y = 470  # altura dos "pés" (ficam escondidos atrás da caixa)

DIALOGUE_BOX = (30, 420, 870, 580)  # caixa de diálogo: x0, y0, x1, y1
BOX_FILL = "#0B1220"
TEXT_FONT = ("Arial", 15)
NAME_FONT = ("Arial", 14, "bold")
FEEDBACK_COLOR = "#FFD166"

TYPE_SPEED_MS = 25  # tempo entre letras (menor = mais rápido)
SLIDE_FRAMES, SLIDE_MS = 14, 16  # animação de entrada/saída dos personagens
SLIDE_DISTANCE = 600  # de quão longe o personagem entra


class DialogueScreen(tk.Frame):
    """Cena de diálogo: quem fala entra na tela, a fala é digitada letra por
    letra e, quando quem fala muda, um personagem sai e o outro entra.
    Clique, Espaço ou Enter avançam (o primeiro clique completa a fala)."""

    def __init__(self, master, engine, t, on_end, on_save):
        super().__init__(master, bg=BG)
        self.engine = engine
        self.t = t
        self.on_end = on_end
        self.on_save = on_save

        self._jobs = set()          # animações agendadas (canceladas ao sair)
        self._type_job = None
        self._on_typed = None
        self._images = {}           # imagens dos personagens já carregadas
        self.buttons = []           # botões de escolha/desafio na tela
        self.current_speaker = None # personagem que está na tela agora
        self.state = "busy"         # busy | typing | waiting | choosing | ended
        self.full_text = ""
        self.typed = 0

        c = self.canvas = tk.Canvas(
            self, width=WIDTH, height=HEIGHT, bg=BG, highlightthickness=0
        )
        c.pack(fill="both", expand=True)
        self.background_img = draw_background(c, DIALOGUE_BACKGROUND)

        # Caixa de diálogo
        x0, y0, x1, y1 = DIALOGUE_BOX
        rounded_rect(c, x0, y0, x1, y1, r=20, fill=BOX_FILL,
                     outline=ACCENT, width=2, tags="box")
        self.text_item = c.create_text(
            x0 + 30, y0 + 32, anchor="nw", width=x1 - x0 - 60,
            font=TEXT_FONT, fill="white", tags="box",
        )
        self.hint = c.create_text(
            x1 - 24, y1 - 18, text="▼", font=("Arial", 12),
            fill=ACCENT, state="hidden", tags="box",
        )

        # Salvar e voltar ao menu (canto superior direito)
        MenuButton(c, 653, 32, t("ui.save"), self.save,
                   width=150, height=36, font_size=12)
        MenuButton(c, 813, 32, t("ui.menu"), on_end,
                   width=150, height=36, font_size=12)

        c.bind("<Button-1>", self._on_click)
        c.bind("<space>", lambda e: self.advance())
        c.bind("<Return>", lambda e: self.advance())
        c.focus_set()

        self.next_dialogue()

    # --- Avançar --------------------------------------------------------
    def _on_click(self, event):
        try:
            tags = self.canvas.gettags("current")
        except tk.TclError:
            return  # a tela já foi fechada por um botão
        if any(tag.startswith("btn_") for tag in tags):
            return  # clique foi num botão, não avança
        self.advance()

    def advance(self):
        if self.state == "typing":
            self._finish_typing()
        elif self.state == "waiting":
            self.next_dialogue()

    def next_dialogue(self):
        self._clear_buttons()
        self._set_feedback("")

        data = self.engine.next_dialogue()

        if data is None:
            self._show_end()
            return

        if data.get("type") == "puzzle":
            self._show_puzzle(data["id"])
            return

        after_typing = None
        if "choices" in data:
            options = [
                (self.t(choice["text_key"]),
                 lambda choice_id=choice["id"]: self._choose(choice_id))
                for choice in data["choices"]
            ]
            after_typing = lambda: self._show_options(options)

        self._present(data["speaker"], self.t(data["text_key"]), after_typing)

    def _present(self, speaker, text, after_typing=None):
        """Troca o personagem (se quem fala mudou) e depois digita a fala."""
        self.state = "busy"
        self.canvas.itemconfigure(self.hint, state="hidden")
        self.canvas.itemconfigure(self.text_item, text="")

        def speak():
            self._draw_name(speaker)
            self._type(text, after_typing)

        if speaker in CHARACTERS and speaker != self.current_speaker:
            self._swap_character(speaker, then=speak)
        else:
            speak()  # mesmo personagem (ou "DESAFIO"): só troca a fala

    # --- Personagens ----------------------------------------------------
    def _swap_character(self, new_speaker, then):
        def enter():
            self._enter_character(new_speaker, then)

        if self.current_speaker:
            self._exit_character(then=enter)
        else:
            enter()

    def _enter_character(self, name, then):
        side = CHARACTERS[name]["side"]
        target_x = CHAR_LEFT_X if side == "left" else CHAR_RIGHT_X
        direction = 1 if side == "left" else -1
        self._draw_character(name, target_x - direction * SLIDE_DISTANCE)
        self.current_speaker = name
        self._slide(direction * SLIDE_DISTANCE, then)

    def _exit_character(self, then):
        side = CHARACTERS[self.current_speaker]["side"]
        direction = -1 if side == "left" else 1

        def done():
            self.canvas.delete("char")
            self.current_speaker = None
            then()

        self._slide(direction * SLIDE_DISTANCE, done)

    def _draw_character(self, name, x):
        c = self.canvas
        image = self._character_image(name)
        if image:
            c.create_image(x, CHAR_BASE_Y, image=image, anchor="s", tags="char")
        else:
            # Silhueta provisória até a imagem existir
            color = CHARACTERS[name]["color"]
            rounded_rect(c, x - 90, CHAR_BASE_Y - 260, x + 90, CHAR_BASE_Y + 40,
                         r=40, fill=color, outline="", tags="char")
            c.create_oval(x - 60, CHAR_BASE_Y - 385, x + 60, CHAR_BASE_Y - 265,
                          fill=color, outline="", tags="char")
            c.create_text(x, CHAR_BASE_Y - 140, text=f"{name}\n(sem imagem)",
                          font=("Arial", 12, "bold"), fill=BG,
                          justify="center", tags="char")
        c.tag_lower("char", "box")  # personagem fica atrás da caixa de diálogo

    def _character_image(self, name):
        if name not in self._images:
            path = CHARACTERS_DIR / CHARACTERS[name]["image"]
            self._images[name] = (
                fit_image(path, CHAR_MAX_W, CHAR_MAX_H) if path.exists() else None
            )
        return self._images[name]

    def _slide(self, distance, then):
        """Move os itens "char" com desaceleração no final."""
        positions = [
            distance * (1 - (1 - i / SLIDE_FRAMES) ** 3)
            for i in range(SLIDE_FRAMES + 1)
        ]
        steps = [b - a for a, b in zip(positions, positions[1:])]

        def step(i=0):
            if i == len(steps):
                then()
                return
            self.canvas.move("char", steps[i], 0)
            self._later(SLIDE_MS, lambda: step(i + 1))

        step()

    # --- Caixa de diálogo -----------------------------------------------
    def _draw_name(self, name):
        c = self.canvas
        c.delete("name")
        if not name:
            return
        side = CHARACTERS.get(name, {}).get("side")
        if side is None and self.current_speaker:
            side = CHARACTERS[self.current_speaker]["side"]
        x0, y0, x1, _ = DIALOGUE_BOX
        w = tkfont.Font(font=NAME_FONT).measure(name) + 40
        nx0 = x0 + 25 if side != "right" else x1 - 25 - w
        rounded_rect(c, nx0, y0 - 17, nx0 + w, y0 + 17, r=14,
                     fill=ACCENT, outline="", tags="name")
        c.create_text(nx0 + w / 2, y0, text=name, font=NAME_FONT,
                      fill=BG, tags="name")

    def _type(self, text, after_typing):
        self.full_text = text
        self.typed = 0
        self._on_typed = after_typing
        self.state = "typing"
        self._type_step()

    def _type_step(self):
        self.typed += 1
        self.canvas.itemconfigure(self.text_item, text=self.full_text[:self.typed])
        if self.typed >= len(self.full_text):
            self._typing_done()
        else:
            self._type_job = self._later(TYPE_SPEED_MS, self._type_step)

    def _finish_typing(self):
        if self._type_job:
            self.after_cancel(self._type_job)
            self._jobs.discard(self._type_job)
        self.canvas.itemconfigure(self.text_item, text=self.full_text)
        self._typing_done()

    def _typing_done(self):
        self._type_job = None
        callback, self._on_typed = self._on_typed, None
        if callback:
            self.state = "choosing"
            callback()
        else:
            self.state = "waiting"
            self.canvas.itemconfigure(self.hint, state="normal")

    def _set_feedback(self, text):
        """Mensagem em destaque logo acima da caixa (acerto/erro, jogo salvo)."""
        c = self.canvas
        c.delete("feedback")
        if not text:
            return
        label = c.create_text(
            WIDTH // 2, 378, text=text, width=760, justify="center",
            font=("Arial", 13, "bold"), fill=FEEDBACK_COLOR, tags="feedback",
        )
        bx0, by0, bx1, by1 = c.bbox(label)
        bubble = rounded_rect(c, bx0 - 16, by0 - 8, bx1 + 16, by1 + 8, r=14,
                              fill=BOX_FILL, outline=FEEDBACK_COLOR, width=1,
                              tags="feedback")
        c.tag_lower(bubble, label)

    # --- Escolhas e desafios --------------------------------------------
    def _show_options(self, options):
        """options: lista de (texto, função). Botões empilhados acima da caixa."""
        self._clear_buttons()
        gap, bottom_y = 62, 320
        first_y = bottom_y - gap * (len(options) - 1)
        for i, (text, command) in enumerate(options):
            self.buttons.append(MenuButton(
                self.canvas, WIDTH // 2, first_y + gap * i, text, command,
                width=560, height=50, font_size=13,
            ))

    def _clear_buttons(self):
        for button in self.buttons:
            button.destroy()
        self.buttons = []

    def _choose(self, choice_id):
        self.engine.make_choice(choice_id)
        self.next_dialogue()

    def _show_puzzle(self, puzzle_id):
        puzzle = self.engine.get_puzzle(puzzle_id)
        options = [
            (self.t(option["text_key"]),
             lambda i=i: self._answer(puzzle_id, i))
            for i, option in enumerate(puzzle["options"])
        ]
        self._present(self.t("ui.challenge"), self.t(puzzle["question_key"]),
                      lambda: self._show_options(options))

    def _answer(self, puzzle_id, option_index):
        correct, message_key = self.engine.answer_puzzle(puzzle_id, option_index)
        audio_manager.play_effect("correct.wav" if correct else "wrong.wav")
        self._set_feedback(self.t(message_key))
        if correct:
            self._clear_buttons()
            self.state = "waiting"
            self.canvas.itemconfigure(self.hint, state="normal")

    # --- Fim do capítulo e salvar ---------------------------------------
    def _show_end(self):
        self.state = "ended"

        def show():
            self._draw_name("")
            self.canvas.itemconfigure(self.text_item, text=self.t("ui.chapter_end"))
            self._show_options([(self.t("ui.back_to_menu"), self.on_end)])

        if self.current_speaker:
            self._exit_character(then=show)
        else:
            show()

    def save(self):
        self.on_save(self.engine)
        self._set_feedback(self.t("ui.saved"))

    # --- Agendamento das animações --------------------------------------
    def _later(self, ms, callback):
        def run():
            self._jobs.discard(job)
            callback()

        job = self.after(ms, run)
        self._jobs.add(job)
        return job

    def destroy(self):
        for job in self._jobs:
            self.after_cancel(job)
        self._jobs.clear()
        super().destroy()
