
import math
import time
import tkinter as tk

from puzzles.time_dilation import TimeDilationPuzzle


# ============================================================
# ASTRA — Chapter 5: Time Dilation
#
# Special relativity: idealized constant-velocity model.
# Acceleration, turnaround effects and gravitational
# time dilation are not included.
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
ERROR = "#FF9999"

FRAME_MS = 30

# One real second represents one simulated Earth year.
SIMULATION_SPEED = 1.0


class TimeDilationUI(tk.Frame):

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=BG)

        self.puzzle = TimeDilationPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.after_id = None
        self.last_frame = time.monotonic()
        self.completed_notified = False

        self.hint_level = 0
        self.attempts = 0

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
            value=(
                "Ada, let's investigate how motion "
                "affects the passage of time. "
                "Choose a velocity and journey duration, "
                "then compare the two clocks!"
            )
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
            highlightthickness=0,
        )
        self.canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        self.panel = tk.Frame(
            self,
            width=WIDTH - SCENE_WIDTH,
            bg=PANEL,
        )
        self.panel.pack(side="right", fill="y")
        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="TIME\nDILATION",
            font=("Arial", 18, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center",
        ).pack(pady=(13, 8))

        tk.Label(
            self.panel,
            text="Spacecraft velocity",
            fg=MUTED,
            bg=PANEL,
            font=("Arial", 10),
        ).pack()

        tk.Label(
            self.panel,
            textvariable=self.velocity_label_var,
            fg=SHIP_COLOR,
            bg=PANEL,
            font=("Arial", 13, "bold"),
        ).pack(pady=2)

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
            highlightthickness=0,
        )
        self.velocity_slider.pack(pady=(0, 8))

        tk.Label(
            self.panel,
            text="Earth journey duration",
            fg=MUTED,
            bg=PANEL,
            font=("Arial", 10),
        ).pack()

        tk.Label(
            self.panel,
            textvariable=self.duration_label_var,
            fg=EARTH_COLOR,
            bg=PANEL,
            font=("Arial", 13, "bold"),
        ).pack(pady=2)

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
            highlightthickness=0,
        )
        self.duration_slider.pack(pady=(0, 8))

        self.start_button = self.make_button(
            "START",
            self.start_simulation,
            "#7056AC",
        )

        self.make_button(
            "COSMO HINT",
            self.request_hint,
            "#40536C",
        )

        self.make_button(
            "RESET",
            self.reset_simulation,
            "#435571",
        )

        if self.on_back is not None:
            self.make_button(
                "BACK",
                self.go_back,
                PANEL,
            )

        tk.Label(
            self.panel,
            textvariable=self.info_var,
            font=("Arial", 9),
            fg=MUTED,
            bg=PANEL,
            justify="left",
            wraplength=220,
        ).pack(
            padx=20,
            pady=(10, 6),
            anchor="w",
        )

        # COSMO message area.
        self.cosmo_frame = tk.Frame(
            self.panel,
            bg="#263750",
            highlightbackground="#48617F",
            highlightthickness=1,
        )
        self.cosmo_frame.pack(
            fill="x",
            padx=12,
            pady=(4, 8),
        )

        tk.Label(
            self.cosmo_frame,
            text="✦ COSMO",
            font=("Arial", 10, "bold"),
            fg=ACCENT,
            bg="#263750",
        ).pack(
            anchor="w",
            padx=10,
            pady=(8, 3),
        )

        self.cosmo_label = tk.Label(
            self.cosmo_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg=TEXT,
            bg="#263750",
            justify="left",
            wraplength=214,
            anchor="nw",
        )
        self.cosmo_label.pack(
            fill="x",
            padx=10,
            pady=(0, 9),
        )

    def make_button(self, text, command, background):
        button = tk.Button(
            self.panel,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            bg=background,
            fg=TEXT,
            activebackground="#8A70D0",
            activeforeground=TEXT,
            relief="flat",
            cursor="hand2",
        )
        button.pack(
            fill="x",
            padx=20,
            pady=3,
            ipady=5,
        )
        return button

    # ========================================================
    # COSMO — Educational guidance
    # ========================================================

    def say(self, message, color=TEXT):
        self.status_var.set(message)
        self.cosmo_label.config(fg=color)

    def request_hint(self):

        state = self.puzzle.get_state()

        if state["completed"]:
            self.say(
                "Excellent work, Ada! The moving clock "
                "accumulated less proper time than the "
                "Earth-frame coordinate time. This is "
                "a real prediction of special relativity!",
                SUCCESS,
            )
            return

        if state["running"]:
            self.say(
                "Watch the clocks carefully! The "
                "spacecraft clock advances more slowly "
                "relative to Earth's reference frame "
                "when the spacecraft is moving.",
                ACCENT,
            )
            return

        self.hint_level = min(
            self.hint_level + 1,
            4,
        )

        if self.hint_level == 1:
            self.say(
                "Einstein's special relativity tells "
                "us that elapsed time depends on the "
                "path an observer takes through spacetime. "
                "Compare the two clocks.",
                ACCENT,
            )

        elif self.hint_level == 2:
            self.say(
                "The closer the spacecraft's speed "
                "gets to the speed of light, the "
                "larger the Lorentz factor becomes. "
                "That increases the time difference.",
                ACCENT,
            )

        elif self.hint_level == 3:
            self.say(
                "Duration matters too! A longer "
                "journey allows the difference "
                "between the clocks to accumulate. "
                "Try balancing speed and duration.",
                ACCENT,
            )

        else:
            self.show_advanced_hint()

    def show_advanced_hint(self):

        state = self.puzzle.get_state()

        difference = state["time_difference"]
        target = state["target_difference"]
        tolerance = state["target_tolerance"]

        if difference < target - tolerance:
            self.say(
                f"The predicted difference is "
                f"{difference:.2f} years, below the "
                f"{target:.2f}-year target. Increase "
                "velocity or journey duration.",
                ACCENT,
            )

        elif difference > target + tolerance:
            self.say(
                f"The predicted difference is "
                f"{difference:.2f} years, above the "
                f"{target:.2f}-year target. Reduce "
                "velocity or journey duration.",
                ACCENT,
            )

        else:
            self.say(
                f"Your predicted difference is "
                f"{difference:.2f} years, within "
                "the target tolerance. Start the "
                "journey to test your configuration!",
                ACCENT,
            )

    def contextual_feedback(self, state):

        status = state["status"]
        difference = (
            state["elapsed_earth_time"]
            - state["elapsed_ship_time"]
        )

        target = state["target_difference"]

        if status == "success":
            self.say(
                f"Mission accomplished, Ada! Earth "
                f"experienced {state['elapsed_earth_time']:.2f} "
                f"years, while the spacecraft experienced "
                f"{state['elapsed_ship_time']:.2f} years. "
                f"The difference is {difference:.2f} years! "
                "The spacecraft clock measured less "
                "proper time along its path.",
                SUCCESS,
            )

        elif status == "insufficient_dilation":
            self.say(
                f"The clocks differ by only "
                f"{difference:.2f} years. We need "
                f"about {target:.2f} years. "
                "Try increasing the spacecraft's "
                "speed or extending the journey.",
                ERROR,
            )

        elif status == "excessive_dilation":
            self.say(
                f"The clocks differ by "
                f"{difference:.2f} years, which "
                f"exceeds our {target:.2f}-year target. "
                "Try reducing the velocity or "
                "shortening the journey.",
                ERROR,
            )

        else:
            self.say(
                "The journey has ended. Review "
                "the clock readings and adjust "
                "your configuration.",
                ACCENT,
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

        if self.puzzle.get_state()["running"]:
            return

        self.puzzle.update({
            "type": "adjust",
            "parameter": "velocity",
            "value": float(value),
        })

        self.completed_notified = False

        self.say(
            "Velocity adjusted. The Lorentz factor "
            "has changed. Check the predicted "
            "difference between the clocks."
        )

        self.update_labels()
        self.update_info()

    def on_duration_change(self, value):

        if self.puzzle.get_state()["running"]:
            return

        self.puzzle.update({
            "type": "adjust",
            "parameter": "duration",
            "value": float(value),
        })

        self.completed_notified = False

        self.say(
            "Journey duration adjusted. The time "
            "difference accumulates over the "
            "duration of the trip."
        )

        self.update_labels()
        self.update_info()

    def start_simulation(self):

        if self.puzzle.get_state()["running"]:
            return

        self.puzzle.update({
            "type": "start",
        })

        self.completed_notified = False

        self.velocity_slider.config(state="disabled")
        self.duration_slider.config(state="disabled")
        self.start_button.config(state="disabled")

        self.say(
            "Journey started! Watch how the "
            "spacecraft clock accumulates time "
            "differently from Earth's clock.",
            ACCENT,
        )

        self.last_frame = time.monotonic()

    def reset_simulation(self):

        self.puzzle.reset()
        state = self.puzzle.get_state()

        self.velocity_var.set(state["velocity"])
        self.duration_var.set(state["duration"])

        self.velocity_slider.config(state="normal")
        self.duration_slider.config(state="normal")
        self.start_button.config(state="normal")

        self.completed_notified = False
        self.hint_level = 0

        self.say(
            "Clocks synchronized! Both begin at "
            "zero. Configure a new journey and "
            "explore how velocity changes elapsed time.",
            ACCENT,
        )

        self.last_frame = time.monotonic()

        self.update_labels()
        self.update_info()
        self.draw_scene()

    def go_back(self):
        self.stop_animation()

        if self.on_back is not None:
            self.on_back()

    def stop_animation(self):
        if self.after_id is not None:
            try:
                self.after_cancel(self.after_id)
            except tk.TclError:
                pass

            self.after_id = None

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
        title,
    ):

        c = self.canvas

        c.create_text(
            cx,
            cy - radius - 45,
            text=title,
            fill=color,
            font=("Arial", 17, "bold"),
        )

        c.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            fill="#16233B",
            outline=color,
            width=4,
        )

        # Clock markers
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

            c.create_line(
                x1, y1,
                x2, y2,
                fill=MUTED,
                width=2,
            )

        # One revolution represents one year.
        angle = (
            2 * math.pi * elapsed_years
            - math.pi / 2
        )

        hand_length = radius * 0.65

        hx = cx + hand_length * math.cos(angle)
        hy = cy + hand_length * math.sin(angle)

        c.create_line(
            cx, cy,
            hx, hy,
            fill=color,
            width=4,
        )

        c.create_oval(
            cx - 5,
            cy - 5,
            cx + 5,
            cy + 5,
            fill=TEXT,
            outline="",
        )

        c.create_text(
            cx,
            cy + radius + 28,
            text=f"{elapsed_years:.2f} years",
            fill=TEXT,
            font=("Arial", 15, "bold"),
        )

    # ========================================================
    # Scene
    # ========================================================

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.draw_background()

        self.canvas.create_text(
            20, 20,
            text="CHAPTER 5 — TIME DILATION",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw",
        )

        self.canvas.create_text(
            20, 50,
            text="Two clocks, different elapsed times",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw",
        )

        earth_time = state["elapsed_earth_time"]
        ship_time = state["elapsed_ship_time"]

        self.draw_clock(
            cx=175,
            cy=260,
            radius=100,
            elapsed_years=earth_time,
            color=EARTH_COLOR,
            title="EARTH",
        )

        self.draw_clock(
            cx=465,
            cy=260,
            radius=100,
            elapsed_years=ship_time,
            color=SHIP_COLOR,
            title="SPACECRAFT",
        )

        self.draw_comparison(
            earth_time,
            ship_time,
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
            anchor="nw",
        )

    def draw_background(self):

        for i in range(75):

            x = (i * 97 + 31) % SCENE_WIDTH
            y = (i * 151 + 47) % HEIGHT

            size = 1 if i % 5 else 2

            self.canvas.create_oval(
                x, y,
                x + size,
                y + size,
                fill="#536A8D",
                outline="",
            )

    def draw_comparison(self, earth_time, ship_time):

        difference = earth_time - ship_time

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            420,
            text="TIME DIFFERENCE",
            fill=MUTED,
            font=("Arial", 12, "bold"),
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            455,
            text=f"{difference:.3f} years",
            fill=ACCENT,
            font=("Arial", 24, "bold"),
        )

        target = self.puzzle.TARGET_DIFFERENCE

        progress = min(
            1.0,
            max(0.0, difference / target),
        )

        left = 130
        right = 510
        top = 495
        bottom = 510

        self.canvas.create_rectangle(
            left, top,
            right, bottom,
            fill="#28384F",
            outline="",
        )

        self.canvas.create_rectangle(
            left, top,
            left + (right - left) * progress,
            bottom,
            fill=SHIP_COLOR,
            outline="",
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            530,
            text=(
                f"Target: {target:.2f} years "
                f"(±{self.puzzle.TARGET_TOLERANCE:.2f})"
            ),
            fill=MUTED,
            font=("Arial", 10),
        )

    # ========================================================
    # Animation
    # ========================================================

    def animate(self):

        now = time.monotonic()

        elapsed = min(
            max(0.0, now - self.last_frame),
            0.1,
        )

        self.last_frame = now

        state = self.puzzle.get_state()

        if state["running"]:

            self.puzzle.update({
                "type": "tick",
                "dt": elapsed * SIMULATION_SPEED,
            })

            state = self.puzzle.get_state()

            if not state["running"]:
                self.finish_simulation(state)

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate,
        )

    def finish_simulation(self, state):

        self.velocity_slider.config(state="normal")
        self.duration_slider.config(state="normal")
        self.start_button.config(state="normal")

        self.contextual_feedback(state)

        if (
            state["completed"]
            and not self.completed_notified
            and self.on_complete is not None
        ):
            self.completed_notified = True
            self.after_idle(self.on_complete)

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
        self.stop_animation()
        super().destroy()


if __name__ == "__main__":

    root = tk.Tk()
    root.title("ASTRA — Time Dilation")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = TimeDilationUI(root)
    screen.pack(fill="both", expand=True)

    root.mainloop()
