
"""Relatório da Missão: o final da primeira missão (Terra -> Marte).

Página 1: como a nave terminou, os momentos que mais pesaram (montados
a partir das escolhas reais da jogadora) e as medalhas.
Página 2: os dados da NASA usados no jogo, com as fontes.

Para testar sozinho: python -m screens.mission_report
"""

import random
import tkinter as tk

from core.mission import MAX_DOSE, MAX_ENERGY, MAX_OXYGEN, START
from core.ui import (
    ACCENT, BOX_FILL, BUTTON_DISABLED, FEEDBACK_COLOR, MINIGAME_MUTED,
    MINIGAME_SUCCESS, TITLE, TITLE_FONT, MenuButton, font_or_fallback,
    rounded_rect,
)

WIDTH, HEIGHT = 900, 600
SPACE_BG = "#070D1A"
ENERGY_COLOR = "#FFD166"
OXYGEN_COLOR = "#8BD3FF"
DOSE_COLOR = "#FF8FA3"
BAD_COLOR = "#FF8FA3"
EMOJI = "Segoe UI Emoji"

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]

# Medalhas: ícone, cor e regra para ganhar
MEDALS = [
    ("oxygen_guardian", "🫁", OXYGEN_COLOR),
    ("solar_shield", "🛡", ACCENT),
    ("scientist", "🔬", MINIGAME_SUCCESS),
    ("energy_saver", "⚡", ENERGY_COLOR),
]


# ============================================================
# O que entra no relatório (sem desenho: dá para testar)
# ============================================================

def build_report(mission):
    """Monta o relatório a partir do estado e do histórico da nave.

    Devolve {"start", "end", "highlights", "medals", "storms"}.
    highlights: lista de (ícone, chave do texto, parâmetros, tom)."""
    history = mission.history
    keys = [item["key"] for day in history for item in day.get("report", [])]

    highlights = []

    # Tempestades solares reais enfrentadas
    storms = []
    for day in history:
        storm = day.get("storm")
        if not storm:
            continue
        storms.append(storm)
        for item in day.get("report", []):
            if item["key"] == "storm_blocked":
                highlights.append(("🛡", "hl_storm_blocked",
                                   {"storm": storm}, "good"))
            elif item["key"] == "storm_hit":
                # Abrigo montado, mas a explosão era forte demais para ele
                partial = "build_shelter" in day.get("actions", [])
                highlights.append(("☢",
                                   "hl_storm_partial" if partial else "hl_storm_hit",
                                   {"storm": storm,
                                    "value": item["params"].get("received", 0)},
                                   "bad"))

    # Lançamento orbital: energia gasta em queimas de correção
    launch = mission.minigames.get("orbital_launch")
    if launch is not None:
        spent = -launch.get("energy", 0)
        if spent:
            highlights.append(("🚀", "hl_launch_fuel", {"value": spent}, "bad"))
        else:
            highlights.append(("🚀", "hl_launch_perfect", {}, "good"))

    # Pulo em Marte: oxigênio da nave para recarregar o traje
    jump = mission.minigames.get("mars_gravity")
    if jump is not None:
        used = -jump.get("oxygen", 0)
        highlights.append(("🫁", "hl_suit_oxygen", {"value": used},
                           "good" if used <= 1 else "bad"))

    # Noite em Marte: frio e poeira
    night_days = [d for d in history if d.get("leg") == "mars_night"]
    if night_days:
        lost = sum(item["params"].get("value", 0)
                   for d in night_days for item in d.get("report", [])
                   if item["key"] == "cold_battery")
        if lost:
            highlights.append(("🌡", "hl_night_cold", {"value": lost}, "bad"))
        else:
            highlights.append(("🌡", "hl_night_warm", {}, "good"))
        cleaned = sum(d["actions"].count("clean_panels") for d in night_days)
        if cleaned:
            highlights.append(("🧹", "hl_cleaned", {"value": cleaned}, "good"))

    if "emergency_oxygen_tank" in keys or "emergency_oxygen_power" in keys:
        highlights.append(("⚠", "hl_tank", {}, "bad"))

    replies = keys.count("earth_reply")
    if replies:
        highlights.append(("📡", "hl_earth", {"value": replies}, "good"))

    used_emergency = ("emergency_oxygen_tank" in keys
                      or "emergency_oxygen_power" in keys)
    medals = {
        "oxygen_guardian": not used_emergency and mission.oxygen >= 3,
        "solar_shield": mission.dose <= 2,
        "scientist": mission.science >= 2,
        "energy_saver": mission.energy >= 5,
    }

    return {
        "start": {"energy": START["energy"], "oxygen": START["oxygen"],
                  "dose": START["dose"]},
        "end": {"energy": mission.energy, "oxygen": mission.oxygen,
                "dose": mission.dose},
        "highlights": highlights[:5],
        "medals": medals,
        "storms": storms,
    }


# ============================================================
# Tela
# ============================================================

class MissionReportScreen(tk.Frame):

    def __init__(self, master, engine, t, language="pt_BR",
                 on_menu=None, on_replay=None):
        super().__init__(master, bg=SPACE_BG)

        self.engine = engine
        self.t = t
        self.language = language
        self.on_menu = on_menu
        self.on_replay = on_replay
        self.report = build_report(engine.mission)
        self.buttons = []

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT,
                                bg=SPACE_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._draw_stars()
        self.show_summary()

    # ---------------- textos ----------------

    def tx(self, key, **params):
        text = self.t(f"report.{key}")
        return text.format(**params) if params else text

    def _date(self, iso_date):
        year, month, day = iso_date.split("-")
        if self.language == "pt_BR":
            return f"{day}/{month}/{year}"
        return f"{MONTHS_EN[int(month) - 1]} {int(day)}, {year}"

    def _highlight_text(self, key, params):
        params = dict(params)
        storm = params.pop("storm", None)
        if storm:
            params["cls"] = storm["class"]
            params["date"] = self._date(storm["date"])
        return self.tx(key, **params)

    # ---------------- desenho base ----------------

    def _draw_stars(self):
        rng = random.Random(11)
        for _ in range(120):
            x, y = rng.randint(0, WIDTH), rng.randint(0, HEIGHT)
            r = rng.choice([1, 1, 2])
            color = rng.choice(["#FFFFFF", "#CBD5E1", "#64748B", ACCENT])
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=color, outline="")

    def _clear(self):
        for button in self.buttons:
            button.destroy()
        self.buttons = []
        self.canvas.delete("ui")

    def _text(self, *args, **kwargs):
        kwargs.setdefault("tags", "ui")
        return self.canvas.create_text(*args, **kwargs)

    def _box(self, x0, y0, x1, y1, outline=ACCENT):
        rounded_rect(self.canvas, x0, y0, x1, y1, r=16, fill=BOX_FILL,
                     outline=outline, width=2, tags="ui")

    def _button(self, *args, **kwargs):
        button = MenuButton(self.canvas, *args, **kwargs)
        self.buttons.append(button)
        return button

    def _title(self, title, subtitle):
        family = font_or_fallback(TITLE_FONT)
        self._text(WIDTH / 2, 36, text=title, font=(family, 24), fill=TITLE)
        self._text(WIDTH / 2, 70, text=subtitle,
                   font=("Arial", 12, "bold"), fill=ACCENT)

    # ---------------- página 1: resumo ----------------

    def show_summary(self):
        self._clear()
        self._title(self.tx("title"), self.tx("subtitle"))
        self._draw_ship()
        self._draw_highlights()
        self._draw_medals()

        self._text(WIDTH / 2, 503, text=self.tx("to_be_continued"),
                   font=("Arial", 11, "italic"), fill=FEEDBACK_COLOR,
                   width=820, justify="center")

        self._button(230, 556, self.tx("nasa_data"), self.show_data,
                     width=200, height=44, font_size=12)
        self._button(450, 556, self.tx("replay"), self._replay,
                     width=200, height=44, font_size=12, primary=True)
        self._button(670, 556, self.tx("menu"), self._menu,
                     width=200, height=44, font_size=12)

    def _draw_ship(self):
        x0, y0, x1, y1 = 26, 96, 300, 330
        self._box(x0, y0, x1, y1)
        self._text(x0 + 18, y0 + 22, anchor="w", text=self.tx("ship"),
                   font=("Arial", 11, "bold"), fill=MINIGAME_MUTED)
        rows = [
            ("energy", "⚡", ENERGY_COLOR, MAX_ENERGY, True),
            ("oxygen", "🫁", OXYGEN_COLOR, MAX_OXYGEN, True),
            ("dose", "☢", DOSE_COLOR, MAX_DOSE, False),
        ]
        y = y0 + 62
        for key, icon, color, maximum, more_is_better in rows:
            start = self.report["start"][key]
            end = self.report["end"][key]
            better = end >= start if more_is_better else end <= start
            self._text(x0 + 18, y, anchor="w", text=icon,
                       font=(EMOJI, 16), fill=color)
            self._text(x0 + 48, y, anchor="w", text=self.tx(key),
                       font=("Arial", 11, "bold"), fill=TITLE)
            self._text(x1 - 18, y, anchor="e", text=f"{start} → {end}",
                       font=("Arial", 13, "bold"),
                       fill=MINIGAME_SUCCESS if better else BAD_COLOR)
            # barra do valor final
            bar_x0, bar_x1 = x0 + 48, x1 - 18
            self.canvas.create_rectangle(bar_x0, y + 18, bar_x1, y + 26,
                                         fill="#1A2438", outline="",
                                         tags="ui")
            self.canvas.create_rectangle(
                bar_x0, y + 18,
                bar_x0 + (bar_x1 - bar_x0) * end / maximum + 0.1, y + 26,
                fill=color, outline="", tags="ui")
            y += 70

    def _draw_highlights(self):
        x0, y0, x1, y1 = 316, 96, 874, 330
        self._box(x0, y0, x1, y1)
        self._text(x0 + 18, y0 + 22, anchor="w", text=self.tx("highlights"),
                   font=("Arial", 11, "bold"), fill=MINIGAME_MUTED)
        y = y0 + 44
        items = self.report["highlights"] or [("✨", "hl_none", {}, "good")]
        for icon, key, params, tone in items:
            color = MINIGAME_SUCCESS if tone == "good" else BAD_COLOR
            self._text(x0 + 18, y, anchor="nw", text=icon,
                       font=(EMOJI, 13), fill=color)
            item = self._text(x0 + 48, y + 2, anchor="nw", width=x1 - x0 - 66,
                              text=self._highlight_text(key, params),
                              font=("Arial", 10), fill=TITLE)
            y = self.canvas.bbox(item)[3] + 8

    def _draw_medals(self):
        self._text(26, 352, anchor="w", text=self.tx("medals"),
                   font=("Arial", 11, "bold"), fill=MINIGAME_MUTED)
        w, gap, x = 206, 11, 26
        for key, icon, color in MEDALS:
            earned = self.report["medals"][key]
            outline = color if earned else "#2A3346"
            self._box(x, 366, x + w, 476, outline=outline)
            self.canvas.create_oval(x + 14, 384, x + 64, 434,
                                    fill="#1E2A44" if earned else "#141B2B",
                                    outline=outline, width=2, tags="ui")
            self._text(x + 39, 409, text=icon, font=(EMOJI, 18),
                       fill=color if earned else BUTTON_DISABLED)
            self._text(x + 76, 392, anchor="w", width=w - 86,
                       text=self.tx(f"medal_{key}"),
                       font=("Arial", 10, "bold"),
                       fill=TITLE if earned else BUTTON_DISABLED)
            self._text(x + 76, 420, anchor="nw", width=w - 86,
                       text=self.tx(f"medal_{key}_rule"),
                       font=("Arial", 8), fill=MINIGAME_MUTED)
            self._text(x + 14, 460, anchor="w",
                       text=self.tx("earned" if earned else "not_yet"),
                       font=("Arial", 9, "bold"),
                       fill=color if earned else BUTTON_DISABLED)
            x += w + gap

    # ---------------- página 2: dados da NASA ----------------

    def show_data(self):
        self._clear()
        self._title(self.tx("data_title"), self.tx("data_subtitle"))

        # tempestades desta partida
        x0, y0, x1, y1 = 26, 96, 874, 214
        self._box(x0, y0, x1, y1, outline=FEEDBACK_COLOR)
        self._text(x0 + 18, y0 + 20, anchor="w", text=self.tx("data_donki_title"),
                   font=("Arial", 11, "bold"), fill=FEEDBACK_COLOR)
        self._text(x0 + 18, y0 + 38, anchor="nw", width=x1 - x0 - 36,
                   text=self.tx("data_donki"), font=("Arial", 10), fill=TITLE)
        storms = self.report["storms"]
        if storms:
            faced = ", ".join(f"{s['class']} ({self._date(s['date'])})"
                              for s in storms)
            line = self.tx("data_storms_faced", storms=faced)
        else:
            line = self.tx("data_no_storms")
        self._text(x0 + 18, y1 - 18, anchor="w", width=x1 - x0 - 36,
                   text=line, font=("Arial", 10, "bold"), fill=FEEDBACK_COLOR)

        # outras fontes, em duas colunas
        blocks = [
            ("data_facts_title", "data_facts"),
            ("data_physics_title", "data_physics"),
            ("data_cases_title", "data_cases"),
            ("data_note_title", "data_note"),
        ]
        positions = [(26, 226, 444, 384), (456, 226, 874, 384),
                     (26, 396, 444, 524), (456, 396, 874, 524)]
        for (title_key, text_key), (bx0, by0, bx1, by1) in zip(blocks, positions):
            self._box(bx0, by0, bx1, by1)
            self._text(bx0 + 16, by0 + 18, anchor="w", text=self.tx(title_key),
                       font=("Arial", 10, "bold"), fill=ACCENT)
            self._text(bx0 + 16, by0 + 34, anchor="nw", width=bx1 - bx0 - 32,
                       text=self.tx(text_key), font=("Arial", 9), fill=TITLE)

        self._button(450, 556, self.tx("back"), self.show_summary,
                     width=200, height=44, font_size=12)

    # ---------------- botões ----------------

    def _replay(self):
        if self.on_replay is not None:
            self.on_replay()

    def _menu(self):
        if self.on_menu is not None:
            self.on_menu()


# ============================================================
# Teste sozinho: python -m screens.mission_report
# ============================================================

if __name__ == "__main__":
    from core.engine import StoryEngine
    from core.localization_manager import LocalizationManager
    from core.ui import load_project_fonts

    root = tk.Tk()
    load_project_fonts()
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    localization = LocalizationManager("pt_BR")
    engine = StoryEngine(chapter=2)
    m = engine.mission
    # uma partida de exemplo
    m.start_leg("travel_earth_mars", 3, "earth")
    m.resolve_day(["make_oxygen", "research"])
    m.resolve_day(["build_shelter"], storm={"class": "X5.8", "date": "2024-05-11"})
    m.resolve_day([], storm={"class": "M6.1", "date": "2024-02-21"})
    m.record_minigame("orbital_launch", {"energy": -1})
    m.record_minigame("mars_gravity", {"oxygen": -2})
    m.start_leg("mars_night", 2, "mars")
    m.resolve_day(["heat_battery", "clean_panels"], conditions={"dust": True, "cold": True})
    m.resolve_day([], conditions={"dust": True, "cold": True})

    screen = MissionReportScreen(root, engine, localization.get,
                                 on_menu=root.destroy, on_replay=root.destroy)
    screen.pack(fill="both", expand=True)
    root.mainloop()
