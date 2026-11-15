
import math
import time
import tkinter as tk
from copy import deepcopy

from puzzles.gravity_assist import GravityAssistPuzzle


class GravityAssistUI(tk.Frame):
    BG = "#081321"
    PANEL = "#142238"
    CARD = "#1B304B"
    TEXT = "#EAF2FF"
    MUTED = "#A5B7CF"
    CYAN = "#65D6FF"
    GREEN = "#77E6B6"
    GOLD = "#FFD17B"
    RED = "#FF808C"
    PURPLE = "#B9A0FF"

    FRAME_MS = 30
    SIMULATION_SPEED = 0.0015

    HINTS = (
        "Gravity pulls the spacecraft toward the planet. "
        "The closer it gets, the stronger the acceleration.",

        "A gravity assist changes the direction of the "
        "spacecraft's planet-relative velocity. Because "
        "the planet is moving around the Sun, this can "
        "also change the spacecraft's Sun-relative speed.",

        "To prepare the return transfer, try losing "
        "heliocentric speed rather than gaining it.",

        "Try an approach distance of 20 planetary radii "
        "and pass on the RIGHT side of both planets. "
        "No thruster correction is required."
    )

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=self.BG)

        self.puzzle = GravityAssistPuzzle()
        self.on_complete = on_complete
        self.on_back = on_back

        self.running = True
        self.after_id = None
        self.last_frame = time.monotonic()
        self.completed_notified = False

        self.hint_index = 0
        self.predicted_trajectory = []

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_scale = 3.0

        self.keys_pressed = set()
        self.button_steering = 0

        self.approach_var = tk.DoubleVar(value=20.0)
        self.side_var = tk.IntVar(value=-1)

        self.planet_var = tk.StringVar()
        self.approach_text = tk.StringVar()
        self.speed_text = tk.StringVar()
        self.relative_text = tk.StringVar()
        self.distance_text = tk.StringVar()
        self.gravity_text = tk.StringVar()
        self.fuel_text = tk.StringVar()
        self.status_text = tk.StringVar()
        self.history_text = tk.StringVar()
        self.hint_text = tk.StringVar()
        self.result_text = tk.StringVar()

        self.build_ui()
        self.bind_controls()

        self.update_prediction()
        self.refresh()
        self.animate()

    # ==================================================
    # WIDGET HELPERS
    # ==================================================

    def make_label(
        self,
        parent,
        value,
        size=10,
        color=None,
        bold=False,
        wrap=0
    ):
        options = {
            "bg": self.PANEL,
            "fg": color or self.TEXT,
            "font": (
                "Arial",
                size,
                "bold" if bold else "normal"
            ),
            "anchor": "w",
            "justify": "left"
        }

        if wrap:
            options["wraplength"] = wrap

        if isinstance(value, tk.Variable):
            options["textvariable"] = value
        else:
            options["text"] = value

        return tk.Label(parent, **options)

    def make_button(
        self,
        parent,
        text,
        command,
        color=None,
        foreground=None
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
            pady=8
        )

    def section(self, title):
        self.make_label(
            self.content,
            title,
            9,
            self.MUTED,
            True
        ).pack(
            anchor="w",
            padx=14,
            pady=(13, 5)
        )

    # ==================================================
    # INTERFACE
    # ==================================================

    def build_ui(self):
        self.scene = tk.Canvas(
            self,
            bg=self.BG,
            highlightthickness=0
        )
        self.scene.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.panel = tk.Frame(
            self,
            bg=self.PANEL,
            width=285
        )
        self.panel.pack(
            side="right",
            fill="y"
        )
        self.panel.pack_propagate(False)

        self.scroll = tk.Canvas(
            self.panel,
            bg=self.PANEL,
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = tk.Scrollbar(
            self.panel,
            orient="vertical",
            command=self.scroll.yview
        )

        self.scroll.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )
        self.scroll.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.content = tk.Frame(
            self.scroll,
            bg=self.PANEL
        )

        self.window_id = self.scroll.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            lambda e: self.scroll.configure(
                scrollregion=self.scroll.bbox("all")
            )
        )

        self.scroll.bind(
            "<Configure>",
            lambda e: self.scroll.itemconfigure(
                self.window_id,
                width=e.width
            )
        )

        self.scroll.bind(
            "<MouseWheel>",
            self.mousewheel
        )
        self.content.bind(
            "<MouseWheel>",
            self.mousewheel
        )

        self.make_label(
            self.content,
            "GRAVITY ASSIST",
            17,
            self.CYAN,
            True
        ).pack(
            anchor="w",
            padx=14,
            pady=(16, 3)
        )

        self.make_label(
            self.content,
            "CHAPTER 08 — RETURN HOME",
            9,
            self.MUTED
        ).pack(
            anchor="w",
            padx=14
        )

        self.make_label(
            self.content,
            self.planet_var,
            13,
            self.TEXT,
            True
        ).pack(
            anchor="w",
            padx=14,
            pady=(12, 2)
        )

        self.section("APPROACH DISTANCE")

        self.make_label(
            self.content,
            self.approach_text,
            10,
            self.CYAN
        ).pack(
            anchor="w",
            padx=14
        )

        self.approach_slider = tk.Scale(
            self.content,
            from_=self.puzzle.MIN_IMPACT,
            to=self.puzzle.MAX_IMPACT,
            resolution=0.5,
            orient="horizontal",
            variable=self.approach_var,
            command=self.change_approach,
            showvalue=False,
            bg=self.PANEL,
            fg=self.TEXT,
            troughcolor=self.CARD,
            highlightthickness=0
        )
        self.approach_slider.pack(
            fill="x",
            padx=14
        )

        self.section("PASSING SIDE")

        side_frame = tk.Frame(
            self.content,
            bg=self.PANEL
        )
        side_frame.pack(
            fill="x",
            padx=14
        )

        self.side_buttons = []

        for value, text in (
            (-1, "LEFT"),
            (1, "RIGHT")
        ):
            radio = tk.Radiobutton(
                side_frame,
                text=text,
                value=value,
                variable=self.side_var,
                command=self.change_side,
                bg=self.PANEL,
                fg=self.TEXT,
                selectcolor=self.CARD,
                activebackground=self.PANEL,
                activeforeground=self.CYAN
            )
            radio.pack(
                side="left",
                padx=(0, 12)
            )
            self.side_buttons.append(radio)

        self.start_button = self.make_button(
            self.content,
            "START FLYBY",
            self.start_flyby,
            self.CYAN,
            self.BG
        )
        self.start_button.pack(
            fill="x",
            padx=14,
            pady=(12, 4)
        )

        self.section("TRAJECTORY CORRECTION")

        self.make_label(
            self.content,
            "Hold A / D or the buttons to steer.",
            9,
            self.MUTED,
            wrap=240
        ).pack(
            anchor="w",
            padx=14
        )

        thrust_frame = tk.Frame(
            self.content,
            bg=self.PANEL
        )
        thrust_frame.pack(
            fill="x",
            padx=14,
            pady=(7, 3)
        )

        self.left_button = self.make_button(
            thrust_frame,
            "LEFT",
            lambda: None
        )
        self.right_button = self.make_button(
            thrust_frame,
            "RIGHT",
            lambda: None
        )

        self.left_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4)
        )
        self.right_button.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.left_button.bind(
            "<ButtonPress-1>",
            lambda e: self.set_button_thrust(-1)
        )
        self.left_button.bind(
            "<ButtonRelease-1>",
            lambda e: self.set_button_thrust(0)
        )

        self.right_button.bind(
            "<ButtonPress-1>",
            lambda e: self.set_button_thrust(1)
        )
        self.right_button.bind(
            "<ButtonRelease-1>",
            lambda e: self.set_button_thrust(0)
        )

        self.section("LIVE PHYSICS")

        for variable in (
            self.speed_text,
            self.relative_text,
            self.distance_text,
            self.gravity_text,
            self.fuel_text
        ):
            self.make_label(
                self.content,
                variable,
                9,
                wrap=240
            ).pack(
                anchor="w",
                padx=14,
                pady=3
            )

        self.fuel_bar = tk.Canvas(
            self.content,
            height=12,
            bg=self.CARD,
            highlightthickness=0
        )
        self.fuel_bar.pack(
            fill="x",
            padx=14,
            pady=(8, 6)
        )

        self.next_button = self.make_button(
            self.content,
            "CONTINUE TO VENUS",
            self.next_encounter,
            self.GREEN,
            self.BG
        )
        self.next_button.pack(
            fill="x",
            padx=14,
            pady=5
        )

        self.section("COSMO — SCIENCE SUPPORT")

        self.hint_button = self.make_button(
            self.content,
            "ASK COSMO FOR A HINT",
            self.show_hint
        )
        self.hint_button.pack(
            fill="x",
            padx=14,
            pady=(0, 8)
        )

        self.make_label(
            self.content,
            self.hint_text,
            9,
            self.GOLD,
            wrap=240
        ).pack(
            anchor="w",
            padx=14
        )

        self.section("MISSION LOG")

        self.make_label(
            self.content,
            self.history_text,
            9,
            wrap=240
        ).pack(
            anchor="w",
            padx=14
        )

        self.section("MISSION RESULT")

        self.make_label(
            self.content,
            self.result_text,
            9,
            self.GREEN,
            wrap=240
        ).pack(
            anchor="w",
            padx=14
        )

        self.make_label(
            self.content,
            self.status_text,
            9,
            self.GOLD,
            wrap=240
        ).pack(
            anchor="w",
            padx=14,
            pady=(10, 12)
        )

        self.make_button(
            self.content,
            "RESET MISSION",
            self.reset_mission
        ).pack(
            fill="x",
            padx=14,
            pady=(0, 8)
        )

        if self.on_back:
            self.make_button(
                self.content,
                "BACK",
                self.go_back
            ).pack(
                fill="x",
                padx=14,
                pady=(0, 15)
            )

    def mousewheel(self, event):
        self.scroll.yview_scroll(
            -int(event.delta / 120),
            "units"
        )

    # ==================================================
    # PLAYER CONTROLS
    # ==================================================

    def bind_controls(self):
        self.master.bind(
            "<KeyPress-a>",
            lambda e: self.set_key("a", True),
            add="+"
        )
        self.master.bind(
            "<KeyRelease-a>",
            lambda e: self.set_key("a", False),
            add="+"
        )
        self.master.bind(
            "<KeyPress-d>",
            lambda e: self.set_key("d", True),
            add="+"
        )
        self.master.bind(
            "<KeyRelease-d>",
            lambda e: self.set_key("d", False),
            add="+"
        )
        self.master.bind(
            "<FocusOut>",
            lambda e: self.release_thrust(),
            add="+"
        )

    def set_key(self, key, pressed):
        if pressed:
            self.keys_pressed.add(key)
        else:
            self.keys_pressed.discard(key)

        self.update_thrust()

    def set_button_thrust(self, direction):
        self.button_steering = direction
        self.update_thrust()

    def release_thrust(self):
        self.keys_pressed.clear()
        self.button_steering = 0
        self.update_thrust()

    def update_thrust(self):
        if self.puzzle.status != "flying":
            return

        if self.button_steering:
            value = self.button_steering
        else:
            value = (
                int("d" in self.keys_pressed)
                - int("a" in self.keys_pressed)
            )

        self.puzzle.update({
            "type": "steer",
            "value": value
        })

    def change_approach(self, value):
        if self.puzzle.status != "ready":
            return

        self.puzzle.update({
            "type": "adjust",
            "approach": float(value)
        })

        self.update_prediction()
        self.refresh()

    def change_side(self):
        if self.puzzle.status != "ready":
            return

        self.puzzle.update({
            "type": "set_side",
            "side": self.side_var.get()
        })

        self.update_prediction()
        self.refresh()

    def start_flyby(self):
        if self.puzzle.status != "ready":
            return

        self.puzzle.update({"type": "start"})
        self.reset_camera()
        self.last_frame = time.monotonic()
        self.refresh()

    def next_encounter(self):
        if self.puzzle.status != "between":
            return

        self.puzzle.update({"type": "next"})

        self.approach_var.set(self.puzzle.impact)
        self.side_var.set(self.puzzle.side)

        self.reset_camera()
        self.update_prediction()
        self.refresh()

    def reset_mission(self):
        self.puzzle.reset()
        self.completed_notified = False

        self.approach_var.set(self.puzzle.impact)
        self.side_var.set(self.puzzle.side)

        self.release_thrust()

        self.hint_index = 0
        self.hint_text.set("")
        self.hint_button.configure(
            state="normal",
            text="ASK COSMO FOR A HINT"
        )

        self.reset_camera()
        self.update_prediction()
        self.refresh()

    def show_hint(self):
        if self.hint_index >= len(self.HINTS):
            return

        self.hint_text.set(
            self.HINTS[self.hint_index]
        )

        self.hint_index += 1

        if self.hint_index == len(self.HINTS):
            self.hint_button.configure(
                state="disabled",
                text="ALL HINTS REVEALED"
            )

    # ==================================================
    # PHYSICS HELPERS
    # ==================================================

    def current_planet_data(self):
        planet = self.puzzle.current_planet()

        if planet is not None:
            return planet

        # Keep the last planet visible after
        # the final encounter.
        return self.puzzle.PLANETS[-1]

    def live_velocity(self):
        """
        The backend stores the heliocentric velocity
        from the last completed encounter in vx/vy.

        During a flyby, its local ux/uy values contain
        the continuously updated planet-relative
        velocity. Convert those to the solar frame.
        """
        loc = self.puzzle.local

        if loc is not None:
            pvx, pvy = loc["planet_velocity"]

            return (
                loc["ux"] + pvx,
                loc["uy"] + pvy
            )

        return self.puzzle.vx, self.puzzle.vy

    def live_speeds(self):
        vx, vy = self.live_velocity()
        sun_speed = math.hypot(vx, vy)

        loc = self.puzzle.local

        if loc is not None:
            relative_speed = math.hypot(
                loc["ux"],
                loc["uy"]
            )
        else:
            planet = self.current_planet_data()
            pvx, pvy = planet["velocity"]

            relative_speed = math.hypot(
                vx - pvx,
                vy - pvy
            )

        return sun_speed, relative_speed

    def gravity_data(self):
        """
        Returns gravitational acceleration in
        AU/year^2 and its planet-centred components.

        No thrust is included in this value.
        """
        loc = self.puzzle.local

        if loc is None:
            return 0.0, 0.0, 0.0

        x = loc["x"]
        y = loc["y"]

        r = max(
            math.hypot(x, y),
            1e-12
        )

        mu = loc["mu"]

        gx = -mu * x / (r ** 3)
        gy = -mu * y / (r ** 3)

        return math.hypot(gx, gy), gx, gy

    # ==================================================
    # PREDICTED TRAJECTORY
    # ==================================================

    def update_prediction(self):
        """
        Run a separate copy of the existing backend
        with zero steering.

        The real game state is never modified.

        This is a prediction for the current approach
        and assumes the player does not use thrusters.
        """
        self.predicted_trajectory = []

        if self.puzzle.status != "ready":
            return

        simulation = deepcopy(self.puzzle)

        simulation.update({
            "type": "start"
        })

        if simulation.status != "flying":
            return

        # Advance the copy until the flyby finishes
        # or the safety limit is reached.
        for _ in range(350):
            if simulation.status != "flying":
                break

            simulation.update({
                "type": "tick",
                "dt": 0.001
            })

        self.predicted_trajectory = list(
            simulation.trajectory
        )

    # ==================================================
    # CAMERA
    # ==================================================

    def reset_camera(self):
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_scale = 3.0

    def update_camera(self, state, width, height):
        x = state["x"]
        y = state["y"]

        if x is None or y is None:
            return

        distance = math.hypot(x, y)

        if distance < 65:
            follow = 0.20
        elif distance < 130:
            follow = 0.45
        else:
            follow = 0.70

        desired_x = x * follow
        desired_y = y * follow

        self.camera_x += (
            desired_x - self.camera_x
        ) * 0.12

        self.camera_y += (
            desired_y - self.camera_y
        ) * 0.12

        visible_radius = max(
            32.0,
            min(
                260.0,
                distance * 0.95 + 25.0
            )
        )

        desired_scale = min(
            width * 0.40,
            height * 0.35
        ) / visible_radius

        self.camera_scale += (
            desired_scale - self.camera_scale
        ) * 0.12

    # ==================================================
    # GRAPHICS HELPERS
    # ==================================================

    def draw_arrow(
        self,
        x1,
        y1,
        x2,
        y2,
        color,
        width=2
    ):
        self.scene.create_line(
            x1, y1, x2, y2,
            fill=color,
            width=width,
            arrow=tk.LAST,
            arrowshape=(10, 12, 4)
        )

    def draw_polyline(
        self,
        trajectory,
        project,
        color,
        dashed=False
    ):
        if len(trajectory) < 2:
            return

        stride = max(
            1,
            len(trajectory) // 1000
        )

        samples = trajectory[::stride]

        if samples[-1] != trajectory[-1]:
            samples.append(trajectory[-1])

        coordinates = []

        for x, y in samples:
            px, py = project(x, y)
            coordinates.extend((px, py))

        if len(coordinates) < 4:
            return

        options = {
            "fill": color,
            "width": 2,
            "smooth": False
        }

        if dashed:
            options["dash"] = (5, 6)

        self.scene.create_line(
            *coordinates,
            **options
        )

    def draw_gravity_field(
        self,
        project,
        planet,
        width,
        height
    ):
        """
        Illustrative radial gravitational field.

        The arrows follow the Newtonian inverse-
        square direction and intensity, but their
        screen lengths are compressed for readability.
        """
        mu = (
            self.puzzle.SOLAR_MU
            * planet["mass_solar"]
        )

        radius_au = planet["radius_au"]

        # Field arrows at fixed planet-relative
        # distances, measured in planetary radii.
        distances = (12, 25, 45, 75, 110)

        for distance in distances:
            for index in range(16):
                angle = index * math.tau / 16

                x = math.cos(angle) * distance
                y = math.sin(angle) * distance

                sx, sy = project(x, y)

                if not (
                    15 < sx < width - 15
                    and 105 < sy < height - 105
                ):
                    continue

                r_au = distance * radius_au
                acceleration = mu / (r_au ** 2)

                # A logarithmic display scale prevents
                # near-planet arrows from dominating.
                strength = math.log1p(acceleration)

                length = min(
                    20.0,
                    4.0 + strength * 2.0
                )

                dx = -math.cos(angle) * length
                dy = math.sin(angle) * length

                color = (
                    "#45658D"
                    if distance >= 75
                    else "#5B7EAA"
                    if distance >= 45
                    else "#739BC6"
                )

                self.draw_arrow(
                    sx,
                    sy,
                    sx + dx,
                    sy + dy,
                    color,
                    1
                )

    def draw_planet(self, px, py, planet):
        name = planet["name"]

        if name == "Jupiter":
            radius = 23

            self.scene.create_oval(
                px - radius,
                py - radius,
                px + radius,
                py + radius,
                fill="#C68F67",
                outline="#E8C3A0",
                width=2
            )

            # Stylized atmospheric bands.
            for offset, color in (
                (-11, "#F0D1A6"),
                (-4, "#A96D52"),
                (5, "#E5B98C"),
                (12, "#9C684F")
            ):
                self.scene.create_line(
                    px - 17,
                    py + offset,
                    px + 17,
                    py + offset,
                    fill=color,
                    width=3
                )

        else:
            radius = 18

            self.scene.create_oval(
                px - radius,
                py - radius,
                px + radius,
                py + radius,
                fill="#D8B46E",
                outline="#FFE4A9",
                width=2
            )

            self.scene.create_arc(
                px - 14,
                py - 11,
                px + 14,
                py + 11,
                start=15,
                extent=150,
                style=tk.ARC,
                outline="#F3D9A1",
                width=3
            )

        self.scene.create_text(
            px,
            py + radius + 15,
            text=name.upper(),
            fill=self.TEXT,
            font=("Arial", 10, "bold")
        )

    # ==================================================
    # MAIN RENDERING
    # ==================================================

    def draw_scene(self, state):
        c = self.scene
        c.delete("all")

        width = max(c.winfo_width(), 300)
        height = max(c.winfo_height(), 350)

        cx = width / 2
        cy = height / 2

        self.update_camera(
            state,
            width,
            height
        )

        scale = self.camera_scale

        def project(x, y):
            return (
                cx + (x - self.camera_x) * scale,
                cy - (y - self.camera_y) * scale
            )

        planet = self.current_planet_data()

        # ------------------------------------------
        # BACKGROUND
        # ------------------------------------------

        for i in range(80):
            x = (i * 173 + 41) % width
            y = (i * 97 + 23) % height

            c.create_oval(
                x, y,
                x + 1.5,
                y + 1.5,
                fill="#344761",
                outline=""
            )

        # ------------------------------------------
        # GRAVITY FIELD
        # ------------------------------------------

        self.draw_gravity_field(
            project,
            planet,
            width,
            height
        )

        # ------------------------------------------
        # PLANET
        # ------------------------------------------

        px, py = project(0, 0)

        self.draw_planet(
            px,
            py,
            planet
        )

        # ------------------------------------------
        # PLANET MOTION
        # ------------------------------------------

        if (
            30 < px < width - 90
            and 100 < py < height - 120
        ):
            self.draw_arrow(
                px + 38,
                py,
                px + 38,
                py - 58,
                self.GOLD,
                3
            )

            c.create_text(
                px + 46,
                py - 65,
                text="PLANET MOTION",
                fill=self.GOLD,
                anchor="w",
                font=("Arial", 9)
            )

        # ------------------------------------------
        # PREDICTED TRAJECTORY
        # ------------------------------------------

        self.draw_polyline(
            self.predicted_trajectory,
            project,
            self.PURPLE,
            dashed=True
        )

        # ------------------------------------------
        # REAL TRAJECTORY
        # ------------------------------------------

        self.draw_polyline(
            state["trajectory"],
            project,
            self.CYAN
        )

        # ------------------------------------------
        # SPACECRAFT AND GRAVITY VECTOR
        # ------------------------------------------

        if (
            state["x"] is not None
            and state["y"] is not None
        ):
            sx, sy = project(
                state["x"],
                state["y"]
            )

            c.create_oval(
                sx - 6,
                sy - 6,
                sx + 6,
                sy + 6,
                fill=self.GREEN,
                outline=self.TEXT,
                width=2
            )

            # Point the gravity vector toward
            # the planet, not along the trajectory.
            gravity, gx, gy = self.gravity_data()

            magnitude = math.hypot(gx, gy)

            if magnitude > 0:
                length = min(
                    72,
                    15 + 11 * math.log1p(gravity)
                )

                dx = gx / magnitude * length
                dy = -gy / magnitude * length

                self.draw_arrow(
                    sx,
                    sy,
                    sx + dx,
                    sy + dy,
                    self.RED,
                    3
                )

            c.create_text(
                sx + 12,
                sy - 13,
                text="ADA + VERA",
                fill=self.GREEN,
                anchor="w",
                font=("Arial", 9, "bold")
            )

        # ------------------------------------------
        # HUD
        # ------------------------------------------

        c.create_text(
            18,
            18,
            text="GRAVITATIONAL FLYBY",
            fill=self.CYAN,
            anchor="nw",
            font=("Arial", 16, "bold")
        )

        c.create_text(
            18,
            48,
            text="Reduce Sun-relative speed by 0.500 AU/yr",
            fill=self.TEXT,
            anchor="nw",
            font=("Arial", 10)
        )

        c.create_text(
            18,
            69,
            text=(
                f"Target: "
                f"{state['target_speed']:.3f} AU/yr"
            ),
            fill=self.MUTED,
            anchor="nw",
            font=("Arial", 10)
        )

        # ------------------------------------------
        # LEGEND
        # ------------------------------------------

        legend_y = height - 112

        c.create_text(
            20,
            legend_y,
            text="— Actual path",
            fill=self.CYAN,
            anchor="w",
            font=("Arial", 9)
        )

        c.create_text(
            145,
            legend_y,
            text="┄ Predicted path",
            fill=self.PURPLE,
            anchor="w",
            font=("Arial", 9)
        )

        c.create_text(
            20,
            legend_y + 20,
            text="→ Gravity direction",
            fill=self.RED,
            anchor="w",
            font=("Arial", 9)
        )

        # ------------------------------------------
        # COSMO BRIEFING
        # ------------------------------------------

        status = state["status"]

        if status == "ready":
            briefing = (
                "COSMO: The dotted line predicts the "
                "trajectory without thruster corrections. "
                "Change the approach to explore gravity."
            )

        elif status == "flying":
            briefing = (
                "COSMO: The red arrow points toward "
                "the planet. Gravity grows stronger "
                "as the spacecraft gets closer."
            )

        elif status == "between":
            briefing = (
                "COSMO: Jupiter's gravity changed our "
                "heliocentric velocity. Let's plan "
                "the Venus encounter."
            )

        elif status == "success":
            briefing = (
                "COSMO: Success! The gravitational "
                "assists reduced our Sun-relative "
                "speed enough for the mission goal."
            )

        else:
            briefing = (
                "COSMO: We haven't achieved the target. "
                "Try changing the approach distance "
                "or passing side."
            )

        c.create_rectangle(
            10,
            height - 83,
            width - 10,
            height - 10,
            fill=self.PANEL,
            outline=self.CARD,
            width=2
        )

        c.create_text(
            23,
            height - 72,
            text="COSMO — SCIENCE BRIEFING",
            fill=self.CYAN,
            anchor="nw",
            font=("Arial", 9, "bold")
        )

        c.create_text(
            23,
            height - 51,
            text=briefing,
            fill=self.TEXT,
            anchor="nw",
            width=width - 48,
            font=("Arial", 9)
        )

        # ------------------------------------------
        # SUCCESS MESSAGE
        # ------------------------------------------

        if status == "success":
            final_speed, _ = self.live_speeds()

            reduction = (
                self.puzzle.start_speed
                - final_speed
            )

            c.create_rectangle(
                cx - 205,
                height * 0.25 - 22,
                cx + 205,
                height * 0.25 + 96,
                fill=self.PANEL,
                outline=self.GREEN,
                width=2
            )

            c.create_text(
                cx,
                height * 0.25 + 2,
                text="MISSION SUCCESS",
                fill=self.GREEN,
                font=("Arial", 21, "bold")
            )

            c.create_text(
                cx,
                height * 0.25 + 39,
                text=(
                    f"Speed reduction: "
                    f"{reduction:.3f} AU/yr"
                ),
                fill=self.TEXT,
                font=("Arial", 11)
            )

            c.create_text(
                cx,
                height * 0.25 + 70,
                text="ADA AND VERA ARE GOING HOME",
                fill=self.CYAN,
                font=("Arial", 10, "bold")
            )

    # ==================================================
    # PANEL UPDATES
    # ==================================================

    def refresh(self):
        state = self.puzzle.get_state()
        status = state["status"]

        planet = self.current_planet_data()

        if status in ("success", "failed") and (
            state["encounter_index"]
            >= state["total_encounters"]
        ):
            self.planet_var.set("FINAL MISSION RESULT")
        else:
            self.planet_var.set(
                f"ENCOUNTER "
                f"{state['encounter_index'] + 1}/2 "
                f"— {planet['name'].upper()}"
            )

        self.approach_text.set(
            f"{state['impact']:.1f} planetary radii"
        )

        sun_speed, relative_speed = (
            self.live_speeds()
        )

        self.speed_text.set(
            f"Sun-relative speed: "
            f"{sun_speed:.3f} AU/yr"
        )

        self.relative_text.set(
            f"Planet-relative speed: "
            f"{relative_speed:.3f} AU/yr"
        )

        distance = state["distance_radii"]

        self.distance_text.set(
            "Distance: —"
            if distance is None
            else f"Distance: {distance:.2f} planetary radii"
        )

        gravity, _, _ = self.gravity_data()

        self.gravity_text.set(
            f"Gravitational acceleration: "
            f"{gravity:.2f} AU/yr²"
        )

        self.fuel_text.set(
            f"Fuel: {state['fuel']:.3f} / "
            f"{state['fuel_capacity']:.3f}"
        )

        self.status_text.set(state["message"])

        # Fuel bar.
        self.fuel_bar.delete("all")

        fuel_fraction = (
            state["fuel"] / state["fuel_capacity"]
        )

        bar_width = max(
            self.fuel_bar.winfo_width(),
            200
        )

        self.fuel_bar.create_rectangle(
            0,
            0,
            bar_width * fuel_fraction,
            12,
            fill=(
                self.GREEN
                if fuel_fraction > 0.25
                else self.RED
            ),
            outline=""
        )

        # Encounter history.
        history_lines = []

        for item in state["history"]:
            history_lines.append(
                f"{item['planet']}\n"
                f"  Incoming: "
                f"{item['incoming_speed']:.3f} AU/yr\n"
                f"  Outgoing: "
                f"{item['outgoing_speed']:.3f} AU/yr\n"
                f"  Change: "
                f"{item['speed_change']:+.3f} AU/yr\n"
                f"  Closest approach: "
                f"{item['closest_radii']:.2f} R"
            )

        self.history_text.set(
            "\n\n".join(history_lines)
            if history_lines
            else "No completed encounters."
        )

        # Final result.
        if status in ("success", "failed"):
            reduction = (
                self.puzzle.start_speed
                - sun_speed
            )

            heading = (
                "MISSION SUCCESS"
                if status == "success"
                else "MISSION FAILED"
            )

            self.result_text.set(
                f"{heading}\n\n"
                f"Initial speed: "
                f"{self.puzzle.start_speed:.3f} AU/yr\n"
                f"Final speed: "
                f"{sun_speed:.3f} AU/yr\n"
                f"Speed reduction: "
                f"{reduction:.3f} AU/yr\n"
                f"Target speed: "
                f"{state['target_speed']:.3f} AU/yr"
            )

        elif status == "between":
            self.result_text.set(
                "Jupiter flyby complete.\n"
                "Prepare the Venus encounter."
            )

        else:
            self.result_text.set(
                "Objective: reduce the spacecraft's "
                "Sun-relative speed by at least "
                "0.500 AU/yr across both encounters."
            )

        ready = status == "ready"
        flying = status == "flying"

        self.start_button.configure(
            state="normal" if ready else "disabled"
        )

        self.next_button.configure(
            state=(
                "normal"
                if status == "between"
                else "disabled"
            )
        )

        self.approach_slider.configure(
            state="normal" if ready else "disabled"
        )

        for radio in self.side_buttons:
            radio.configure(
                state="normal" if ready else "disabled"
            )

        self.left_button.configure(
            state="normal" if flying else "disabled"
        )

        self.right_button.configure(
            state="normal" if flying else "disabled"
        )

        self.draw_scene(state)

    # ==================================================
    # ANIMATION
    # ==================================================

    def animate(self):
        if not self.running:
            return

        now = time.monotonic()

        elapsed = min(
            now - self.last_frame,
            0.1
        )
        self.last_frame = now

        if self.puzzle.status == "flying":
            self.puzzle.update({
                "type": "tick",
                "dt": (
                    elapsed
                    * self.SIMULATION_SPEED
                )
            })

        self.refresh()

        if (
            self.puzzle.completed
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete:
                self.after_idle(
                    self.on_complete
                )

        self.after_id = self.after(
            self.FRAME_MS,
            self.animate
        )

    # ==================================================
    # CLEANUP
    # ==================================================

    def go_back(self):
        self.running = False

        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        if self.on_back:
            self.on_back()

    def destroy(self):
        self.running = False

        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

        super().destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title(
        "ASTRA — Chapter 08: Gravity Assist"
    )
    root.geometry("1000x650")
    root.minsize(850, 550)

    app = GravityAssistUI(root)
    app.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
