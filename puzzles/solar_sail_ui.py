
import math
import time
import tkinter as tk

from puzzles.solar_sail import SolarSailPuzzle


# ============================================================
# ASTRA — CHAPTER 7: SOLAR SAIL
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 590
PANEL_WIDTH = WIDTH - SCENE_WIDTH

BG = "#0B1425"
PANEL_BG = "#1D2B40"
CARD_BG = "#263951"

TEXT = "#F5F7FF"
MUTED = "#AABBD3"
CYAN = "#7ADCF3"
PURPLE = "#B6A1F6"
GOLD = "#F5C66F"
GREEN = "#8FE4AE"
RED = "#FF9999"

FRAME_MS = 30
SIMULATION_SPEED = 0.40

PHASE_DURATION = SolarSailPuzzle.REFERENCE_PHASE_DURATION
PHASE_COUNT = 6

REFERENCE_ANGLES = [
    -55.0,
    1.6,
    83.2,
    -2.9,
    53.5,
    None
]


# ============================================================
# COSMO — SCIENTIFIC GUIDANCE
# ============================================================

COSMO_INTRO = (
    "COSMO: Ada, Vera is moving around the Sun, "
    "just like you.\n\n"
    "Your solar sail reflects sunlight to produce "
    "a small but continuous acceleration.\n\n"
    "Changing the sail's orientation changes "
    "your orbit. To reach Vera safely, you must "
    "match both her position and velocity."
)

COSMO_HINTS = [
    (
        "HINT 1/4 — SOLAR PRESSURE\n\n"
        "Sunlight carries momentum. When photons "
        "reflect from your sail, they transfer "
        "momentum to the spacecraft.\n\n"
        "The sail does not need fuel, but its "
        "acceleration depends on its orientation."
    ),
    (
        "HINT 2/4 — ORBITAL MOTION\n\n"
        "Pointing the sail straight away from "
        "the Sun produces mainly radial acceleration.\n\n"
        "Tilting it introduces a tangential "
        "component, changing orbital energy "
        "and angular momentum."
    ),
    (
        "HINT 3/4 — RENDEZVOUS\n\n"
        "Reaching Vera's position is not enough.\n\n"
        "If your relative velocity is too high, "
        "you may pass her or collide.\n\n"
        "Use several sail orientations to "
        "reshape your orbit, then retract the "
        "sail and coast toward the encounter."
    ),
    (
        "HINT 4/4 — FLIGHT PLAN\n\n"
        "Try a six-phase maneuver. Each phase "
        "lasts 5/6 of a simulated year.\n\n"
        "Start with approximately:\n"
        "-55.0°, +1.6°, +83.2°, -2.9°, +53.5°.\n\n"
        "Retract the sail during phase six.\n\n"
        "Use PREVIEW ROUTE to check whether "
        "your plan reaches safe docking conditions."
    )
]

COSMO_SUCCESS = (
    "COSMO: Rendezvous confirmed!\n\n"
    "Ada matched Vera's orbital position and "
    "reduced their relative velocity enough "
    "for a safe approach.\n\n"
    "Solar sailing demonstrates how continuous "
    "radiation pressure can gradually modify "
    "a spacecraft's trajectory without "
    "consuming propellant.\n\n"
    "This simulation uses amplified sail "
    "acceleration for educational gameplay."
)


# ============================================================
# MAIN UI
# ============================================================

class SolarSailUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = SolarSailPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = True
        self.after_id = None
        self.completed_notified = False

        self.last_frame = time.monotonic()

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 75.0

        self.mode = tk.StringVar(value="planned")

        self.angle_var = tk.DoubleVar(value=0.0)
        self.angle_label_var = tk.StringVar(value="+0.0°")

        self.sail_button_var = tk.StringVar(
            value="DEPLOY SAIL"
        )

        self.info_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Plan a safe orbital rendezvous."
        )

        self.cosmo_var = tk.StringVar(
            value=COSMO_INTRO
        )

        self.hint_level = 0

        self.phase_vars = []
        self.planned_angles = None
        self.current_phase = -1

        self.preview_trajectory = []
        self.preview_target_trajectory = []
        self.preview_result = None

        self.build_ui()

        self.update_labels()
        self.update_info()
        self.draw_scene()

        self.animate()

    # ========================================================
    # UI BUILDING
    # ========================================================

    def build_ui(self):

        self.canvas = tk.Canvas(
            self,
            width=SCENE_WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.panel = tk.Frame(
            self,
            width=PANEL_WIDTH,
            bg=PANEL_BG
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        # Scrollable control panel.

        self.panel_canvas = tk.Canvas(
            self.panel,
            width=PANEL_WIDTH - 18,
            height=HEIGHT,
            bg=PANEL_BG,
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            self.panel,
            orient="vertical",
            command=self.panel_canvas.yview
        )

        self.panel_canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.panel_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.controls = tk.Frame(
            self.panel_canvas,
            bg=PANEL_BG
        )

        self.panel_window = (
            self.panel_canvas.create_window(
                (0, 0),
                window=self.controls,
                anchor="nw",
                width=PANEL_WIDTH - 18
            )
        )

        self.controls.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.panel_canvas.bind(
            "<Configure>",
            self.resize_panel_window
        )

        self.build_header()
        self.build_mode_controls()
        self.build_planning_controls()
        self.build_manual_controls()
        self.build_action_controls()
        self.build_information()
        self.build_cosmo_panel()

        self.refresh_mode()

    def update_scroll_region(self, event=None):

        self.panel_canvas.configure(
            scrollregion=(
                self.panel_canvas.bbox("all")
            )
        )

    def resize_panel_window(self, event):

        self.panel_canvas.itemconfigure(
            self.panel_window,
            width=event.width
        )

    def add_label(
        self,
        parent,
        text,
        size=10,
        color=MUTED,
        bold=False,
        pady=4
    ):

        label = tk.Label(
            parent,
            text=text,
            font=(
                "Arial",
                size,
                "bold" if bold else "normal"
            ),
            fg=color,
            bg=parent.cget("bg"),
            justify="left",
            wraplength=PANEL_WIDTH - 48
        )

        label.pack(
            anchor="w",
            padx=16,
            pady=pady
        )

        return label

    def create_button(
        self,
        parent,
        text,
        command,
        color="#435571"
    ):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            bg=color,
            fg=TEXT,
            activebackground=color,
            activeforeground=TEXT,
            relief="flat",
            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=16,
            pady=4,
            ipady=7
        )

        return button

    def build_header(self):

        self.add_label(
            self.controls,
            "SOLAR SAIL",
            size=19,
            color=TEXT,
            bold=True,
            pady=12
        )

        self.add_label(
            self.controls,
            "CHAPTER 7 — ORBITAL RENDEZVOUS",
            size=9,
            color=CYAN
        )

    def build_mode_controls(self):

        self.add_label(
            self.controls,
            "FLIGHT CONTROL",
            size=11,
            color=GOLD,
            bold=True,
            pady=10
        )

        self.mode_frame = tk.Frame(
            self.controls,
            bg=PANEL_BG
        )

        self.mode_frame.pack(
            fill="x",
            padx=16
        )

        for text, value in (
            ("PLANNED", "planned"),
            ("MANUAL", "manual")
        ):

            tk.Radiobutton(
                self.mode_frame,
                text=text,
                variable=self.mode,
                value=value,
                command=self.refresh_mode,
                bg=PANEL_BG,
                fg=TEXT,
                selectcolor=CARD_BG,
                activebackground=PANEL_BG,
                activeforeground=CYAN,
                font=("Arial", 9, "bold")
            ).pack(
                side="left",
                padx=4
            )

    def build_planning_controls(self):

        self.planning_frame = tk.Frame(
            self.controls,
            bg=PANEL_BG
        )

        self.add_label(
            self.planning_frame,
            "SIX-PHASE FLIGHT PLAN",
            size=11,
            color=CYAN,
            bold=True,
            pady=10
        )

        self.add_label(
            self.planning_frame,
            "Each phase lasts 0.8333 simulated years. "
            "Set the sail angle for phases 1–5. "
            "Phase 6 uses coasting.",
            size=9
        )

        for index, reference in enumerate(
            REFERENCE_ANGLES
        ):

            row = tk.Frame(
                self.planning_frame,
                bg=PANEL_BG
            )

            row.pack(
                fill="x",
                padx=16,
                pady=3
            )

            tk.Label(
                row,
                text=f"PHASE {index + 1}",
                width=10,
                anchor="w",
                font=("Arial", 9, "bold"),
                fg=MUTED,
                bg=PANEL_BG
            ).pack(side="left")

            if reference is None:

                tk.Label(
                    row,
                    text="SAIL RETRACTED",
                    font=("Arial", 9, "bold"),
                    fg=GOLD,
                    bg=PANEL_BG
                ).pack(side="left")

                self.phase_vars.append(None)

            else:

                variable = tk.StringVar(
                    value=f"{reference:+.1f}"
                )

                entry = tk.Entry(
                    row,
                    textvariable=variable,
                    width=9,
                    justify="center",
                    font=("Arial", 11),
                    bg=CARD_BG,
                    fg=TEXT,
                    insertbackground=TEXT,
                    relief="flat"
                )

                entry.pack(side="left")

                tk.Label(
                    row,
                    text="degrees",
                    font=("Arial", 9),
                    fg=MUTED,
                    bg=PANEL_BG
                ).pack(
                    side="left",
                    padx=6
                )

                self.phase_vars.append(variable)

        self.preview_button = self.create_button(
            self.planning_frame,
            "PREVIEW ROUTE",
            self.preview_route,
            "#386A76"
        )

        self.preview_label_var = tk.StringVar(
            value="No trajectory preview calculated."
        )

        tk.Label(
            self.planning_frame,
            textvariable=self.preview_label_var,
            font=("Arial", 9),
            fg=GOLD,
            bg=PANEL_BG,
            justify="left",
            wraplength=PANEL_WIDTH - 48
        ).pack(
            padx=16,
            pady=8,
            anchor="w"
        )

    def build_manual_controls(self):

        self.manual_frame = tk.Frame(
            self.controls,
            bg=PANEL_BG
        )

        self.add_label(
            self.manual_frame,
            "MANUAL SAIL ORIENTATION",
            size=11,
            color=CYAN,
            bold=True,
            pady=10
        )

        tk.Label(
            self.manual_frame,
            textvariable=self.angle_label_var,
            font=("Arial", 17, "bold"),
            fg=CYAN,
            bg=PANEL_BG
        ).pack(pady=5)

        self.angle_slider = tk.Scale(
            self.manual_frame,
            from_=-85,
            to=85,
            resolution=0.1,
            orient="horizontal",
            variable=self.angle_var,
            command=self.on_angle_change,
            length=245,
            showvalue=False,
            bg=PANEL_BG,
            fg=TEXT,
            troughcolor="#465976",
            highlightthickness=0
        )

        self.angle_slider.pack(pady=5)

        self.sail_button = self.create_button(
            self.manual_frame,
            "DEPLOY SAIL",
            self.toggle_sail,
            "#386A76"
        )

        self.sail_button.configure(
            textvariable=self.sail_button_var
        )

    def build_action_controls(self):

        self.action_frame = tk.Frame(
            self.controls,
            bg=PANEL_BG
        )

        self.action_frame.pack(
            fill="x",
            pady=10
        )

        self.start_button = self.create_button(
            self.action_frame,
            "START SIMULATION",
            self.start_simulation,
            "#7356AE"
        )

        self.create_button(
            self.action_frame,
            "RESET",
            self.reset_simulation
        )

        if self.on_back is not None:

            self.create_button(
                self.action_frame,
                "BACK",
                self.go_back,
                "#35445C"
            )

    def build_information(self):

        self.add_label(
            self.controls,
            "FLIGHT TELEMETRY",
            size=11,
            color=GOLD,
            bold=True,
            pady=10
        )

        tk.Label(
            self.controls,
            textvariable=self.info_var,
            font=("Arial", 9),
            fg=MUTED,
            bg=PANEL_BG,
            justify="left",
            wraplength=PANEL_WIDTH - 48
        ).pack(
            anchor="w",
            padx=16,
            pady=6
        )

        tk.Label(
            self.controls,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=GOLD,
            bg=PANEL_BG,
            justify="left",
            wraplength=PANEL_WIDTH - 48
        ).pack(
            anchor="w",
            padx=16,
            pady=10
        )

    def build_cosmo_panel(self):

        frame = tk.Frame(
            self.controls,
            bg=CARD_BG,
            padx=12,
            pady=12
        )

        frame.pack(
            fill="x",
            padx=12,
            pady=(8, 20)
        )

        tk.Label(
            frame,
            text="COSMO — MISSION SCIENCE",
            font=("Arial", 10, "bold"),
            fg=CYAN,
            bg=CARD_BG
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.cosmo_label = tk.Label(
            frame,
            textvariable=self.cosmo_var,
            font=("Arial", 9),
            fg=TEXT,
            bg=CARD_BG,
            justify="left",
            anchor="nw",
            wraplength=PANEL_WIDTH - 65
        )

        self.cosmo_label.pack(
            fill="x"
        )

        self.hint_button = tk.Button(
            frame,
            text="COSMO HINT (0/4)",
            command=self.show_hint,
            font=("Arial", 9, "bold"),
            bg="#386A76",
            fg=TEXT,
            relief="flat"
        )

        self.hint_button.pack(
            fill="x",
            pady=(12, 0),
            ipady=6
        )

    # ========================================================
    # MODES
    # ========================================================

    def refresh_mode(self):

        self.planning_frame.pack_forget()
        self.manual_frame.pack_forget()

        if self.mode.get() == "planned":

            self.planning_frame.pack(
                fill="x",
                before=self.action_frame
            )

        else:

            self.manual_frame.pack(
                fill="x",
                before=self.action_frame
            )

        self.update_scroll_region()

    # ========================================================
    # COSMO
    # ========================================================

    def say(self, message):

        self.cosmo_var.set(message)

    def show_hint(self):

        if self.puzzle.completed:
            return

        if self.hint_level >= len(COSMO_HINTS):
            self.say(COSMO_HINTS[-1])
            return

        self.say(
            COSMO_HINTS[self.hint_level]
        )

        self.hint_level += 1

        self.hint_button.configure(
            text=(
                f"COSMO HINT "
                f"({self.hint_level}/4)"
            )
        )

    # ========================================================
    # FLIGHT PLAN
    # ========================================================

    def read_flight_plan(self):

        angles = []

        for index, variable in enumerate(
            self.phase_vars
        ):

            if variable is None:
                angles.append(None)
                continue

            raw = variable.get().strip()

            # Accept both decimal separators.
            raw = raw.replace(",", ".")

            try:
                angle = float(raw)

            except ValueError:

                raise ValueError(
                    f"Phase {index + 1}: "
                    "enter a valid angle."
                )

            if not math.isfinite(angle):

                raise ValueError(
                    f"Phase {index + 1}: "
                    "angle must be finite."
                )

            if not -85.0 <= angle <= 85.0:

                raise ValueError(
                    f"Phase {index + 1}: "
                    "angle must be between "
                    "-85° and +85°."
                )

            angles.append(angle)

        return angles

    @staticmethod
    def apply_phase_to_puzzle(
        puzzle,
        angles,
        phase
    ):

        angle = angles[phase]

        if angle is None:

            puzzle.update({
                "type": "retract"
            })

        else:

            puzzle.update({
                "type": "adjust",
                "angle": angle
            })

            puzzle.update({
                "type": "deploy"
            })

    @staticmethod
    def get_phase_index(simulation_time):

        phase = int(
            (simulation_time + 1e-10)
            / PHASE_DURATION
        )

        return min(
            phase,
            PHASE_COUNT - 1
        )

    # ========================================================
    # PREVIEW SIMULATION
    # ========================================================

    def preview_route(self):

        if self.puzzle.status != "ready":

            self.say(
                "COSMO: Reset the simulation "
                "before calculating a new "
                "flight preview."
            )

            return

        try:
            angles = self.read_flight_plan()

        except ValueError as error:

            self.preview_label_var.set(
                str(error)
            )

            self.say(
                f"COSMO: {error}"
            )

            return

        # Use a separate backend instance.
        # The actual game state remains untouched.

        preview = SolarSailPuzzle()

        self.apply_phase_to_puzzle(
            preview,
            angles,
            0
        )

        preview.update({
            "type": "launch"
        })

        current_phase = 0

        # Run the same physics as the real game.
        # Split steps at phase boundaries.

        while preview.status == "flying":

            phase = self.get_phase_index(
                preview.time
            )

            if phase != current_phase:

                current_phase = phase

                self.apply_phase_to_puzzle(
                    preview,
                    angles,
                    phase
                )

            dt = preview.TIME_STEP

            if phase < PHASE_COUNT - 1:

                boundary = (
                    (phase + 1)
                    * PHASE_DURATION
                )

                remaining = (
                    boundary - preview.time
                )

                if remaining > 1e-10:

                    dt = min(
                        dt,
                        remaining
                    )

            preview.update({
                "type": "tick",
                "dt": dt
            })

        state = preview.get_state()

        self.preview_trajectory = list(
            state["trajectory"]
        )

        self.preview_target_trajectory = list(
            state["target_trajectory"]
        )

        self.preview_result = {
            "status": state["status"],
            "time": state["time"],
            "distance": state["distance"],
            "relative_speed": state["relative_speed"],
            "closest_distance": (
                state["closest_distance"]
            ),
            "closest_relative_speed": (
                state["closest_relative_speed"]
            )
        }

        if state["status"] == "success":

            self.preview_label_var.set(
                "SAFE RENDEZVOUS PREDICTED\n"
                f"Time: {state['time']:.3f} yr\n"
                f"Distance: {state['distance']:.5f} AU\n"
                "Relative speed: "
                f"{state['relative_speed']:.4f} AU/yr"
            )

            self.say(
                "COSMO: Your predicted trajectory "
                "satisfies both docking conditions!\n\n"
                "Ada approaches Vera closely enough "
                "and with a sufficiently low "
                "relative velocity.\n\n"
                "Start the simulation to execute "
                "your flight plan."
            )

        else:

            self.preview_label_var.set(
                "RENDEZVOUS NOT ACHIEVED\n"
                f"Result: {state['status']}\n"
                "Closest distance: "
                f"{state['closest_distance']:.5f} AU\n"
                "Speed at closest approach: "
                f"{state['closest_relative_speed']:.4f} "
                "AU/yr"
            )

            self.say(
                "COSMO: The predicted trajectory "
                "does not achieve a safe rendezvous.\n\n"
                "Compare the closest distance "
                "and relative speed with the "
                "docking limits.\n\n"
                "Try changing one phase at a time "
                "to see how the trajectory responds."
            )

        self.draw_scene()

    # ========================================================
    # MANUAL CONTROLS
    # ========================================================

    def on_angle_change(self, value):

        if self.mode.get() != "manual":
            return

        self.puzzle.update({
            "type": "adjust",
            "angle": float(value)
        })

        self.update_labels()

    def toggle_sail(self):

        if self.mode.get() != "manual":
            return

        state = self.puzzle.get_state()

        if state["status"] not in (
            "ready",
            "flying"
        ):
            return

        if state["sail_deployed"]:

            self.puzzle.update({
                "type": "retract"
            })

            self.sail_button_var.set(
                "DEPLOY SAIL"
            )

            self.status_var.set(
                "Sail retracted. Gravity only."
            )

        else:

            self.puzzle.update({
                "type": "deploy"
            })

            self.sail_button_var.set(
                "RETRACT SAIL"
            )

            self.status_var.set(
                "Sail deployed."
            )

        self.draw_scene()

    # ========================================================
    # START / RESET
    # ========================================================

    def start_simulation(self):

        if self.puzzle.status != "ready":
            return

        if self.mode.get() == "planned":

            try:
                self.planned_angles = (
                    self.read_flight_plan()
                )

            except ValueError as error:

                self.say(
                    f"COSMO: {error}"
                )

                return

            self.current_phase = 0

            self.apply_phase_to_puzzle(
                self.puzzle,
                self.planned_angles,
                0
            )

        else:

            self.planned_angles = None
            self.current_phase = -1

        self.puzzle.update({
            "type": "launch"
        })

        self.last_frame = time.monotonic()

        self.start_button.configure(
            state="disabled"
        )

        self.status_var.set(
            "Simulation running."
        )

        self.say(
            "COSMO: Flight initiated.\n\n"
            "Watch how Ada's orbit changes "
            "under solar radiation pressure.\n\n"
            "Remember: successful docking "
            "requires both close proximity "
            "and low relative velocity."
        )

    def reset_simulation(self):

        self.puzzle.reset()

        self.completed_notified = False

        self.planned_angles = None
        self.current_phase = -1

        self.preview_trajectory = []
        self.preview_target_trajectory = []
        self.preview_result = None

        self.preview_label_var.set(
            "No trajectory preview calculated."
        )

        self.angle_var.set(0.0)

        self.sail_button_var.set(
            "DEPLOY SAIL"
        )

        self.start_button.configure(
            state="normal"
        )

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.zoom = 75.0

        self.last_frame = time.monotonic()

        self.hint_level = 0

        self.hint_button.configure(
            text="COSMO HINT (0/4)"
        )

        self.status_var.set(
            "Simulation reset. Plan your route."
        )

        self.say(COSMO_INTRO)

        self.update_labels()
        self.update_info()
        self.draw_scene()

    def go_back(self):

        self.running = False

        if self.after_id is not None:

            self.after_cancel(
                self.after_id
            )

            self.after_id = None

        if self.on_back is not None:
            self.on_back()

    # ========================================================
    # TELEMETRY
    # ========================================================

    def update_labels(self):

        self.angle_label_var.set(
            f"{self.angle_var.get():+.1f}°"
        )

    def update_info(self):

        state = self.puzzle.get_state()

        phase_text = ""

        if (
            self.planned_angles is not None
            and state["status"] != "ready"
        ):

            phase_text = (
                f"Flight phase: "
                f"{self.current_phase + 1}/6\n"
            )

        self.info_var.set(
            f"Time: {state['time']:.3f} yr\n"
            f"{phase_text}"
            f"Distance: {state['distance']:.5f} AU\n"
            "Relative speed: "
            f"{state['relative_speed']:.4f} AU/yr\n"
            "Docking range: "
            f"{state['docking_distance']:.3f} AU\n"
            "Safe speed: "
            f"{state['docking_speed']:.2f} AU/yr\n"
            "Sail: "
            f"{'DEPLOYED' if state['sail_deployed'] else 'RETRACTED'}"
        )

    # ========================================================
    # CAMERA
    # ========================================================

    def update_camera(self, state):

        ship_x = state["x"]
        ship_y = state["y"]

        target_x = state["target_x"]
        target_y = state["target_y"]

        midpoint_x = (
            ship_x + target_x
        ) / 2

        midpoint_y = (
            ship_y + target_y
        ) / 2

        distance = state["distance"]

        if distance < 0.8:

            desired_x = midpoint_x
            desired_y = midpoint_y

            desired_zoom = min(
                850.0,
                max(
                    90.0,
                    350.0 / max(
                        distance,
                        0.05
                    )
                )
            )

        else:

            desired_x = 0.0
            desired_y = 0.0
            desired_zoom = 75.0

        smoothing = 0.05

        self.camera_x += (
            desired_x - self.camera_x
        ) * smoothing

        self.camera_y += (
            desired_y - self.camera_y
        ) * smoothing

        self.zoom += (
            desired_zoom - self.zoom
        ) * smoothing

    def world_to_screen(self, x, y):

        sx = (
            SCENE_WIDTH / 2
            + (x - self.camera_x) * self.zoom
        )

        sy = (
            HEIGHT / 2
            - (y - self.camera_y) * self.zoom
        )

        return sx, sy

    # ========================================================
    # DRAWING
    # ========================================================

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.update_camera(state)

        self.draw_stars()
        self.draw_orbits()

        if self.preview_trajectory:

            self.draw_path(
                self.preview_trajectory,
                GOLD,
                dashed=True
            )

        self.draw_path(
            state["trajectory"],
            CYAN
        )

        self.draw_path(
            state["target_trajectory"],
            PURPLE
        )

        self.draw_sun()
        self.draw_connection(state)
        self.draw_spacecraft(state)
        self.draw_hud(state)

    def draw_stars(self):

        for i in range(90):

            x = (
                i * 97 + 23
            ) % SCENE_WIDTH

            y = (
                i * 157 + 41
            ) % HEIGHT

            size = 2 if i % 5 == 0 else 1

            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#53698B",
                outline=""
            )

    def draw_orbits(self):

        center_x, center_y = (
            self.world_to_screen(0, 0)
        )

        for radius, color in (
            (
                self.puzzle.START_RADIUS,
                "#314B68"
            ),
            (
                self.puzzle.TARGET_RADIUS,
                "#493C69"
            )
        ):

            r = radius * self.zoom

            self.canvas.create_oval(
                center_x - r,
                center_y - r,
                center_x + r,
                center_y + r,
                outline=color,
                dash=(3, 5)
            )

    def draw_path(
        self,
        points,
        color,
        dashed=False
    ):

        if len(points) < 2:
            return

        stride = max(
            1,
            len(points) // 600
        )

        sampled = list(
            points[::stride]
        )

        if sampled[-1] != points[-1]:

            sampled.append(
                points[-1]
            )

        coordinates = []

        for x, y in sampled:

            sx, sy = self.world_to_screen(
                x, y
            )

            coordinates.extend(
                (sx, sy)
            )

        if len(coordinates) < 4:
            return

        options = {
            "fill": color,
            "width": 2
        }

        if dashed:
            options["dash"] = (5, 5)

        self.canvas.create_line(
            *coordinates,
            **options
        )

    def draw_sun(self):

        x, y = self.world_to_screen(
            0, 0
        )

        radius = max(
            8,
            min(
                24,
                0.12 * self.zoom
            )
        )

        self.canvas.create_oval(
            x - radius * 1.6,
            y - radius * 1.6,
            x + radius * 1.6,
            y + radius * 1.6,
            fill="#654A29",
            outline=""
        )

        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=GOLD,
            outline="#FFF0AD",
            width=2
        )

    def draw_connection(self, state):

        x1, y1 = self.world_to_screen(
            state["x"],
            state["y"]
        )

        x2, y2 = self.world_to_screen(
            state["target_x"],
            state["target_y"]
        )

        if (
            state["distance"]
            <= state["docking_distance"]
        ):

            color = GREEN

        else:

            color = "#5C789A"

        self.canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill=color,
            dash=(4, 5)
        )

    def draw_spacecraft(self, state):

        ship_x, ship_y = (
            self.world_to_screen(
                state["x"],
                state["y"]
            )
        )

        target_x, target_y = (
            self.world_to_screen(
                state["target_x"],
                state["target_y"]
            )
        )

        self.draw_ship(
            ship_x,
            ship_y,
            CYAN,
            "ADA"
        )

        self.draw_ship(
            target_x,
            target_y,
            PURPLE,
            "VERA"
        )

        if state["sail_deployed"]:

            self.draw_sail(
                ship_x,
                ship_y,
                state
            )

    def draw_ship(
        self,
        x,
        y,
        color,
        label
    ):

        self.canvas.create_polygon(
            x,
            y - 11,
            x - 8,
            y + 9,
            x,
            y + 5,
            x + 8,
            y + 9,
            fill=color,
            outline=TEXT
        )

        self.canvas.create_text(
            x,
            y + 23,
            text=label,
            fill=color,
            font=("Arial", 10, "bold")
        )

    def draw_sail(
        self,
        x,
        y,
        state
    ):

        radial_angle = math.atan2(
            state["y"],
            state["x"]
        )

        normal_angle = (
            radial_angle
            + math.radians(
                state["sail_angle"]
            )
        )

        surface_angle = (
            normal_angle
            + math.pi / 2
        )

        dx = (
            math.cos(surface_angle)
            * 23
        )

        dy = (
            math.sin(surface_angle)
            * 23
        )

        self.canvas.create_line(
            x - dx,
            y + dy,
            x + dx,
            y - dy,
            fill=GOLD,
            width=4
        )

        self.canvas.create_line(
            x - dx,
            y + dy,
            x + dx,
            y - dy,
            fill="#FFF2C6",
            width=1
        )

    def draw_hud(self, state):

        self.canvas.create_text(
            20,
            20,
            text="CHAPTER 7 — SOLAR SAIL",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            49,
            text="Solar radiation pressure",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

        if self.preview_trajectory:

            self.canvas.create_text(
                20,
                HEIGHT - 35,
                text=(
                    "GOLD: predicted route  |  "
                    "CYAN: Ada  |  PURPLE: Vera"
                ),
                fill=GOLD,
                font=("Arial", 9),
                anchor="nw"
            )

        status = state["status"]

        if status == "success":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="SAFE RENDEZVOUS ACHIEVED",
                fill=GREEN,
                font=("Arial", 16, "bold")
            )

        elif status == "collision":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="COLLISION — UNSAFE SPEED",
                fill=RED,
                font=("Arial", 13, "bold")
            )

        elif status == "sun_collision":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="SOLAR COLLISION",
                fill=RED,
                font=("Arial", 15, "bold")
            )

        elif status == "timeout":

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                100,
                text="TIME LIMIT REACHED",
                fill=RED,
                font=("Arial", 15, "bold")
            )

    # ========================================================
    # STATUS AND FEEDBACK
    # ========================================================

    def handle_status(self, state):

        status = state["status"]

        if status == "success":

            self.status_var.set(
                "Success! Ada reached Vera safely."
            )

            self.say(COSMO_SUCCESS)

            if (
                not self.completed_notified
                and self.on_complete is not None
            ):

                self.completed_notified = True

                self.after_idle(
                    self.on_complete
                )

        elif status == "collision":

            self.status_var.set(
                "Collision! Relative speed too high."
            )

            self.say(
                "COSMO: Ada reached Vera's "
                "position, but the approach "
                "velocity was unsafe.\n\n"
                "An orbital rendezvous requires "
                "matching velocities, not just "
                "intersecting trajectories.\n\n"
                "Try adjusting the later phases "
                "to reduce relative speed."
            )

        elif status == "sun_collision":

            self.status_var.set(
                "Ada's ship collided with the Sun."
            )

            self.say(
                "COSMO: The trajectory brought "
                "Ada dangerously close to the Sun.\n\n"
                "Solar gravity grows stronger "
                "as distance decreases.\n\n"
                "Try changing the sail orientation "
                "earlier in the flight."
            )

        elif status == "timeout":

            self.status_var.set(
                "Time limit reached."
            )

            self.say(
                "COSMO: Eight simulated years "
                "have passed without a safe "
                "rendezvous.\n\n"
                "Review the predicted trajectory "
                "and the closest approach.\n\n"
                "A smaller distance alone is "
                "not enough: relative velocity "
                "must also be low."
            )

    # ========================================================
    # ANIMATION AND PHASE EXECUTION
    # ========================================================

    def advance_planned_flight(self, dt):

        remaining = dt

        while (
            remaining > 1e-12
            and self.puzzle.status == "flying"
        ):

            phase = self.get_phase_index(
                self.puzzle.time
            )

            if phase != self.current_phase:

                self.current_phase = phase

                self.apply_phase_to_puzzle(
                    self.puzzle,
                    self.planned_angles,
                    phase
                )

            step = remaining

            if phase < PHASE_COUNT - 1:

                boundary = (
                    (phase + 1)
                    * PHASE_DURATION
                )

                until_boundary = (
                    boundary
                    - self.puzzle.time
                )

                if until_boundary > 1e-10:

                    step = min(
                        step,
                        until_boundary
                    )

            if step <= 1e-12:
                break

            self.puzzle.update({
                "type": "tick",
                "dt": step
            })

            remaining -= step

    def animate(self):

        if not self.running:
            return

        now = time.monotonic()

        elapsed = min(
            max(
                0.0,
                now - self.last_frame
            ),
            0.1
        )

        self.last_frame = now

        previous_status = (
            self.puzzle.status
        )

        if previous_status == "flying":

            dt = (
                elapsed
                * SIMULATION_SPEED
            )

            if self.planned_angles is not None:

                self.advance_planned_flight(
                    dt
                )

            else:

                self.puzzle.update({
                    "type": "tick",
                    "dt": dt
                })

        state = self.puzzle.get_state()

        if (
            previous_status == "flying"
            and state["status"] != "flying"
        ):

            self.handle_status(state)

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate
        )

    # ========================================================
    # CLEANUP
    # ========================================================

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


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "ASTRA — Chapter 7: Solar Sail"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(
        False,
        False
    )

    screen = SolarSailUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
