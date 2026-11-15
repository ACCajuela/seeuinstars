
"""Diário de Bordo: a simulação dos recursos da nave durante uma viagem.

Cada dia:
  1. O COSMO avisa se vem uma tempestade solar (dados reais do DONKI).
  2. A jogadora escolhe cartas de ação (cada uma gasta energia).
  3. "Passar a noite": as regras de core/mission.py são aplicadas.
  4. O relatório mostra as consequências, com o botão "Por quê?".

Para testar sozinho: python -m screens.mission_log
"""

import random
import tkinter as tk

from core.mission import (
    ACTIONS, LEGS, MAX_DOSE, MAX_ENERGY, MAX_OXYGEN,
    load_donki_events, pick_storm,
)
from core.ui import (
    ACCENT, BG, BOX_FILL, BUTTON_BG, BUTTON_DISABLED, BUTTON_HOVER,
    FEEDBACK_COLOR, MINIGAME_MUTED, MINIGAME_SUCCESS, PROJECT_ROOT, TITLE,
    TITLE_FONT, CosmoHint, MenuButton, font_or_fallback, rounded_rect,
)

WIDTH, HEIGHT = 900, 600

# Cores de cada recurso
ENERGY_COLOR = "#FFD166"
OXYGEN_COLOR = "#8BD3FF"
DOSE_COLOR = "#FF8FA3"
TRIP_COLOR = "#B8A6FF"
SPACE_BG = "#070D1A"
BAD_COLOR = "#FF8FA3"

ICON_FONT = ("Segoe UI Emoji", 22)
ICONS = {
    "energy": "⚡",
    "oxygen": "🫁",
    "dose": "☢",
    "trip": "🚀",
    "make_oxygen": "🫁",
    "build_shelter": "🛡",
    "boost_engines": "🚀",
    "research": "🔬",
    "call_earth": "📡",
}

# Ordem das cartas na tela
CARD_ORDER = ["make_oxygen", "build_shelter", "boost_engines",
              "research", "call_earth"]

# Qual explicação do "Por quê?" combina com cada item do relatório
WHY_FOR_REPORT = {
    "solar_income": "why_solar",
    "rtg_income": "why_solar",
    "action_make_oxygen": "why_oxygen",
    "action_build_shelter": "why_shelter",
    "action_boost_engines": "why_engines",
    "action_call_earth": "why_delay",
    "earth_reply": "why_delay",
    "oxygen_used": "why_breathing",
    "storm_hit": "why_storm",
    "storm_blocked": "why_shelter",
    "emergency_dose": "why_storm",
}

TONE_COLORS = {"good": MINIGAME_SUCCESS, "bad": BAD_COLOR, "info": MINIGAME_MUTED}

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]


class MissionLogScreen(tk.Frame):

    def __init__(self, master, engine, leg_id, t, language="pt_BR",
                 on_complete=None, rng=None):
        super().__init__(master, bg=SPACE_BG)

        self.engine = engine
        self.mission = engine.mission
        self.leg_id = leg_id
        self.leg = LEGS[leg_id]
        self.t = t
        self.language = language
        self.on_complete = on_complete
        self.rng = rng or random.Random()

        self.storms, self.storm_source = load_donki_events(PROJECT_ROOT)
        self.cards_text = self._research_cards()

        # Começa o trecho (ou continua, se o jogo foi salvo no meio dele)
        if self.mission.leg != leg_id or self.mission.leg_finished():
            self.mission.start_leg(leg_id, self.leg["days"],
                                   self.leg["location"])

        self.selected = []
        self.buttons = []
        self.storm = None
        self.report = []
        self.mode = "plan"

        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT,
                                bg=SPACE_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._draw_stars()

        # Balão do COSMO: criado uma vez só (a imagem é pesada)
        self.hint = CosmoHint(self.canvas, right=660)

        self.start_day()

    # ========================================================
    # Textos
    # ========================================================

    def tx(self, key, **params):
        text = self.t(f"mission.{key}")
        return text.format(**params) if params else text

    def _research_cards(self):
        cards = self.t("mission.research_cards")
        return cards if isinstance(cards, list) else []

    def _format_date(self, iso_date):
        year, month, day = iso_date.split("-")
        if self.language == "pt_BR":
            return f"{day}/{month}/{year}"
        return f"{MONTHS_EN[int(month) - 1]} {int(day)}, {year}"

    # ========================================================
    # Fluxo do dia
    # ========================================================

    def start_day(self):
        index = self.mission.day
        chances = self.leg["storm_chance"]
        chance = chances[min(index, len(chances) - 1)]
        self.storm = pick_storm(self.storms, chance, self.rng)

        # A nave vai se afastando do Sol durante a viagem
        path = self.leg.get("path")
        if path:
            self.mission.location = path[min(index, len(path) - 1)]
        self.selected = []
        self.mode = "plan"
        self.redraw()

    def toggle_card(self, action):
        if action in self.selected:
            self.selected.remove(action)
        elif self.mission.can_afford(self.selected + [action]):
            self.selected.append(action)
        else:
            self.hint.set(self.tx("not_enough"), BAD_COLOR)
            return
        self.redraw()

    def end_day(self):
        self.report = self.mission.resolve_day(self.selected, storm=self.storm)
        # Carta de ciência sorteada para cada pesquisa feita hoje
        self.new_cards = [self.rng.choice(self.cards_text)
                          for a in self.selected if a == "research"
                          and self.cards_text]
        self.mode = "report"
        self.redraw()

    def after_report(self):
        if self.mission.leg_finished():
            self.mode = "summary"
            self.redraw()
        else:
            self.start_day()

    def finish(self):
        if self.on_complete is not None:
            self.on_complete({
                "completed": True,
                "leg": self.leg_id,
                "state": self.mission.snapshot(),
            })

    # ========================================================
    # Desenho
    # ========================================================

    def _draw_stars(self):
        rng = random.Random(7)
        for _ in range(110):
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

    def redraw(self):
        self._clear()
        self._draw_header()
        self._draw_gauges()

        # O COSMO só aparece no planejamento (os painéis cobrem o lugar dele)
        self.canvas.itemconfigure(
            "hint", state="normal" if self.mode == "plan" else "hidden"
        )

        if self.mode == "plan":
            self._draw_cards()
            self._draw_plan_footer()
            self.hint.raise_()
        elif self.mode == "report":
            self._draw_report()
        elif self.mode == "why":
            self._draw_why()
        elif self.mode == "summary":
            self._draw_summary()

    def _text(self, *args, **kwargs):
        kwargs.setdefault("tags", "ui")
        return self.canvas.create_text(*args, **kwargs)

    def _button(self, *args, **kwargs):
        button = MenuButton(self.canvas, *args, **kwargs)
        self.canvas.addtag_withtag("ui", button.tag)
        self.buttons.append(button)
        return button

    def _draw_header(self):
        family = font_or_fallback(TITLE_FONT)
        self._text(26, 28, anchor="w", text=self.tx("title"),
                   font=(family, 22), fill=TITLE)
        self._text(26, 58, anchor="w",
                   text=self.tx(f"route_{self.leg_id}"),
                   font=("Arial", 12, "bold"), fill=ACCENT)
        day = min(self.mission.day + (1 if self.mode == "plan" else 0),
                  self.leg["days"])
        self._text(WIDTH - 26, 40, anchor="e",
                   text=self.tx("day", day=day, total=self.leg["days"]),
                   font=(family, 18), fill=TITLE)
        self._text(WIDTH - 26, 66, anchor="e", text=self.tx("source"),
                   font=("Arial", 8), fill="#7C8BA5")

    def _draw_gauges(self):
        m = self.mission
        spend = (m.actions_cost(self.selected)
                 if self.mode == "plan" else 0)
        gauges = [
            ("energy", m.energy, MAX_ENERGY, ENERGY_COLOR, spend,
             self.tx("income", value=m.energy_income())),
            ("oxygen", m.oxygen, MAX_OXYGEN, OXYGEN_COLOR, 0, ""),
            ("dose", m.dose, MAX_DOSE, DOSE_COLOR, 0,
             f"{m.dose}/{MAX_DOSE}"),
        ]
        x = 26
        for key, value, maximum, color, dim, note in gauges:
            self._gauge(x, 86, 202, key, value, maximum, color, dim, note)
            x += 214

        # Viagem: dias que faltam
        rounded_rect(self.canvas, x, 86, x + 206, 176, r=14, fill=BOX_FILL,
                     outline=TRIP_COLOR, width=2, tags="ui")
        self._text(x + 16, 108, anchor="w", text=ICONS["trip"],
                   font=ICON_FONT, fill=TRIP_COLOR)
        self._text(x + 50, 108, anchor="w", text=self.tx("trip"),
                   font=("Arial", 12, "bold"), fill=TITLE)
        left = m.days_left
        label = (self.tx("arrived") if left <= 0 else
                 self.tx("days_left_one") if left == 1 else
                 self.tx("days_left", value=left))
        self._text(x + 16, 140, anchor="w", text=label,
                   font=("Arial", 13, "bold"), fill=TRIP_COLOR)
        total = self.leg["days"]
        done = (total - left) / total if total else 1
        self.canvas.create_line(x + 16, 162, x + 190, 162, fill="#24324F",
                                width=6, capstyle="round", tags="ui")
        self.canvas.create_line(x + 16, 162, x + 16 + 174 * done + 0.1, 162,
                                fill=TRIP_COLOR, width=6, capstyle="round",
                                tags="ui")

    def _gauge(self, x, y, w, key, value, maximum, color, dim, note):
        c = self.canvas
        rounded_rect(c, x, y, x + w, y + 90, r=14, fill=BOX_FILL,
                     outline=color, width=2, tags="ui")
        self._text(x + 16, y + 22, anchor="w", text=ICONS[key],
                   font=ICON_FONT, fill=color)
        self._text(x + 50, y + 22, anchor="w", text=self.tx(key),
                   font=("Arial", 12, "bold"), fill=TITLE)
        self._text(x + w - 14, y + 22, anchor="e", text=str(value),
                   font=("Arial", 16, "bold"), fill=color)
        # 10 quadradinhos; os que serão gastos hoje ficam apagados
        seg_w, gap = 15, 3
        for i in range(maximum):
            sx = x + 16 + i * (seg_w + gap)
            filled = i < value
            spent = filled and i >= value - dim
            fill = ("#3A4A66" if spent else color) if filled else "#1A2438"
            c.create_rectangle(sx, y + 46, sx + seg_w, y + 62, fill=fill,
                               outline="", tags="ui")
        if note:
            self._text(x + 16, y + 76, anchor="w", text=note,
                       font=("Arial", 9), fill=MINIGAME_MUTED)

    # ---------------- Planejamento (cartas) ----------------

    def _draw_cards(self):
        self._text(26, 200, anchor="w", text=self.tx("choose"),
                   font=("Arial", 12, "bold"), fill=TITLE)
        card_w, card_h, gap = 160, 210, 12
        x = 26
        for action in CARD_ORDER:
            self._card(x, 218, card_w, card_h, action)
            x += card_w + gap

    def _card(self, x, y, w, h, action):
        c = self.canvas
        tag = f"card_{action}"
        selected = action in self.selected
        cost = ACTIONS[action]["cost"]
        affordable = selected or self.mission.can_afford(self.selected + [action])

        fill = BUTTON_HOVER if selected else BUTTON_BG
        outline = ACCENT if selected else ("#3A4A66" if affordable else "#2A3346")
        text_color = TITLE if affordable else BUTTON_DISABLED

        rounded_rect(c, x, y, x + w, y + h, r=16, fill=fill, outline=outline,
                     width=3 if selected else 2, tags=("ui", tag))
        self._text(x + w / 2, y + 42, text=ICONS[action],
                   font=("Segoe UI Emoji", 30),
                   fill=ACCENT if affordable else BUTTON_DISABLED,
                   tags=("ui", tag))
        self._text(x + w / 2, y + 92, text=self.tx(f"action_{action}_name"),
                   font=("Arial", 12, "bold"), fill=text_color,
                   width=w - 16, justify="center", tags=("ui", tag))
        self._text(x + w / 2, y + 136, text=self.tx(f"action_{action}_desc"),
                   font=("Arial", 10), fill=MINIGAME_MUTED if affordable
                   else BUTTON_DISABLED, width=w - 20, justify="center",
                   tags=("ui", tag))
        # custo
        rounded_rect(c, x + w / 2 - 34, y + h - 38, x + w / 2 + 34,
                     y + h - 12, r=10, fill="#2A2410" if affordable
                     else "#1A2032", outline="", tags=("ui", tag))
        self._text(x + w / 2, y + h - 25, text=f"-{cost} ⚡",
                   font=("Segoe UI Emoji", 11, "bold"),
                   fill=ENERGY_COLOR if affordable else BUTTON_DISABLED,
                   tags=("ui", tag))
        if selected:
            self._text(x + w - 18, y + 18, text="✔", font=("Segoe UI Symbol", 14,
                       "bold"), fill=ACCENT, tags=("ui", tag))

        c.tag_bind(tag, "<Button-1>", lambda e, a=action: self.toggle_card(a))
        c.tag_bind(tag, "<Enter>", lambda e: c.configure(cursor="hand2"))
        c.tag_bind(tag, "<Leave>", lambda e: c.configure(cursor=""))

    def _draw_plan_footer(self):
        if self.storm:
            message = self.tx("forecast_storm", cls=self.storm["class"])
            color = FEEDBACK_COLOR
        elif self.mission.day == 0 and self.leg_id == "travel_earth_mars":
            message, color = self.tx("forecast_first"), TITLE
        else:
            message, color = self.tx("forecast_calm"), TITLE
        self.hint.set(message, color)

        left = self.mission.energy - self.mission.actions_cost(self.selected)
        self._text(787, 470, text=self.tx("energy_after", value=left),
                   font=("Arial", 10, "bold"), fill=ENERGY_COLOR, width=200,
                   justify="center")
        self._button(787, 535, self.tx("end_day"), self.end_day,
                     width=190, height=56, font_size=13, primary=True)


    # ---------------- Relatório da noite ----------------

    def _panel(self, title):
        rounded_rect(self.canvas, 90, 196, 810, 586, r=20, fill=BOX_FILL,
                     outline=ACCENT, width=2, tags="ui")
        self._text(450, 226, text=title,
                   font=(font_or_fallback(TITLE_FONT), 17), fill=TITLE)

    def _draw_report(self):
        self._panel(self.tx("report_title", day=self.mission.day))
        y = 258
        for item in self.report:
            text = self.tx(f"report_{item['key']}", **{
                k: v for k, v in item["params"].items()
                if isinstance(v, (int, str))
            })
            color = TONE_COLORS[item["tone"]]
            dot = {"good": "✔", "bad": "!", "info": "•"}[item["tone"]]
            self._text(124, y, anchor="nw", text=dot,
                       font=("Segoe UI Symbol", 12, "bold"), fill=color)
            item_id = self._text(146, y, anchor="nw", text=text, width=630,
                                 font=("Arial", 12), fill=color)
            y = self.canvas.bbox(item_id)[3] + 8

        # Tempestade real: mostra de onde veio o dado
        if self.storm:
            self._text(146, y + 2, anchor="nw", width=630,
                       text=self.tx("storm_source", cls=self.storm["class"],
                                    date=self._format_date(self.storm["date"])),
                       font=("Arial", 10, "italic"), fill=FEEDBACK_COLOR)
            y += 26

        # Cartas de ciência ganhas hoje
        for card in self.new_cards:
            card_id = self._text(146, y + 10, anchor="nw", width=610,
                                 text="🔬  " + card, font=("Segoe UI Emoji", 10),
                                 fill=TITLE)
            box = self.canvas.bbox(card_id)
            rect = rounded_rect(self.canvas, 132, box[1] - 8, 776, box[3] + 8,
                                r=10, fill=BUTTON_BG, outline=ACCENT, width=1,
                                tags="ui")
            self.canvas.tag_lower(rect, card_id)
            y = box[3] + 18

        last = self.mission.leg_finished()
        self._button(330, 552, self.tx("why"), self.show_why,
                     width=180, height=44, font_size=12)
        self._button(570, 552, self.tx("arrive" if last else "next_day"),
                     self.after_report, width=200, height=44, font_size=12,
                     primary=True)

    def show_why(self):
        self.mode = "why"
        self.redraw()

    def back_to_report(self):
        self.mode = "report"
        self.redraw()

    def _draw_why(self):
        self._panel(self.tx("why_title"))
        keys = []
        for item in self.report:
            why = WHY_FOR_REPORT.get(item["key"])
            if why and why not in keys:
                keys.append(why)
        y = 258
        for key in keys[:4]:
            item_id = self._text(124, y, anchor="nw", width=652,
                                 text="• " + self.tx(key),
                                 font=("Arial", 11), fill=TITLE)
            y = self.canvas.bbox(item_id)[3] + 10
        if self.storm:
            self._text(124, y + 2, anchor="nw", width=652,
                       text=self.storm.get("url", ""),
                       font=("Arial", 9, "underline"), fill=ACCENT)
        self._button(450, 552, self.tx("back"), self.back_to_report,
                     width=180, height=44, font_size=12)

    # ---------------- Fim da viagem ----------------

    def _draw_summary(self):
        self._panel(self.tx("summary_title"))
        m = self.mission
        self._text(450, 300, width=640, justify="center",
                   text=self.tx("summary", energy=m.energy, oxygen=m.oxygen,
                                dose=m.dose, science=m.science),
                   font=("Arial", 14), fill=TITLE)
        self._button(450, 552, self.tx("arrive"), self.finish,
                     width=200, height=44, font_size=12, primary=True)


# ============================================================
# Teste sozinho: python -m screens.mission_log
# ============================================================

if __name__ == "__main__":
    from core.engine import StoryEngine
    from core.localization_manager import LocalizationManager
    from core.ui import load_project_fonts

    root = tk.Tk()
    load_project_fonts()
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)
    root.title("ASTRA - Diário de Bordo")

    localization = LocalizationManager("pt_BR")
    engine = StoryEngine(chapter=1)
    screen = MissionLogScreen(
        root, engine, "travel_earth_mars", localization.get,
        language="pt_BR", on_complete=lambda result: root.destroy(),
    )
    screen.pack(fill="both", expand=True)
    root.mainloop()
