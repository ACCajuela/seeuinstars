
import math
import time
import tkinter as tk
from pathlib import Path

import pygame

from puzzles.radio_signal import RadioSignalPuzzle


# ============================================================
# ASTRA — Chapter 6: Radio Communication
#
# Animated radio transmission, Doppler tuning,
# radio static and synthetic breathing.
# ============================================================

WIDTH = 900
HEIGHT = 600
SCENE_WIDTH = 640
PANEL_WIDTH = 260

BG = "#0B1425"
PANEL = "#1D2B40"

TEXT = "#F5F7FF"
MUTED = "#AABBD3"

CYAN = "#7ADCF3"
PURPLE = "#B6A1F6"
GOLD = "#F5C66F"
GREEN = "#8FE4AE"
RED = "#FF9999"

FRAME_MS = 30

# One real second = two simulated minutes.
SIMULATION_SPEED = 2.0

AUDIO_DIRECTORY = (
    Path(__file__).resolve().parent.parent
    / "shared_assets"
    / "audio"
)


class RadioSignalUI(tk.Frame):

    def __init__(
        self,
        master,
        on_complete=None,
        on_back=None
    ):
        super().__init__(master, bg=BG)

        self.puzzle = RadioSignalPuzzle()

        self.on_complete = on_complete
        self.on_back = on_back

        self.after_id = None
        self.last_frame = time.monotonic()
        self.animation_time = 0.0

        self.completed_notified = False
        self.message_unlocked = False

        self.frequency_var = tk.DoubleVar(
            value=self.puzzle.get_state()[
                "tuned_frequency"
            ]
        )

        self.frequency_label_var = tk.StringVar()
        self.info_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value="Tune the receiver and start transmission."
        )

        self.setup_audio()

        self.build_ui()
        self.update_labels()
        self.update_info()
        self.draw_scene()

        self.animate()

    # ========================================================
    # Audio
    # ========================================================

    def setup_audio(self):

        self.audio_available = False

        self.static_sound = None
        self.breath_sound = None

        self.static_channel = None
        self.breath_channel = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.set_num_channels(
                max(8, pygame.mixer.get_num_channels())
            )

            self.static_sound = pygame.mixer.Sound(
                str(
                    AUDIO_DIRECTORY
                    / "radio_static.wav"
                )
            )

            self.breath_sound = pygame.mixer.Sound(
                str(
                    AUDIO_DIRECTORY
                    / "radio_breathing.wav"
                )
            )

            self.static_channel = pygame.mixer.Channel(2)
            self.breath_channel = pygame.mixer.Channel(3)

            self.static_channel.set_volume(0.20)
            self.breath_channel.set_volume(0.0)

            self.static_channel.play(
                self.static_sound,
                loops=-1
            )

            self.audio_available = True

        except (pygame.error, OSError) as error:
            print(
                "[RadioSignalUI] Audio unavailable:",
                error
            )

    def update_audio(self):

        if not self.audio_available:
            return

        state = self.puzzle.get_state()
        quality = self.get_signal_quality()

        if self.message_unlocked:

            self.static_channel.set_volume(0.025)
            self.breath_channel.set_volume(0.60)

        elif state["signal_arrived"]:

            volume = (
                0.20 * (1.0 - quality)
                + 0.02
            )

            self.static_channel.set_volume(
                max(0.02, min(0.22, volume))
            )

            self.breath_channel.set_volume(0.0)

        else:

            self.static_channel.set_volume(0.20)
            self.breath_channel.set_volume(0.0)

    def play_breathing(self):

        if not self.audio_available:
            return

        if not self.breath_channel.get_busy():

            self.breath_channel.set_volume(0.60)

            self.breath_channel.play(
                self.breath_sound,
                loops=-1
            )

    def stop_breathing(self):

        if not self.audio_available:
            return

        self.breath_channel.stop()
        self.breath_channel.set_volume(0.0)

    def stop_audio(self):

        if not self.audio_available:
            return

        self.static_channel.stop()
        self.breath_channel.stop()

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
            text="RADIO\nSIGNAL",
            font=("Arial", 19, "bold"),
            fg=TEXT,
            bg=PANEL,
            justify="center"
        ).pack(pady=(23, 15))

        tk.Label(
            self.panel,
            text="Receiver frequency",
            font=("Arial", 10),
            fg=MUTED,
            bg=PANEL
        ).pack()

        tk.Label(
            self.panel,
            textvariable=self.frequency_label_var,
            font=("Arial", 15, "bold"),
            fg=CYAN,
            bg=PANEL
        ).pack(pady=6)

        self.frequency_slider = tk.Scale(
            self.panel,
            from_=50.0,
            to=250.0,
            resolution=0.1,
            orient="horizontal",
            variable=self.frequency_var,
            command=self.on_frequency_change,
            length=210,
            showvalue=False,
            bg=PANEL,
            fg=TEXT,
            troughcolor="#465976",
            highlightthickness=0
        )

        self.frequency_slider.pack(
            pady=(0, 15)
        )

        tk.Button(
            self.panel,
            text="TRANSMIT",
            command=self.start_transmission,
            font=("Arial", 11, "bold"),
            bg="#7356AE",
            fg=TEXT,
            relief="flat"
        ).pack(
            fill="x",
            padx=20,
            pady=5,
            ipady=8
        )

        tk.Button(
            self.panel,
            text="DECODE",
            command=self.decode_signal,
            font=("Arial", 11, "bold"),
            bg="#386A76",
            fg=TEXT,
            relief="flat"
        ).pack(
            fill="x",
            padx=20,
            pady=5,
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
            pady=(18, 10),
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

    # ========================================================
    # Controls
    # ========================================================

    def update_labels(self):

        self.frequency_label_var.set(
            f"{self.frequency_var.get():.1f} MHz"
        )

    def on_frequency_change(self, value):

        self.puzzle.update({
            "type": "tune",
            "frequency": float(value)
        })

        self.update_labels()
        self.update_info()
        self.update_audio()

        state = self.puzzle.get_state()

        if self.message_unlocked:
            return

        if state["signal_arrived"]:

            self.status_var.set(
                "Receiver adjusted. Press DECODE."
            )

        else:

            self.status_var.set(
                "Receiver frequency adjusted."
            )

    def start_transmission(self):

        self.stop_breathing()

        self.message_unlocked = False
        self.completed_notified = False

        self.puzzle.update({
            "type": "start"
        })

        self.last_frame = time.monotonic()

        self.status_var.set(
            "Transmission traveling through space..."
        )

        self.update_audio()
        self.update_info()

    def decode_signal(self):

        if self.message_unlocked:
            return

        self.puzzle.update({
            "type": "submit"
        })

        state = self.puzzle.get_state()

        self.handle_status(state)

    def reset_simulation(self):

        self.stop_breathing()

        self.puzzle.reset()

        self.frequency_var.set(
            self.puzzle.get_state()[
                "tuned_frequency"
            ]
        )

        self.message_unlocked = False
        self.completed_notified = False

        self.status_var.set(
            "Receiver reset. Awaiting transmission."
        )

        self.last_frame = time.monotonic()

        self.update_labels()
        self.update_info()
        self.update_audio()
        self.draw_scene()

    def go_back(self):

        self.stop_audio()

        if self.after_id is not None:

            self.after_cancel(self.after_id)
            self.after_id = None

        if self.on_back is not None:
            self.on_back()

    # ========================================================
    # Signal quality
    # ========================================================

    def get_signal_quality(self):

        state = self.puzzle.get_state()

        if not state["signal_arrived"]:
            return 0.0

        error = abs(
            state["tuned_frequency"]
            - state["received_frequency"]
        )

        # UI-only indicator, not a physical noise model.
        return max(
            0.0,
            1.0 - error / 20.0
        )

    # ========================================================
    # Scene
    # ========================================================

    def draw_scene(self):

        self.canvas.delete("all")

        state = self.puzzle.get_state()

        self.draw_background()
        self.draw_titles()
        self.draw_spacecraft(state)
        self.draw_radio_waves(state)
        self.draw_signal_progress(state)
        self.draw_receiver(state)

        if self.message_unlocked:
            self.draw_message()

    def draw_background(self):

        for i in range(90):

            x = (i * 97 + 23) % SCENE_WIDTH
            y = (i * 157 + 41) % HEIGHT

            size = 1 if i % 5 else 2

            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#53698B",
                outline=""
            )

    def draw_titles(self):

        self.canvas.create_text(
            20,
            20,
            text="CHAPTER 6 — RADIO COMMUNICATION",
            fill=TEXT,
            font=("Arial", 15, "bold"),
            anchor="nw"
        )

        self.canvas.create_text(
            20,
            50,
            text="Relativistic Doppler effect",
            fill=MUTED,
            font=("Arial", 10),
            anchor="nw"
        )

    def draw_ship_icon(
        self,
        x,
        y,
        color,
        direction=1
    ):

        self.canvas.create_polygon(
            x + direction * 24,
            y,
            x - direction * 15,
            y - 15,
            x - direction * 8,
            y,
            x - direction * 15,
            y + 15,
            fill=color,
            outline=TEXT,
            width=1
        )

        self.canvas.create_oval(
            x - 5,
            y - 5,
            x + 5,
            y + 5,
            fill="#FFFFFF",
            outline=""
        )

    def draw_spacecraft(self, state):

        source_x = 130
        receiver_x = 510
        y = 225

        # Decorative motion. Not to physical scale.
        motion = (
            12 * math.sin(
                self.animation_time * 0.7
            )
        )

        self.draw_ship_icon(
            source_x + motion,
            y,
            PURPLE,
            direction=-1
        )

        self.draw_ship_icon(
            receiver_x,
            y,
            CYAN,
            direction=1
        )

        self.canvas.create_text(
            source_x,
            y + 40,
            text="VERA",
            fill=PURPLE,
            font=("Arial", 12, "bold")
        )

        self.canvas.create_text(
            receiver_x,
            y + 40,
            text="ADA",
            fill=CYAN,
            font=("Arial", 12, "bold")
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            120,
            text=(
                "Relative radial velocity: "
                f"{state['source_velocity']:+.2f} c"
            ),
            fill=MUTED,
            font=("Arial", 11)
        )

    def draw_radio_waves(self, state):

        if not (
            state["running"]
            or state["signal_arrived"]
        ):
            return

        progress = state["signal_progress"]

        start_x = 155
        end_x = 485

        wave_front = (
            start_x
            + (end_x - start_x) * progress
        )

        y = 225

        self.canvas.create_line(
            start_x,
            y,
            wave_front,
            y,
            fill=GOLD,
            width=2,
            dash=(5, 4)
        )

        for i in range(7):

            phase = progress * 7 - i

            if phase < 0:
                continue

            fraction = phase / 7

            x = (
                start_x
                + (end_x - start_x) * fraction
            )

            if x > wave_front:
                continue

            radius = 8 + i * 2

            self.canvas.create_arc(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                start=290,
                extent=140,
                style="arc",
                outline=GOLD,
                width=2
            )

        if state["signal_arrived"]:

            self.canvas.create_text(
                SCENE_WIDTH / 2,
                315,
                text="SIGNAL RECEIVED",
                fill=GREEN,
                font=("Arial", 14, "bold")
            )

    def draw_signal_progress(self, state):

        progress = state["signal_progress"]

        left = 110
        right = 530
        top = 365
        bottom = 382

        self.canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="#263750",
            outline=""
        )

        self.canvas.create_rectangle(
            left,
            top,
            left + (right - left) * progress,
            bottom,
            fill=GOLD,
            outline=""
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            405,
            text=(
                "Signal propagation: "
                f"{progress * 100:.0f}%"
            ),
            fill=MUTED,
            font=("Arial", 11)
        )

    def draw_receiver(self, state):

        quality = self.get_signal_quality()

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            445,
            text="RECEIVER SIGNAL QUALITY",
            fill=MUTED,
            font=("Arial", 11, "bold")
        )

        left = 170
        right = 470
        top = 470
        bottom = 490

        self.canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="#263750",
            outline=""
        )

        color = (
            GREEN if quality >= 0.975
            else GOLD if quality >= 0.5
            else RED
        )

        self.canvas.create_rectangle(
            left,
            top,
            left + (right - left) * quality,
            bottom,
            fill=color,
            outline=""
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            515,
            text=f"{quality * 100:.1f}%",
            fill=color,
            font=("Arial", 13, "bold")
        )

    def draw_message(self):

        self.canvas.create_rectangle(
            70,
            330,
            570,
            555,
            fill="#192C3C",
            outline=GREEN,
            width=2
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            355,
            text="TRANSMISSION DECODED",
            fill=GREEN,
            font=("Arial", 15, "bold")
        )

        self.canvas.create_text(
            SCENE_WIDTH / 2,
            430,
            text=(
                "VERA: Ada? Can you hear me?\n\n"
                "I'm still here. Please find me."
            ),
            fill=TEXT,
            font=("Arial", 14),
            justify="center",
            width=450
        )

    # ========================================================
    # Status
    # ========================================================

    def handle_status(self, state):

        status = state["status"]

        if status == "success":

            self.message_unlocked = True

            self.status_var.set(
                "Transmission decoded successfully!"
            )

            self.play_breathing()
            self.update_audio()

            if (
                not self.completed_notified
                and self.on_complete is not None
            ):

                self.completed_notified = True

                self.after_idle(
                    self.on_complete
                )

        elif status == "signal_not_arrived":

            self.status_var.set(
                "The signal has not arrived yet."
            )

        elif status == "frequency_too_low":

            self.status_var.set(
                "Receiver frequency is too low."
            )

        elif status == "frequency_too_high":

            self.status_var.set(
                "Receiver frequency is too high."
            )

        else:

            self.status_var.set(
                f"Receiver status: {status}"
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

        was_running = self.puzzle.get_state()["running"]

        if was_running:

            self.puzzle.update({
                "type": "tick",
                "dt": elapsed * SIMULATION_SPEED
            })

            state = self.puzzle.get_state()

            if not state["running"]:
                self.handle_status(state)

        self.update_audio()
        self.update_info()
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

        self.info_var.set(
            "Emitted frequency: "
            f"{state['emitted_frequency']:.1f} MHz\n"
            "Relative velocity: "
            f"{state['source_velocity']:+.2f} c\n"
            "Distance at emission: "
            f"{state['distance']:.1f} light-min\n"
            "Propagation delay: "
            f"{state['signal_delay']:.1f} min"
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

        self.stop_audio()

        super().destroy()


# ============================================================
# Standalone test
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.title(
        "ASTRA — Radio Communication"
    )

    root.geometry(
        f"{WIDTH}x{HEIGHT}"
    )

    root.resizable(False, False)

    screen = RadioSignalUI(root)

    screen.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
