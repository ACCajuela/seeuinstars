
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
    FRAME_MS = 30
    SIMULATION_SPEED = 0.0015

    HINTS = [
        (
            "HINT 1 — GRAVITY ASSIST",
            "A moving planet can change a spacecraft's "
            "speed relative to the Sun. The spacecraft "
            "exchanges a tiny amount of orbital momentum "
            "with the planet."
        ),
        (
            "HINT 2 — PASSING SIDE",
            "The side of the planet matters. Depending "
            "on the geometry, the spacecraft can gain "
            "or lose heliocentric speed."
        ),
        (
            "HINT 3 — RETURN HOME",
            "Your goal is to slow down. Try passing "
            "on the RIGHT side of both Jupiter and "
            "Venus. You may not need your thrusters."
        ),
        (
            "HINT 4 — SOLUTION",
            "Set the approach distance to 20 planetary "
            "radii and select RIGHT for Jupiter. "
            "Repeat the same settings for Venus. "
            "Do not use the thrusters."
        ),
    ]

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

        self.running = True
        self.after_id = None
        self.completed_notified = False
        self.last_frame = time.monotonic()

        self.keys_pressed = set()
        self.button_steering = 0
        self.hint_index = 0

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_scale = None

        self.approach_var = tk.DoubleVar(value=20.0)
        self.side_var = tk.IntVar(value=-1)

        self.planet_var = tk.StringVar()
        self.impact_var = tk.StringVar()
        self.speed_var = tk.StringVar()
        self.distance_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.fuel_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.history_var = tk.StringVar()
        self.hint_var = tk.StringVar()
        self.result_var = tk.StringVar()

        self.build_ui()
        self.bind_controls()
        self.refresh()
        self.animate()

    # ==================================================
    # UI HELPERS
    # ==================================================

    def label(
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

    def button(
        self,
        parent,
        text,
        command,
        bg=None,
        fg=None
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg or self.CARD,
            fg=fg or self.TEXT,
            activebackground=self.ACCENT,
            activeforeground=self.BG,
            disabledforeground="#65758A",
            relief="flat",
            bd=0,
            font=("Arial", 9, "bold"),
            cursor="hand2",
            pady=8
        )

    def section(self, text):
        self.label(
            self.content,
            text,
            9,
            self.MUTED,
            True
        ).pack(
            anchor="w",
            padx=14,
            pady=(12, 4)
        )

    # ==================================================
    # SCROLLABLE PANEL
    # ==================================================

    def build_ui(self):
        self.pack_propagate(False)

        self.canvas = tk.Canvas(
            self,
            width=625,
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
            bg=self.PANEL,
            width=275
        )
        self.panel.pack(
            side="right",
            fill="y"
        )
        self.panel.pack_propagate(False)

        self.scroll_canvas = tk.Canvas(
            self.panel,
            bg=self.PANEL,
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = tk.Scrollbar(
            self.panel,
            orient="vertical",
            command=self.scroll_canvas.yview
        )

        self.scroll_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )
        self.scroll_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.content = tk.Frame(
            self.scroll_canvas,
            bg=self.PANEL
        )

        self.content_window = (
            self.scroll_canvas.create_window(
                (0, 0),
                window=self.content,
                anchor="nw"
            )
        )

        self.content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.scroll_canvas.bind(
            "<Configure>",
            self.resize_scroll_content
        )

        self.scroll_canvas.bind(
            "<Enter>",
            lambda e: self.bind_mousewheel()
        )
        self.scroll_canvas.bind(
            "<Leave>",
            lambda e: self.unbind_mousewheel()
        )

        self.label(
            self.content,
            "GRAVITY ASSIST",
            17,
            self.ACCENT,
            True
        ).pack(
            anchor="w",
            padx=14,
            pady=(15, 3)
        )

        self.label(
            self.content,
            "CHAPTER 08 — RETURN HOME",
            9,
            self.MUTED
        ).pack(
            anchor="w",
            padx=14,
            pady=(0, 12)
        )

        self.label(
            self.content,
            self.planet_var,
            13,
            self.TEXT,
            True
        ).pack(
            anchor="w",
            padx=14
        )

        self.section("APPROACH DISTANCE")

        self.label(
            self.content,
            self.impact_var,
            10,
            self.ACCENT
        ).pack(anchor="w", padx=14)

        self.approach_slider = tk.Scale(
            self.content,
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
            highlightthickness=0,
            length=220
        )
        self.approach_slider.pack(
            padx=14,
            pady=(0, 4)
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

        for value, name in (
            (-1, "LEFT"),
            (1, "RIGHT")
        ):
            radio = tk.Radiobutton(
                side_frame,
                text=name,
                variable=self.side_var,
                value=value,
                command=self.on_side_change,
                bg=self.PANEL,
                fg=self.TEXT,
                selectcolor=self.CARD,
                activebackground=self.PANEL,
                activeforeground=self.ACCENT,
                highlightthickness=0
            )
            radio.pack(side="left", padx=(0, 15))
            self.side_buttons.append(radio)

        self.start_button = self.button(
            self.content,
            "START FLYBY",
            self.start_flyby,
            self.ACCENT,
            self.BG
        )
        self.start_button.pack(
            fill="x",
            padx=14,
            pady=(12, 3)
        )

        self.section("TRAJECTORY CORRECTION")

        self.label(
            self.content,
            "Hold A / D or the buttons",
            9
        ).pack(anchor="w", padx=14)

        thrust_frame = tk.Frame(
            self.content,
            bg=self.PANEL
        )
        thrust_frame.pack(
            fill="x",
            padx=14,
            pady=(7, 4)
        )

        self.left_button = self.button(
            thrust_frame,
            "◀ LEFT",
            lambda: None
        )
        self.left_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4)
        )

        self.right_button = self.button(
            thrust_frame,
            "RIGHT ▶",
            lambda: None
        )
        self.right_button.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.left_button.bind(
            "<ButtonPress-1>",
            lambda e: self.set_button_steering(-1)
        )
        self.left_button.bind(
            "<ButtonRelease-1>",
            lambda e: self.set_button_steering(0)
        )
        self.right_button.bind(
            "<ButtonPress-1>",
            lambda e: self.set_button_steering(1)
        )
        self.right_button.bind(
            "<ButtonRelease-1>",
            lambda e: self.set_button_steering(0)
        )

        self.section("FLIGHT DATA")

        for variable in (
            self.speed_var,
            self.distance_var,
            self.time_var,
            self.fuel_var
        ):
            self.label(
                self.content,
                variable,
                9
            ).pack(
                anchor="w",
                padx=14,
                pady=2
            )

        self.fuel_canvas = tk.Canvas(
            self.content,
            width=220,
            height=12,
            bg=self.CARD,
            highlightthickness=0
        )
        self.fuel_canvas.pack(
            padx=14,
            pady=(7, 8)
        )

        self.next_button = self.button(
            self.content,
            "CONTINUE TO VENUS",
            self.next_encounter,
            self.GREEN,
            self.BG
        )
        self.next_button.pack(
            fill="x",
            padx=14,
            pady=4
        )

        self.section("COSMO — MISSION SUPPORT")

        self.hint_button = self.button(
            self.content,
            "ASK COSMO FOR A HINT",
            self.show_hint
        )
        self.hint_button.pack(
            fill="x",
            padx=14,
            pady=(0, 8)
        )

        self.label(
            self.content,
            self.hint_var,
            9,
            self.GOLD,
            wrap=225
        ).pack(
            anchor="w",
            padx=14,
            pady=(0, 8)
        )

        self.section("MISSION LOG")

        self.label(
            self.content,
            self.history_var,
            9,
            wrap=225
        ).pack(
            anchor="w",
            padx=14
        )

        self.section("MISSION RESULT")

        self.label(
            self.content,
            self.result_var,
            10,
            self.GREEN,
            wrap=225
        ).pack(
            anchor="w",
            padx=14,
            pady=(0, 8)
        )

        self.label(
            self.content,
            self.status_var,
            9,
            self.GOLD,
            wrap=225
        ).pack(
            anchor="w",
            padx=14,
            pady=(0, 12)
        )

        self.reset_button = self.button(
            self.content,
            "RESET MISSION",
            self.reset_simulation
        )
        self.reset_button.pack(
            fill="x",
            padx=14,
            pady=(0, 7)
        )

        if self.on_back:
            self.button(
                self.content,
                "BACK",
                self.go_back
            ).pack(
                fill="x",
                padx=14,
                pady=(0, 15)
            )

    def update_scroll_region(self, event=None):
        self.scroll_canvas.configure(
            scrollregion=self.scroll_canvas.bbox("all")
        )

    def resize_scroll_content(self, event):
        self.scroll_canvas.itemconfigure(
            self.content_window,
            width=event.width
        )

    def bind_mousewheel(self):
        self.scroll_canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

    def unbind_mousewheel(self):
        self.scroll_canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        self.scroll_canvas.yview_scroll(
            -int(event.delta / 120),
            "units"
        )

    # ==================================================
    # COSMO HINTS
    # ==================================================

    def show_hint(self):
        if self.hint_index >= len(self.HINTS):
            return

        title, explanation = self.HINTS[
            self.hint_index
        ]

        self.hint_var.set(
            f"{title}\n\n{explanation}"
        )

        self.hint_index += 1

        if self.hint_index == len(self.HINTS):
            self.hint_button.configure(
                text="ALL HINTS REVEALED",
                state="disabled"
            )

    # ==================================================
    # KEYBOARD AND THRUST
    # ==================================================

    def bind_controls(self):
        for key in ("a", "d"):
            self.master.bind(
                f"<KeyPress-{key}>",
                self.on_key_press,
                add="+"
            )
            self.master.bind(
                f"<KeyRelease-{key}>",
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
            value = (
                int("d" in self.keys_pressed)
                - int("a" in self.keys_pressed)
            )

        self.puzzle.update({
            "type": "steer",
            "value": value
        })

    # ==================================================
    # PLAYER ACTIONS
    # ==================================================

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

        self.reset_camera()
        self.last_frame = time.monotonic()
        self.refresh()

    def next_encounter(self):
        if self.puzzle.status != "between":
            return

        self.puzzle.update({
            "type": "next"
        })

        self.approach_var.set(self.puzzle.impact)
        self.side_var.set(self.puzzle.side)

        self.reset_camera()
        self.refresh()

    def reset_simulation(self):
        self.puzzle.reset()

        self.completed_notified = False
        self.keys_pressed.clear()
        self.button_steering = 0

        self.approach_var.set(self.puzzle.impact)
        self.side_var.set(self.puzzle.side)

        self.hint_index = 0
        self.hint_var.set("")

        self.hint_button.configure(
            text="ASK COSMO FOR A HINT",
            state="normal"
        )

        self.reset_camera()
        self.last_frame = time.monotonic()
        self.refresh()

    def reset_camera(self):
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_scale = None

    # ==================================================
    # ANIMATION LOOP
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
                    elapsed * self.SIMULATION_SPEED
                )
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

    # ==================================================
    # INFORMATION PANEL
    # ==================================================

    def refresh(self):
        state = self.puzzle.get_state()
        status = state["status"]
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

        self.distance_var.set(
            "DISTANCE: —"
            if distance is None
            else f"DISTANCE: {distance:.1f} R"
        )

        self.time_var.set(
            "ENCOUNTER TIME: "
            f"{state['encounter_elapsed']:.5f} yr"
        )

        self.fuel_var.set(
            f"FUEL: {state['fuel']:.3f} / "
            f"{state['fuel_capacity']:.3f}"
        )

        self.status_var.set(state["message"])

        fraction = max(
            0.0,
            min(
                1.0,
                state["fuel"] / state["fuel_capacity"]
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

        initial_speed = self.puzzle.start_speed
        final_speed = state["speed"]
        reduction = initial_speed - final_speed

        if status == "success":
            self.result_var.set(
                "MISSION SUCCESS!\n\n"
                f"Initial speed: {initial_speed:.3f} AU/yr\n"
                f"Final speed: {final_speed:.3f} AU/yr\n"
                f"Speed reduction: {reduction:.3f} AU/yr\n"
                "Required reduction: 0.500 AU/yr\n\n"
                "Ada and Vera have prepared their "
                "return trajectory to Earth!"
            )

        elif status == "failed":
            self.result_var.set(
                "MISSION FAILED\n\n"
                f"Current speed: {final_speed:.3f} AU/yr\n"
                f"Speed reduction: {reduction:.3f} AU/yr\n\n"
                "Try another approach or passing side."
            )

        elif status == "between":
            self.result_var.set(
                "JUPITER FLYBY COMPLETE\n\n"
                f"Current speed: {final_speed:.3f} AU/yr\n"
                f"Speed reduction: {reduction:.3f} AU/yr\n\n"
                "One more gravitational assist remains."
            )

        else:
            self.result_var.set(
                "GOAL\n\n"
                f"Initial speed: {initial_speed:.3f} AU/yr\n"
                f"Target speed: {state['target_speed']:.3f} AU/yr"
            )

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

    # ==================================================
    # CAMERA
    # ==================================================

    def update_camera(self, state, width, height):
        trajectory = state["trajectory"]

        if not trajectory:
            return

        x = state["x"]
        y = state["y"]

        if x is None or y is None:
            return

        distance = math.hypot(x, y)

        # Keep the planet visible during close flybys.
        # Follow the spacecraft more closely as it
        # travels farther away.
        if distance < 55:
            desired_x = x * 0.20
            desired_y = y * 0.20
        elif distance < 110:
            desired_x = x * 0.45
            desired_y = y * 0.45
        else:
            desired_x = x * 0.75
            desired_y = y * 0.75

        # Camera smoothing.
        self.camera_x += (
            desired_x - self.camera_x
        ) * 0.12

        self.camera_y += (
            desired_y - self.camera_y
        ) * 0.12

        # Zoom out when the spacecraft moves farther
        # from the planet, but preserve useful detail
        # during the close approach.
        visible_radius = max(
            28.0,
            min(
                220.0,
                distance * 1.05 + 22.0
            )
        )

        desired_scale = min(
            width * 0.43,
            height * 0.39
        ) / visible_radius

        if self.camera_scale is None:
            self.camera_scale = desired_scale
        else:
            self.camera_scale += (
                desired_scale - self.camera_scale
            ) * 0.10

    # ==================================================
    # SCENE RENDERING
    # ==================================================

    def draw_scene(self, state):
        canvas = self.canvas
        canvas.delete("all")

        width = max(
            canvas.winfo_width(),
            625
        )
        height = max(
            canvas.winfo_height(),
            600
        )

        cx = width / 2
        cy = height / 2

        self.update_camera(
            state,
            width,
            height
        )

        scale = self.camera_scale or 4.0

        def project(x, y):
            return (
                cx + (x - self.camera_x) * scale,
                cy - (y - self.camera_y) * scale
            )

        # ------------------------------------------
        # STAR FIELD
        # ------------------------------------------

        for i in range(75):
            sx = (i * 173 + 41) % width
            sy = (i * 97 + 23) % height

            canvas.create_oval(
                sx,
                sy,
                sx + 1.5,
                sy + 1.5,
                fill="#304562",
                outline=""
            )

        # ------------------------------------------
        # PLANET AND ORBITAL GRID
        # ------------------------------------------

        px, py = project(0.0, 0.0)

        for radius in (10, 20, 40, 80, 120):
            r = radius * scale

            if r < 3:
                continue

            canvas.create_oval(
                px - r,
                py - r,
                px + r,
                py + r,
                outline="#223751",
                dash=(3, 6)
            )

        planet_name = state["planet"] or "Venus"

        planet_color = (
            "#D7A16D"
            if planet_name == "Jupiter"
            else "#E9C88C"
        )

        planet_radius = (
            17
            if planet_name == "Jupiter"
            else 12
        )

        # The planet is deliberately enlarged
        # for visibility, not drawn to scale.
        canvas.create_oval(
            px - planet_radius,
            py - planet_radius,
            px + planet_radius,
            py + planet_radius,
            fill=planet_color,
            outline="#F4E0BC",
            width=2
        )

        canvas.create_text(
            px,
            py + planet_radius + 17,
            text=planet_name.upper(),
            fill=self.MUTED,
            font=("Arial", 10, "bold")
        )

        # Planet's heliocentric velocity.
        if -100 < px < width + 100:
            canvas.create_line(
                px + 36,
                py,
                px + 36,
                py - 58,
                fill=self.GOLD,
                width=3,
                arrow=tk.LAST
            )

            canvas.create_text(
                px + 45,
                py - 66,
                text="PLANET MOTION",
                fill=self.GOLD,
                anchor="w",
                font=("Arial", 9)
            )

        # ------------------------------------------
        # TRAJECTORY
        # ------------------------------------------

        trajectory = state["trajectory"]

        if len(trajectory) > 1:
            stride = max(
                1,
                len(trajectory) // 1500
            )

            sampled = trajectory[::stride]

            if sampled[-1] != trajectory[-1]:
                sampled.append(trajectory[-1])

            points = []

            for x, y in sampled:
                sx, sy = project(x, y)
                points.extend((sx, sy))

            if len(points) >= 4:
                canvas.create_line(
                    *points,
                    fill=self.ACCENT,
                    width=2
                )

        # ------------------------------------------
        # SPACECRAFT
        # ------------------------------------------

        if state["x"] is not None:
            sx, sy = project(
                state["x"],
                state["y"]
            )

            canvas.create_oval(
                sx - 6,
                sy - 6,
                sx + 6,
                sy + 6,
                fill=self.GREEN,
                outline=self.TEXT,
                width=2
            )

            canvas.create_text(
                sx + 12,
                sy - 12,
                text="ADA + VERA",
                fill=self.GREEN,
                anchor="w",
                font=("Arial", 10, "bold")
            )

        # ------------------------------------------
        # TOP HUD
        # ------------------------------------------

        canvas.create_text(
            20,
            20,
            text="RETURN TRANSFER",
            fill=self.ACCENT,
            anchor="nw",
            font=("Arial", 16, "bold")
        )

        canvas.create_text(
            20,
            50,
            text=(
                "Reduce heliocentric speed "
                "by at least 0.500 AU/year"
            ),
            fill=self.TEXT,
            anchor="nw",
            font=("Arial", 10)
        )

        canvas.create_text(
            20,
            72,
            text=(
                "Target speed: "
                f"{state['target_speed']:.3f} AU/year"
            ),
            fill=self.MUTED,
            anchor="nw",
            font=("Arial", 10)
        )

        # ------------------------------------------
        # SCIENTIFIC FEEDBACK
        # ------------------------------------------

        status = state["status"]

        if status == "ready":
            explanation = (
                "COSMO: Choose your approach distance "
                "and passing side. Gravity will bend "
                "the spacecraft's path."
            )

        elif status == "flying":
            explanation = (
                "COSMO: Watch the trajectory curve. "
                "The planet changes the direction "
                "of the spacecraft's velocity."
            )

        elif status == "between":
            explanation = (
                "COSMO: Jupiter flyby complete! "
                "Check the speed change in the "
                "mission log before approaching Venus."
            )

        elif status == "success":
            explanation = (
                "COSMO: Excellent! Both gravitational "
                "assists prepared a slower return "
                "trajectory. Ada and Vera can go home!"
            )

        else:
            explanation = (
                "COSMO: The maneuver did not meet "
                "the mission requirements. Try a "
                "different approach or passing side."
            )

        canvas.create_rectangle(
            12,
            height - 95,
            width - 12,
            height - 12,
            fill=self.PANEL,
            outline=self.CARD,
            width=2
        )

        canvas.create_text(
            26,
            height - 80,
            text="COSMO — SCIENCE BRIEFING",
            fill=self.ACCENT,
            anchor="nw",
            font=("Arial", 10, "bold")
        )

        canvas.create_text(
            26,
            height - 58,
            text=explanation,
            fill=self.TEXT,
            anchor="nw",
            width=width - 60,
            font=("Arial", 10)
        )

        # ------------------------------------------
        # VICTORY OVERLAY
        # ------------------------------------------

        if status == "success":
            canvas.create_rectangle(
                cx - 220,
                height * 0.25 - 20,
                cx + 220,
                height * 0.25 + 95,
                fill=self.PANEL,
                outline=self.GREEN,
                width=2
            )

            canvas.create_text(
                cx,
                height * 0.25 + 5,
                text="MISSION SUCCESS",
                fill=self.GREEN,
                font=("Arial", 22, "bold")
            )

            reduction = (
                self.puzzle.start_speed
                - state["speed"]
            )

            canvas.create_text(
                cx,
                height * 0.25 + 42,
                text=(
                    f"Speed reduced by "
                    f"{reduction:.3f} AU/year"
                ),
                fill=self.TEXT,
                font=("Arial", 12)
            )

            canvas.create_text(
                cx,
                height * 0.25 + 70,
                text="ADA AND VERA ARE GOING HOME",
                fill=self.ACCENT,
                font=("Arial", 11, "bold")
            )

    # ==================================================
    # CLEANUP
    # ==================================================

    def go_back(self):
        self.running = False

        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

        self.unbind_mousewheel()

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

        self.unbind_mousewheel()
        super().destroy()


# ======================================================
# STANDALONE TEST
# ======================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ASTRA — Chapter 08: Gravity Assist")
    root.geometry("900x600")
    root.resizable(False, False)

    app = GravityAssistUI(root)
    app.pack(fill="both", expand=True)

    root.mainloop()
