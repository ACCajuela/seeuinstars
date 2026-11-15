
import tkinter as tk
import random
import math
import time
import json
from pathlib import Path

import pygame


class IntroScreen(tk.Frame):
    WIDTH = 900
    HEIGHT = 600
    FRAME_MS = 33

    BG = "#030712"
    ACCENT = "#8BD3FF"
    BOX_BG = "#0B1220"

    FALLBACK_DURATION = 210.86

    # A última legenda termina em aproximadamente 202.9s.
    # O título aparece depois dela.
    TITLE_OFFSET = 7.5

    def __init__(self, master, on_finish=None):
        super().__init__(master, bg=self.BG)

        self.on_finish = on_finish
        self.running = True
        self.job = None
        self.started_at = 0.0

        # ---------------------------------
        # PATHS
        # ---------------------------------

        self.root_path = (
            Path(__file__).resolve().parent.parent
        )

        self.audio_path = (
            self.root_path
            / "shared_assets"
            / "audio"
            / "intro"
            / "pale_blue_dot.wav"
        )

        self.subtitle_path = (
            self.root_path
            / "chapters"
            / "intro"
            / "subtitles.json"
        )

        self.settings_path = (
            self.root_path / "settings.json"
        )

        self.locales_path = (
            self.root_path / "locales"
        )

        # ---------------------------------
        # AUDIO STATE
        # ---------------------------------

        self.audio_channel = None
        self.audio_sound = None
        self.duration = self.FALLBACK_DURATION

        # ---------------------------------
        # LOCALIZATION
        # ---------------------------------

        self.language = self.load_language()
        self.subtitles = self.load_subtitles()
        self.translations = self.load_translations()

        print(f"[INTRO] Language: {self.language}")
        print(f"[INTRO] Subtitle cues: {len(self.subtitles)}")
        print(
            "[INTRO] Translations: "
            f"{len(self.translations)}"
        )

        # ---------------------------------
        # CANVAS
        # ---------------------------------

        self.canvas = tk.Canvas(
            self,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg=self.BG,
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # ---------------------------------
        # STARS
        # ---------------------------------

        rng = random.Random(42)

        self.stars = [
            (
                rng.randint(0, self.WIDTH),
                rng.randint(0, self.HEIGHT),
                rng.choice([1, 1, 1, 2]),
                rng.uniform(0.3, 1.0)
            )
            for _ in range(100)
        ]

        # ---------------------------------
        # INPUT
        # ---------------------------------

        self.canvas.bind(
            "<Button-1>",
            self.on_click
        )

        self.canvas.bind(
            "<Escape>",
            lambda event: self.finish()
        )

        self.canvas.bind(
            "<space>",
            lambda event: self.finish()
        )

        self.canvas.focus_set()

        # ---------------------------------
        # START
        # ---------------------------------

        self.start_audio()

        self.started_at = time.monotonic()

        self.animate()

    # =====================================
    # UTILITIES
    # =====================================

    @staticmethod
    def clamp(value):
        return max(0.0, min(1.0, value))

    @classmethod
    def smoothstep(cls, value):
        x = cls.clamp(value)
        return x * x * (3 - 2 * x)

    @staticmethod
    def blend(color_a, color_b, amount):
        amount = max(0.0, min(1.0, amount))

        a = [
            int(color_a[i:i + 2], 16)
            for i in (1, 3, 5)
        ]

        b = [
            int(color_b[i:i + 2], 16)
            for i in (1, 3, 5)
        ]

        rgb = [
            round(x + (y - x) * amount)
            for x, y in zip(a, b)
        ]

        return "#{:02x}{:02x}{:02x}".format(*rgb)

    # =====================================
    # LANGUAGE
    # =====================================

    def load_language(self):
        if not self.settings_path.exists():
            print(
                "[INTRO] settings.json not found. "
                "Using English."
            )
            return "en"

        try:
            with open(
                self.settings_path,
                "r",
                encoding="utf-8"
            ) as file:
                settings = json.load(file)

            language = settings.get(
                "language",
                "en"
            )

            if language not in ("en", "pt_BR"):
                print(
                    f"[INTRO] Unsupported language: "
                    f"{language}. Using English."
                )
                return "en"

            return language

        except (OSError, json.JSONDecodeError) as error:
            print(
                f"[INTRO] Settings error: {error}"
            )
            return "en"

    # =====================================
    # SUBTITLE TIMINGS
    # =====================================

    def load_subtitles(self):
        if not self.subtitle_path.exists():
            print(
                "[INTRO] subtitles.json not found: "
                f"{self.subtitle_path}"
            )
            return []

        try:
            with open(
                self.subtitle_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            subtitles = data.get(
                "subtitles",
                []
            )

            subtitles.sort(
                key=lambda item: item["start"]
            )

            return subtitles

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError
        ) as error:
            print(
                f"[INTRO] Subtitle timing error: {error}"
            )
            return []

    # =====================================
    # SUBTITLE TRANSLATIONS
    # =====================================

    def load_translations(self):
        locale_path = (
            self.locales_path
            / f"{self.language}.json"
        )

        if not locale_path.exists():
            print(
                "[INTRO] Locale not found: "
                f"{locale_path}"
            )
            return {}

        try:
            with open(
                locale_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            translations = data.get(
                "intro_subtitles",
                {}
            )

            return translations

        except (
            OSError,
            json.JSONDecodeError,
            TypeError
        ) as error:
            print(
                f"[INTRO] Translation error: {error}"
            )
            return {}

    # =====================================
    # AUDIO
    # =====================================

    def start_audio(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            # Pausa a música do menu ANTES
            # de iniciar a narração.
            pygame.mixer.music.pause()

            if not self.audio_path.exists():
                print(
                    "[INTRO] Narration not found: "
                    f"{self.audio_path}"
                )
                return

            self.audio_sound = pygame.mixer.Sound(
                str(self.audio_path)
            )

            self.duration = (
                self.audio_sound.get_length()
            )

            # Canal dedicado à narração.
            self.audio_channel = (
                pygame.mixer.Channel(7)
            )

            self.audio_channel.set_volume(1.0)

            self.audio_channel.play(
                self.audio_sound
            )

            print(
                "[INTRO] Narration started: "
                f"{self.duration:.2f}s"
            )

        except pygame.error as error:
            print(
                f"[INTRO] Audio error: {error}"
            )

    def stop_audio(self):
        if self.audio_channel is not None:
            self.audio_channel.stop()
            self.audio_channel = None

        # NÃO retomamos a background.wav.
        # Ela permanece pausada após a intro.

    # =====================================
    # INPUT
    # =====================================

    def on_click(self, event):
        if event.x >= 740 and event.y <= 65:
            self.finish()

    # =====================================
    # STARS
    # =====================================

    def draw_stars(self, t):
        fade = self.smoothstep(t / 12)

        for x, y, radius, brightness in self.stars:
            twinkle = (
                0.85
                + 0.15 * math.sin(t + x)
            )

            intensity = (
                fade * brightness * twinkle
            )

            color = self.blend(
                self.BG,
                "#C7D9F6",
                intensity
            )

            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline=""
            )

    # =====================================
    # LIGHT BEAM
    # =====================================

    def draw_beam(self, t):
        fade_in = self.smoothstep(
            (t - 15) / 20
        )

        fade_out = (
            1
            - self.smoothstep(
                (t - 180) / 20
            )
        )

        strength = fade_in * fade_out

        if strength <= 0:
            return

        for layer in range(18, 0, -1):
            width = layer * 6

            intensity = strength * (
                0.15
                + 0.2 * (1 - layer / 18)
            )

            color = self.blend(
                self.BG,
                "#B8B3A1",
                intensity
            )

            self.canvas.create_polygon(
                390 - width,
                -30,
                390 + width,
                -30,
                515 + width,
                630,
                515 - width,
                630,
                fill=color,
                outline=""
            )

    # =====================================
    # EARTH PLACEHOLDER
    # =====================================

    def draw_earth(self, t):
        # O ponto azul aparece logo no começo.
        appearance = self.smoothstep(
            t / 5
        )

        # Aproximação lenta da Terra.
        zoom = self.smoothstep(
            (t - 60) / 125
        )

        radius = 3 + 145 * zoom

        x = 455
        y = 310

        blue = self.blend(
            self.BG,
            "#67C8F4",
            appearance
        )

        # Halo
        self.canvas.create_oval(
            x - radius * 1.2,
            y - radius * 1.2,
            x + radius * 1.2,
            y + radius * 1.2,
            outline=self.blend(
                self.BG,
                "#294C75",
                appearance * 0.7
            ),
            width=2
        )

        # Planeta
        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=blue,
            outline=""
        )

        # Continentes abstratos.
        # A Bri substituirá pela arte final.
        if radius > 30:
            self.canvas.create_oval(
                x - radius * 0.5,
                y - radius * 0.3,
                x + radius * 0.05,
                y + radius * 0.25,
                fill="#70BCA8",
                outline=""
            )

            self.canvas.create_oval(
                x + radius * 0.15,
                y + radius * 0.05,
                x + radius * 0.55,
                y + radius * 0.6,
                fill="#70BCA8",
                outline=""
            )

    # =====================================
    # DIALOGUE BOX / SUBTITLES
    # =====================================

    def draw_subtitles(self, t):
        current_id = None

        for subtitle in self.subtitles:
            start = subtitle.get("start", 0)
            end = subtitle.get("end", 0)

            if start <= t < end:
                current_id = subtitle.get("id")
                break

        if current_id is None:
            return

        current_text = self.translations.get(
            current_id
        )

        if not current_text:
            return

        # Caixa de diálogo
        self.canvas.create_rectangle(
            35,
            455,
            865,
            565,
            fill=self.BOX_BG,
            outline=self.ACCENT,
            width=2
        )

        # Nome do narrador
        self.canvas.create_text(
            55,
            473,
            text="CARL SAGAN",
            anchor="nw",
            fill=self.ACCENT,
            font=("Arial", 11, "bold")
        )

        # Texto da legenda
        self.canvas.create_text(
            450,
            522,
            text=current_text,
            width=770,
            justify="center",
            fill="#FFFFFF",
            font=("Arial", 16)
        )

    # =====================================
    # ASTRA TITLE
    # =====================================

    def draw_title(self, t):
        title_start = max(
            0,
            self.duration - self.TITLE_OFFSET
        )

        fade = self.smoothstep(
            (t - title_start) / 3
        )

        if fade <= 0:
            return

        background = self.blend(
            self.BG,
            "#111C30",
            fade
        )

        self.canvas.create_rectangle(
            0,
            0,
            self.WIDTH,
            self.HEIGHT,
            fill=background,
            outline=""
        )

        self.canvas.create_text(
            450,
            280,
            text="ASTRA",
            font=("Arial", 54, "bold"),
            fill=self.blend(
                background,
                "#FFFFFF",
                fade
            )
        )

        self.canvas.create_text(
            450,
            335,
            text="A JOURNEY BEYOND EARTH",
            font=("Arial", 14),
            fill=self.blend(
                background,
                "#A9C9ED",
                fade
            )
        )

    # =====================================
    # ANIMATION LOOP
    # =====================================

    def animate(self):
        if not self.running:
            return

        t = (
            time.monotonic()
            - self.started_at
        )

        self.canvas.delete("all")

        # Ordem de renderização:
        self.draw_stars(t)
        self.draw_beam(t)
        self.draw_earth(t)

        # Título sobre a animação.
        self.draw_title(t)

        # Legendas sobre a animação e título.
        self.draw_subtitles(t)

        # Skip
        self.canvas.create_text(
            870,
            28,
            text="SKIP INTRO >>",
            anchor="e",
            fill="#8EA4C3",
            font=("Arial", 10, "bold")
        )

        if t >= self.duration:
            self.finish()
            return

        self.job = self.after(
            self.FRAME_MS,
            self.animate
        )

    # =====================================
    # FINISH
    # =====================================

    def finish(self):
        if not self.running:
            return

        self.running = False

        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None

        self.stop_audio()

        if self.on_finish:
            self.on_finish()

    # =====================================
    # CLEANUP
    # =====================================

    def destroy(self):
        self.running = False

        if self.job is not None:
            self.after_cancel(self.job)
            self.job = None

        self.stop_audio()

        super().destroy()


# =========================================
# STANDALONE TEST
# =========================================

if __name__ == "__main__":
    root = tk.Tk()

    root.title(
        "ASTRA - Pale Blue Dot"
    )

    root.geometry("900x600")
    root.resizable(False, False)

    intro = IntroScreen(
        root,
        on_finish=root.destroy
    )

    intro.pack(
        fill="both",
        expand=True
    )

    root.mainloop()
