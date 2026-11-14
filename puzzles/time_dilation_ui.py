
import math
import time
import tkinter as tk

from puzzles.time_dilation import TimeDilationPuzzle


# ============================================================
# ASTRA — Chapter 5: Time Dilation
#
# Two animated clocks:
# Earth coordinate time and spacecraft proper time.
#
# Educational model:
# Constant relative velocity, no acceleration,
# no gravitational time dilation.
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 640

BG = "#0B1425"
PANEL = "#1D2B40"
TEXT = "#F5F7FF"
MUTED = "#ACBDD5"

EARTH_COLOR = "#83B7FF"
SHIP_COLOR = "#E6B5FF"
ACCENT = "#F6CA78"
SUCCESS = "#91E4AE"

FRAME_MS = 30

# One real second represents one simulated Earth year.
SIMULATION_SPEED = 1.0


class TimeDilationUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = TimeDilationPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.after_id = None
        self.last_frame = time.monotonic()
        self.completed_notified = False

        state = self.puzzle.get_state()

        self.velocity_var = tk.DoubleVar(
            value=state["velocity"]
        )

        self.duration_var = tk.DoubleVar(
            value=state["duration"]
        )

        self.velocity_label_var = tk.StringVar()
        self.duration_label_var = tk.StringVar()

        self.info_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value="Configure the journey, then press START."
        )

        self.build_ui()
        self.update_labels()
        self.update_info()
        self.draw_scene()

        self.animate()

    # ========================================================
    # Interface
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
            width=WIDTH - SCENE_WIDTH,
            bg=PANEL
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="TIME\nDILATION",
            font=("Arial", 19, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(23, 17))

        tk.Label(
            self.panel,
            text="Spacecraft velocity",
            fg=MUTED,
            bg=PANEL,
            font=("Arial", 10)
        ).pack()

        tk.Label(
            self.panel,
            textvariable=self.velocity_label_var,
            fg=SHIP_COLOR,
            bg=PANEL,
            font=("Arial", 14, "bold")
        ).pack(pady=4)

        self.velocity_slider = tk.Scale(
            self.panel,
            from_=0.0,
            to=0.99,
            resolution=0.01,
            orient="horizontal",
            variable=self.velocity_var,
            command=self.on_velocity_change,
            length=210,
            showvalue=False,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#455774",
            highlightthickness=0
        )

        self.velocity_slider.pack(pady=(0, 14))

        tk.Label(
            self.panel,
            text="Earth journey duration",
            fg=MUTED,
            bg=PANEL,
            font=("Arial", 10)
        ).pack()

        tk.Label(
            self.panel,
            textvariable=self.duration_label_var,
            fg=EARTH_COLOR,
            bg=PANEL,
            font=("Arial", 14, "bold")
        ).pack(pady=4)

        self.duration_slider = tk.Scale(
            self.panel,
            from_=1.0,
            to=30.0,
            resolution=0.5,
            orient="horizontal",
            variable=self.duration_var,
            command=self.on_duration_change,
            length=210,
            showvalue=False,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#455774",
            highlightthickness=0
        )

        self.duration_slider.pack(pady=(0, 14))

        self.start_button = tk.Button(
            self.panel,
            text="START",
            command=self.start_simulation,
            font=("Arial", 11, "bold"),
            bg="#7056AC",
            fg=TEXT,
            relief="flat"
        )

        self.start_button.pack(
            fill="x",
            padx=20,
            pady=(8, 5),
            ipady=8
        )

        tk.Button(
            self.panel,
            text="RESET",
            command=self.reset_simulation,
            font=("Arial", 10, "bold"),
            bg="#435571",
            fg=TEXT,
            relief="flat"
        ).pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=7
        )

        if self.on_back is not None:

            tk.Button(
                self.panel,
                text="BACK",
                command=self.go_back,
                font=("Arial", 10),
                bg=PANEL,
                fg=MUTED,
                relief="flat"
            ).pack(pady=6)

        tk.Label(
            self.panel,
            textvariable=self.info_var,
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL,
            justify="left",
            wraplength=220
        ).pack(
            padx=20,
            pady=(18, 8),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=ACCENT,
            bg=PANEL,
            wraplength=220,
            justify="center"
        ).pack(
            padx=15,
            pady=8
        )

    # ========================================================
    # Controls
    # ========================================================

    def update_labels(self):

        self.velocity_label_var.set(
            f"{self.velocity_var.get():.2f} c"
        )

        self.duration_label_var.set(
            f"{self.duration_var.get():.1f} years"
        )

    def on_velocity_change(self, value):

        self.puzzle.update({
            "type": "adjust",
            "parameter": "velocity",
            "value": float(value)
        })

        self.completed_notified = False

        self.status_var.set(
            "Velocity adjusted."
        )

        self.update_labels()
        self.update_info()

    def on_duration_change(self, value):

        self.puzzle.update({
            "type": "adjust",
            "parameter": "duration",
            "value": float(value)
        })

        self.completed_notified = False

        self.status_var.set(
            "Journey duration adjusted."
        )

        self.update_labels()
        self.update_info()

    def start_simulation(self):

        if self.puzzle.get_state()["running"]:
            return

        self.puzzle.update({
            "type": "start"
        })

        self.completed_notified = False

        self.velocity_slider.config(
            state="disabled"
        )

        self.duration_slider.config(
            state="disabled"
        )

        self.start_button.config(
            state="disabled"
        )

        self.status_var.set(
            "Journey in progress..."
        )

        self.last_frame = time.monotonic()

    def reset_simulation(self):

        self.puzzle.reset()

        state = self.puzzle.get_state()

        self.velocity_var.set(
            state["velocity"]
        )

        self.duration_var.set(
            state["duration"]
        )

        self.velocity_slider.config(
            state="normal"
        )

        self.duration_slider.config(
            state="normal"
        )

        self.start_button.config(
            state="normal"
        )

        self.completed_notified = False

        self.status_var.set(
            "Clocks synchronized."
        )

        self.last_frame = time.monotonic()

        self.update_labels()
        self.update_info()
        self.draw_scene()

    def go_back(self):

        if self.after_id is not None:

            self.after_cancel(
                self.after_id
            )

            self.after_id = None

        if self.on_back is not None:
            self.on_back()

    # ========================================================
    # Clock drawing
    # ========================================================

    def draw_clock(
        self,
        cx,
        cy,
        radius,
        elapsed_years,
        color,
        title
    ):

        self.canvas.create_text(
            cx,
            cy - radius - 45,
            text=title,
            fill=color,
            font=("Arial", 17, "bold")
        )

        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill="#16233B",
            outline=color,
            width=4
        )

        # Clock markers.
        for hour in range(12):

            angle = (
                2 * math.pi * hour / 12
                - math.pi / 2
            )

            outer = radius - 9
            inner = radius - 21

            x1 = cx + inner * math.cos(angle)
            y1 = cy + inner * math.sin(angle)

            x2 = cx + outer * math.cos(angle)
            y2 = cy + outer * math.sin(angle)

            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=MUTED,
                width=2
            )

        # One full revolution represents one year.
        angle = (
            2 * math.pi * elapsed_years
            - math.pi / 2
        )

        hand_length = radius * 0.65

        hx = (
            cx
            + hand_length * math.cos(angle)
        )

        hy = (
            cy
            + hand_length * math.sin(angle)
        )

        self.canvas.create_line(
            cx,
            cy,
            hx,
            hy,
            fill=color,
            width=4
        )

        self.canvas.create_oval(
            cx - 5,
            cy - 5,
            cx + 5,
            cy + 5,
            fill=TEXT,
            outline=""
        )

        self.canvas.create_text(
            cx,
            cy + radius + 28,
            text=f"{elapsed_years:.2f} years",
            fill=TEXT,
            font=("Arial", 15, "bold")
        )

    # ========================================================
    # Scene
    # ========================================================

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.draw_background()

        self.canvas.create_text(
            20,
            20,
            text="CHAPTER 5 — TIME DILATION",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            50,
            text="Two clocks, different elapsed times",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

        earth_time = state[
            "elapsed_earth_time"
        ]

        ship_time = state[
            "elapsed_ship_time"
        ]

        self.draw_clock(
            cx=175,
            cy=260,
            radius=100,
            elapsed_years=earth_time,
            color=EARTH_COLOR,
            title="EARTH"
        )

        self.draw_clock(
            cx=465,
            cy=260,
            radius=100,
            elapsed_years=ship_time,
            color=SHIP_COLOR,
            title="SPACECRAFT"
        )

        self.draw_comparison(
            earth_time,
            ship_time
        )

        self.canvas.create_text(
            20,
            HEIGHT - 24,
            text=(
                "Idealized constant-velocity model "
                "— one clock revolution = one year"
            ),
            fill=MUTED,
            font=("Arial", 9),
            anchor="nw"
        )

    def draw_background(self):

        for i in range(75):

            x = (
                i * 97 + 31
            ) % SCENE_WIDTH

            y = (
                i * 151 + 47
            ) % HEIGHT

            size = 1 if i % 5 else 2

            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#536A8D",
                outline=""
            )

    def draw_comparison(
        self,
        earth_time,
        ship_time
    ):

        difference = (
            earth_time - ship_time
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            420,
            text="TIME DIFFERENCE",
            fill=MUTED,
            font=("Arial", 12, "bold")
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            455,
            text=f"{difference:.3f} years",
            fill=ACCENT,
            font=("Arial", 24, "bold")
        )

        # Progress towards the target difference.
        target = (
            self.puzzle.TARGET_DIFFERENCE
        )

        progress = min(
            1.0,
            difference / target
        )

        left = 130
        right = 510
        top = 495
        bottom = 510

        self.canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="#28384F",
            outline=""
        )

        self.canvas.create_rectangle(
            left,
            top,
            left + (right - left) * progress,
            bottom,
            fill=SHIP_COLOR,
            outline=""
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            530,
            text=(
                f"Target: {target:.2f} years "
                f"(±{self.puzzle.TARGET_TOLERANCE:.2f})"
            ),
            fill=MUTED,
            font=("Arial", 10)
        )

    # ========================================================
    # Animation
    # ========================================================

    def animate(self):

        now = time.monotonic()

        elapsed = min(
            now - self.last_frame,
            0.1
        )

        self.last_frame = now

        state = self.puzzle.get_state()

        if state["running"]:

            self.puzzle.update({
                "type": "tick",
                "dt": elapsed * SIMULATION_SPEED
            })

            state = self.puzzle.get_state()

            if not state["running"]:
                self.finish_simulation(state)

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate
        )

    def finish_simulation(self, state):

        self.velocity_slider.config(
            state="normal"
        )

        self.duration_slider.config(
            state="normal"
        )

        self.start_button.config(
            state="normal"
        )

        status = state["status"]

        if status == "success":

            self.status_var.set(
                "Success! Target time difference reached."
            )

            if (
                not self.completed_notified
                and self.on_complete is not None
            ):

                self.completed_notified = True

                self.after_idle(
                    self.on_complete
                )

        elif status == "insufficient_dilation":

            self.status_var.set(
                "Time difference is too small."
            )

        elif status == "excessive_dilation":

            self.status_var.set(
                "Time difference is too large."
            )

        else:

            self.status_var.set(
                f"Simulation ended: {status}"
            )

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):

        state = self.puzzle.get_state()

        self.info_var.set(
            f"Lorentz factor: {state['gamma']:.3f}\n"
            f"Predicted Earth time: "
            f"{state['earth_time']:.2f} years\n"
            f"Predicted ship time: "
            f"{state['ship_time']:.2f} years\n"
            f"Predicted difference: "
            f"{state['time_difference']:.2f} years"
        )

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy(self):

        if self.after_id is not None:

            self.after_cancel(
                self.after_id
            )

            self.after_id = None

        super().destroy()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "ASTRA — Time Dilation"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(False, False)

    screen = TimeDilationUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
