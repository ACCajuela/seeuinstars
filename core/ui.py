
import sys
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from core.audio_manager import AudioManager


# ============================================================
# CAMINHOS E CONFIGURAÇÕES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
FONTS_DIR = PROJECT_ROOT / "assets" / "fonts"

BACKGROUND_IMAGE = IMAGES_DIR / "fundo-home.png"
from core.paths import SAVE_FILE  # noqa: E402  (pasta do usuário)

WIDTH, HEIGHT = 900, 600

MENU_X, MENU_Y, MENU_GAP = 650, 225, 65

# Logo do jogo (substitui o título em texto). Se o arquivo não existir,
# o título "ASTRA" em texto aparece no lugar.
LOGO_IMAGE = IMAGES_DIR / "logo.png"
LOGO_X, LOGO_Y = 245, 240        # centro da logo
LOGO_MAX_W, LOGO_MAX_H = 580, 330  # tamanho máximo da logo

TITLE_FONT = "Sunborn Sans One"
TITLE_X, TITLE_Y = 250, 200
TITLE_SIZE, SUBTITLE_SIZE = 80, 16

SHADOW_COLOR = "#2B1208"
SHADOW_X, SHADOW_Y = 1, 1

BG = "#101827"
TITLE = "#FFFFFF"
ACCENT = "#8BD3FF"
BUTTON_BG = "#1E2A44"
BUTTON_HOVER = "#2C3E66"
BUTTON_BORDER = "#8BD3FF"
BUTTON_DISABLED = "#4A5568"

audio_manager = AudioManager()
audio_manager.play_music("background.wav")


# ============================================================
# FONTES E IMAGENS
# ============================================================

def load_project_fonts():
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
            str(font_file),
            FR_PRIVATE,
            0
        )


def font_or_fallback(family, fallback="Arial"):
    return family if family in tkfont.families() else fallback


def rounded_rect(canvas, x0, y0, x1, y1, r=18, **options):
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

    return canvas.create_polygon(
        points,
        smooth=True,
        **options
    )


def fit_image(path, max_w, max_h):
    img = tk.PhotoImage(file=str(path))

    factor = max(
        1,
        -(-img.width() // max_w),
        -(-img.height() // max_h)
    )

    return img.subsample(factor) if factor > 1 else img


def fit_content(path, target_w):
    """Abre um PNG com fundo transparente, acha onde está o desenho (ignora
    as sobras transparentes em volta) e reduz a imagem para o desenho ficar
    com ~target_w pixels de largura.

    Devolve (imagem, (x0, y0, x1, y1)): a caixa do desenho dentro da imagem
    já reduzida, para posicionar o desenho com precisão."""
    img = tk.PhotoImage(file=str(path))
    step = 16  # verifica 1 a cada 16 pixels (rápido e preciso o bastante)

    xs, ys = [], []
    for y in range(0, img.height(), step):
        for x in range(0, img.width(), step):
            if not img.transparency_get(x, y):
                xs.append(x)
                ys.append(y)

    if not xs:  # imagem sem nada visível: usa a imagem inteira
        xs, ys = [0, img.width() - step], [0, img.height() - step]

    box = (min(xs), min(ys), max(xs) + step, max(ys) + step)
    factor = max(1, round((box[2] - box[0]) / target_w))

    if factor > 1:
        img = img.subsample(factor)

    return img, tuple(v / factor for v in box)


def draw_background(canvas, path):
    if not path.exists():
        return None

    img = tk.PhotoImage(file=str(path))

    factor = max(
        1,
        img.width() // WIDTH,
        img.height() // HEIGHT
    )

    if factor > 1:
        img = img.subsample(factor)

    canvas.create_image(
        WIDTH // 2,
        HEIGHT // 2,
        image=img
    )

    return img


# ============================================================
# BOTÕES
# ============================================================

class MenuButton:
    def __init__(
        self,
        canvas,
        x,
        y,
        text,
        command,
        width=260,
        height=52,
        enabled=True,
        font_size=15,
        primary=False
    ):
        self.canvas = canvas
        self.command = command
        self.enabled = enabled
        self.tag = f"btn_{id(self)}"

        # primary=True: botão de destaque (ação principal do minigame)
        if primary:
            self.fill, self.hover_fill, self.text_color = ACCENT, "#B5E4FF", BG
        else:
            self.fill, self.hover_fill, self.text_color = BUTTON_BG, BUTTON_HOVER, TITLE

        x0 = x - width // 2
        y0 = y - height // 2
        x1 = x + width // 2
        y1 = y + height // 2

        self.shape = rounded_rect(
            canvas,
            x0, y0, x1, y1,
            r=18,
            width=2,
            tags=self.tag
        )

        self.label = canvas.create_text(
            x,
            y,
            text=text,
            font=("Arial", font_size, "bold"),
            tags=self.tag,
            width=width - 24,
            justify="center"
        )

        self._paint(self.fill)

        canvas.tag_bind(
            self.tag,
            "<Enter>",
            lambda e: self._hover(True)
        )

        canvas.tag_bind(
            self.tag,
            "<Leave>",
            lambda e: self._hover(False)
        )

        canvas.tag_bind(
            self.tag,
            "<Button-1>",
            lambda e: self._click()
        )

    def _paint(self, fill):
        border = (
            BUTTON_BORDER
            if self.enabled
            else BUTTON_DISABLED
        )

        color = self.text_color if self.enabled else BUTTON_DISABLED

        if not self.enabled:
            fill = BUTTON_BG

        self.canvas.itemconfigure(
            self.shape,
            fill=fill,
            outline=border
        )

        self.canvas.itemconfigure(
            self.label,
            fill=color
        )

    def _hover(self, inside):
        if not self.enabled:
            return

        self._paint(
            self.hover_fill if inside else self.fill
        )

        self.canvas.configure(
            cursor="hand2" if inside else ""
        )

    def _click(self):
        if not self.enabled:
            return

        audio_manager.play_effect("click.wav")
        self.command()

    def config(self, state=None, text=None):
        """Mesmo jeito de usar de um tk.Button:
        botao.config(state="disabled") / botao.config(text="...")."""
        if text is not None:
            self.canvas.itemconfigure(self.label, text=text)

        if state is not None:
            self.enabled = state != "disabled"
            self._paint(self.fill)

            if not self.enabled:
                self.canvas.configure(cursor="")

    def destroy(self):
        self.canvas.delete(self.tag)
        self.canvas.configure(cursor="")


class CanvasSlider:
    """Barra deslizante no estilo do jogo, desenhada no Canvas.
    Funciona como um tk.Scale: aceita variable, command e config(state=...)."""

    def __init__(
        self,
        canvas,
        x,
        y,
        length,
        from_,
        to,
        resolution=1,
        variable=None,
        command=None
    ):
        self.canvas = canvas
        self.x0, self.x1, self.y = x, x + length, y
        self.from_, self.to = from_, to
        self.resolution = resolution
        self.variable = variable or tk.DoubleVar(value=from_)
        self.command = command
        self.enabled = True
        self.tag = f"slider_{id(self)}"

        # trilho, parte preenchida e botão redondo
        self.track = rounded_rect(
            canvas, self.x0, y - 4, self.x1, y + 4, r=4,
            fill="#24324F", outline="", tags=self.tag
        )
        self.fill_bar = rounded_rect(
            canvas, self.x0, y - 4, self.x0 + 8, y + 4, r=4,
            fill=ACCENT, outline="", tags=self.tag
        )
        self.knob = canvas.create_oval(
            0, 0, 0, 0, fill=TITLE, outline=ACCENT, width=3, tags=self.tag
        )

        canvas.tag_bind(self.tag, "<Button-1>", self._drag)
        canvas.tag_bind(self.tag, "<B1-Motion>", self._drag)
        canvas.tag_bind(self.tag, "<Enter>", lambda e: self._cursor(True))
        canvas.tag_bind(self.tag, "<Leave>", lambda e: self._cursor(False))

        self._draw()

    def _cursor(self, inside):
        self.canvas.configure(cursor="hand2" if inside and self.enabled else "")

    def _drag(self, event):
        if not self.enabled:
            return

        ratio = (event.x - self.x0) / (self.x1 - self.x0)
        ratio = min(1, max(0, ratio))
        value = self.from_ + ratio * (self.to - self.from_)
        value = round(value / self.resolution) * self.resolution

        self.variable.set(value)
        self._draw()

        if self.command is not None:
            self.command(value)

    def _draw(self):
        ratio = (self.variable.get() - self.from_) / (self.to - self.from_)
        kx = self.x0 + min(1, max(0, ratio)) * (self.x1 - self.x0)
        y, r = self.y, 10
        color = ACCENT if self.enabled else BUTTON_DISABLED

        self.canvas.coords(self.knob, kx - r, y - r, kx + r, y + r)
        self.canvas.itemconfigure(self.knob, outline=color)
        self.canvas.delete(self.fill_bar)
        self.fill_bar = rounded_rect(
            self.canvas, self.x0, y - 4, max(kx, self.x0 + 8), y + 4, r=4,
            fill=color, outline="", tags=self.tag
        )
        self.canvas.tag_raise(self.knob)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)
        self._draw()

    def config(self, state=None):
        if state is not None:
            self.enabled = state != "disabled"
            self._draw()


# ============================================================
# TELA BASE
# ============================================================

class TitleScreen(tk.Frame):
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
        if LOGO_IMAGE.exists():
            self.logo_img = fit_image(LOGO_IMAGE, LOGO_MAX_W, LOGO_MAX_H)
            self.canvas.create_image(LOGO_X, LOGO_Y, image=self.logo_img)
            return

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
        self.background_img = draw_background(
            self.canvas,
            BACKGROUND_IMAGE
        )


# ============================================================
# HOME
# ============================================================

class HomeScreen(TitleScreen):
    def __init__(
        self,
        master,
        t,
        on_new_game,
        on_continue,
        on_options,
        on_quit
    ):
        super().__init__(master)

        x, y, gap = MENU_X, MENU_Y, MENU_GAP

        has_save = SAVE_FILE.exists()

        MenuButton(
            self.canvas, x, y,
            t("ui.new_game"),
            on_new_game
        )

        MenuButton(
            self.canvas, x, y + gap,
            t("ui.continue"),
            on_continue,
            enabled=has_save
        )

        MenuButton(
            self.canvas, x, y + gap * 2,
            t("ui.options"),
            on_options
        )

        MenuButton(
            self.canvas, x, y + gap * 3,
            t("ui.quit"),
            on_quit
        )

        def sound_text():
            key = (
                "ui.sound_on"
                if audio_manager.enabled
                else "ui.sound_off"
            )
            return t(key)

        def toggle_sound():
            audio_manager.toggle_audio()

            self.canvas.itemconfigure(
                sound_button.label,
                text=sound_text()
            )

        sound_button = MenuButton(
            self.canvas,
            x,
            y + gap * 4,
            sound_text(),
            toggle_sound
        )


# ============================================================
# SELEÇÃO DE IDIOMA
# ============================================================

class LanguageScreen(TitleScreen):
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


# ============================================================
# CONFIGURAÇÕES DO DIÁLOGO
# ============================================================

CHARACTERS_DIR = IMAGES_DIR / "characters"
DIALOGUE_BACKGROUND = IMAGES_DIR / "fundo-dialogo.png"

CHARACTERS = {
    "Ada": {
        "image": "Ada.png",
        "side": "left",
        "color": "#F4A261"
    },
    "COSMO": {
        "image": "Cosmo.png",
        "side": "right",
        "color": "#8BD3FF"
    },
    "Vera": {
        "image": "Vera.png",
        "side": "right",
        "color": "#C084FC"
    }
}

CHAR_MAX_W, CHAR_MAX_H = 360, 400
CHAR_LEFT_X, CHAR_RIGHT_X = 220, 680
CHAR_BASE_Y = 470

DIALOGUE_BOX = (30, 420, 870, 580)

BOX_FILL = "#0B1220"
TEXT_FONT = ("Arial", 15)
NAME_FONT = ("Arial", 14, "bold")
FEEDBACK_COLOR = "#FFD166"

TYPE_SPEED_MS = 25
SLIDE_FRAMES, SLIDE_MS = 14, 16
SLIDE_DISTANCE = 600


# ============================================================
# TELA DE DIÁLOGO
# ============================================================

class DialogueScreen(tk.Frame):
    def __init__(self, master, engine, t, on_end, on_save):
        super().__init__(master, bg=BG)

        self.engine = engine
        self.t = t
        self.on_end = on_end
        self.on_save = on_save

        self._jobs = set()
        self._type_job = None
        self._on_typed = None

        self._images = {}
        self.buttons = []

        self.current_speaker = None
        self.state = "busy"

        self.full_text = ""
        self.typed = 0

        c = self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        c.pack(fill="both", expand=True)

        # Fundo: muda conforme a cena (campo "background" no story.json,
        # na cena ou no capítulo). Sem o campo, usa DIALOGUE_BACKGROUND.
        self.background_img = None
        self.background_path = None
        self.background_item = c.create_image(
            WIDTH // 2, HEIGHT // 2
        )
        self._update_background()

        # Caixa de diálogo
        x0, y0, x1, y1 = DIALOGUE_BOX

        rounded_rect(
            c, x0, y0, x1, y1,
            r=20,
            fill=BOX_FILL,
            outline=ACCENT,
            width=2,
            tags="box"
        )

        self.text_item = c.create_text(
            x0 + 30,
            y0 + 32,
            anchor="nw",
            width=x1 - x0 - 60,
            font=TEXT_FONT,
            fill="white",
            tags="box"
        )

        self.hint = c.create_text(
            x1 - 24,
            y1 - 18,
            text="▼",
            font=("Arial", 12),
            fill=ACCENT,
            state="hidden",
            tags="box"
        )

        # Botões superiores
        MenuButton(
            c, 653, 32,
            t("ui.save"),
            self.save,
            width=150,
            height=36,
            font_size=12
        )

        MenuButton(
            c, 813, 32,
            t("ui.menu"),
            on_end,
            width=150,
            height=36,
            font_size=12
        )

        c.bind("<Button-1>", self._on_click)
        c.bind("<space>", lambda e: self.advance())
        c.bind("<Return>", lambda e: self.advance())

        c.focus_set()

        self.next_dialogue()

    # --------------------------------------------------------
    # AVANÇAR DIÁLOGO
    # --------------------------------------------------------

    def _on_click(self, event):
        try:
            tags = self.canvas.gettags("current")
        except tk.TclError:
            return

        if any(tag.startswith("btn_") for tag in tags):
            return

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

        # A cena pode ter mudado: troca o fundo se precisar
        self._update_background()

        if data is None:
            self._show_end()
            return

        if data.get("type") == "puzzle":
            self._show_puzzle(data["id"])
            return

        after_typing = None

        if "choices" in data:
            options = [
                (
                    self.t(choice["text_key"]),
                    lambda choice_id=choice["id"]:
                        self._choose(choice_id)
                )
                for choice in data["choices"]
            ]

            after_typing = lambda: self._show_options(options)

        self._present(
            data["speaker"],
            self.t(data["text_key"]),
            after_typing
        )

    def _background_for_scene(self):
        """Fundo da cena atual: "background" da cena, senão do capítulo,
        senão o fundo padrão do diálogo."""
        scene = self.engine.scene or {}
        name = (
            scene.get("background")
            or self.engine.story.get("background")
        )
        return IMAGES_DIR / name if name else DIALOGUE_BACKGROUND

    def _update_background(self):
        self._update_props()

        path = self._background_for_scene()

        if path == self.background_path:
            return

        self.background_path = path
        self.background_img = None

        if path.exists():
            img = tk.PhotoImage(file=str(path))
            factor = max(1, img.width() // WIDTH, img.height() // HEIGHT)
            if factor > 1:
                img = img.subsample(factor)
            self.background_img = img  # manter referência

        self.canvas.itemconfigure(
            self.background_item,
            image=self.background_img or ""
        )

    def _update_props(self):
        """Objetos no cenário da cena (campo "props" no story.json), por
        cima do fundo e atrás dos personagens. Exemplo:
            "props": [{"image": "hover.png", "x": 735, "y": 412, "width": 230}]
        x, y: onde fica a base do objeto (o chão) | width: largura do desenho"""
        scene = self.engine.scene or {}
        props = scene.get("props", [])
        signature = repr(props)

        if signature == getattr(self, "_props_signature", None):
            return

        self._props_signature = signature
        self.canvas.delete("prop")
        self._prop_images = []
        cache = self.__dict__.setdefault("_prop_cache", {})

        for prop in props:
            path = IMAGES_DIR / prop["image"]
            if not path.exists():
                continue
            key = (prop["image"], prop.get("width", 200))
            if key not in cache:
                cache[key] = fit_content(path, prop.get("width", 200))
            img, (x0, y0, x1, y1) = cache[key]
            self._prop_images.append(img)
            # base do desenho em (x, y), centralizado na horizontal
            self.canvas.create_image(
                prop["x"] - (x0 + x1) / 2,
                prop["y"] - y1,
                image=img,
                anchor="nw",
                tags="prop"
            )

        # logo acima do fundo, abaixo dos personagens e da caixa
        self.canvas.tag_raise("prop", self.background_item)

    def _present(self, speaker, text, after_typing=None):
        self.state = "busy"

        self.canvas.itemconfigure(
            self.hint,
            state="hidden"
        )

        self.canvas.itemconfigure(
            self.text_item,
            text=""
        )

        def speak():
            self._draw_name(speaker)
            self._type(text, after_typing)

        if (
            speaker in CHARACTERS
            and speaker != self.current_speaker
        ):
            self._swap_character(speaker, then=speak)
        else:
            speak()

    # --------------------------------------------------------
    # PERSONAGENS E ANIMAÇÕES
    # --------------------------------------------------------

    def _swap_character(self, new_speaker, then):
        def enter():
            self._enter_character(new_speaker, then)

        if self.current_speaker:
            self._exit_character(then=enter)
        else:
            enter()

    def _enter_character(self, name, then):
        side = CHARACTERS[name]["side"]

        target_x = (
            CHAR_LEFT_X if side == "left"
            else CHAR_RIGHT_X
        )

        direction = 1 if side == "left" else -1

        self._draw_character(
            name,
            target_x - direction * SLIDE_DISTANCE
        )

        self.current_speaker = name

        self._slide(
            direction * SLIDE_DISTANCE,
            then
        )

    def _exit_character(self, then):
        side = CHARACTERS[self.current_speaker]["side"]
        direction = -1 if side == "left" else 1

        def done():
            self.canvas.delete("char")
            self.current_speaker = None
            then()

        self._slide(
            direction * SLIDE_DISTANCE,
            done
        )

    def _draw_character(self, name, x):
        c = self.canvas
        image = self._character_image(name)

        if image:
            c.create_image(
                x,
                CHAR_BASE_Y,
                image=image,
                anchor="s",
                tags="char"
            )
        else:
            color = CHARACTERS[name]["color"]

            rounded_rect(
                c,
                x - 90,
                CHAR_BASE_Y - 260,
                x + 90,
                CHAR_BASE_Y + 40,
                r=40,
                fill=color,
                outline="",
                tags="char"
            )

            c.create_oval(
                x - 60,
                CHAR_BASE_Y - 385,
                x + 60,
                CHAR_BASE_Y - 265,
                fill=color,
                outline="",
                tags="char"
            )

            c.create_text(
                x,
                CHAR_BASE_Y - 140,
                text=f"{name}\n(sem imagem)",
                font=("Arial", 12, "bold"),
                fill=BG,
                justify="center",
                tags="char"
            )

        c.tag_lower("char", "box")

    def _character_image(self, name):
        if name not in self._images:
            path = (
                CHARACTERS_DIR
                / CHARACTERS[name]["image"]
            )

            self._images[name] = (
                fit_image(path, CHAR_MAX_W, CHAR_MAX_H)
                if path.exists()
                else None
            )

        return self._images[name]

    def _slide(self, distance, then):
        positions = [
            distance * (1 - (1 - i / SLIDE_FRAMES) ** 3)
            for i in range(SLIDE_FRAMES + 1)
        ]

        steps = [
            b - a
            for a, b in zip(positions, positions[1:])
        ]

        def step(i=0):
            if i == len(steps):
                then()
                return

            self.canvas.move("char", steps[i], 0)

            self._later(
                SLIDE_MS,
                lambda: step(i + 1)
            )

        step()

    # --------------------------------------------------------
    # CAIXA DE DIÁLOGO
    # --------------------------------------------------------

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

        nx0 = (
            x0 + 25
            if side != "right"
            else x1 - 25 - w
        )

        rounded_rect(
            c,
            nx0,
            y0 - 17,
            nx0 + w,
            y0 + 17,
            r=14,
            fill=ACCENT,
            outline="",
            tags="name"
        )

        c.create_text(
            nx0 + w / 2,
            y0,
            text=name,
            font=NAME_FONT,
            fill=BG,
            tags="name"
        )

    def _type(self, text, after_typing):
        self.full_text = text
        self.typed = 0
        self._on_typed = after_typing
        self.state = "typing"

        if not text:
            self._typing_done()
        else:
            self._type_step()

    def _type_step(self):
        self.typed += 1

        self.canvas.itemconfigure(
            self.text_item,
            text=self.full_text[:self.typed]
        )

        if self.typed >= len(self.full_text):
            self._typing_done()
        else:
            self._type_job = self._later(
                TYPE_SPEED_MS,
                self._type_step
            )

    def _finish_typing(self):
        if self._type_job:
            self.after_cancel(self._type_job)
            self._jobs.discard(self._type_job)
            self._type_job = None

        self.canvas.itemconfigure(
            self.text_item,
            text=self.full_text
        )

        self._typing_done()

    def _typing_done(self):
        self._type_job = None

        callback = self._on_typed
        self._on_typed = None

        if callback:
            self.state = "choosing"
            callback()
        else:
            self.state = "waiting"
            self.canvas.itemconfigure(
                self.hint,
                state="normal"
            )

    def _set_feedback(self, text):
        c = self.canvas
        c.delete("feedback")

        if not text:
            return

        label = c.create_text(
            WIDTH // 2,
            378,
            text=text,
            width=760,
            justify="center",
            font=("Arial", 13, "bold"),
            fill=FEEDBACK_COLOR,
            tags="feedback"
        )

        bx0, by0, bx1, by1 = c.bbox(label)

        bubble = rounded_rect(
            c,
            bx0 - 16,
            by0 - 8,
            bx1 + 16,
            by1 + 8,
            r=14,
            fill=BOX_FILL,
            outline=FEEDBACK_COLOR,
            width=1,
            tags="feedback"
        )

        c.tag_lower(bubble, label)

    # --------------------------------------------------------
    # ESCOLHAS E PUZZLES
    # --------------------------------------------------------

    def _show_options(self, options):
        self._clear_buttons()

        gap = 62
        bottom_y = 320

        first_y = (
            bottom_y - gap * (len(options) - 1)
        )

        for i, (text, command) in enumerate(options):
            button = MenuButton(
                self.canvas,
                WIDTH // 2,
                first_y + gap * i,
                text,
                command,
                width=560,
                height=50,
                font_size=13
            )

            self.buttons.append(button)

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
            (
                self.t(option["text_key"]),
                lambda i=i: self._answer(puzzle_id, i)
            )
            for i, option in enumerate(puzzle["options"])
        ]

        self._present(
            self.t("ui.challenge"),
            self.t(puzzle["question_key"]),
            lambda: self._show_options(options)
        )

    def _answer(self, puzzle_id, option_index):
        correct, message_key = self.engine.answer_puzzle(
            puzzle_id,
            option_index
        )

        audio_manager.play_effect(
            "correct.wav" if correct else "wrong.wav"
        )

        self._set_feedback(
            self.t(message_key)
        )

        if correct:
            self._clear_buttons()
            self.state = "waiting"

            self.canvas.itemconfigure(
                self.hint,
                state="normal"
            )

    # --------------------------------------------------------
    # SALVAR E FINALIZAR
    # --------------------------------------------------------

    def _show_end(self):
        self.state = "ended"

        def show():
            self._draw_name("")

            self.canvas.itemconfigure(
                self.text_item,
                text=self.t("ui.chapter_end")
            )

            self._show_options([
                (
                    self.t("ui.back_to_menu"),
                    self.on_end
                )
            ])

        if self.current_speaker:
            self._exit_character(then=show)
        else:
            show()

    def save(self):
        self.on_save(self.engine)

        self._set_feedback(
            self.t("ui.saved")
        )

    # --------------------------------------------------------
    # AGENDAMENTO DAS ANIMAÇÕES
    # --------------------------------------------------------

    def _later(self, ms, callback):
        def run():
            self._jobs.discard(job)
            callback()

        job = self.after(ms, run)
        self._jobs.add(job)

        return job

    def destroy(self):
        for job in self._jobs:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass

        self._jobs.clear()
        super().destroy()


# ============================================================
# SUBMENU DE OPÇÕES
# ============================================================

class OptionsScreen(TitleScreen):
    def __init__(
        self,
        master,
        t,
        on_audio,
        on_language,
        on_back
    ):
        super().__init__(master)

        x = MENU_X
        y = MENU_Y

        self.canvas.create_text(
            x,
            y - 65,
            text=t("ui.options"),
            font=("Arial", 22, "bold"),
            fill=TITLE
        )

        MenuButton(
            self.canvas,
            x,
            y,
            t("ui.audio"),
            on_audio
        )

        MenuButton(
            self.canvas,
            x,
            y + MENU_GAP,
            t("ui.language"),
            on_language
        )

        MenuButton(
            self.canvas,
            x,
            y + MENU_GAP * 2,
            t("ui.back"),
            on_back
        )


# ============================================================
# CONFIGURAÇÕES DE ÁUDIO
# ============================================================

class AudioSettingsScreen(tk.Frame):
    def __init__(self, master, t, on_back):
        super().__init__(master, bg=BG)

        english = t("ui.quit") == "Quit"

        title = (
            "Audio Settings"
            if english
            else "Configurações de áudio"
        )

        self.music_text = (
            "Music" if english else "Música"
        )

        self.effects_text = (
            "Sound Effects"
            if english
            else "Efeitos sonoros"
        )

        back_text = (
            "Back" if english else "Voltar"
        )

        tk.Label(
            self,
            text=title,
            font=("Arial", 24, "bold"),
            fg=ACCENT,
            bg=BG
        ).pack(pady=(65, 35))

        # Volume da música
        self.music_label = tk.Label(
            self,
            fg="white",
            bg=BG,
            font=("Arial", 14)
        )

        self.music_label.pack(pady=10)

        self.music_slider = tk.Scale(
            self,
            from_=0,
            to=100,
            orient="horizontal",
            length=350,
            bg=BG,
            fg="white",
            troughcolor=BUTTON_BG,
            highlightthickness=0,
            command=self.change_music
        )

        self.music_slider.pack()

        # Volume dos efeitos
        self.effects_label = tk.Label(
            self,
            fg="white",
            bg=BG,
            font=("Arial", 14)
        )

        self.effects_label.pack(pady=(35, 10))

        self.effects_slider = tk.Scale(
            self,
            from_=0,
            to=100,
            orient="horizontal",
            length=350,
            bg=BG,
            fg="white",
            troughcolor=BUTTON_BG,
            highlightthickness=0,
            command=self.change_effects
        )

        self.effects_slider.pack()

        # Valores atuais
        self.music_slider.set(
            round(audio_manager.music_volume * 100)
        )

        self.effects_slider.set(
            round(audio_manager.effects_volume * 100)
        )

        self.update_labels()

        # Botão Voltar com o mesmo estilo da Home
        self.back_canvas = tk.Canvas(
            self,
            width=300,
            height=70,
            bg=BG,
            highlightthickness=0
        )

        self.back_canvas.pack(pady=35)

        self.back_button = MenuButton(
            self.back_canvas,
            150,
            35,
            back_text,
            on_back
        )

    def update_labels(self):
        self.music_label.config(
            text=(
                f"{self.music_text}: "
                f"{self.music_slider.get()}%"
            )
        )

        self.effects_label.config(
            text=(
                f"{self.effects_text}: "
                f"{self.effects_slider.get()}%"
            )
        )

    def change_music(self, value):
        audio_manager.set_music_volume(
            float(value) / 100
        )

        if hasattr(self, "music_text"):
            self.update_labels()

    def change_effects(self, value):
        audio_manager.set_effects_volume(
            float(value) / 100
        )

        if hasattr(self, "effects_text"):
            self.update_labels()


# ============================================================
# MINIGAMES — peças visuais compartilhadas
# ============================================================
# Usadas em puzzles/*_ui.py para os minigames terem a mesma cara
# do resto do jogo (painel, títulos, COSMO dando dicas).

MINIGAME_PANEL = (690, 15, 885, 585)   # painel lateral: x0, y0, x1, y1
MINIGAME_SUCCESS = "#8CE7B0"           # cor de mensagem de acerto
MINIGAME_MUTED = "#A9BDD4"             # textos secundários


class CanvasLabel:
    """Texto do Canvas que aceita .config(text=..., fg=...) como um tk.Label."""

    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def config(self, text=None, fg=None):
        if text is not None:
            self.canvas.itemconfigure(self.item, text=text)
        if fg is not None:
            self.canvas.itemconfigure(self.item, fill=fg)


def draw_minigame_panel(canvas, title):
    """Painel lateral com o mesmo estilo da caixa de diálogo + título."""
    x0, y0, x1, y1 = MINIGAME_PANEL
    rounded_rect(canvas, x0, y0, x1, y1, r=20, fill=BOX_FILL,
                 outline=ACCENT, width=2)
    canvas.create_text(
        (x0 + x1) / 2, y0 + 55, text=title, justify="center",
        font=(font_or_fallback(TITLE_FONT), 20), fill=TITLE,
    )


def draw_minigame_heading(canvas, title, subtitle):
    """Título do capítulo no canto superior esquerdo, na fonte do jogo."""
    family = font_or_fallback(TITLE_FONT)
    canvas.create_text(27, 27, text=title, anchor="nw",
                       font=(family, 18), fill="#000000")
    canvas.create_text(25, 25, text=title, anchor="nw",
                       font=(family, 18), fill=TITLE)
    canvas.create_text(25, 58, text=subtitle, anchor="nw",
                       font=("Arial", 11), fill=MINIGAME_MUTED)


class CosmoHint:
    """COSMO no canto inferior esquerdo com um balão de fala (dicas e
    resultados do minigame), no mesmo estilo da cena de diálogo."""

    def __init__(self, canvas, right=660):
        self.canvas = canvas
        x0, y0, x1, y1 = 135, 500, right, 585

        path = CHARACTERS_DIR / CHARACTERS["COSMO"]["image"]
        self.image = fit_image(path, 150, 150) if path.exists() else None
        if self.image:
            canvas.create_image(70, 598, image=self.image, anchor="s",
                                tags="hint")

        rounded_rect(canvas, x0, y0, x1, y1, r=18, fill=BOX_FILL,
                     outline=ACCENT, width=2, tags="hint")
        name_w = tkfont.Font(font=NAME_FONT).measure("COSMO") + 32
        rounded_rect(canvas, x0 + 20, y0 - 14, x0 + 20 + name_w, y0 + 14,
                     r=12, fill=ACCENT, outline="", tags="hint")
        canvas.create_text(x0 + 20 + name_w / 2, y0, text="COSMO",
                           font=NAME_FONT, fill=BG, tags="hint")
        self.text = canvas.create_text(
            x0 + 22, (y0 + y1) / 2 + 4, anchor="w", width=x1 - x0 - 40,
            font=("Arial", 12, "bold"), fill=TITLE, tags="hint",
        )

    def set(self, text, color=TITLE):
        self.canvas.itemconfigure(self.text, text=text, fill=color)

    def raise_(self):
        self.canvas.tag_raise("hint")
