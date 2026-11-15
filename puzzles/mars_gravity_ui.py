
import math
import time
import tkinter as tk

from core.ui import (
    ACCENT, BACKGROUND_IMAGE, BG as UI_BG, BOX_FILL, CHARACTERS,
    CHARACTERS_DIR, FEEDBACK_COLOR, IMAGES_DIR, MINIGAME_MUTED,
    MINIGAME_PANEL, MINIGAME_SUCCESS, TITLE, TITLE_FONT,
    CanvasSlider, CosmoHint, MenuButton, draw_minigame_heading,
    draw_minigame_panel, fit_content, fit_image, font_or_fallback,
    rounded_rect,
)


# Imagens usadas no minigame (sem o arquivo, volta o desenho simples)
MARS_BACKGROUND = BACKGROUND_IMAGE                 # paisagem de Marte
ADA_IMAGE = CHARACTERS_DIR / CHARACTERS["Ada"]["image"]
ROVER_IMAGE = IMAGES_DIR / "hover.png"

WIDTH, HEIGHT = 900, 600
SCENE_WIDTH = 680          # a cena fica à esquerda do painel


class MarsGravityUI(tk.Frame):
    # Cores (identidade visual do jogo, de core/ui.py)
    BG = "#1A0E0B"
    PANEL = BOX_FILL
    CARD = "#1E2A44"
    TEXT = TITLE
    MUTED = MINIGAME_MUTED
    CYAN = ACCENT
    GREEN = MINIGAME_SUCCESS
    GOLD = FEEDBACK_COLOR
    RED = "#FF808C"

    # Terreno
    ROCK = "#8E4B3B"
    ROCK_EDGE = "#C37A58"
    ROCK_TOP = "#E3A076"
    ROCK_DOT = "#B16A50"

    GRAVITY_MARS = 3.71
    GRAVITY_EARTH = 9.81

    FRAME_MS = 20
    WORLD_WIDTH = 1500
    GROUND_Y = 440

    PLAYER_RADIUS = 13
    HORIZONTAL_SPEED = 125.0
    MAX_JUMP_SPEED = 12.0

    # Sobe o mundo na tela para a Ada não ficar atrás do COSMO
    WORLD_OFFSET_Y = -12

    # Consequência na nave: o traje tem pouco oxigênio. Ele gasta com o
    # tempo e cada queda gasta mais (a Ada se esforça para subir de novo).
    SUIT_O2_PER_SECOND = 0.6     # % por segundo
    SUIT_O2_PER_FALL = 12        # % por queda
    SUIT_LOW = 30                # abaixo disso, o COSMO avisa

    TEXTS = {
        "pt_BR": {
            "title": "GRAVIDADE MARCIANA",
            "chapter": "CAPÍTULO 02 — CHEGADA A MARTE",
            "objective": "Ajude a Ada a pular pelas pedras até chegar ao rover.",
            "gravity": "Gravidade",
            "earth": "Terra",
            "mars": "Marte",
            "jump_force": "Força do pulo",
            "jump_value": "{value:.1f} m/s",
            "instructions": (
                "Escolha a força do pulo. Use A e D ou as setas para andar."
            ),
            "jump": "PULAR",
            "reset": "REINICIAR",
            "back": "VOLTAR",
            "hint": "DICA DO COSMO",
            "hint_title": "COSMO — DICAS",
            "status_title": "COMO ESTÁ A MISSÃO",
            "status_ready": "Encontre um caminho até o rover.",
            "status_air": "A Ada está no ar!",
            "status_ground": "A Ada está num lugar seguro.",
            "status_fall": "A Ada caiu! Voltando para o último lugar seguro.",
            "status_success": "Chegamos ao rover! Missão cumprida.",
            "success": "MISSÃO CUMPRIDA",
            "success_detail": "A Ada chegou ao rover!",
            "continue": "CONTINUAR",
            "distance": "Distância até o rover: {value:.0f} m",
            "velocity": "Velocidade para cima: {value:.1f} m/s",
            "height": "Altura do pulo: {value:.1f} m",
            "checkpoint": "Lugar seguro!",
            "rover": "ROVER",
            "ada": "ADA",
            "platform": "PLATAFORMA",
            "hint_1": (
                "Em Marte, a gravidade puxa menos: só um pouco mais de um terço da gravidade da Terra."
            ),
            "hint_2": (
                "A Ada não muda nada. Ela só fica mais leve porque Marte puxa menos."
            ),
            "hint_3": (
                "Com a mesma força, você pula mais de 2 vezes e meia mais alto em Marte do que na Terra!"
            ),
            "hint_4": (
                "Pule mais forte para chegar às pedras altas. E cuidado ao andar para não passar do ponto!"
            ),
            "all_hints": "VOCÊ JÁ VIU TODAS AS DICAS",
            "cosmo_ready": (
                "COSMO: Vamos chegar até o rover! Em Marte, você pula bem mais alto com a mesma força."
            ),
            "cosmo_air": (
                "COSMO: Olha o seu pulo! A gravidade vai te freando na subida e te puxando de volta na descida."
            ),
            "cosmo_success": (
                "COSMO: Muito bem, Ada! Você usou a gravidade fraca de Marte para chegar ao rover."
            ),
            "cosmo_fall": (
                "COSMO: Não deu dessa vez. Vamos mudar a força do pulo e tentar de novo!"
            ),
            "comparison": "Gravidade: Terra x Marte",
            "weight": "Em Marte, você pesa só 38% do seu peso na Terra",
            "trajectory": "CAMINHO DO PULO",
            "legend": "Linha tracejada: pulo reto para cima, sem andar",
            "telemetry": "TELEMETRIA",
            "suit_o2": "Oxigênio do traje",
            "suit_refill": "O oxigênio do traje acabou! Troquei o cilindro, mas isso gastou oxigênio da nave.",
            "suit_low": "Cuidado: o oxigênio do traje está acabando. Cada queda gasta mais!",
            "o2_cost": "Para recarregar o traje, a nave gastou {value} de oxigênio.",
        },
        "en": {
            "title": "MARTIAN GRAVITY",
            "chapter": "CHAPTER 02 — ARRIVAL AT MARS",
            "objective": "Help Ada jump across the rocks to reach the rover.",
            "gravity": "Gravity",
            "earth": "Earth",
            "mars": "Mars",
            "jump_force": "Jump power",
            "jump_value": "{value:.1f} m/s",
            "instructions": (
                "Pick how hard to jump. Use A and D or the arrow keys to walk."
            ),
            "jump": "JUMP",
            "reset": "RESET",
            "back": "BACK",
            "hint": "COSMO'S HINT",
            "hint_title": "COSMO — TIPS",
            "status_title": "MISSION STATUS",
            "status_ready": "Find a path to the rover.",
            "status_air": "Ada is in the air!",
            "status_ground": "Ada is on a safe spot.",
            "status_fall": "Ada fell! Going back to the last safe spot.",
            "status_success": "We reached the rover! Mission complete.",
            "success": "MISSION COMPLETE",
            "success_detail": "Ada made it to the rover!",
            "continue": "CONTINUE",
            "distance": "Distance to rover: {value:.0f} m",
            "velocity": "Upward speed: {value:.1f} m/s",
            "height": "Jump height: {value:.1f} m",
            "checkpoint": "Safe spot reached!",
            "rover": "ROVER",
            "ada": "ADA",
            "platform": "PLATFORM",
            "hint_1": (
                "On Mars, gravity pulls less: just over a third of Earth's gravity."
            ),
            "hint_2": (
                "Ada doesn't change at all. She just feels lighter because Mars pulls less."
            ),
            "hint_3": (
                "With the same push, you jump more than 2.5 times higher on Mars than on Earth!"
            ),
            "hint_4": (
                "Jump harder to reach the tall rocks. And be careful when walking so you don't overshoot!"
            ),
            "all_hints": "YOU'VE SEEN ALL THE TIPS",
            "cosmo_ready": (
                "COSMO: Let's reach the rover! On Mars, you jump much higher with the same push."
            ),
            "cosmo_air": (
                "COSMO: Look at your jump! Gravity slows you down on the way up and pulls you back on the way down."
            ),
            "cosmo_success": (
                "COSMO: Great job, Ada! You used Mars's weak gravity to reach the rover."
            ),
            "cosmo_fall": (
                "COSMO: Not this time. Let's change how hard you jump and try again!"
            ),
            "comparison": "Gravity: Earth vs Mars",
            "weight": "On Mars, you weigh only 38% of your Earth weight",
            "trajectory": "JUMP PATH",
            "legend": "Dashed line: jumping straight up, without walking",
            "telemetry": "TELEMETRY",
            "suit_o2": "Suit oxygen",
            "suit_refill": "The suit ran out of oxygen! I swapped the tank, but that used the ship's oxygen.",
            "suit_low": "Careful: the suit is running low on oxygen. Every fall uses more!",
            "o2_cost": "To refill the suit, the ship used {value} oxygen.",
        },
    }

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None,
        language="pt_BR",
    ):
        super().__init__(master, bg=self.BG)

        self.on_complete = on_complete
        self.on_back = on_back
        self.language = self.normalize_language(language)

        self.running = True
        self.after_id = None
        self.last_frame = time.monotonic()
        self.completed_notified = False

        self.jump_var = tk.DoubleVar(value=7.0)

        self.hint_index = 0
        self.hint_text = tk.StringVar(value="")
        self.status_text = tk.StringVar()
        self.distance_text = tk.StringVar()
        self.velocity_text = tk.StringVar()
        self.height_text = tk.StringVar()

        self.keys_pressed = set()
        self.button_direction = 0
        self.camera_x = 0.0

        # Coordinates use meters in a simplified 2D environment.
        # Screen Y increases downward.
        # Ground/platform Y is the character's foot position.
        self.platforms = [
            (0, 240, 440),
            (290, 430, 427),
            (480, 620, 414),
            (670, 820, 425),
            (875, 1020, 407),
            (1070, 1230, 420),
            (1280, 1500, 440),
        ]

        self.rover_x = 1430
        self.rover_y = 440

        self.continue_button = None
        self.suit_o2 = 100.0
        self.suit_refills = 0
        self.notice = None          # (texto, até quando) aviso do COSMO
        self.reset_player()
        self.build_ui()
        self.bind_controls()
        self.refresh()
        self.animate()

    # ==================================================
    # LANGUAGE
    # ==================================================

    @staticmethod
    def normalize_language(language):
        value = str(language).lower().replace("-", "_")

        if value in ("pt", "pt_br", "portuguese"):
            return "pt_BR"

        return "en"

    def tr(self, key, **kwargs):
        text = self.TEXTS[self.language].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def set_language(self, language):
        """Troca o idioma redesenhando a parte fixa da tela."""
        self.language = self.normalize_language(language)
        self.canvas.delete("all")
        for button in self.static_buttons:
            button.destroy()
        self.build_static()
        self.refresh()

    # ==================================================
    # INTERFACE (identidade visual do jogo)
    # ==================================================

    def build_ui(self):
        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=self.BG,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Mantém o nome antigo usado pelo resto do código
        self.scene = self.canvas

        # Imagens (carregadas uma vez só)
        self.background_img = None
        if MARS_BACKGROUND.exists():
            img = tk.PhotoImage(file=str(MARS_BACKGROUND))
            factor = max(1, img.width() // WIDTH, img.height() // HEIGHT)
            self.background_img = img.subsample(factor) if factor > 1 else img

        self.ada_img = (
            fit_image(ADA_IMAGE, 34, 44) if ADA_IMAGE.exists() else None
        )

        self.rover_img = None
        if ROVER_IMAGE.exists():
            self.rover_img, self.rover_box = fit_content(ROVER_IMAGE, 90)

        self.static_buttons = []
        self.build_static()

    def build_static(self):
        """Partes que não se movem: fundo, título, painel e COSMO."""
        c = self.canvas

        if self.background_img is not None:
            c.create_image(0, 0, image=self.background_img, anchor="nw")

        # Tudo o que se move é desenhado logo acima deste marcador
        self.layer_marker = c.create_line(0, 0, 0, 0, state="hidden")

        draw_minigame_heading(c, self.tr("chapter"), self.tr("objective"))

        # ---------------- Painel ----------------
        draw_minigame_panel(c, self.tr("title").replace(" ", "\n", 1))
        x0, y0, x1, y1 = MINIGAME_PANEL
        cx = (x0 + x1) / 2
        left = x0 + 18
        text_w = (x1 - x0) - 36

        c.create_text(
            left, 106, anchor="nw", width=text_w,
            text=(
                f"{self.tr('earth')}: {self.GRAVITY_EARTH:.2f} m/s²\n"
                f"{self.tr('mars')}: {self.GRAVITY_MARS:.2f} m/s²"
            ),
            font=("Arial", 10, "bold"), fill=self.TEXT,
        )
        c.create_text(
            left, 142, anchor="nw", width=text_w,
            text=self.tr("weight"),
            font=("Arial", 9), fill=self.MUTED,
        )

        c.create_text(cx, 196, text=self.tr("jump_force"),
                      font=("Arial", 10), fill=self.MUTED)
        self.jump_value_item = c.create_text(
            cx, 217, font=("Arial", 16, "bold"), fill=self.CYAN,
        )
        self.jump_slider = CanvasSlider(
            c, x0 + 22, 243, (x1 - x0) - 44,
            from_=3.0, to=self.MAX_JUMP_SPEED, resolution=0.5,
            variable=self.jump_var, command=self.change_jump,
        )

        # Andar: segurar o botão (ou usar A/D e as setas)
        for text, direction, bx in (("◀", -1, cx - 42), ("▶", 1, cx + 42)):
            button = MenuButton(c, bx, 274, text, lambda: None,
                                width=76, height=32, font_size=13)
            c.tag_bind(button.tag, "<ButtonPress-1>",
                       lambda e, d=direction: self.set_button_direction(d))
            c.tag_bind(button.tag, "<ButtonRelease-1>",
                       lambda e: self.set_button_direction(0))
            self.static_buttons.append(button)

        self.jump_button = MenuButton(
            c, cx, 314, self.tr("jump"), self.jump,
            width=160, height=40, font_size=13, primary=True,
        )
        self.hint_button = MenuButton(
            c, cx, 354, self.tr("hint"), self.show_hint,
            width=160, height=32, font_size=10,
        )
        self.reset_button = MenuButton(
            c, cx, 390, self.tr("reset"), self.reset_mission,
            width=160, height=32, font_size=10,
        )
        self.static_buttons += [self.jump_button, self.hint_button,
                                self.reset_button]

        if self.on_back:
            self.back_button = MenuButton(
                c, cx, 426, self.tr("back"), self.go_back,
                width=160, height=32, font_size=10,
            )
            self.static_buttons.append(self.back_button)
            line_y = 454
        else:
            line_y = 418

        # Telemetria
        c.create_line(x0 + 18, line_y, x1 - 18, line_y,
                      fill="#24324F", width=2)
        c.create_text(left, line_y + 8, anchor="nw",
                      text=self.tr("telemetry"),
                      font=("Arial", 9, "bold"), fill=self.MUTED)
        self.telemetry_item = c.create_text(
            left, line_y + 26, anchor="nw", width=text_w,
            font=("Arial", 9), fill=self.TEXT,
        )

        # COSMO no canto inferior esquerdo
        self.hint = CosmoHint(c, right=SCENE_WIDTH - 20)

    # ==================================================
    # PLAYER STATE
    # ==================================================

    def reset_player(self):
        self.x = 65.0
        self.y = float(self.GROUND_Y)

        self.vx = 0.0
        self.vy = 0.0

        self.grounded = True
        self.completed = False

        self.checkpoint_x = 65.0
        self.checkpoint_y = float(self.GROUND_Y)
        self.checkpoint_index = 0

        self.jump_origin_y = self.y
        self.jump_peak = 0.0

        self.status_key = "status_ready"

    def reset_mission(self):
        self.reset_player()
        self.suit_o2 = 100.0
        self.suit_refills = 0
        self.notice = None

        self.keys_pressed.clear()
        self.button_direction = 0

        self.hint_index = 0
        self.hint_text.set("")
        self.hint_button.config(
            state="normal",
            text=self.tr("hint"),
        )

        self.completed_notified = False
        self.camera_x = 0.0
        self.last_frame = time.monotonic()

        self._hide_continue()
        self.refresh()

    # ==================================================
    # CONTROLS
    # ==================================================

    def bind_controls(self):
        root = self.winfo_toplevel()

        for key in ("a", "d", "Left", "Right"):
            root.bind(
                f"<KeyPress-{key}>",
                lambda event, k=key: self.set_key(k, True),
                add="+",
            )
            root.bind(
                f"<KeyRelease-{key}>",
                lambda event, k=key: self.set_key(k, False),
                add="+",
            )

        root.bind(
            "<KeyPress-space>",
            self.jump,
            add="+",
        )

        root.bind(
            "<FocusOut>",
            lambda event: self.release_controls(),
            add="+",
        )

    def set_key(self, key, pressed):
        if not self.running:
            return

        if pressed:
            self.keys_pressed.add(key)
        else:
            self.keys_pressed.discard(key)

    def set_button_direction(self, direction):
        self.button_direction = direction

    def release_controls(self):
        self.keys_pressed.clear()
        self.button_direction = 0

    def movement_direction(self):
        if self.button_direction:
            return self.button_direction

        right = (
            "d" in self.keys_pressed
            or "Right" in self.keys_pressed
        )
        left = (
            "a" in self.keys_pressed
            or "Left" in self.keys_pressed
        )

        return int(right) - int(left)

    def change_jump(self, value):
        self.refresh()

    def jump(self, event=None):
        if self.completed or not self.grounded:
            return

        self.vy = -self.jump_var.get()
        self.grounded = False

        self.jump_origin_y = self.y
        self.jump_peak = 0.0
        self.status_key = "status_air"

    # ==================================================
    # PHYSICS
    # ==================================================

    def physics_step(self, dt):
        if self.completed:
            return

        direction = self.movement_direction()

        self.vx = direction * self.HORIZONTAL_SPEED

        old_x = self.x
        old_y = self.y

        self.x += self.vx * dt
        self.x = max(
            self.PLAYER_RADIUS,
            min(
                self.x,
                self.WORLD_WIDTH - self.PLAYER_RADIUS,
            ),
        )

        if self.grounded:
            # Remain on a platform only while the
            # character's center is above its surface.
            support = self.find_support(self.x, self.y)

            if support is None:
                self.grounded = False
                self.vy = 0.0

        if not self.grounded:
            # Convert physical vertical acceleration
            # into screen coordinates.
            # 1 simulation meter = 10 screen pixels.
            self.vy += self.GRAVITY_MARS * dt

            self.y += self.vy * dt * 10.0

            self.jump_peak = max(
                self.jump_peak,
                (self.jump_origin_y - self.y) / 10.0,
            )

            if self.vy >= 0:
                landing = self.find_landing(
                    old_x,
                    old_y,
                    self.x,
                    self.y,
                )

                if landing is not None:
                    index, surface_y = landing

                    self.y = surface_y
                    self.vy = 0.0
                    self.grounded = True
                    self.status_key = "status_ground"

                    if index > self.checkpoint_index:
                        self.checkpoint_index = index
                        self.checkpoint_x = self.x
                        self.checkpoint_y = self.y

        if self.y > 620:
            self.respawn()

        if (
            self.grounded
            and abs(self.x - self.rover_x) < 42
            and abs(self.y - self.rover_y) < 20
        ):
            self.finish()

    def find_support(self, x, y):
        for index, (left, right, top) in enumerate(
            self.platforms
        ):
            if (
                left <= x <= right
                and abs(y - top) < 1.0
            ):
                return index

        return None

    def find_landing(
        self,
        old_x,
        old_y,
        new_x,
        new_y,
    ):
        for index, (left, right, top) in enumerate(
            self.platforms
        ):
            # Landing requires crossing the surface
            # from above while descending.
            if (
                old_y <= top <= new_y
                and left <= new_x <= right
            ):
                return index, top

        return None

    def respawn(self):
        self.x = self.checkpoint_x
        self.y = self.checkpoint_y

        self.vx = 0.0
        self.vy = 0.0
        self.grounded = True

        self.status_key = "status_fall"
        self.use_suit_o2(self.SUIT_O2_PER_FALL)

    def finish(self):
        if self.completed:
            return

        self.completed = True
        self.grounded = True
        self.vx = 0.0
        self.vy = 0.0

        self.status_key = "status_success"

        self._show_continue()

    def complete_mission(self):
        if not self.completed:
            return

        if self.completed_notified:
            return

        self.completed_notified = True
        self.stop()

        if self.on_complete:
            self.on_complete()

    # ==================================================
    # SCIENCE
    # ==================================================

    def maximum_jump_height(self):
        velocity = self.jump_var.get()

        return (
            velocity ** 2
            / (2 * self.GRAVITY_MARS)
        )

    def flight_time(self):
        return (
            2 * self.jump_var.get()
            / self.GRAVITY_MARS
        )

    def predicted_trajectory(self):
        velocity = self.jump_var.get()

        points = []

        duration = self.flight_time()

        for index in range(61):
            t = duration * index / 60

            vertical_displacement = (
                velocity * t
                - 0.5 * self.GRAVITY_MARS * t * t
            )

            x = self.x
            y = self.y - vertical_displacement * 10

            points.append((x, y))

        return points

    def show_hint(self):
        if self.hint_index >= 4:
            return

        self.hint_index += 1

        self.hint_text.set(
            self.tr(f"hint_{self.hint_index}")
        )

        if self.hint_index >= 4:
            self.hint_button.config(
                state="disabled",
                text=self.tr("all_hints"),
            )


    # ==================================================
    # OXIGÊNIO DO TRAJE (consequência na nave)
    # ==================================================

    def use_suit_o2(self, amount):
        was_low = self.suit_o2 < self.SUIT_LOW
        self.suit_o2 -= amount
        if self.suit_o2 <= 0:
            # Não termina o jogo: o COSMO troca o cilindro
            self.suit_o2 = 100.0
            self.suit_refills += 1
            self.notice = (self.tr("suit_refill"), time.monotonic() + 4)
        elif self.suit_o2 < self.SUIT_LOW and not was_low:
            self.notice = (self.tr("suit_low"), time.monotonic() + 3)

    def oxygen_cost(self):
        """Oxigênio da nave gasto para recarregar o traje."""
        cost = 1 + self.suit_refills
        if self.suit_o2 < 50:
            cost += 1
        return cost

    def mission_effects(self):
        """O que este minigame muda nos recursos da nave."""
        return {"oxygen": -self.oxygen_cost()}

    # Botão "Continuar" dentro da mensagem de vitória
    def _show_continue(self):
        self._hide_continue()
        self.continue_button = MenuButton(
            self.canvas, SCENE_WIDTH / 2, 262, self.tr("continue"),
            self.complete_mission, width=200, height=42, font_size=12,
            primary=True,
        )

    def _hide_continue(self):
        button = getattr(self, "continue_button", None)
        if button is not None:
            button.destroy()
        self.continue_button = None

    # ==================================================
    # DRAWING
    # ==================================================

    def draw_scene(self):
        canvas = self.canvas
        canvas.delete("dyn")

        width = SCENE_WIDTH
        height = HEIGHT

        # Follow Ada as she moves across the map.
        desired_camera = max(
            0,
            min(
                self.x - width * 0.35,
                self.WORLD_WIDTH - width,
            ),
        )

        self.camera_x += (
            desired_camera - self.camera_x
        ) * 0.12

        offset_y = self.WORLD_OFFSET_Y

        def screen(x, y):
            return (
                x - self.camera_x,
                y + offset_y,
            )

        def item(kind, *args, **kwargs):
            kwargs["tags"] = "dyn"
            return getattr(canvas, f"create_{kind}")(*args, **kwargs)

        # ------------------------------------------
        # MARTIAN TERRAIN
        # ------------------------------------------

        for index, (left, right, top) in enumerate(
            self.platforms
        ):
            x1, y1 = screen(left, top)
            x2, _ = screen(right, top)

            if x2 < 0 or x1 > width:
                continue

            x2 = min(x2, width)

            item("rectangle", x1, y1, x2, height,
                 fill=self.ROCK, outline=self.ROCK_EDGE, width=2)
            item("line", x1, y1, x2, y1, fill=self.ROCK_TOP, width=5)

            # Decorative rocks.
            for rock in range(3):
                rx = x1 + 18 + rock * 37

                if rx < x2 - 10:
                    item("oval", rx - 6, y1 - 7, rx + 8, y1 + 2,
                         fill=self.ROCK_DOT, outline="")

        # ------------------------------------------
        # PREDICTED JUMP
        # ------------------------------------------

        if self.grounded and not self.completed:
            coordinates = []

            for x, y in self.predicted_trajectory():
                sx, sy = screen(x, y)
                coordinates.extend((sx, sy))

            if len(coordinates) >= 4:
                item("line", *coordinates, fill=self.GOLD, width=2,
                     dash=(4, 5))

        # ------------------------------------------
        # ROVER
        # ------------------------------------------

        rover_x, rover_y = screen(self.rover_x, self.rover_y)

        if rover_x < width + 80:
            if self.rover_img is not None:
                bx0, by0, bx1, by1 = self.rover_box
                item("oval", rover_x - (bx1 - bx0) / 2, rover_y - 5,
                     rover_x + (bx1 - bx0) / 2, rover_y + 6,
                     fill="#3A1A12", outline="")
                item("image", rover_x - (bx0 + bx1) / 2, rover_y - by1,
                     image=self.rover_img, anchor="nw")
                label_y = rover_y - (by1 - by0) - 14
            else:
                item("rectangle", rover_x - 25, rover_y - 33,
                     rover_x + 25, rover_y - 10, fill="#D8B46E",
                     outline="#FFE4A9", width=2)
                for wheel_x in (rover_x - 17, rover_x + 17):
                    item("oval", wheel_x - 7, rover_y - 14, wheel_x + 7,
                         rover_y, fill="#35445A", outline=self.TEXT)
                label_y = rover_y - 50

            item("text", rover_x, label_y, text=self.tr("rover"),
                 fill=self.TEXT, font=("Arial", 10, "bold"))

        # ------------------------------------------
        # ADA
        # ------------------------------------------

        px, py = screen(self.x, self.y)

        if self.ada_img is not None:
            item("image", px, py + 2, image=self.ada_img, anchor="s")
            label_y = py - 52
        else:
            item("oval", px - 12, py - 37, px + 12, py - 13,
                 fill="#EAF2FF", outline=self.CYAN, width=2)
            item("rectangle", px - 9, py - 13, px + 9, py - 2,
                 fill="#EAF2FF", outline=self.CYAN)
            label_y = py - 49

        item("text", px, label_y, text=self.tr("ada"), fill=self.TEXT,
             font=("Arial", 9, "bold"))

        # ------------------------------------------
        # COSMO BRIEFING
        # ------------------------------------------

        notice = self.notice if self.notice and time.monotonic() < self.notice[1] else None
        if self.completed:
            briefing = (self.tr("cosmo_success") + " "
                        + self.tr("o2_cost", value=self.oxygen_cost()))
            color = self.GREEN
        elif notice:
            briefing, color = notice[0], self.GOLD
        elif self.status_key == "status_fall":
            briefing, color = self.tr("cosmo_fall"), self.GOLD
        elif not self.grounded:
            briefing, color = self.tr("cosmo_air"), self.TEXT
        elif self.hint_text.get():
            briefing, color = self.hint_text.get(), self.GOLD
        else:
            briefing, color = self.tr("cosmo_ready"), self.TEXT

        self.hint.set(briefing.replace("COSMO: ", ""), color)

        # O que se move fica acima do fundo e atrás do painel e do COSMO
        canvas.tag_raise("dyn", self.layer_marker)

        # ------------------------------------------
        # SUIT OXYGEN
        # ------------------------------------------

        gx0, gy0, gx1, gy1 = 470, 18, 668, 66
        low = self.suit_o2 < self.SUIT_LOW
        bar_color = self.RED if low else self.CYAN
        rounded_rect(canvas, gx0, gy0, gx1, gy1, r=12, fill=self.PANEL,
                     outline=bar_color, width=2, tags="dyn")
        item("text", gx0 + 12, gy0 + 15, anchor="w", text="🫁",
             font=("Segoe UI Emoji", 13), fill=bar_color)
        item("text", gx0 + 36, gy0 + 15, anchor="w",
             text=self.tr("suit_o2"), font=("Arial", 9, "bold"),
             fill=self.TEXT)
        item("text", gx1 - 12, gy0 + 15, anchor="e",
             text=f"{max(0, self.suit_o2):.0f}%", font=("Arial", 10, "bold"),
             fill=bar_color)
        item("rectangle", gx0 + 12, gy0 + 30, gx1 - 12, gy0 + 38,
             fill="#24324F", outline="")
        item("rectangle", gx0 + 12, gy0 + 30,
             gx0 + 12 + (gx1 - gx0 - 24) * max(0, self.suit_o2) / 100,
             gy0 + 38, fill=bar_color, outline="")

        # ------------------------------------------
        # SUCCESS OVERLAY
        # ------------------------------------------

        if self.completed:
            cx = width / 2
            rounded_rect(canvas, cx - 200, 150, cx + 200, 290, r=20,
                         fill=self.PANEL, outline=self.GREEN, width=2,
                         tags=("dyn", "success"))
            canvas.create_text(cx, 190, text=self.tr("success"),
                               fill=self.GREEN, tags=("dyn", "success"),
                               font=(font_or_fallback(TITLE_FONT), 20))
            canvas.create_text(cx, 228, text=self.tr("success_detail"),
                               fill=self.TEXT, tags=("dyn", "success"),
                               font=("Arial", 11))
            canvas.tag_raise("success")
            if self.continue_button is not None:
                canvas.tag_raise(self.continue_button.tag)

    # ==================================================
    # REFRESH
    # ==================================================

    def refresh(self):
        c = self.canvas

        c.itemconfigure(
            self.jump_value_item,
            text=self.tr("jump_value", value=self.jump_var.get()),
        )

        self.distance_text.set(
            self.tr("distance", value=max(0, self.rover_x - self.x) / 10)
        )
        self.velocity_text.set(self.tr("velocity", value=-self.vy + 0.0))
        self.height_text.set(self.tr("height", value=self.jump_peak))
        self.status_text.set(self.tr(self.status_key))

        c.itemconfigure(
            self.telemetry_item,
            text="\n".join((
                self.distance_text.get(),
                self.velocity_text.get(),
                self.height_text.get(),
            )),
        )

        self.jump_button.config(
            state=(
                "normal"
                if self.grounded and not self.completed
                else "disabled"
            )
        )

        self.draw_scene()

    # ==================================================
    # ANIMATION LOOP
    # ==================================================

    def animate(self):
        if not self.running:
            return

        now = time.monotonic()

        dt = min(
            now - self.last_frame,
            0.05,
        )

        self.last_frame = now

        # Smaller substeps improve landing detection.
        steps = max(1, math.ceil(dt / 0.005))
        step_dt = dt / steps

        for _ in range(steps):
            self.physics_step(step_dt)

        if not self.completed:
            self.use_suit_o2(self.SUIT_O2_PER_SECOND * dt)

        self.refresh()

        self.after_id = self.after(
            self.FRAME_MS,
            self.animate,
        )

    # ==================================================
    # LIFECYCLE
    # ==================================================

    def stop(self):
        self.running = False

        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

        self.release_controls()

    def go_back(self):
        self.stop()

        if self.on_back:
            self.on_back()

    def destroy(self):
        self.stop()
        super().destroy()


# ======================================================
# STANDALONE TEST: python -m puzzles.mars_gravity_ui
# ======================================================

if __name__ == "__main__":
    from core.ui import load_project_fonts

    root = tk.Tk()
    load_project_fonts()
    root.title("ASTRA — Mars Gravity")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    def completed():
        print("Mars gravity puzzle completed!")

    puzzle = MarsGravityUI(
        root,
        on_complete=completed,
        on_back=root.destroy,
        language="pt_BR",
    )

    puzzle.pack(
        fill="both",
        expand=True,
    )

    root.mainloop()
