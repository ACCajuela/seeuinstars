
import math
import time
import tkinter as tk

from core.ui import (
    ACCENT, BACKGROUND_IMAGE, BG, BUTTON_BG, CHARACTERS, CHARACTERS_DIR,
    FEEDBACK_COLOR, MINIGAME_MUTED as MUTED, MINIGAME_PANEL,
    MINIGAME_SUCCESS as SUCCESS, TITLE as TEXT,
    CanvasLabel, CanvasSlider, CosmoHint, MenuButton,
    IMAGES_DIR, draw_minigame_heading, draw_minigame_panel, fit_content,
    fit_image,
)
from puzzles.mars_gravity import MarsGravityPuzzle


# ============================================================
# ASTRA — Chapter 2: Mars Gravity
# Visual com a identidade do jogo (cores, botões e painel de core/ui.py).
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 680

# Cenário: a mesma paisagem de Marte da home
MARS_BACKGROUND = BACKGROUND_IMAGE
SKY = "#3A1F1A"                   # cor de fundo se a imagem não existir

GROUND = "#9C4E37"
GROUND_DARK = "#68372F"
GROUND_EDGE = "#C46A47"
TRAJECTORY = FEEDBACK_COLOR
SUIT = "#EAF2FA"
ROVER_COLOR = ACCENT

ADA_MAX_W, ADA_MAX_H = 48, 60     # tamanho da Ada no minigame

# Imagem do rover (PNG com fundo transparente). Sem o arquivo, o rover
# é desenhado. ROVER_SCALE: largura do rover em relação à plataforma de pouso.
ROVER_IMAGE = IMAGES_DIR / "hover.png"
ROVER_SCALE = 2.2


class MarsGravityUI(tk.Frame):

    FRAME_MS = 30

    def __init__(self, master, on_complete=None, on_back=None):
        super().__init__(master, bg=SKY)

        self.puzzle = MarsGravityPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.running = False
        self.after_id = None
        self.completed_notified = False

        self.ground_y = 430
        self.origin_x = 65
        self.pixels_per_meter = 13

        self.trajectory = []

        self.velocity_var = tk.DoubleVar(value=8.6)
        self.angle_var = tk.DoubleVar(value=45)

        self.status_var = tk.StringVar(
            value="Watch the rover and time your jump!"
        )

        self.info_var = tk.StringVar()

        self.last_frame_time = time.monotonic()
        self.accumulator = 0.0

        self.build_ui()
        self.update_controls()
        self.update_info()
        self.draw_scene()

        # Start animation immediately.
        self.after_id = self.after(
            self.FRAME_MS,
            self.animate
        )

    # --------------------------------------------------------
    # Interface
    # --------------------------------------------------------

    def build_ui(self):

        self.canvas = tk.Canvas(
            self,
            width=WIDTH,
            height=HEIGHT,
            bg=SKY,
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)
        c = self.canvas

        # Imagem da Ada (se existir); senão, o desenho simples é usado
        ada_path = CHARACTERS_DIR / CHARACTERS["Ada"]["image"]
        self.ada_img = (
            fit_image(ada_path, ADA_MAX_W, ADA_MAX_H)
            if ada_path.exists() else None
        )

        # Imagem do rover (se existir)
        self.rover_img = None
        if ROVER_IMAGE.exists():
            target_w = (
                self.puzzle.ROVER_WIDTH * self.pixels_per_meter * ROVER_SCALE
            )
            self.rover_img, self.rover_box = fit_content(ROVER_IMAGE, target_w)

        # Cenário fixo (desenhado uma vez só)
        self.draw_sky()
        self.draw_ground()
        draw_minigame_heading(
            c,
            "CHAPTER 2 — ARRIVAL ON MARS",
            "Land on the moving rover."
        )

        # Painel lateral
        draw_minigame_panel(c, "MARS\nGRAVITY")
        x0, y0, x1, y1 = MINIGAME_PANEL
        cx = (x0 + x1) / 2
        slider_x, slider_len = x0 + 22, (x1 - x0) - 44

        c.create_text(cx, 128, text="Impulse velocity",
                      font=("Arial", 11), fill=MUTED)
        self.velocity_label = CanvasLabel(c, c.create_text(
            cx, 155, font=("Arial", 18, "bold"), fill=ACCENT
        ))
        self.velocity_slider = CanvasSlider(
            c, slider_x, 188, slider_len,
            from_=0, to=30, resolution=0.1,
            variable=self.velocity_var,
            command=lambda _: self.update_controls()
        )

        c.create_text(cx, 222, text="Launch angle",
                      font=("Arial", 11), fill=MUTED)
        self.angle_label = CanvasLabel(c, c.create_text(
            cx, 249, font=("Arial", 18, "bold"), fill=ACCENT
        ))
        self.angle_slider = CanvasSlider(
            c, slider_x, 282, slider_len,
            from_=0, to=90, resolution=1,
            variable=self.angle_var,
            command=lambda _: self.update_controls()
        )

        self.launch_button = MenuButton(
            c, cx, 330, "JUMP", self.start_jump,
            width=160, height=42, font_size=13, primary=True
        )

        MenuButton(
            c, cx, 377, "RESET", self.reset_simulation,
            width=160, height=38, font_size=12
        )

        if self.on_back is not None:
            MenuButton(
                c, cx, 421, "BACK", self.go_back,
                width=160, height=38, font_size=12
            )

        c.create_line(x0 + 20, 450, x1 - 20, 450, fill="#24324F", width=2)

        info_item = c.create_text(
            x0 + 20, 460, anchor="nw", width=(x1 - x0) - 36,
            font=("Arial", 9), fill=MUTED
        )
        self.info_var.trace_add(
            "write",
            lambda *_: c.itemconfigure(info_item, text=self.info_var.get())
        )

        # COSMO comenta o salto no balão
        self.hint = CosmoHint(c, right=SCENE_WIDTH - 20)
        self.status_var.trace_add("write", lambda *_: self.show_status())
        self.show_status()

    def show_status(self):
        """Mostra a mensagem no balão do COSMO, colorida pelo resultado."""
        status = self.puzzle.get_state()["status"]

        if status == "success":
            color = SUCCESS
        elif status in ("too_short", "too_far", "timeout"):
            color = FEEDBACK_COLOR
        else:
            color = TEXT

        self.hint.set(self.status_var.get(), color)

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    def update_controls(self):
        self.velocity_label.config(
            text=f"{self.velocity_var.get():.1f} m/s"
        )

        self.angle_label.config(
            text=f"{self.angle_var.get():.0f}°"
        )

    def start_jump(self):
        if self.running or self.puzzle.status != "ready":
            return

        self.trajectory.clear()
        self.completed_notified = False

        self.puzzle.update({
            "type": "launch",
            "velocity": self.velocity_var.get(),
            "angle": self.angle_var.get()
        })

        self.running = True

        self.velocity_slider.config(state="disabled")
        self.angle_slider.config(state="disabled")
        self.launch_button.config(state="disabled")

        self.status_var.set("Jump in progress...")

    def reset_simulation(self):
        self.puzzle.reset()
        self.trajectory.clear()

        self.running = False
        self.completed_notified = False
        self.accumulator = 0.0
        self.last_frame_time = time.monotonic()

        self.velocity_slider.config(state="normal")
        self.angle_slider.config(state="normal")
        self.launch_button.config(state="normal")

        self.status_var.set(
            "Watch the rover and time your jump!"
        )

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
        self.running = False

    # --------------------------------------------------------
    # Continuous simulation
    # --------------------------------------------------------

    def animate(self):
        now = time.monotonic()

        elapsed = min(
            now - self.last_frame_time,
            0.1
        )

        self.last_frame_time = now
        self.accumulator += elapsed

        dt = self.puzzle.TIME_STEP

        while self.accumulator >= dt:
            self.puzzle.update({
                "type": "tick",
                "dt": dt
            })

            self.accumulator -= dt

            state = self.puzzle.get_state()

            if self.running:
                self.trajectory.append(
                    (state["x"], state["y"])
                )

                if not state["launched"]:
                    self.finish_jump()
                    break

        self.update_info()
        self.draw_scene()

        self.after_id = self.after(
            self.FRAME_MS,
            self.animate
        )

    def finish_jump(self):
        self.running = False

        self.velocity_slider.config(state="normal")
        self.angle_slider.config(state="normal")
        self.launch_button.config(state="normal")

        state = self.puzzle.get_state()

        messages = {
            "success": "Perfect landing! Mission complete.",
            "too_short": "Too short! Try a stronger impulse.",
            "too_far": "Too far! Try a weaker impulse.",
            "timeout": "Jump timed out. Try again."
        }

        self.status_var.set(
            messages.get(
                state["status"],
                "Jump finished."
            )
        )

        if (
            self.puzzle.validate()
            and not self.completed_notified
        ):
            self.completed_notified = True

            if self.on_complete is not None:
                self.after_idle(self.on_complete)

    # --------------------------------------------------------
    # Rendering
    # --------------------------------------------------------

    def world_to_screen(self, x, y):
        return (
            self.origin_x + x * self.pixels_per_meter,
            self.ground_y - y * self.pixels_per_meter
        )

    def draw_scene(self):

        # Apaga só o que se move; cenário e painel ficam.
        self.canvas.delete("dyn")

        self.draw_rover()
        self.draw_trajectory()
        self.draw_astronaut()

        self.hint.raise_()

    def draw_sky(self):

        if MARS_BACKGROUND.exists():
            img = tk.PhotoImage(file=str(MARS_BACKGROUND))
            factor = max(1, img.width() // WIDTH, img.height() // HEIGHT)
            if factor > 1:
                img = img.subsample(factor)
            self.sky_img = img  # manter referência, senão a imagem some
            self.canvas.create_image(0, 0, image=img, anchor="nw")
            return

        # Sem imagem: céu simples com sol
        self.canvas.create_oval(
            490, 90, 580, 180,
            fill="#E4A17A",
            outline=""
        )

    def draw_ground(self):

        c = self.canvas

        c.create_rectangle(
            0,
            self.ground_y,
            SCENE_WIDTH,
            HEIGHT,
            fill=GROUND,
            outline=""
        )

        c.create_line(0, self.ground_y, SCENE_WIDTH, self.ground_y,
                      fill=GROUND_EDGE, width=3)

        for i in range(12):
            x = i * 65

            c.create_oval(
                x,
                self.ground_y + 20 + (i % 3) * 17,
                x + 30,
                self.ground_y + 26 + (i % 3) * 17,
                fill=GROUND_DARK,
                outline=""
            )

    def draw_rover(self):

        c = self.canvas
        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["rover_x"],
            0
        )

        half_width = (
            state["rover_width"]
            * self.pixels_per_meter
            / 2
        )

        direction = (
            "→"
            if state["rover_direction"] > 0
            else "←"
        )

        if self.rover_img is not None:
            # Desenho do rover centralizado e com as rodas no chão
            x0, y0, x1, y1 = self.rover_box
            w = (x1 - x0) / 2
            c.create_oval(  # sombra no chão
                x - w, y - 6, x + w, y + 8,
                fill="#3A1A12", outline="", tags="dyn"
            )
            c.create_image(
                x - (x0 + x1) / 2, y - y1,
                image=self.rover_img, anchor="nw", tags="dyn"
            )
            # Área de pouso marcada no chão
            c.create_line(
                x - half_width, y + 3, x + half_width, y + 3,
                fill=ROVER_COLOR, width=3, tags="dyn"
            )
            c.create_text(
                x, y - (y1 - y0) - 12,
                text=f"ROVER {direction}",
                fill=TEXT,
                font=("Arial", 10, "bold"),
                tags="dyn"
            )
            return

        # Sem imagem: plataforma de pouso desenhada
        c.create_rectangle(
            x - half_width, y - 20, x + half_width, y - 8,
            fill=BUTTON_BG, outline=ROVER_COLOR, width=2, tags="dyn"
        )

        # Cabine com antena
        c.create_rectangle(
            x - 12, y - 30, x + 12, y - 20,
            fill=ROVER_COLOR, outline="", tags="dyn"
        )
        c.create_line(x + 8, y - 30, x + 8, y - 40,
                      fill=ROVER_COLOR, width=2, tags="dyn")
        c.create_oval(x + 5, y - 44, x + 11, y - 38,
                      fill=FEEDBACK_COLOR, outline="", tags="dyn")

        for wheel_x in (x - half_width + 8, x, x + half_width - 8):
            c.create_oval(
                wheel_x - 6, y - 10, wheel_x + 6, y + 2,
                fill="#1A2236", outline=ROVER_COLOR, width=2, tags="dyn"
            )

        c.create_text(
            x, y - 56,
            text=f"ROVER {direction}",
            fill=TEXT,
            font=("Arial", 10, "bold"),
            tags="dyn"
        )

    def draw_trajectory(self):

        if len(self.trajectory) < 2:
            return

        points = []

        for x, y in self.trajectory:
            sx, sy = self.world_to_screen(x, y)
            points.extend((sx, sy))

        self.canvas.create_line(
            *points,
            fill=TRAJECTORY,
            width=2,
            dash=(6, 4),
            tags="dyn"
        )

    def draw_astronaut(self):

        state = self.puzzle.get_state()

        x, y = self.world_to_screen(
            state["x"],
            state["y"]
        )

        if self.ada_img is not None:
            self.canvas.create_image(
                x, y + 4, image=self.ada_img, anchor="s", tags="dyn"
            )
            return

        # Sem imagem: astronauta simples
        self.canvas.create_oval(
            x - 7, y - 22, x + 7, y - 8,
            fill=SUIT, outline=ACCENT, width=2, tags="dyn"
        )
        self.canvas.create_rectangle(
            x - 8, y - 8, x + 8, y + 6,
            fill=SUIT, outline=ACCENT, tags="dyn"
        )

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    def update_info(self):
        state = self.puzzle.get_state()

        self.info_var.set(
            f"Mars gravity: {state['gravity']:.2f} m/s²\n"
            f"Earth gravity: 9.81 m/s²\n\n"
            f"Ada distance: {state['x']:.2f} m\n"
            f"Ada height: {state['y']:.2f} m\n"
            f"Maximum height: {state['max_height']:.2f} m\n"
            f"Rover position: {state['rover_x']:.2f} m\n"
            f"Time: {state['time']:.2f} s"
        )

    def destroy(self):
        self.stop_animation()
        super().destroy()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ASTRA — Mars Gravity Test")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    screen = MarsGravityUI(root)
    screen.pack(fill="both", expand=True)

    root.mainloop()
