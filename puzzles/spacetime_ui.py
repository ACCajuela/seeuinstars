
import math
import time
import tkinter as tk

from puzzles.spacetime import SpacetimePuzzle


# ============================================================
# ASTRA — Chapter 4: Spacetime Geometry
#
# Animated pseudo-3D visualization using Tkinter Canvas.
#
# Educational visualization:
# The grid is a conceptual embedding diagram.
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

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = SpacetimePuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.after_id = None
        self.last_frame = time.monotonic()

        self.animation_time = 0.0
        self.completed_notified = False

        # Smooth visual parameters.
        state = self.puzzle.get_state()

        self.visual_curvature = state["curvature"]
        self.visual_radius = state["throat_radius"]
        self.visual_stabilization = state["stabilization"]

        # Camera projection.
        self.camera_yaw = 0.0
        self.camera_pitch = 0.58

        self.camera_distance = 7.5
        self.projection_scale = 620.0

        self.scene_center_x = SCENE_WIDTH / 2
        self.scene_center_y = HEIGHT / 2 + 25

        # Animation.
        self.rotation_speed = 0.12

        # Controls.
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
            value="Adjust the geometry to stabilize "
                  "the hypothetical passage."
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
            bg=PANEL
        )

        self.panel.pack(
            side="right",
            fill="y"
        )

        self.panel.pack_propagate(False)

        tk.Label(
            self.panel,
            text="SPACETIME\nGEOMETRY",
            font=("Arial", 17, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(20, 12))

        self.curvature_label = self.make_slider(
            "Curvature",
            self.curvature_var,
            "curvature"
        )

        self.radius_label = self.make_slider(
            "Throat radius",
            self.radius_var,
            "throat_radius"
        )

        self.stabilization_label = self.make_slider(
            "Stabilization",
            self.stabilization_var,
            "stabilization"
        )

        tk.Button(
            self.panel,
            text="STABILIZE",
            command=self.submit,
            bg="#7258B4",
            fg=TEXT,
            activebackground="#8A70D0",
            font=("Arial", 11, "bold"),
            relief="flat"
        ).pack(
            fill="x",
            padx=20,
            pady=(15, 5),
            ipady=8
        )

        tk.Button(
            self.panel,
            text="RESET",
            command=self.reset_simulation,
            bg="#40536C",
            fg=TEXT,
            font=("Arial", 10, "bold"),
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
                bg=PANEL,
                fg=MUTED,
                relief="flat"
            ).pack(pady=5)

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
            pady=(15, 5),
            anchor="w"
        )

        tk.Label(
            self.panel,
            textvariable=self.status_var,
            font=("Arial", 10, "bold"),
            fg=GOLD,
            bg=PANEL,
            wraplength=220,
            justify="center"
        ).pack(
            padx=15,
            pady=10
        )

    def make_slider(
        self,
        title,
        variable,
        parameter
    ):

        frame = tk.Frame(
            self.panel,
            bg=PANEL
        )

        frame.pack(
            fill="x",
            padx=18,
            pady=7
        )

        tk.Label(
            frame,
            text=title,
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL
        ).pack(anchor="w")

        value_label = tk.Label(
            frame,
            text=f"{variable.get():.2f}",
            font=("Arial", 12, "bold"),
            fg=CYAN,
            bg=PANEL
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
            command=lambda value: self.adjust(
                parameter,
                value,
                value_label
            )
        )

        slider.pack()

        return value_label

    # ========================================================
    # Puzzle actions
    # ========================================================

    def adjust(
        self,
        parameter,
        value,
        label
    ):

        value = float(value)

        label.config(
            text=f"{value:.2f}"
        )

        self.puzzle.update({
            "type": "adjust",
            "parameter": parameter,
            "value": value
        })

        self.completed_notified = False

        self.status_var.set(
            "Geometry updated. Evaluate stability."
        )

        self.update_info()

    def submit(self):

        self.puzzle.update({
            "type": "submit"
        })

        state = self.puzzle.get_state()

        messages = {
            "success":
                "Passage stabilized!",
            "insufficient_curvature":
                "Curvature is too weak.",
            "excessive_curvature":
                "Curvature is excessive.",
            "narrow_passage":
                "The passage is too narrow.",
            "unstable":
                "Additional stabilization required.",
            "low_stability":
                "Overall stability is insufficient."
        }

        self.status_var.set(
            messages.get(
                state["status"],
                state["status"]
            )
        )

        self.update_info()

        if (
            state["completed"]
            and not self.completed_notified
            and self.on_complete is not None
        ):

            self.completed_notified = True

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

        self.completed_notified = False

        self.status_var.set(
            "Geometry reset."
        )

        self.update_info()

    def go_back(self):

        if self.after_id is not None:

            self.after_cancel(
                self.after_id
            )

            self.after_id = None

        if self.on_back is not None:
            self.on_back()

    # ========================================================
    # Pseudo-3D projection
    # ========================================================

    def project(self, x, y, z):

        # Rotate around vertical axis.
        cos_yaw = math.cos(
            self.camera_yaw
        )

        sin_yaw = math.sin(
            self.camera_yaw
        )

        rx = (
            x * cos_yaw
            - y * sin_yaw
        )

        ry = (
            x * sin_yaw
            + y * cos_yaw
        )

        # Tilt the surface.
        cos_pitch = math.cos(
            self.camera_pitch
        )

        sin_pitch = math.sin(
            self.camera_pitch
        )

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
                self.camera_distance + depth
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
    # Geometry
    # ========================================================

    def calculate_height(self, x, y):

        distance = math.hypot(
            x,
            y
        )

        curvature = (
            self.visual_curvature
        )

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

        # Localized conceptual gravity well.
        well = (
            -deformation
            * math.exp(
                -(distance ** 2)
                / (2 * radius ** 2)
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

        self.canvas.delete("all")

        self.draw_stars()

        self.draw_spacetime_grid()

        self.draw_throat()

        self.draw_titles()

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
                x,
                y,
                x + size,
                y + size,
                fill="#526788",
                outline=""
            )

    def draw_spacetime_grid(self):

        grid_size = 27
        extent = 2.6

        coordinates = [
            -extent
            + 2 * extent * i / (grid_size - 1)
            for i in range(grid_size)
        ]

        # Draw rows.
        for y in coordinates:

            segment = []

            for x in coordinates:

                if self.is_inside_throat(x, y):

                    if len(segment) >= 4:

                        self.canvas.create_line(
                            *segment,
                            fill="#416C9C",
                            width=1
                        )

                    segment = []
                    continue

                z = self.calculate_height(
                    x,
                    y
                )

                sx, sy = self.project(
                    x,
                    y,
                    z
                )

                segment.extend(
                    [sx, sy]
                )

            if len(segment) >= 4:

                self.canvas.create_line(
                    *segment,
                    fill="#416C9C",
                    width=1
                )

        # Draw columns.
        for x in coordinates:

            segment = []

            for y in coordinates:

                if self.is_inside_throat(x, y):

                    if len(segment) >= 4:

                        self.canvas.create_line(
                            *segment,
                            fill="#416C9C",
                            width=1
                        )

                    segment = []
                    continue

                z = self.calculate_height(
                    x,
                    y
                )

                sx, sy = self.project(
                    x,
                    y,
                    z
                )

                segment.extend(
                    [sx, sy]
                )

            if len(segment) >= 4:

                self.canvas.create_line(
                    *segment,
                    fill="#416C9C",
                    width=1
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

        # Opening ring.
        points = []

        for i in range(97):

            angle = (
                2 * math.pi * i / 96
            )

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            z = self.calculate_height(
                x,
                y
            )

            sx, sy = self.project(
                x,
                y,
                z
            )

            points.extend(
                [sx, sy]
            )

        self.canvas.create_line(
            *points,
            fill=color,
            width=3
        )

        # Pulsing center.
        center_z = self.calculate_height(
            0,
            0
        )

        cx, cy = self.project(
            0,
            0,
            center_z
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
            width=2
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
                dash=(4, 4)
            )

    def draw_titles(self):

        self.canvas.create_text(
            20,
            20,
            text="CHAPTER 4 — SPACETIME",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            50,
            text="Interactive conceptual geometry",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
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
            anchor="nw"
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

        self.animation_time += elapsed

        # Slowly rotate the viewpoint.
        self.camera_yaw += (
            elapsed * self.rotation_speed
        )

        state = self.puzzle.get_state()

        smoothing = min(
            1.0,
            elapsed * 5.0
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
            self.animate
        )

    # ========================================================
    # Information
    # ========================================================

    def update_info(self):

        state = self.puzzle.get_state()

        geometry = state["geometry"]

        score = (
            state["stability_score"]
            * 100
        )

        margin = (
            geometry["stabilization_margin"]
        )

        self.info_var.set(
            f"Stability score: {score:.1f}%\n"
            f"Stabilization margin: {margin:+.2f}\n"
            f"Passage quality: "
            f"{geometry['passage_quality'] * 100:.0f}%"
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
        "ASTRA — Spacetime Geometry"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(False, False)

    screen = SpacetimeUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
