
"""Testes do estado da nave (core/mission.py) e da ligação com a
história e o save. Rodar com: python test_mission.py"""

import json
import os

from core.mission import MissionState, MAX_DOSE, pick_storm


def check(description, condition):
    print(("OK   " if condition else "FALHOU ") + description)
    if not condition:
        raise SystemExit(1)


# ------------------------------------------------------------
# Energia solar cai com a distância do Sol
# ------------------------------------------------------------
m = MissionState()
for place, expected in (("earth", 4), ("mars", 2), ("jupiter", 0), ("saturn", 0)):
    m.location = place
    check(f"energia solar em {place} = {expected}", m.solar_income() == expected)

m.location = "jupiter"
m.rtg_online = True
check("com a bateria nuclear (RTG) em Júpiter, entra energia", m.energy_income() == 2)

# ------------------------------------------------------------
# Um dia normal
# ------------------------------------------------------------
m = MissionState()
m.start_leg("earth_mars", days=3, location="earth")
report = m.resolve_day(["make_oxygen"])
check("energia: 6 + 4 (sol) - 2 (fazer oxigênio) = 8", m.energy == 8)
check("oxigênio: 6 + 2 (feito) - 1 (Ada respirou) = 7", m.oxygen == 7)
check("faltam 2 dias", m.days_left == 2)
check("relatório tem os itens do dia",
      [r["key"] for r in report] == ["solar_income", "action_make_oxygen", "oxygen_used"])

# Sem energia suficiente
m = MissionState()
m.energy = 2
try:
    m.resolve_day(["boost_engines"])
    check("não deixa gastar mais energia do que tem", False)
except ValueError:
    check("não deixa gastar mais energia do que tem", True)

# ------------------------------------------------------------
# Tempestade solar e abrigo
# ------------------------------------------------------------
m = MissionState()
m.resolve_day([], storm={"class": "X"})
check("tempestade X sem abrigo: dose +3", m.dose == 3)

m = MissionState()
m.resolve_day(["build_shelter"], storm={"class": "X"})
check("tempestade X com abrigo (2): dose +1", m.dose == 1)
check("abrigo é desmontado depois da noite", m.shield == 0)

m = MissionState()
r = m.resolve_day(["build_shelter"], storm={"class": "M"})
check("tempestade M com abrigo: nenhuma dose", m.dose == 0 and r[-1]["key"] == "storm_blocked")

m = MissionState()
m.dose = 9
r = m.resolve_day([], storm={"class": "X"})
check("dose nunca passa do limite", m.dose == MAX_DOSE)
check("aviso de dose alta", any(i["key"] == "emergency_dose" for i in r))

# ------------------------------------------------------------
# Motores e atraso das mensagens
# ------------------------------------------------------------
m = MissionState()
m.start_leg("earth_mars", days=3, location="earth")
m.resolve_day(["boost_engines"])
check("motores: o trecho anda 2 dias em 1", m.days_left == 1)

m = MissionState()
m.start_leg("mars_jupiter", days=3, location="mars")
r1 = m.resolve_day(["call_earth"])
check("perto de Marte, a resposta não chega no mesmo dia",
      not any(i["key"] == "earth_reply" for i in r1))
energy_before = m.energy
r2 = m.resolve_day([])
check("a resposta da Terra chega no dia seguinte",
      any(i["key"] == "earth_reply" for i in r2))
check("a resposta traz +2 de energia (dica do controle)",
      m.energy == min(10, energy_before + m.energy_income() + 2))

# ------------------------------------------------------------
# Emergência de oxigênio (não termina o jogo)
# ------------------------------------------------------------
m = MissionState()
m.oxygen = 1
r = m.resolve_day([])
check("oxigênio acabou: usa o tanque reserva", m.oxygen == 3 and m.reserve_tanks == 0)
m.oxygen = 1
r = m.resolve_day([])
check("sem tanque: o COSMO usa toda a energia para fazer oxigênio",
      m.oxygen == 2 and m.energy == 0)

# Duas pessoas respiram o dobro
m = MissionState()
m.crew = 2
m.resolve_day([])
check("com a Vera a bordo, gasta 2 de oxigênio por noite", m.oxygen == 4)

# ------------------------------------------------------------
# Efeitos dos minigames
# ------------------------------------------------------------
m = MissionState()
m.apply_effects({"energy": -10, "oxygen": +20})
check("efeitos respeitam os limites (0 a 10)", m.energy == 0 and m.oxygen == 10)
try:
    m.apply_effects({"pizza": 1})
    check("recusa recurso desconhecido", False)
except KeyError:
    check("recusa recurso desconhecido", True)

# ------------------------------------------------------------
# Salvar e carregar
# ------------------------------------------------------------
m = MissionState()
m.start_leg("earth_mars", 3, "earth")
m.resolve_day(["research", "call_earth"], storm={"class": "C", "date": "2024-05-10"})
copy = MissionState.from_dict(json.loads(json.dumps(m.to_dict())))
check("o estado vira JSON e volta igual", copy.to_dict() == m.to_dict())

check("sorteio de tempestade com chance 0 nunca acontece",
      pick_storm([{"class": "X"}], chance=0.0) is None)
check("sorteio de tempestade com chance 1 sempre acontece",
      pick_storm([{"class": "X"}], chance=1.0) == {"class": "X"})


# ------------------------------------------------------------
# Noite em Marte: poeira e frio
# ------------------------------------------------------------
night = {"dust": True, "cold": True}

m = MissionState()
m.location = "mars"
m.resolve_day([], conditions=night)
check("poeira: painéis sujos não geram energia; frio: bateria perde 3",
      m.energy == 6 + 0 - 3)

m = MissionState()
m.location = "mars"
m.resolve_day(["heat_battery"], conditions=night)
check("aquecedor: gasta 2 e a bateria não perde nada", m.energy == 6 - 2)

m = MissionState()
m.location = "mars"
r = m.resolve_day(["clean_panels", "heat_battery"], conditions=night)
check("limpar os painéis: volta a energia solar de Marte (+2)", m.energy == 6 + 2 - 2)
check("limpar os painéis gasta 1 de oxigênio do traje (+1 respirado)", m.oxygen == 6 - 1 - 1)
check("relatório não fala de poeira quando os painéis foram limpos",
      not any(i["key"] == "dust_no_power" for i in r))

m = MissionState()
m.energy = 1
m.location = "mars"
m.resolve_day([], conditions=night)
check("o frio não deixa a energia negativa", m.energy == 0)


# ------------------------------------------------------------
# Consequências dos minigames
# ------------------------------------------------------------
import tkinter as tk
from puzzles.orbital_launch_ui import OrbitalLaunchUI
from puzzles.mars_gravity_ui import MarsGravityUI

root = tk.Tk()
o = OrbitalLaunchUI(root, language="pt_BR")
check("lançamento de primeira não gasta energia", o.mission_effects() == {"energy": 0})
o.contextual_feedback("collision")
o.contextual_feedback("escape")
check("2 lançamentos errados gastam 2 de energia", o.mission_effects() == {"energy": -2})
for _ in range(5):
    o.contextual_feedback("collision")
check("o gasto de energia do lançamento tem limite (3)", o.mission_effects() == {"energy": -3})
o.destroy()

g = MarsGravityUI(root, language="pt_BR")
check("traje cheio: a nave gasta 1 de oxigênio para recarregar", g.mission_effects() == {"oxygen": -1})
g.use_suit_o2(60)
check("traje abaixo de 50%: gasta 2", g.mission_effects() == {"oxygen": -2})
g.use_suit_o2(50)
check("traje esvaziou: troca o cilindro e volta a 100%", g.suit_o2 == 100 and g.suit_refills == 1)
check("cada troca de cilindro custa +1 de oxigênio da nave", g.mission_effects() == {"oxygen": -2})
g.destroy()
root.destroy()


# ------------------------------------------------------------
# Relatório da missão (final)
# ------------------------------------------------------------
from screens.mission_report import build_report

m = MissionState()
m.start_leg("travel_earth_mars", 3, "earth")
m.resolve_day(["build_shelter"], storm={"class": "M6.1", "date": "2024-02-21"})
m.resolve_day(["build_shelter"], storm={"class": "X5.8", "date": "2024-05-11"})
m.resolve_day([], storm={"class": "M2.0", "date": "2024-03-01"})
m.record_minigame("orbital_launch", {"energy": 0})
rep = build_report(m)
keys = [h[1] for h in rep["highlights"]]
check("relatório: abrigo que bloqueou tudo", keys[0] == "hl_storm_blocked")
check("relatório: abrigo que segurou só parte", keys[1] == "hl_storm_partial")
check("relatório: tempestade sem abrigo", keys[2] == "hl_storm_hit")
check("relatório: lançamento de primeira", "hl_launch_perfect" in keys)
check("relatório: lista as tempestades reais enfrentadas", len(rep["storms"]) == 3)
check("relatório: radiação 2 ganha o Escudo Solar", rep["medals"]["solar_shield"] == (m.dose <= 2))
check("relatório: início e fim da nave", rep["start"]["energy"] == 6 and rep["end"]["energy"] == m.energy)
check("relatório: no máximo 5 destaques", len(build_report(m)["highlights"]) <= 5)

# ------------------------------------------------------------
# Ligação com a história e o save
# ------------------------------------------------------------
from core.engine import StoryEngine
from core.localization_manager import LocalizationManager
from core.save_manager import SaveManager

e = StoryEngine(chapter=2)
hit = None
for _ in range(300):
    d = e.next_dialogue()
    if d is None or d.get("type") == "puzzle":
        hit = d
        break
check("capítulo 2 chega no minigame de Marte sem erro",
      hit == {"type": "puzzle", "id": "mars_gravity"})

e.complete_puzzle("mars_gravity", {"completed": True, "effects": {"oxygen": -2}})
check("o resultado do minigame muda os recursos da nave", e.mission.oxygen == 4)

e = StoryEngine(chapter=0)
e.mission.energy = 3
e.load_chapter(1)
check("os recursos continuam ao trocar de capítulo", e.mission.energy == 3)

sm = SaveManager()
sm.save_path = sm.save_path.with_name("save_test_mission.json")
loc = LocalizationManager("pt_BR")
e1 = StoryEngine(chapter=1)
e1.change_scene("hangar")
e1.mission.oxygen = 2
sm.save_game(e1, loc)
e2 = StoryEngine(chapter=0)
sm.load_game(e2, loc)
os.remove(sm.save_path)
check("save do capítulo 1 carrega no capítulo e cena certos",
      e2.chapter == 1 and e2.scene_id == "hangar")
check("save guarda os recursos da nave", e2.mission.oxygen == 2)

print("\nTodos os testes passaram!")
