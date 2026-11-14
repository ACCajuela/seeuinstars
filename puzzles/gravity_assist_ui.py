
import math
import time
import tkinter as tk

from puzzles.gravity_assist import GravityAssistPuzzle


class GravityAssistUI(tk.Frame):

    BG = "#0B1425"
    PANEL = "#142238"
    CARD = "#1B2C45"
    TEXT = "#EAF2FF"
    MUTED = "#9FB3CE"
    ACCENT = "#65D6FF"
    GREEN = "#77E6B6"
    RED = "#FF808C"
    GOLD = "#FFD17B"

    WIDTH = 900
    HEIGHT = 600
    CANVAS_WIDTH = 640

    FRAME_MS = 30

    # Simulation years per real second.
    # Can be adjusted for gameplay.
    SIMULATION_SPEED = 0.00065

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):

        super().__init__(
            master,
            bg=self.BG,
            width=self.WIDTH,
            height=self.HEIGHT
        )

        self.puzzle = GravityAssistPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.completed_notified = False

        self.after_id = None
        self.running = True
        self.last_frame = time.monotonic()

        self.keys_pressed = set()
        self.button_steering = 0

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 1.0

        self.approach_var = tk.DoubleVar(
            value=self.puzzle.impact
        )

        self.side_var = tk.IntVar(
            value=self.puzzle.side
        )

        self.planet_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.speed_var = tk.StringVar()
        self.distance_var = tk.StringVar()
        self.fuel_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.impact_var = tk.StringVar()
        self.history_var = tk.StringVar()

        self.build_ui()
        self.bind_controls()

        self.refresh()
        self.animate()

    # ====================================================
    # UI
    # ====================================================

    def build_ui(self):

        self.pack_propagate(False)

        self.canvas = tk.Canvas(
            self,
            width=self.CANVAS_WIDTH,
            height=self.HEIGHT,
            bg=self.BG,
            highlightthickness=0
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.panel = tk.Frame(
            self,
            width=260,
            bg=self.PANEL
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        self.add_label(
            "GRAVITY ASSIST",
            17,
            self.ACCENT,
            bold=True
        ).pack(
            anchor="w",
            padx=16,
            pady=(16, 3)
        )

        self.add_label(
            "CHAPTER 08 — RETURN HOME",
            9,
            self.MUTED
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 14)
        )

        self.add_label(
            self.planet_var,
            14,
            self.TEXT,
            bold=True
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 14)
        )

        self.add_label(
            "APPROACH PARAMETER",
            9,
            self.MUTED,
            bold=True
        ).pack(
            anchor="w",
            padx=16
        )

        self.add_label(
            self.impact_var,
            11,
            self.ACCENT
        ).pack(
            anchor="w",
            padx=16,
            pady=(4, 0)
        )

        self.approach_slider = tk.Scale(
            self.panel,
            from_=self.puzzle.MIN_IMPACT,
            to=self.puzzle.MAX_IMPACT,
            resolution=0.5,
            orient="horizontal",
            variable=self.approach_var,
            command=self.on_approach_change,
            showvalue=False,
            bg=self.PANEL,
            fg=self.TEXT,
            troughcolor=self.CARD,
            activebackground=self.ACCENT,
            highlightthickness=0,
            length=220
        )

        self.approach_slider.pack(
            padx=12,
            pady=(0, 10)
        )

        self.add_label(
            "PASSING SIDE",
            9,
            self.MUTED,
            bold=True
        ).pack(
            anchor="w",
            padx=16
        )

        side_frame = tk.Frame(
            self.panel,
            bg=self.PANEL
        )

        side_frame.pack(
            fill="x",
            padx=12,
            pady=(5, 12)
        )

        self.side_buttons = []

        for value, title in (
            (-1, "LEFT"),
            (1, "RIGHT")
        ):

            button = tk.Radiobutton(
                side_frame,
                text=title,
                variable=self.side_var,
                value=value,
                command=self.on_side_change,
                bg=self.PANEL,
                fg=self.TEXT,
                selectcolor=self.CARD,
                activebackground=self.PANEL,
                activeforeground=self.ACCENT,
                font=("Arial", 9),
                highlightthickness=0
            )

            button.pack(
                side="left",
                padx=4
            )

            self.side_buttons.append(button)

        self.start_button = self.add_button(
            "START FLYBY",
            self.start_flyby,
            self.ACCENT
        )

        self.start_button.pack(
            fill="x",
            padx=16,
            pady=(0, 12)
        )

        self.add_label(
            "TRAJECTORY CORRECTION",
            9,
            self.MUTED,
            bold=True
        ).pack(
            anchor="w",
            padx=16
        )

        self.add_label(
            "Hold A / D or the buttons",
            9,
            self.TEXT
        ).pack(
            anchor="w",
            padx=16,
            pady=(4, 7)
        )

        thrust_frame = tk.Frame(
            self.panel,
            bg=self.PANEL
        )

        thrust_frame.pack(
            fill="x",
            padx=16,
            pady=(0, 12)
        )

        self.left_button = tk.Button(
            thrust_frame,
            text="◀ LEFT",
            bg=self.CARD,
            fg=self.TEXT,
            activebackground=self.ACCENT,
            activeforeground=self.BG,
            font=("Arial", 10, "bold"),
            relief="flat",
            width=10,
            pady=9
        )

        self.left_button.pack(
            side="left",
            padx=(0, 4)
        )

        self.right_button = tk.Button(
            thrust_frame,
            text="RIGHT ▶",
            bg=self.CARD,
            fg=self.TEXT,
            activebackground=self.ACCENT,
            activeforeground=self.BG,
            font=("Arial", 10, "bold"),
            relief="flat",
            width=10,
            pady=9
        )

        self.right_button.pack(
            side="left"
        )

        self.left_button.bind(
            "<ButtonPress-1>",
            lambda event: self.set_button_steering(-1)
        )

        self.left_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.set_button_steering(0)
        )

        self.right_button.bind(
            "<ButtonPress-1>",
            lambda event: self.set_button_steering(1)
        )

        self.right_button.bind(
            "<ButtonRelease-1>",
            lambda event: self.set_button_steering(0)
        )

        self.add_label(
            self.speed_var,
            10,
            self.TEXT
        ).pack(
            anchor="w",
            padx=16,
            pady=2
        )

        self.add_label(
            self.distance_var,
            10,
            self.TEXT
        ).pack(
            anchor="w",
            padx=16,
            pady=2
        )

        self.add_label(
            self.time_var,
            10,
            self.TEXT
        ).pack(
            anchor="w",
            padx=16,
            pady=2
        )

        self.add_label(
            self.fuel_var,
            10,
            self.GREEN
        ).pack(
            anchor="w",
            padx=16,
            pady=(7, 4)
        )

        self.fuel_canvas = tk.Canvas(
            self.panel,
            width=220,
            height=12,
            bg=self.CARD,
            highlightthickness=0
        )

        self.fuel_canvas.pack(
            padx=16,
            pady=(0, 12)
        )

        self.next_button = self.add_button(
            "CONTINUE TO VENUS",
            self.next_encounter,
            self.GREEN
        )

        self.next_button.pack(
            fill="x",
            padx=16,
            pady=(0, 7)
        )

        self.reset_button = self.add_button(
            "RESET MISSION",
            self.reset_simulation,
            self.CARD,
            fg=self.TEXT
        )

        self.reset_button.pack(
            fill="x",
            padx=16,
            pady=(0, 5)
        )

        if self.on_back:

            self.add_button(
                "BACK",
                self.go_back,
                self.CARD,
                fg=self.TEXT
            ).pack(
                fill="x",
                padx=16,
                pady=3
            )

        self.add_label(
            "MISSION LOG",
            9,
            self.MUTED,
            bold=True
        ).pack(
            anchor="w",
            padx=16,
            pady=(12, 3)
        )

        self.add_label(
            self.history_var,
            9,
            self.TEXT,
            wraplength=220
        ).pack(
            anchor="w",
            padx=16
        )

        self.add_label(
            self.status_var,
            9,
            self.GOLD,
            wraplength=220
        ).pack(
            side="bottom",
            fill="x",
            padx=16,
            pady=12
        )

    def add_label(
        self,
        value,
        size,
        color,
        bold=False,
        wraplength=0
    ):

        options = {
            "bg": self.PANEL,
            "fg": color,
            "font": (
                "Arial",
                size,
                "bold" if bold else "normal"
            ),
            "anchor": "w",
            "justify": "left"
        }

        if wraplength:
            options["wraplength"] = wraplength

        if isinstance(value, tk.Variable):
            options["textvariable"] = value
        else:
            options["text"] = value

        return tk.Label(
            self.panel,
            **options
        )

    def add_button(
        self,
        text,
        command,
        bg,
        fg=None
    ):

        return tk.Button(
            self.panel,
            text=text,
            command=command,
            bg=bg,
            fg=fg or self.BG,
            activebackground=self.GREEN,
            activeforeground=self.BG,
            relief="flat",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            pady=8
        )

    # ====================================================
    # Keyboard controls
    # ====================================================

    def bind_controls(self):

        self.master.bind(
            "<KeyPress-a>",
            self.on_key_press,
            add="+"
        )

        self.master.bind(
            "<KeyPress-d>",
            self.on_key_press,
            add="+"
        )

        self.master.bind(
            "<KeyRelease-a>",
            self.on_key_release,
            add="+"
        )

        self.master.bind(
            "<KeyRelease-d>",
            self.on_key_release,
            add="+"
        )

        self.master.bind(
            "<FocusOut>",
            self.on_focus_out,
            add="+"
        )

    def on_key_press(self, event):

        if self.puzzle.status != "flying":
            return

        self.keys_pressed.add(
            event.keysym.lower()
        )

        self.update_steering()

    def on_key_release(self, event):

        self.keys_pressed.discard(
            event.keysym.lower()
        )

        self.update_steering()

    def on_focus_out(self, event):

        self.keys_pressed.clear()
        self.button_steering = 0

        self.update_steering()

    def set_button_steering(self, value):

        if self.puzzle.status != "flying":
            return

        self.button_steering = value

        self.update_steering()

    def update_steering(self):

        if self.puzzle.status != "flying":
            return

        if self.button_steering:

            value = self.button_steering

        else:

            left = "a" in self.keys_pressed
            right = "d" in self.keys_pressed

            value = int(right) - int(left)

        self.puzzle.update({
            "type": "steer",
            "value": value
        })

    # ====================================================
    # Player actions
    # ====================================================

    def on_approach_change(self, value):

        if self.puzzle.status != "ready":
            return

        self.puzzle.update({
            "type": "adjust",
            "approach": float(value)
        })

        self.refresh()

    def on_side_change(self):

        if self.puzzle.status != "ready":
            return

        self.puzzle.update({
            "type": "set_side",
            "side": self.side_var.get()
        })

        self.refresh()

    def start_flyby(self):

        if self.puzzle.status != "ready":
            return

        self.keys_pressed.clear()
        self.button_steering = 0

        self.puzzle.update({
            "type": "start"
        })

        self.last_frame = time.monotonic()

        self.refresh()

    def next_encounter(self):

        if self.puzzle.status != "between":
            return

        self.puzzle.update({
            "type": "next"
        })

        self.approach_var.set(
            self.puzzle.impact
        )

        self.side_var.set(
            self.puzzle.side
        )

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 1.0

        self.refresh()

    def reset_simulation(self):

        self.puzzle.reset()

        self.completed_notified = False

        self.keys_pressed.clear()
        self.button_steering = 0

        self.approach_var.set(
            self.puzzle.impact
        )

        self.side_var.set(
            self.puzzle.side
        )

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 1.0

        self.last_frame = time.monotonic()

        self.refresh()

    def go_back(self):

        self.running = False

        if self.after_id is not None:

            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

        if self.on_back:
            self.on_back()

    # ====================================================
    # Animation loop
    # ====================================================

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

            dt = (
                elapsed
                * self.SIMULATION_SPEED
            )

            self.puzzle.update({
                "type": "tick",
                "dt": dt
            })

        self.refresh()

        state = self.puzzle.get_state()

        if (
            state["completed"]
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

    # ====================================================
    # Information panel
    # ====================================================

    def refresh(self):

        state = self.puzzle.get_state()

        index = state["encounter_index"]

        if state["planet"]:

            self.planet_var.set(
                f"{index + 1}/2 — "
                f"{state['planet'].upper()}"
            )

        else:

            self.planet_var.set(
                "MISSION COMPLETE"
            )

        self.impact_var.set(
            f"{state['impact']:.1f} planetary radii"
        )

        self.speed_var.set(
            f"SPEED: {state['speed']:.3f} AU/yr"
        )

        distance = state["distance_radii"]

        if distance is None:

            self.distance_var.set(
                "DISTANCE: —"
            )

        else:

            self.distance_var.set(
                f"DISTANCE: {distance:.1f} R"
            )

        self.time_var.set(
            "ENCOUNTER TIME: "
            f"{state['encounter_elapsed']:.5f} yr"
        )

        self.fuel_var.set(
            "FUEL: "
            f"{state['fuel']:.3f} / "
            f"{state['fuel_capacity']:.3f}"
        )

        self.status_var.set(
            state["message"]
        )

        fraction = max(
            0.0,
            min(
                1.0,
                state["fuel"]
                / state["fuel_capacity"]
            )
        )

        self.fuel_canvas.delete("all")

        self.fuel_canvas.create_rectangle(
            0,
            0,
            220 * fraction,
            12,
            fill=(
                self.GREEN
                if fraction > 0.25
                else self.RED
            ),
            outline=""
        )

        history = []

        for item in state["history"]:

            history.append(
                f"{item['planet']}: "
                f"{item['speed_change']:+.3f} AU/yr"
            )

        self.history_var.set(
            "\n".join(history)
            if history
            else "No completed flybys."
        )

        status = state["status"]

        self.start_button.configure(
            state=(
                "normal"
                if status == "ready"
                else "disabled"
            )
        )

        self.next_button.configure(
            state=(
                "normal"
                if status == "between"
                else "disabled"
            )
        )

        self.approach_slider.configure(
            state=(
                "normal"
                if status == "ready"
                else "disabled"
            )
        )

        for button in self.side_buttons:

            button.configure(
                state=(
                    "normal"
                    if status == "ready"
                    else "disabled"
                )
            )

        thrust_state = (
            "normal"
            if status == "flying"
            else "disabled"
        )

        self.left_button.configure(
            state=thrust_state
        )

        self.right_button.configure(
            state=thrust_state
        )

        self.draw_scene(state)

    # ====================================================
    # Camera
    # ====================================================

    def update_camera(self, state):

        trajectory = state["trajectory"]

        if not trajectory:
            return

        x = state["x"]
        y = state["y"]

        if x is None or y is None:
            return

        # Follow the spacecraft while keeping
        # the planet visible during close passes.

        distance = math.hypot(x, y)

        if distance < 100:

            desired_x = x * 0.35
            desired_y = y * 0.35

        else:

            desired_x = x
            desired_y = y

        self.camera_x += (
            desired_x - self.camera_x
        ) * 0.08

        self.camera_y += (
            desired_y - self.camera_y
        ) * 0.08

        # Keep scale fairly stable so players
        # can understand the gravitational bend.

        self.zoom = 2.0

    def world_to_screen(self, x, y):

        cx = self.CANVAS_WIDTH / 2
        cy = self.HEIGHT / 2

        return (
            cx + (x - self.camera_x) * self.zoom,
            cy - (y - self.camera_y) * self.zoom
        )

    # ====================================================
    # Drawing
    # ====================================================

    def draw_stars(self):

        for i in range(85):

            x = (
                i * 97 + 31
            ) % self.CANVAS_WIDTH

            y = (
                i * 61 + 47
            ) % self.HEIGHT

            radius = 1 if i % 6 else 2

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="#435A7D",
                outline=""
            )

    def draw_planet(self, name):

        x, y = self.world_to_screen(
            0,
            0
        )

        radius = 35

        color = (
            "#D8A675"
            if name == "Jupiter"
            else "#E8C987"
        )

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=color,
            outline="#FFF0C8",
            width=2
        )

        if name == "Jupiter":

            for offset in (-13, -4, 8, 17):

                if abs(offset) >= radius:
                    continue

                dx = math.sqrt(
                    radius**2 - offset**2
                )

                self.canvas.create_line(
                    x - dx,
                    y + offset,
                    x + dx,
                    y + offset,
                    fill="#A9775C",
                    width=3
                )

        self.canvas.create_text(
            x,
            y + radius + 18,
            text=name.upper(),
            fill=self.TEXT,
            font=("Arial", 11, "bold")
        )

    def draw_trajectory(self, trajectory):

        if len(trajectory) < 2:
            return

        # Sample older points if necessary.
        step = max(
            1,
            len(trajectory) // 900
        )

        points = trajectory[::step]

        if points[-1] != trajectory[-1]:
            points.append(trajectory[-1])

        coords = []

        for x, y in points:

            sx, sy = self.world_to_screen(
                x, y
            )

            coords.extend((sx, sy))

        if len(coords) >= 4:

            self.canvas.create_line(
                *coords,
                fill=self.ACCENT,
                width=2,
                smooth=False
            )

    def draw_ship(self, x, y, steering):

        sx, sy = self.world_to_screen(
            x, y
        )

        self.canvas.create_polygon(
            sx + 12, sy,
            sx - 9, sy - 7,
            sx - 5, sy,
            sx - 9, sy + 7,
            fill=self.GREEN,
            outline=self.TEXT
        )

        if steering:

            flame_color = (
                self.GOLD
                if steering > 0
                else self.RED
            )

            self.canvas.create_line(
                sx,
                sy,
                sx,
                sy + steering * 20,
                fill=flame_color,
                width=4
            )

        self.canvas.create_text(
            sx,
            sy - 20,
            text="ADA + VERA",
            fill=self.TEXT,
            font=("Arial", 9, "bold")
        )

    def draw_ready_scene(self, state):

        self.canvas.create_text(
            320,
            90,
            text="PLAN YOUR GRAVITY ASSIST",
            fill=self.TEXT,
            font=("Arial", 18, "bold")
        )

        self.canvas.create_text(
            320,
            125,
            text=(
                "Choose the passing side and "
                "impact parameter."
            ),
            fill=self.MUTED,
            font=("Arial", 11)
        )

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 2.0

        self.draw_planet(
            state["planet"]
        )

        side = state["side"]

        offset = side * state["impact"] * 2

        self.canvas.create_line(
            50,
            300 - offset,
            590,
            300 - offset,
            fill=self.ACCENT,
            dash=(6, 5),
            width=2,
            arrow=tk.LAST
        )

        self.canvas.create_text(
            320,
            520,
            text=(
                "The dashed line is the "
                "initial approach direction."
            ),
            fill=self.MUTED,
            font=("Arial", 10)
        )

    def draw_flying_scene(self, state):

        self.update_camera(state)

        planet_name = (
            state["planet"]
            or self.puzzle.PLANETS[
                min(
                    state["encounter_index"],
                    len(self.puzzle.PLANETS) - 1
                )
            ]["name"]
        )

        self.draw_trajectory(
            state["trajectory"]
        )

        self.draw_planet(
            planet_name
        )

        if (
            state["x"] is not None
            and state["y"] is not None
        ):

            self.draw_ship(
                state["x"],
                state["y"],
                state["steering"]
            )

        self.canvas.create_text(
            20,
            70,
            text="LIVE GRAVITATIONAL ENCOUNTER",
            fill=self.ACCENT,
            font=("Arial", 11, "bold"),
            anchor="w"
        )

        self.canvas.create_text(
            20,
            95,
            text="A / D — LATERAL THRUST",
            fill=self.MUTED,
            font=("Arial", 10),
            anchor="w"
        )

    def draw_between_scene(self, state):

        self.canvas.create_text(
            320,
            200,
            text="FLYBY COMPLETE",
            fill=self.GREEN,
            font=("Arial", 22, "bold")
        )

        self.canvas.create_text(
            320,
            250,
            text="Next destination: VENUS",
            fill=self.TEXT,
            font=("Arial", 15)
        )

        self.canvas.create_text(
            320,
            300,
            text=(
                "The spacecraft has changed "
                "its heliocentric velocity."
            ),
            fill=self.MUTED,
            font=("Arial", 11)
        )

        self.canvas.create_text(
            320,
            365,
            text="Continue when ready.",
            fill=self.ACCENT,
            font=("Arial", 12)
        )

    def draw_final_scene(self, state):

        success = state["completed"]

        color = (
            self.GREEN
            if success
            else self.RED
        )

        title = (
            "WELCOME HOME"
            if success
            else "RETURN TRANSFER FAILED"
        )

        self.canvas.create_text(
            320,
            155,
            text=title,
            fill=color,
            font=("Arial", 23, "bold")
        )

        self.canvas.create_text(
            320,
            215,
            text=(
                f"FINAL SPEED: "
                f"{state['speed']:.3f} AU/yr"
            ),
            fill=self.TEXT,
            font=("Arial", 14)
        )

        self.canvas.create_text(
            320,
            245,
            text=(
                f"TARGET: "
                f"≤ {state['target_speed']:.3f} AU/yr"
            ),
            fill=self.MUTED,
            font=("Arial", 12)
        )

        # Earth illustration.
        cx = 320
        cy = 380
        r = 65

        self.canvas.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            fill="#2978B8",
            outline="#8DDFFF",
            width=3
        )

        self.canvas.create_polygon(
            cx - 32, cy - 28,
            cx + 5, cy - 40,
            cx + 35, cy - 10,
            cx + 10, cy + 12,
            cx - 18, cy,
            fill="#62C99C",
            outline=""
        )

        self.canvas.create_polygon(
            cx + 12, cy + 24,
            cx + 43, cy + 15,
            cx + 23, cy + 51,
            cx - 4, cy + 42,
            fill="#62C99C",
            outline=""
        )

        self.canvas.create_text(
            320,
            505,
            text=(
                "ADA AND VERA ARE GOING HOME!"
                if success
                else "RESET TO TRY ANOTHER ROUTE"
            ),
            fill=color,
            font=("Arial", 13, "bold")
        )

    def draw_scene(self, state):

        self.canvas.delete("all")

        self.draw_stars()

        self.canvas.create_text(
            20,
            25,
            text="ASTRA — A JOURNEY BEYOND EARTH",
            fill=self.TEXT,
            font=("Arial", 13, "bold"),
            anchor="w"
        )

        status = state["status"]

        if status == "ready":

            self.draw_ready_scene(state)

        elif status == "flying":

            self.draw_flying_scene(state)

        elif status == "between":

            self.draw_between_scene(state)

        else:

            self.draw_final_scene(state)

    # ====================================================
    # Cleanup
    # ====================================================

    def destroy(self):

        self.running = False

        if self.after_id is not None:

            try:
                self.after_cancel(
                    self.after_id
                )
            except tk.TclError:
                pass

            self.after_id = None

        super().destroy()


# ========================================================
# Standalone test
# ========================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "ASTRA — Chapter 8: Gravity Assist"
    )

    root.geometry("900x600")
    root.resizable(False, False)

    app = GravityAssistUI(root)

    app.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
