
import math
import time
import tkinter as tk


class MarsGravityUI(tk.Frame):
    BG = "#081321"
    PANEL = "#142238"
    CARD = "#1B304B"
    TEXT = "#EAF2FF"
    MUTED = "#A5B7CF"
    CYAN = "#65D6FF"
    GREEN = "#77E6B6"
    GOLD = "#FFD17B"
    RED = "#FF808C"

    GRAVITY_MARS = 3.71
    GRAVITY_EARTH = 9.81

    FRAME_MS = 20
    WORLD_WIDTH = 1500
    GROUND_Y = 440

    PLAYER_RADIUS = 13
    HORIZONTAL_SPEED = 125.0
    MAX_JUMP_SPEED = 12.0

    TEXTS = {
        "pt_BR": {
            "title": "GRAVIDADE MARCIANA",
            "chapter": "CAPÍTULO 02 — CHEGADA A MARTE",
            "objective": "Ajude Ada a atravessar o terreno e alcançar o rover.",
            "gravity": "Gravidade",
            "earth": "Terra",
            "mars": "Marte",
            "jump_force": "Velocidade inicial do salto",
            "jump_value": "{value:.1f} m/s",
            "instructions": (
                "Ajuste a velocidade do salto e use A/D ou "
                "as setas para se movimentar."
            ),
            "jump": "SALTAR",
            "reset": "REINICIAR",
            "back": "VOLTAR",
            "hint": "PEDIR DICA AO COSMO",
            "hint_title": "COSMO — APOIO CIENTÍFICO",
            "status_title": "STATUS DA MISSÃO",
            "status_ready": "Encontre um caminho até o rover.",
            "status_air": "Ada está no ar.",
            "status_ground": "Ada está em uma superfície segura.",
            "status_fall": "Ada caiu! Retornando ao último ponto seguro.",
            "status_success": "Rover alcançado! Missão concluída.",
            "success": "MISSÃO CONCLUÍDA",
            "success_detail": "Ada conseguiu alcançar o rover.",
            "continue": "CONTINUAR",
            "distance": "Distância até o rover: {value:.0f} m",
            "velocity": "Velocidade vertical: {value:.1f} m/s",
            "height": "Altura do salto: {value:.1f} m",
            "checkpoint": "Ponto seguro alcançado!",
            "rover": "ROVER",
            "ada": "ADA",
            "platform": "PLATAFORMA",
            "hint_1": (
                "Em Marte, a aceleração gravitacional é de "
                "aproximadamente 3,71 m/s². Na Terra, é 9,81 m/s²."
            ),
            "hint_2": (
                "A massa de Ada não muda, mas seu peso é menor "
                "em Marte, porque a gravidade é mais fraca."
            ),
            "hint_3": (
                "A altura máxima de um salto vertical ideal é "
                "h = v² / (2g), em que v é a velocidade inicial "
                "e g é a aceleração gravitacional."
            ),
            "hint_4": (
                "Aumente a velocidade inicial para alcançar "
                "plataformas mais altas. Controle também o "
                "movimento horizontal para não ultrapassá-las."
            ),
            "all_hints": "TODAS AS DICAS EXIBIDAS",
            "cosmo_ready": (
                "COSMO: Precisamos alcançar o rover. "
                "A gravidade de Marte permitirá saltos mais altos "
                "com a mesma velocidade inicial."
            ),
            "cosmo_air": (
                "COSMO: Observe sua trajetória. A gravidade "
                "reduz sua velocidade vertical durante a subida "
                "e acelera a descida."
            ),
            "cosmo_success": (
                "COSMO: Excelente, Ada! Você utilizou as condições "
                "gravitacionais de Marte para alcançar o módulo."
            ),
            "cosmo_fall": (
                "COSMO: A trajetória não foi suficiente. "
                "Podemos ajustar a velocidade inicial e tentar novamente."
            ),
            "comparison": "Comparação gravitacional",
            "weight": "Peso relativo em Marte: aproximadamente 38%",
            "trajectory": "TRAJETÓRIA PREVISTA",
            "legend": "Linha tracejada: salto ideal sem movimento horizontal",
        },
        "en": {
            "title": "MARTIAN GRAVITY",
            "chapter": "CHAPTER 02 — ARRIVAL AT MARS",
            "objective": "Help Ada cross the terrain and reach the rover.",
            "gravity": "Gravity",
            "earth": "Earth",
            "mars": "Mars",
            "jump_force": "Initial jump velocity",
            "jump_value": "{value:.1f} m/s",
            "instructions": (
                "Adjust the jump velocity and use A/D "
                "or the arrow keys to move."
            ),
            "jump": "JUMP",
            "reset": "RESET",
            "back": "BACK",
            "hint": "ASK COSMO FOR A HINT",
            "hint_title": "COSMO — SCIENCE SUPPORT",
            "status_title": "MISSION STATUS",
            "status_ready": "Find a path to the rover.",
            "status_air": "Ada is airborne.",
            "status_ground": "Ada is on a safe surface.",
            "status_fall": "Ada fell! Returning to the last safe position.",
            "status_success": "Rover reached! Mission complete.",
            "success": "MISSION COMPLETE",
            "success_detail": "Ada successfully reached the rover.",
            "continue": "CONTINUE",
            "distance": "Distance to rover: {value:.0f} m",
            "velocity": "Vertical velocity: {value:.1f} m/s",
            "height": "Jump height: {value:.1f} m",
            "checkpoint": "Safe checkpoint reached!",
            "rover": "ROVER",
            "ada": "ADA",
            "platform": "PLATFORM",
            "hint_1": (
                "On Mars, gravitational acceleration is "
                "approximately 3.71 m/s². On Earth, it is 9.81 m/s²."
            ),
            "hint_2": (
                "Ada's mass remains unchanged, but her weight "
                "is lower on Mars because gravity is weaker."
            ),
            "hint_3": (
                "The maximum height of an ideal vertical jump is "
                "h = v² / (2g), where v is initial velocity "
                "and g is gravitational acceleration."
            ),
            "hint_4": (
                "Increase the initial velocity to reach higher "
                "platforms. Control horizontal movement so "
                "you do not overshoot them."
            ),
            "all_hints": "ALL HINTS REVEALED",
            "cosmo_ready": (
                "COSMO: We must reach the rover. "
                "Martian gravity allows higher jumps "
                "with the same initial velocity."
            ),
            "cosmo_air": (
                "COSMO: Observe your trajectory. Gravity "
                "reduces vertical velocity during ascent "
                "and accelerates the descent."
            ),
            "cosmo_success": (
                "COSMO: Excellent, Ada! You used the gravitational "
                "conditions on Mars to reach the module."
            ),
            "cosmo_fall": (
                "COSMO: That trajectory was insufficient. "
                "We can adjust the initial velocity and try again."
            ),
            "comparison": "Gravity comparison",
            "weight": "Relative weight on Mars: approximately 38%",
            "trajectory": "PREDICTED TRAJECTORY",
            "legend": "Dashed line: ideal jump without horizontal movement",
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
        self.language = self.normalize_language(language)

        self.title_label.config(text=self.tr("title"))
        self.chapter_label.config(text=self.tr("chapter"))
        self.objective_label.config(text=self.tr("objective"))

        self.gravity_label.config(text=self.tr("comparison"))
        self.earth_label.config(
            text=f"{self.tr('earth')}: {self.GRAVITY_EARTH:.2f} m/s²"
        )
        self.mars_label.config(
            text=f"{self.tr('mars')}: {self.GRAVITY_MARS:.2f} m/s²"
        )
        self.weight_label.config(text=self.tr("weight"))

        self.jump_label.config(text=self.tr("jump_force"))
        self.instructions_label.config(text=self.tr("instructions"))
        self.jump_button.config(text=self.tr("jump"))
        self.reset_button.config(text=self.tr("reset"))

        self.hint_title.config(text=self.tr("hint_title"))
        self.status_title.config(text=self.tr("status_title"))

        if self.on_back:
            self.back_button.config(text=self.tr("back"))

        self.continue_button.config(text=self.tr("continue"))

        if self.hint_index >= 4:
            self.hint_button.config(text=self.tr("all_hints"))
        else:
            self.hint_button.config(text=self.tr("hint"))

        if self.hint_index:
            self.hint_text.set(
                self.tr(f"hint_{self.hint_index}")
            )

        self.refresh()

    # ==================================================
    # UI HELPERS
    # ==================================================

    def make_label(
        self,
        parent,
        text=None,
        variable=None,
        size=10,
        color=None,
        bold=False,
        wrap=0,
    ):
        options = {
            "bg": self.PANEL,
            "fg": color or self.TEXT,
            "font": (
                "Arial",
                size,
                "bold" if bold else "normal",
            ),
            "anchor": "w",
            "justify": "left",
        }

        if wrap:
            options["wraplength"] = wrap

        if variable is not None:
            options["textvariable"] = variable
        else:
            options["text"] = text

        return tk.Label(parent, **options)

    def make_button(
        self,
        parent,
        text,
        command,
        color=None,
        foreground=None,
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color or self.CARD,
            fg=foreground or self.TEXT,
            activebackground=self.CYAN,
            activeforeground=self.BG,
            disabledforeground="#708199",
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            pady=8,
        )

    def section(self, text):
        label = self.make_label(
            self.content,
            text=text,
            size=9,
            color=self.MUTED,
            bold=True,
        )
        label.pack(
            anchor="w",
            padx=14,
            pady=(15, 5),
        )
        return label

    # ==================================================
    # INTERFACE
    # ==================================================

    def build_ui(self):
        self.scene = tk.Canvas(
            self,
            bg=self.BG,
            highlightthickness=0,
        )
        self.scene.pack(
            side="left",
            fill="both",
            expand=True,
        )

        self.panel = tk.Frame(
            self,
            bg=self.PANEL,
            width=300,
        )
        self.panel.pack(side="right", fill="y")
        self.panel.pack_propagate(False)

        self.scroll = tk.Canvas(
            self.panel,
            bg=self.PANEL,
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(
            self.panel,
            orient="vertical",
            command=self.scroll.yview,
        )
        self.scroll.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")
        self.scroll.pack(
            side="left",
            fill="both",
            expand=True,
        )

        self.content = tk.Frame(
            self.scroll,
            bg=self.PANEL,
        )

        window_id = self.scroll.create_window(
            (0, 0),
            window=self.content,
            anchor="nw",
        )

        self.content.bind(
            "<Configure>",
            lambda event: self.scroll.configure(
                scrollregion=self.scroll.bbox("all")
            ),
        )

        self.scroll.bind(
            "<Configure>",
            lambda event: self.scroll.itemconfigure(
                window_id,
                width=event.width,
            ),
        )

        self.scroll.bind(
            "<MouseWheel>",
            lambda event: self.scroll.yview_scroll(
                -int(event.delta / 120),
                "units",
            ),
        )

        self.title_label = self.make_label(
            self.content,
            text=self.tr("title"),
            size=16,
            color=self.CYAN,
            bold=True,
        )
        self.title_label.pack(
            anchor="w",
            padx=14,
            pady=(16, 4),
        )

        self.chapter_label = self.make_label(
            self.content,
            text=self.tr("chapter"),
            size=9,
            color=self.MUTED,
        )
        self.chapter_label.pack(
            anchor="w",
            padx=14,
        )

        self.objective_label = self.make_label(
            self.content,
            text=self.tr("objective"),
            wrap=260,
        )
        self.objective_label.pack(
            anchor="w",
            padx=14,
            pady=(15, 10),
        )

        self.gravity_label = self.section(
            self.tr("comparison")
        )

        self.earth_label = self.make_label(
            self.content,
            text=(
                f"{self.tr('earth')}: "
                f"{self.GRAVITY_EARTH:.2f} m/s²"
            ),
        )
        self.earth_label.pack(anchor="w", padx=14)

        self.mars_label = self.make_label(
            self.content,
            text=(
                f"{self.tr('mars')}: "
                f"{self.GRAVITY_MARS:.2f} m/s²"
            ),
            color=self.GOLD,
        )
        self.mars_label.pack(
            anchor="w",
            padx=14,
            pady=4,
        )

        self.weight_label = self.make_label(
            self.content,
            text=self.tr("weight"),
            wrap=260,
            color=self.MUTED,
        )
        self.weight_label.pack(
            anchor="w",
            padx=14,
        )

        self.jump_label = self.section(
            self.tr("jump_force")
        )

        self.jump_value_label = self.make_label(
            self.content,
            color=self.CYAN,
            size=12,
            bold=True,
        )
        self.jump_value_label.pack(
            anchor="w",
            padx=14,
        )

        self.jump_slider = tk.Scale(
            self.content,
            from_=3.0,
            to=self.MAX_JUMP_SPEED,
            resolution=0.5,
            orient="horizontal",
            variable=self.jump_var,
            command=self.change_jump,
            showvalue=False,
            bg=self.PANEL,
            fg=self.TEXT,
            troughcolor=self.CARD,
            highlightthickness=0,
        )
        self.jump_slider.pack(
            fill="x",
            padx=14,
        )

        self.instructions_label = self.make_label(
            self.content,
            text=self.tr("instructions"),
            size=9,
            color=self.MUTED,
            wrap=260,
        )
        self.instructions_label.pack(
            anchor="w",
            padx=14,
            pady=(10, 5),
        )

        movement = tk.Frame(
            self.content,
            bg=self.PANEL,
        )
        movement.pack(
            fill="x",
            padx=14,
            pady=5,
        )

        self.left_button = self.make_button(
            movement,
            "◀",
            lambda: None,
        )
        self.right_button = self.make_button(
            movement,
            "▶",
            lambda: None,
        )

        self.left_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
        )
        self.right_button.pack(
            side="left",
            fill="x",
            expand=True,
        )

        self.left_button.bind(
            "<ButtonPress-1>",
            lambda event: self.set_button_direction(-1),
        )
        self.left_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.set_button_direction(0),
        )
        self.right_button.bind(
            "<ButtonPress-1>",
            lambda event: self.set_button_direction(1),
        )
        self.right_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.set_button_direction(0),
        )

        self.jump_button = self.make_button(
            self.content,
            self.tr("jump"),
            self.jump,
            self.CYAN,
            self.BG,
        )
        self.jump_button.pack(
            fill="x",
            padx=14,
            pady=(8, 5),
        )

        self.section("TELEMETRY / TELEMETRIA")

        for variable in (
            self.distance_text,
            self.velocity_text,
            self.height_text,
        ):
            self.make_label(
                self.content,
                variable=variable,
                size=9,
            ).pack(
                anchor="w",
                padx=14,
                pady=3,
            )

        self.hint_title = self.section(
            self.tr("hint_title")
        )

        self.hint_button = self.make_button(
            self.content,
            self.tr("hint"),
            self.show_hint,
        )
        self.hint_button.pack(
            fill="x",
            padx=14,
            pady=5,
        )

        self.make_label(
            self.content,
            variable=self.hint_text,
            color=self.GOLD,
            wrap=260,
            size=9,
        ).pack(
            anchor="w",
            padx=14,
            pady=5,
        )

        self.status_title = self.section(
            self.tr("status_title")
        )

        self.make_label(
            self.content,
            variable=self.status_text,
            color=self.GREEN,
            wrap=260,
            size=9,
        ).pack(
            anchor="w",
            padx=14,
            pady=5,
        )

        self.continue_button = self.make_button(
            self.content,
            self.tr("continue"),
            self.complete_mission,
            self.GREEN,
            self.BG,
        )
        self.continue_button.pack(
            fill="x",
            padx=14,
            pady=(15, 5),
        )
        self.continue_button.pack_forget()

        self.reset_button = self.make_button(
            self.content,
            self.tr("reset"),
            self.reset_mission,
        )
        self.reset_button.pack(
            fill="x",
            padx=14,
            pady=(10, 5),
        )

        if self.on_back:
            self.back_button = self.make_button(
                self.content,
                self.tr("back"),
                self.go_back,
            )
            self.back_button.pack(
                fill="x",
                padx=14,
                pady=(5, 15),
            )

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

        self.keys_pressed.clear()
        self.button_direction = 0

        self.hint_index = 0
        self.hint_text.set("")
        self.hint_button.configure(
            state="normal",
            text=self.tr("hint"),
        )

        self.completed_notified = False
        self.camera_x = 0.0
        self.last_frame = time.monotonic()

        self.continue_button.pack_forget()
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

    def finish(self):
        if self.completed:
            return

        self.completed = True
        self.grounded = True
        self.vx = 0.0
        self.vy = 0.0

        self.status_key = "status_success"

        self.continue_button.pack(
            fill="x",
            padx=14,
            pady=(15, 5),
            before=self.reset_button,
        )

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
            self.hint_button.configure(
                state="disabled",
                text=self.tr("all_hints"),
            )

    # ==================================================
    # DRAWING
    # ==================================================

    def draw_scene(self):
        canvas = self.scene
        canvas.delete("all")

        width = max(canvas.winfo_width(), 400)
        height = max(canvas.winfo_height(), 400)

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

        offset_y = max(0, (height - 560) / 2)

        def screen(x, y):
            return (
                x - self.camera_x,
                y + offset_y,
            )

        # ------------------------------------------
        # SKY
        # ------------------------------------------

        for index in range(90):
            sx = (
                index * 193 + 47
            ) % max(width, 1)

            sy = (
                index * 79 + 31
            ) % max(height, 1)

            canvas.create_oval(
                sx,
                sy,
                sx + 1.5,
                sy + 1.5,
                fill="#43516C",
                outline="",
            )

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

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                height,
                fill="#8E4B3B",
                outline="#C37A58",
                width=2,
            )

            canvas.create_line(
                x1,
                y1,
                x2,
                y1,
                fill="#E3A076",
                width=5,
            )

            # Decorative rocks.
            for rock in range(3):
                rx = x1 + 18 + rock * 37

                if rx < x2 - 10:
                    canvas.create_oval(
                        rx - 6,
                        y1 - 7,
                        rx + 8,
                        y1 + 2,
                        fill="#B16A50",
                        outline="",
                    )

        # ------------------------------------------
        # PREDICTED JUMP
        # ------------------------------------------

        if self.grounded and not self.completed:
            trajectory = self.predicted_trajectory()

            coordinates = []

            for x, y in trajectory:
                sx, sy = screen(x, y)
                coordinates.extend((sx, sy))

            if len(coordinates) >= 4:
                canvas.create_line(
                    *coordinates,
                    fill=self.GOLD,
                    width=2,
                    dash=(4, 5),
                )

        # ------------------------------------------
        # ROVER
        # ------------------------------------------

        rover_x, rover_y = screen(
            self.rover_x,
            self.rover_y,
        )

        canvas.create_rectangle(
            rover_x - 25,
            rover_y - 33,
            rover_x + 25,
            rover_y - 10,
            fill="#D8B46E",
            outline="#FFE4A9",
            width=2,
        )

        for wheel_x in (
            rover_x - 17,
            rover_x + 17,
        ):
            canvas.create_oval(
                wheel_x - 7,
                rover_y - 14,
                wheel_x + 7,
                rover_y,
                fill="#35445A",
                outline=self.TEXT,
            )

        canvas.create_line(
            rover_x,
            rover_y - 33,
            rover_x,
            rover_y - 60,
            fill=self.TEXT,
            width=2,
        )

        canvas.create_oval(
            rover_x - 5,
            rover_y - 66,
            rover_x + 5,
            rover_y - 56,
            fill=self.CYAN,
            outline="",
        )

        canvas.create_text(
            rover_x,
            rover_y - 80,
            text=self.tr("rover"),
            fill=self.GREEN,
            font=("Arial", 11, "bold"),
        )

        # ------------------------------------------
        # ADA
        # ------------------------------------------

        px, py = screen(self.x, self.y)

        # Helmet
        canvas.create_oval(
            px - 12,
            py - 37,
            px + 12,
            py - 13,
            fill="#EAF2FF",
            outline=self.CYAN,
            width=2,
        )

        # Visor
        canvas.create_oval(
            px - 8,
            py - 31,
            px + 8,
            py - 19,
            fill="#65B6D6",
            outline="",
        )

        # Suit
        canvas.create_rectangle(
            px - 9,
            py - 13,
            px + 9,
            py - 2,
            fill="#EAF2FF",
            outline=self.CYAN,
        )

        # Boots
        canvas.create_line(
            px - 6,
            py - 2,
            px - 6,
            py,
            fill=self.GOLD,
            width=5,
        )
        canvas.create_line(
            px + 6,
            py - 2,
            px + 6,
            py,
            fill=self.GOLD,
            width=5,
        )

        canvas.create_text(
            px,
            py - 49,
            text=self.tr("ada"),
            fill=self.TEXT,
            font=("Arial", 9, "bold"),
        )

        # ------------------------------------------
        # HUD
        # ------------------------------------------

        canvas.create_text(
            18,
            18,
            text=self.tr("title"),
            fill=self.CYAN,
            anchor="nw",
            font=("Arial", 17, "bold"),
        )

        canvas.create_text(
            18,
            50,
            text=(
                f"{self.tr('mars')}: "
                f"{self.GRAVITY_MARS:.2f} m/s²"
            ),
            fill=self.GOLD,
            anchor="nw",
            font=("Arial", 11),
        )

        canvas.create_text(
            18,
            74,
            text=(
                f"{self.tr('jump_force')}: "
                f"{self.jump_var.get():.1f} m/s"
            ),
            fill=self.TEXT,
            anchor="nw",
            font=("Arial", 10),
        )

        # ------------------------------------------
        # COSMO BRIEFING
        # ------------------------------------------

        if self.completed:
            briefing = self.tr("cosmo_success")
        elif self.status_key == "status_fall":
            briefing = self.tr("cosmo_fall")
        elif not self.grounded:
            briefing = self.tr("cosmo_air")
        else:
            briefing = self.tr("cosmo_ready")

        canvas.create_rectangle(
            10,
            height - 90,
            width - 10,
            height - 10,
            fill=self.PANEL,
            outline=self.CARD,
            width=2,
        )

        canvas.create_text(
            22,
            height - 76,
            text=self.tr("hint_title"),
            fill=self.CYAN,
            anchor="nw",
            font=("Arial", 9, "bold"),
        )

        canvas.create_text(
            22,
            height - 53,
            text=briefing,
            fill=self.TEXT,
            anchor="nw",
            width=width - 48,
            font=("Arial", 9),
        )

        # ------------------------------------------
        # SUCCESS OVERLAY
        # ------------------------------------------

        if self.completed:
            canvas.create_rectangle(
                width / 2 - 190,
                height * 0.25 - 30,
                width / 2 + 190,
                height * 0.25 + 95,
                fill=self.PANEL,
                outline=self.GREEN,
                width=2,
            )

            canvas.create_text(
                width / 2,
                height * 0.25,
                text=self.tr("success"),
                fill=self.GREEN,
                font=("Arial", 19, "bold"),
            )

            canvas.create_text(
                width / 2,
                height * 0.25 + 45,
                text=self.tr("success_detail"),
                fill=self.TEXT,
                font=("Arial", 10),
            )

    # ==================================================
    # REFRESH
    # ==================================================

    def refresh(self):
        self.jump_value_label.configure(
            text=self.tr(
                "jump_value",
                value=self.jump_var.get(),
            )
        )

        self.distance_text.set(
            self.tr(
                "distance",
                value=max(0, self.rover_x - self.x) / 10,
            )
        )

        self.velocity_text.set(
            self.tr(
                "velocity",
                value=-self.vy,
            )
        )

        self.height_text.set(
            self.tr(
                "height",
                value=self.jump_peak,
            )
        )

        self.status_text.set(
            self.tr(self.status_key)
        )

        self.jump_button.configure(
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
# STANDALONE TEST
# ======================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ASTRA — Mars Gravity")
    root.geometry("1200x700")
    root.minsize(900, 550)

    def completed():
        print("Mars gravity puzzle completed!")

    puzzle = MarsGravityUI(
        root,
        on_complete=completed,
        language="pt_BR",
    )

    puzzle.pack(
        fill="both",
        expand=True,
    )

    root.mainloop()
