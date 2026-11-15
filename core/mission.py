
"""Estado da nave da Ada e regras da simulação da missão.

A nave de treino é o "posto avançado" do jogo. Ela tem 3 recursos e
1 indicador, que duram o jogo inteiro e são salvos no save:

    energia    (0 a 10)  bateria da nave
    oxigênio   (0 a 10)  ar para respirar
    blindagem  (0 a 3)   abrigo contra radiação montado hoje
    dose       (0 a 10)  radiação que a Ada já recebeu (só sobe)

Cada trecho de viagem tem alguns dias. Em cada dia a jogadora escolhe
ações (que gastam energia), depois a noite passa: o oxigênio é
consumido, a blindagem é desmontada e pode chegar uma tempestade solar.

Os números são simplificados para crianças de 7 a 12 anos, mas cada
regra corresponde a algo real (veja SCIENCE abaixo).
"""

import random

# ============================================================
# LIMITES E VALORES INICIAIS
# ============================================================

MAX_ENERGY = 10
MAX_OXYGEN = 10
MAX_SHIELD = 3
MAX_DOSE = 10          # limite de segurança de radiação

START = {
    "energy": 6,
    "oxygen": 6,
    "shield": 0,
    "dose": 0,
    "reserve_tanks": 1,  # tanque de oxigênio de emergência
}

# Quanta energia os painéis solares geram por dia, perto da Terra.
PANEL_OUTPUT = 4

# Fração da luz do Sol que chega em cada lugar, comparada com a Terra.
# É a regra do inverso do quadrado da distância: 1 / (distância em UA)².
#   Marte   1,52 UA -> 1/2,32  ≈ 0,43
#   Júpiter 5,20 UA -> 1/27,0  ≈ 0,037
#   Saturno 9,54 UA -> 1/91,0  ≈ 0,011
SOLAR_FACTOR = {
    "earth": 1.0,
    "mars": 0.43,
    "jupiter": 0.037,
    "saturn": 0.011,
}

# Longe do Sol, os painéis quase não funcionam. A partir de Júpiter a
# nave liga a bateria nuclear (RTG), como as sondas Cassini e o rover
# Curiosity, que gera um pouco de energia todo dia, com ou sem Sol.
RTG_OUTPUT = 2

# Quantos dias do jogo uma mensagem leva para ir e voltar da Terra.
# (Na vida real: Marte 6 a 44 min ida e volta; Júpiter ~1h30; Saturno ~2h40.)
MESSAGE_DELAY_DAYS = {
    "earth": 1,   # já viajando: a resposta chega no dia seguinte
    "mars": 1,
    "jupiter": 2,
    "saturn": 2,
}

# ============================================================
# AÇÕES DO DIA (as cartas que a jogadora escolhe)
# ============================================================
# cost: energia gasta | effects: o que muda no estado

ACTIONS = {
    "make_oxygen": {
        "cost": 2,
        "effects": {"oxygen": +2},
    },
    "build_shelter": {
        "cost": 1,
        "effects": {"shield": +2},
    },
    "boost_engines": {
        "cost": 3,
        "effects": {"days_left": -1},
    },
    "research": {
        "cost": 1,
        "effects": {"science": +1},
    },
    "call_earth": {
        "cost": 1,
        "effects": {},  # a resposta chega dias depois (veja resolve_day)
    },
    # --- Só na superfície de Marte (Noite em Marte) ---
    "heat_battery": {
        "cost": 2,
        "effects": {},  # protege a bateria do frio (veja resolve_day)
    },
    "clean_panels": {
        "cost": 0,
        "effects": {"oxygen": -1},  # sair com o traje gasta oxigênio
    },
    "rover_data": {
        "cost": 1,
        "effects": {"science": +1},
    },
}

# Quanto de energia a bateria perde numa noite gelada sem aquecedor
COLD_BATTERY_LOSS = 3

# Cartas que aparecem em cada trecho (por padrão, as da viagem)
TRAVEL_ACTIONS = ["make_oxygen", "build_shelter", "boost_engines",
                  "research", "call_earth"]

# Gravidade das tempestades solares: quanta dose de radiação elas dão
# se a nave estiver sem blindagem. Usa a classe real das explosões
# solares registradas pela NASA no DONKI (C < M < X, cada letra é
# 10 vezes mais forte que a anterior).
def storm_severity(flare_class):
    """'X8.7' -> 3 | 'M6.1' -> 2 | 'M2.0' -> 1 | 'C5' -> 1"""
    letter = (flare_class or "C")[0].upper()
    if letter == "X":
        return 3
    if letter == "M":
        try:
            return 2 if float(flare_class[1:]) >= 5 else 1
        except ValueError:
            return 2
    return 1


# Trechos de viagem do jogo.
# storm_chance: chance de tempestade em cada dia (o 1º dia é calmo,
# para a jogadora aprender; depois o Sol fica imprevisível).
LEGS = {
    "travel_earth_mars": {
        "days": 3,
        "location": "earth",
        "destination": "mars",
        # onde a nave está em cada dia (a energia solar cai perto de Marte)
        "path": ["earth", "earth", "mars"],
        "storm_chance": [0.0, 1.0, 0.4],
    },
    # Posto avançado: uma noite na superfície de Marte, ao lado do rover,
    # durante uma tempestade de poeira (como a que parou o Opportunity).
    "mars_night": {
        "days": 2,
        "location": "mars",
        "path": ["mars", "mars"],
        "storm_chance": [0.0, 0.0],
        "actions": ["heat_battery", "clean_panels", "make_oxygen",
                    "call_earth", "rover_data"],
        # dust: a poeira cobre os painéis | cold: a noite congela a bateria
        "conditions": [
            {"dust": True, "cold": True},
            {"dust": True, "cold": True},
        ],
        # nomes das partes da noite (em vez de "Dia 1 de 2")
        "phases": ["phase_evening", "phase_midnight"],
        "trip_icon": "🌙",
        "research_cards": "research_cards_mars",
    },
}

DONKI_FILE = "data/donki_flares_2024.json"


def load_donki_events(project_root):
    """Lê as tempestades solares reais (DONKI) salvas no jogo."""
    import json
    from pathlib import Path
    path = Path(project_root) / DONKI_FILE
    if not path.exists():
        return [], {}
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    events = data.pop("events", [])
    return events, data

# Ciência por trás de cada regra (para o botão "Por quê?").
SCIENCE = {
    "oxygen": "electrolysis",        # oxigênio feito da água, como na ISS
    "shield": "storm_shelter",       # abrigo com caixas de água/comida (Orion)
    "solar": "inverse_square",       # luz do Sol cai com a distância²
    "rtg": "nuclear_battery",        # bateria nuclear das sondas
    "delay": "light_delay",          # rádio viaja na velocidade da luz
    "dose": "radiation_dose",        # radiação acumula no corpo
}


def _clamp(value, low, high):
    return max(low, min(high, value))


class MissionState:
    """Tudo o que a nave tem e onde ela está. Salvo junto com o jogo."""

    def __init__(self):
        self.energy = START["energy"]
        self.oxygen = START["oxygen"]
        self.shield = START["shield"]
        self.dose = START["dose"]
        self.reserve_tanks = START["reserve_tanks"]

        self.crew = 1             # só a Ada; vira 2 quando a Vera embarca
        self.location = "earth"
        self.rtg_online = False

        self.leg = None           # trecho de viagem atual
        self.day = 0              # dia dentro do trecho
        self.days_left = 0        # dias até o fim do trecho
        self.science = 0          # cartas de pesquisa coletadas
        self.messages = []        # mensagens para a Terra ainda sem resposta
        self.history = []         # relatório de cada dia (para o final)
        self.minigames = {}       # consequências de cada minigame (idem)

    # --------------------------------------------------------
    # Energia que entra por dia
    # --------------------------------------------------------

    def solar_income(self):
        return round(PANEL_OUTPUT * SOLAR_FACTOR.get(self.location, 1.0))

    def energy_income(self):
        income = self.solar_income()
        if self.rtg_online:
            income = max(income, RTG_OUTPUT)
        return income

    # --------------------------------------------------------
    # Trechos de viagem
    # --------------------------------------------------------

    def start_leg(self, leg_id, days, location):
        """Começa um trecho de viagem (ex.: Terra -> Marte, 3 dias)."""
        self.leg = leg_id
        self.day = 0
        self.days_left = days
        self.location = location

    def leg_finished(self):
        return self.days_left <= 0

    # --------------------------------------------------------
    # Escolhas do dia
    # --------------------------------------------------------

    @staticmethod
    def actions_cost(actions):
        return sum(ACTIONS[a]["cost"] for a in actions)

    def can_afford(self, actions):
        return self.actions_cost(actions) <= self.energy

    def resolve_day(self, actions, storm=None, conditions=None):
        """Aplica as ações escolhidas e passa a noite.

        actions:    lista de ids de ACTIONS (ex.: ["make_oxygen", "research"])
        storm:      None ou {"class": "M", ...} (evento do DONKI)
        conditions: None ou {"dust": True, "cold": True} (Noite em Marte)

        Devolve uma lista de itens do relatório do dia:
            {"key": "...", "tone": "good"|"bad"|"info", "params": {...}}
        """
        if not self.can_afford(actions):
            raise ValueError("Not enough energy for these actions")

        conditions = conditions or {}
        report = []
        self.day += 1

        # 1) Painéis solares (ou bateria nuclear) recarregam a bateria.
        #    Na tempestade de poeira, painel sujo não gera nada.
        income = self.energy_income()
        dusty = conditions.get("dust") and "clean_panels" not in actions
        if dusty:
            income = 0
            report.append({"key": "dust_no_power", "tone": "bad",
                           "params": {}})
        else:
            report.append({
                "key": "rtg_income"
                if self.rtg_online and income > self.solar_income()
                else "solar_income",
                "tone": "info",
                "params": {"value": income},
            })
        self.energy = _clamp(self.energy + income, 0, MAX_ENERGY)

        # 2) Ações escolhidas
        self.energy -= self.actions_cost(actions)
        for action in actions:
            for field, delta in ACTIONS[action]["effects"].items():
                self._change(field, delta)
            report.append({"key": f"action_{action}", "tone": "good",
                           "params": {}})
            if action == "call_earth":
                arrives = self.day + MESSAGE_DELAY_DAYS.get(self.location, 1)
                self.messages.append({"sent": self.day, "arrives": arrives})

        # 3) A noite: a tripulação respira
        self.oxygen -= self.crew
        report.append({"key": "oxygen_used", "tone": "info",
                       "params": {"value": self.crew}})

        # 3b) Noite gelada: sem aquecedor, a bateria perde carga
        if conditions.get("cold"):
            if "heat_battery" in actions:
                report.append({"key": "battery_warm", "tone": "good",
                               "params": {}})
            else:
                lost = min(self.energy, COLD_BATTERY_LOSS)
                self.energy -= lost
                report.append({"key": "cold_battery", "tone": "bad",
                               "params": {"value": lost}})

        # 4) Tempestade solar
        if storm:
            severity = storm_severity(storm.get("class", "C"))
            blocked = min(self.shield, severity)
            received = severity - blocked
            self.dose = _clamp(self.dose + received, 0, MAX_DOSE)
            report.append({
                "key": "storm_blocked" if received == 0 else "storm_hit",
                "tone": "good" if received == 0 else "bad",
                "params": {"severity": severity, "received": received,
                           "storm": storm},
            })

        # 5) O abrigo é desmontado de manhã (as caixas voltam ao lugar)
        self.shield = 0

        # 6) Respostas da Terra que chegaram hoje
        arrived = [m for m in self.messages if m["arrives"] <= self.day]
        for message in arrived:
            self.messages.remove(message)
            self.energy = _clamp(self.energy + 2, 0, MAX_ENERGY)
            report.append({"key": "earth_reply", "tone": "good",
                           "params": {"sent": message["sent"]}})

        # 7) A viagem avança um dia
        self.days_left = max(0, self.days_left - 1)

        # 8) Emergências (não terminam o jogo: ensinam)
        report += self._check_emergencies()

        self.history.append({
            "leg": self.leg, "day": self.day, "actions": list(actions),
            "storm": storm, "state": self.snapshot(),
            # o que aconteceu no dia (sem repetir os dados da tempestade)
            "report": [
                {"key": item["key"], "tone": item["tone"],
                 "params": {k: v for k, v in item["params"].items()
                            if k != "storm"}}
                for item in report
            ],
        })
        return report

    def _check_emergencies(self):
        report = []
        if self.oxygen <= 0:
            if self.reserve_tanks > 0:
                self.reserve_tanks -= 1
                self.oxygen = 3
                report.append({"key": "emergency_oxygen_tank", "tone": "bad",
                               "params": {}})
            else:
                # Sem tanque: o COSMO desliga o resto da nave e faz oxigênio
                self.oxygen = 2
                self.energy = 0
                report.append({"key": "emergency_oxygen_power", "tone": "bad",
                               "params": {}})
        if self.dose >= MAX_DOSE:
            report.append({"key": "emergency_dose", "tone": "bad",
                           "params": {}})
        return report

    # --------------------------------------------------------
    # Efeitos vindos dos minigames e da história
    # --------------------------------------------------------

    def apply_effects(self, effects):
        """Aplica mudanças como {"energy": -2, "dose": +1}."""
        for field, delta in (effects or {}).items():
            self._change(field, delta)

    def record_minigame(self, puzzle_id, effects):
        """Guarda as consequências de um minigame para o relatório final."""
        self.minigames[puzzle_id] = dict(effects or {})

    def _change(self, field, delta):
        limits = {
            "energy": (0, MAX_ENERGY),
            "oxygen": (0, MAX_OXYGEN),
            "shield": (0, MAX_SHIELD),
            "dose": (0, MAX_DOSE),
            "days_left": (0, 99),
            "science": (0, 999),
            "reserve_tanks": (0, 5),
            "crew": (1, 4),
        }
        if field not in limits:
            raise KeyError(f"Unknown mission field: {field}")
        low, high = limits[field]
        setattr(self, field, _clamp(getattr(self, field) + delta, low, high))

    # --------------------------------------------------------
    # Salvar e carregar
    # --------------------------------------------------------

    FIELDS = ("energy", "oxygen", "shield", "dose", "reserve_tanks", "crew",
              "location", "rtg_online", "leg", "day", "days_left", "science",
              "messages", "history", "minigames")

    def snapshot(self):
        return {"energy": self.energy, "oxygen": self.oxygen,
                "dose": self.dose, "days_left": self.days_left}

    def to_dict(self):
        return {field: getattr(self, field) for field in self.FIELDS}

    @classmethod
    def from_dict(cls, data):
        state = cls()
        for field in cls.FIELDS:
            if field in (data or {}):
                setattr(state, field, data[field])
        return state


def pick_storm(events, chance, rng=None):
    """Sorteia se uma tempestade chega hoje e qual (da lista do DONKI)."""
    rng = rng or random.Random()
    if not events or rng.random() >= chance:
        return None
    return rng.choice(events)


# ============================================================
# TESTE NO TERMINAL: python -m core.mission
# ============================================================
# Uma viagem de 3 dias (Terra -> Marte) para sentir as regras antes da
# tela do Diário de Bordo existir. As tempestades aqui são exemplos; as
# reais (DONKI) entram no passo 3.

if __name__ == "__main__":
    NAMES = {
        "make_oxygen": "Fazer oxigênio   (-2 energia, +2 oxigênio)",
        "build_shelter": "Montar abrigo    (-1 energia, protege da radiação hoje)",
        "boost_engines": "Acelerar motores (-3 energia, chega 1 dia antes)",
        "research": "Pesquisar        (-1 energia, +1 carta de ciência)",
        "call_earth": "Chamar a Terra   (-1 energia, resposta chega depois)",
    }
    EXAMPLE_STORMS = [{"class": "C"}, {"class": "M"}, {"class": "X"}]

    mission = MissionState()
    location = input("Onde a nave está? (earth/mars/jupiter/saturn) [earth]: ").strip() or "earth"
    mission.start_leg("teste", days=3, location=location)
    if location in ("jupiter", "saturn"):
        mission.rtg_online = True

    ids = list(NAMES)
    while not mission.leg_finished():
        print(f"\n===== DIA {mission.day + 1} | faltam {mission.days_left} dias =====")
        print(f"⚡ energia {mission.energy}  🫁 oxigênio {mission.oxygen}  "
              f"☢️ dose {mission.dose}/{MAX_DOSE}  🔬 ciência {mission.science}  "
              f"(amanhã entra +{mission.energy_income()} de energia)")
        storm = pick_storm(EXAMPLE_STORMS, chance=0.5)
        if storm:
            print(f"⚠️  COSMO: uma tempestade solar classe {storm['class']} vai chegar esta noite!")
        for n, action in enumerate(ids, 1):
            print(f"  {n}. {NAMES[action]}")

        while True:
            raw = input("Escolha os números separados por espaço (Enter = nada): ").split()
            try:
                chosen = [ids[int(n) - 1] for n in raw]
            except (ValueError, IndexError):
                print("Número inválido.")
                continue
            if mission.can_afford(chosen):
                break
            print(f"Energia insuficiente: isso custa {mission.actions_cost(chosen)}, "
                  f"você tem {mission.energy}.")

        for item in mission.resolve_day(chosen, storm=storm):
            print(f"  [{item['tone']}] {item['key']} {item['params'] or ''}")

    print(f"\nFIM DA VIAGEM: ⚡ {mission.energy}  🫁 {mission.oxygen}  "
          f"☢️ {mission.dose}  🔬 {mission.science}")
