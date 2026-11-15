
import math
import time
import tkinter as tk

from core.ui import CosmoHint
from puzzles.spacetime import SpacetimePuzzle


# ============================================================
# ASTRA — Chapter 4: Spacetime Geometry
#
# Conceptual pseudo-3D geometry visualization.
# Wormhole stabilization is fictional.
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 640
PANEL_WIDTH = WIDTH - SCENE_WIDTH

BG = "#0B1020"
PANEL = "#1B2638"

TEXT = "#F5F7FF"
MUTED = "#A9B9D1"

CYAN = "#76D9F4"
PURPLE = "#A38BFA"
GOLD = "#F4C66C"
GREEN = "#8FE4B0"
RED = "#FF9999"

FRAME_MS = 33


class SpacetimeUI(tk.Frame):

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=BG)

        self.puzzle = SpacetimePuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.after_id = None
        self.last_frame = time.monotonic()

        self.animation_time = 0.0
        self.completed_notified = False

        # COSMO tutorial progress
        self.hint_level = 0
        self.attempts = 0

        state = self.puzzle.get_state()

        # Smooth visual parameters
        self.visual_curvature = state["curvature"]
        self.visual_radius = state["throat_radius"]
        self.visual_stabilization = state["stabilization"]

        # Camera projection
        self.camera_yaw = 0.0
        self.camera_pitch = 0.58
        self.camera_distance = 7.5
        self.projection_scale = 620.0

        self.scene_center_x = SCENE_WIDTH / 2
        self.scene_center_y = HEIGHT / 2 + 25

        self.rotation_speed = 0.12

        # Controls
        self.curvature_var = tk.DoubleVar(
            value=state["curvature"]
        )

        self.radius_var = tk.DoubleVar(
            value=state["throat_radius"]
        )

        self.stabilization_var = tk.DoubleVar(
            value=state["stabilization"]
        )

        self.info_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value=(
                "COSMO: Ada, this is a conceptual "
                "spacetime model. Adjust curvature, "
                "opening size, and hypothetical "
                "stabilization to balance the passage."
            )
        )

        self.build_ui()
        self.update_info()
        self.draw_scene()
        self.animate()

    # ========================================================
    # UI
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
            width=PANEL_WIDTH,
            bg=PANEL,
        )

        self.panel.pack(
            side="right",
            fill="y",
        )

        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="SPACETIME\nGEOMETRY",
            font=("Arial", 17, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center",
        ).pack(pady=(15, 7))

        self.curvature_label = self.make_slider(
            "Curvature",
            self.curvature_var,
            "curvature",
        )

        self.radius_label = self.make_slider(
            "Throat radius",
            self.radius_var,
            "throat_radius",
        )

        self.stabilization_label = self.make_slider(
            "Stabilization",
            self.stabilization_var,
            "stabilization",
        )

        self.make_button(
            "STABILIZE",
            self.submit,
            "#7258B4",
        )

        self.make_button(
            "COSMO HINT",
            self.request_hint,
            "#40536C",
        )

        self.make_button(
            "RESET",
            self.reset_simulation,
            "#40536C",
        )

        if self.on_back is not None:
            self.make_button(
                "BACK",
                self.go_back,
                PANEL,
                fg=MUTED,
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
            pady=(12, 4),
            anchor="w",
        )

        # COSMO bubble on the animated scene.
        self.hint = CosmoHint(
            self.canvas,
            right=SCENE_WIDTH - 20,
        )

        self.status_var.trace_add(
            "write",
            lambda *_: self.show_status(),
        )

        self.show_status()

    def make_button(
        self,
        title,
        command,
        background,
        fg=TEXT,
    ):
        button = tk.Button(
            self.panel,
            text=title,
            command=command,
            bg=background,
            fg=fg,
            activebackground="#8A70D0",
            activeforeground=TEXT,
            font=("Arial", 10, "bold"),
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

    def make_slider(
        self,
        title,
        variable,
        parameter,
    ):

        frame = tk.Frame(
            self.panel,
            bg=PANEL,
        )

        frame.pack(
            fill="x",
            padx=18,
            pady=3,
        )

        tk.Label(
            frame,
            text=title,
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL,
        ).pack(anchor="w")

        value_label = tk.Label(
            frame,
            text=f"{variable.get():.2f}",
            font=("Arial", 11, "bold"),
            fg=CYAN,
            bg=PANEL,
        )

        value_label.pack(anchor="w")

        slider = tk.Scale(
            frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            variable=variable,
            showvalue=False,
            length=210,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#43546D",
            highlightthickness=0,
            sliderlength=15,
            command=lambda value: self.adjust(
                parameter,
                value,
                value_label,
            ),
        )

        slider.pack()

        return value_label

    # ========================================================
    # COSMO — educational guidance
    # ========================================================

    def say(self, message):
        self.status_var.set(
            "COSMO: " + message
        )

    def show_status(self):
        status = self.puzzle.get_state()["status"]

        if status == "success":
            color = GREEN

        elif status in (
            "insufficient_curvature",
            "excessive_curvature",
            "narrow_passage",
            "unstable",
            "low_stability",
        ):
            color = RED

        else:
            color = TEXT

        self.hint.set(
            self.status_var.get(),
            color,
        )

    def request_hint(self):
        state = self.puzzle.get_state()

        if state["completed"]:
            self.say(
                "Excellent! You balanced the three "
                "parameters in our fictional model. "
                "Remember: real traversable wormholes "
                "have not been demonstrated."
            )
            return

        self.hint_level = min(
            self.hint_level + 1,
            4,
        )

        if self.hint_level == 1:
            self.say(
                "In general relativity, gravity is "
                "described through spacetime curvature. "
                "Our grid is a simplified illustration, "
                "not spacetime itself."
            )

        elif self.hint_level == 2:
            self.say(
                "The throat is the narrowest part "
                "of a hypothetical wormhole. "
                "In this game, a wider throat "
                "improves passage quality."
            )

        elif self.hint_level == 3:
            self.say(
                "Our fictional stabilizer must "
                "overcome the required stabilization. "
                "Check the stabilization margin: "
                "a negative value means the model "
                "does not have enough support."
            )

        else:
            self.show_advanced_hint()

    def show_advanced_hint(self):
        state = self.puzzle.get_state()
        geometry = state["geometry"]

        curvature = state["curvature"]
        radius = state["throat_radius"]
        stabilization = state["stabilization"]

        required = geometry["required_stabilization"]
        score = state["stability_score"]

        if curvature < 0.40:
            self.say(
                "Try increasing curvature to at "
                "least 0.40. The game requires "
                "a moderate amount of deformation."
            )

        elif curvature > 0.85:
            self.say(
                "Curvature above 0.85 is too high "
                "for this model. Reduce it."
            )

        elif radius < 0.45:
            self.say(
                "The throat radius must reach "
                "at least 0.45 to provide "
                "a usable opening."
            )

        elif stabilization < required:
            self.say(
                f"This configuration requires "
                f"stabilization of at least "
                f"{required:.2f}. Increase "
                "the stabilizer or reduce "
                "the model's demands."
            )

        elif score < 0.65:
            self.say(
                "The stabilization requirement "
                "is satisfied, but the overall "
                "score is still low. In this model, "
                "curvature near 0.65 and throat "
                "radius near 0.60 improve quality."
            )

        else:
            self.say(
                f"The current stability score is "
                f"{score * 100:.1f}%, and the "
                "stabilization margin is nonnegative. "
                "Try pressing STABILIZE."
            )

    def contextual_feedback(self, state):
        status = state["status"]
        geometry = state["geometry"]

        if status == "insufficient_curvature":
            self.say(
                f"Curvature is {state['curvature']:.2f}. "
                "Our model requires at least 0.40. "
                "Increase curvature to strengthen "
                "the conceptual connection."
            )

        elif status == "excessive_curvature":
            self.say(
                f"Curvature is {state['curvature']:.2f}, "
                "above the model's limit of 0.85. "
                "Reduce it to avoid excessive "
                "deformation in this simulation."
            )

        elif status == "narrow_passage":
            self.say(
                f"The throat radius is "
                f"{state['throat_radius']:.2f}. "
                "It must be at least 0.45. "
                "Increase the opening size."
            )

        elif status == "unstable":
            margin = geometry["stabilization_margin"]

            self.say(
                f"The stabilization margin is "
                f"{margin:+.2f}. A negative margin "
                "means the hypothetical stabilizer "
                "is below the model's requirement."
            )

        elif status == "low_stability":
            score = state["stability_score"] * 100

            self.say(
                f"The overall stability score is "
                f"{score:.1f}%, below the required "
                "65%. Try balancing curvature "
                "and throat radius while maintaining "
                "enough stabilization."
            )

        elif status == "success":
            self.say(
                "Passage stabilized! You balanced "
                "curvature, throat radius, and "
                "hypothetical stabilization. "
                "This is a fictional engineering "
                "challenge inspired by spacetime "
                "geometry, not proof that real "
                "wormholes can be stabilized."
            )

        else:
            self.say(
                "The geometry has been evaluated. "
                "Adjust the parameters and try again."
            )

    # ========================================================
    # Puzzle actions
    # ========================================================

    def adjust(
        self,
        parameter,
        value,
        label,
    ):
        value = float(value)

        label.config(
            text=f"{value:.2f}"
        )

        self.puzzle.update({
            "type": "adjust",
            "parameter": parameter,
            "value": value,
        })

        self.completed_notified = False

        self.say(
            "Geometry updated. Watch the surface "
            "respond, then evaluate the model's "
            "stability."
        )

        self.update_info()

    def submit(self):
        self.puzzle.update({
            "type": "submit",
        })

        self.attempts += 1

        state = self.puzzle.get_state()

        self.contextual_feedback(state)
        self.update_info()

        if (
            state["completed"]
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.after_idle(
                    self.on_complete
                )

    def reset_simulation(self):
        self.puzzle.reset()

        state = self.puzzle.get_state()

        self.curvature_var.set(
            state["curvature"]
        )

        self.radius_var.set(
            state["throat_radius"]
        )

        self.stabilization_var.set(
            state["stabilization"]
        )

        self.curvature_label.config(
            text=f"{state['curvature']:.2f}"
        )

        self.radius_label.config(
            text=f"{state['throat_radius']:.2f}"
        )

        self.stabilization_label.config(
            text=f"{state['stabilization']:.2f}"
        )

        self.completed_notified = False
        self.hint_level = 0

        self.say(
            "Geometry reset. Let's explore "
            "how the three parameters interact."
        )

        self.update_info()

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
    # Pseudo-3D projection
    # ========================================================

    def project(self, x, y, z):

        cos_yaw = math.cos(self.camera_yaw)
        sin_yaw = math.sin(self.camera_yaw)

        rx = (
            x * cos_yaw
            - y * sin_yaw
        )

        ry = (
            x * sin_yaw
            + y * cos_yaw
        )

        cos_pitch = math.cos(self.camera_pitch)
        sin_pitch = math.sin(self.camera_pitch)

        projected_y = (
            ry * sin_pitch
            - z * cos_pitch
        )

        depth = (
            ry * cos_pitch
            + z * sin_pitch
        )

        perspective = (
            self.projection_scale
            / max(
                2.0,
                self.camera_distance + depth,
            )
        )

        screen_x = (
            self.scene_center_x
            + rx * perspective
        )

        screen_y = (
            self.scene_center_y
            + projected_y * perspective
        )

        return screen_x, screen_y

    # ========================================================
    # Conceptual geometry
    # ========================================================

    def calculate_height(self, x, y):

        distance = math.hypot(x, y)

        curvature = self.visual_curvature

        radius = (
            0.15
            + self.visual_radius * 0.85
        )

        deformation = (
            curvature
            * (1.0 - 0.35 * self.visual_radius)
        )

        # Fictional instability oscillation.
        instability = (
            1.0 - self.visual_stabilization
        )

        wave = (
            0.09
            * instability
            * math.sin(
                5.0 * distance
                - 3.0 * self.animation_time
            )
        )

        # Conceptual gravity-well illustration.
        well = (
            -deformation
            * math.exp(
                -(distance**2)
                / (2 * radius**2)
            )
        )

        return well + wave

    def is_inside_throat(self, x, y):
        opening_radius = (
            0.12
            + self.visual_radius * 0.40
        )

        return (
            math.hypot(x, y)
            < opening_radius
        )

    # ========================================================
    # Drawing
    # ========================================================

    def draw_scene(self):

        # Redraw only the animated scene.
        # COSMO's canvas items remain intact.
        self.canvas.delete("spacetime_dyn")

        self.draw_stars()
        self.draw_spacetime_grid()
        self.draw_throat()
        self.draw_titles()

        self.hint.raise_()

    def draw_stars(self):

        for i in range(70):
            x = (
                i * 97 + 31
            ) % SCENE_WIDTH

            y = (
                i * 157 + 19
            ) % HEIGHT

            size = (
                1 if i % 4 else 2
            )

            self.canvas.create_oval(
                x, y,
                x + size, y + size,
                fill="#526788",
                outline="",
                tags="spacetime_dyn",
            )

    def draw_spacetime_grid(self):

        grid_size = 27
        extent = 2.6

        coordinates = [
            -extent
            + 2 * extent * i / (grid_size - 1)
            for i in range(grid_size)
        ]

        # Rows
        for y in coordinates:
            segment = []

            for x in coordinates:

                if self.is_inside_throat(x, y):
                    if len(segment) >= 4:
                        self.canvas.create_line(
                            *segment,
                            fill="#416C9C",
                            width=1,
                            tags="spacetime_dyn",
                        )

                    segment = []
                    continue

                z = self.calculate_height(x, y)
                sx, sy = self.project(x, y, z)

                segment.extend((sx, sy))

            if len(segment) >= 4:
                self.canvas.create_line(
                    *segment,
                    fill="#416C9C",
                    width=1,
                    tags="spacetime_dyn",
                )

        # Columns
        for x in coordinates:
            segment = []

            for y in coordinates:

                if self.is_inside_throat(x, y):
                    if len(segment) >= 4:
                        self.canvas.create_line(
                            *segment,
                            fill="#416C9C",
                            width=1,
                            tags="spacetime_dyn",
                        )

                    segment = []
                    continue

                z = self.calculate_height(x, y)
                sx, sy = self.project(x, y, z)

                segment.extend((sx, sy))

            if len(segment) >= 4:
                self.canvas.create_line(
                    *segment,
                    fill="#416C9C",
                    width=1,
                    tags="spacetime_dyn",
                )

    def draw_throat(self):

        radius = (
            0.12
            + self.visual_radius * 0.40
        )

        state = self.puzzle.get_state()

        is_stable = state["completed"]

        color = (
            GREEN if is_stable else PURPLE
        )

        # Opening ring
        points = []

        for i in range(97):
            angle = (
                2 * math.pi * i / 96
            )

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            z = self.calculate_height(x, y)

            sx, sy = self.project(x, y, z)

            points.extend((sx, sy))

        self.canvas.create_line(
            *points,
            fill=color,
            width=3,
            tags="spacetime_dyn",
        )

        # Pulsing center
        center_z = self.calculate_height(0, 0)

        cx, cy = self.project(
            0, 0, center_z
        )

        pulse = (
            1.0
            + 0.15
            * math.sin(
                self.animation_time * 3
            )
        )

        size = (
            6 + radius * 10
        ) * pulse

        self.canvas.create_oval(
            cx - size,
            cy - size,
            cx + size,
            cy + size,
            fill=(
                "#285E50"
                if is_stable
                else "#35275F"
            ),
            outline=color,
            width=2,
            tags="spacetime_dyn",
        )

        if is_stable:
            halo = size * 1.8

            self.canvas.create_oval(
                cx - halo,
                cy - halo,
                cx + halo,
                cy + halo,
                outline=GREEN,
                width=1,
                dash=(4, 4),
                tags="spacetime_dyn",
            )

    def draw_titles(self):

        self.canvas.create_text(
            20, 20,
            text="CHAPTER 4 — SPACETIME",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw",
            tags="spacetime_dyn",
        )

        self.canvas.create_text(
            20, 50,
            text="Interactive conceptual geometry",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw",
            tags="spacetime_dyn",
        )

        self.canvas.create_text(
            20,
            HEIGHT - 45,
            text=(
                "Conceptual visualization — "
                "not a physical wormhole simulation"
            ),
            fill=MUTED,
            font=("Arial", 9),
            anchor="nw",
            tags="spacetime_dyn",
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

        self.animation_time += elapsed

        # Slowly rotate the viewpoint.
        self.camera_yaw += (
            elapsed * self.rotation_speed
        )

        state = self.puzzle.get_state()

        smoothing = min(
            1.0,
            elapsed * 5.0,
        )

        self.visual_curvature += (
            state["curvature"]
            - self.visual_curvature
        ) * smoothing

        self.visual_radius += (
            state["throat_radius"]
            - self.visual_radius
        ) * smoothing

        self.visual_stabilization += (
            state["stabilization"]
            - self.visual_stabilization
        ) * smoothing

        self.draw_scene()

        self.after_id = self.after(
            FRAME_MS,
            self.animate,
        )

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):

        state = self.puzzle.get_state()
        geometry = state["geometry"]

        score = (
            state["stability_score"] * 100
        )

        margin = (
            geometry["stabilization_margin"]
        )

        passage_quality = (
            geometry["passage_quality"] * 100
        )

        self.info_var.set(
            f"Stability score: {score:.1f}%\n"
            f"Stabilization margin: {margin:+.2f}\n"
            f"Passage quality: {passage_quality:.0f}%"
        )

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy(self):
        self.stop_animation()
        super().destroy()


if __name__ == "__main__":

    root = tk.Tk()

    root.title("ASTRA — Spacetime Geometry")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = SpacetimeUI(root)

    screen.pack(
        fill="both",
        expand=True,
    )

    root.mainloop()
