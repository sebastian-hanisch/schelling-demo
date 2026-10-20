"""Kennzahlen, Messreihen und Verdikte der Demo „Schelling-Segregation“. Verdikte sind reine Funktionen (Art, Text); jede Zahl im Text kommt aus der Rechnung.

Modell: zwei Betriebstypen auf einem Gitter oder den Knoten eines Netzes, ein Betrieb ist zufrieden, wenn mindestens der Anteil τ seiner Nachbarn zum eigenen Typ gehört; unzufriedene Betriebe ziehen nach einer Zugregel
auf freie Flächen. Maße: Entmischungsindex (mittlerer Anteil gleichartiger Nachbarn), Modularität der Typen-Partition, Anteil Unzufriedener, Cluster, Endstatus (alle zufrieden, blockiert, Obergrenze).
Jede Messreihe mittelt über feste Starts (`SWEEP_SEEDS`); jede Zelle hat ihren eigenen Zufallsstrom."""

import math
import os
from dataclasses import dataclass

# BLAS-Threads: siehe sch_algorithm.py (muss vor dem ersten Import von numpy stehen).
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

import sch_algorithm as A
import sch_constants as C
from sch_scenario import make_instance

NAN = float("nan")
MAX_STEPS_EXP = 30000     # Obergrenze der Schritte je Lauf in den Experimenten der App (die README-Messreihe nutzt `MAX_STEPS`)


def de(x, digits=1) -> str:
    """Dezimalzahl mit Komma (deutsche Texte); eine nicht definierte Zahl erscheint als Gedankenstrich."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    s = f"{x:.{digits}f}"
    if float(s) == 0.0:
        s = s.lstrip("-")                       # „−0,00“ liest sich wie eine Zahl kleiner null
    return s.replace(".", ",").replace("-", "−")


def pct(x, digits=0) -> str:
    return de(100.0 * x, digits)


def tp(tau) -> str:
    """Toleranzschwelle als Prozentangabe mit Komma („30 %“, „37,5 %“)."""
    p = round(100.0 * tau, 1)
    return f"{de(p, 0 if p == int(p) else 1)} %"


def _rng(*parts):
    return np.random.default_rng([int(p) for p in parts])


def _mean(values):
    return float(np.mean(values)) if len(values) else NAN


def _median(values):
    return float(np.median(values)) if len(values) else NAN


# --- Räume --------------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True, eq=False)
class Space:
    nbrs: tuple             # Nachbartabelle
    positions: object       # (Zeile, Spalte) je Fläche im Gitter, sonst None
    labels: object          # Verbund je Fläche (nur Netz „Verbünde“), sonst None
    pos: tuple              # Zeichenposition (x, y) je Fläche
    shape: object           # (Zeilen, Spalten) im Gitter, sonst None
    edges: tuple            # Kanten (i, j) mit i < j für die Zeichnung des Netzes (leer im Gitter)

    @property
    def n_cells(self) -> int:
        return len(self.nbrs)


def build_space(space, l, n, c, radius, seed, layout=False) -> Space:
    """Gitter l × l mit der Nachbarschaft nach `radius`, oder eines der Netze aus Stück 1 mit n Flächen."""
    if space == C.T_GRID:
        pos = tuple(((j + 0.5) / l, 1.0 - (i + 0.5) / l) for i in range(l) for j in range(l))
        return Space(A.grid_neighbors(l, l, radius), A.grid_positions(l, l), None, pos, (l, l), ())
    inst = make_instance(space, n, c, seed, layout=layout)
    edges = tuple((i, j) for i, nb in enumerate(inst.adj) for j in nb if i < j)
    return Space(A.adj_neighbors(inst.adj), None, np.array(inst.groups) if inst.groups is not None else None, inst.pos, None, edges)


# --- Hauptanalyse -----------------------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    raum: str = C.T_GRID
    l: int = C.DEFAULT_L
    n: int = C.DEFAULT_N
    c: int = C.DEFAULT_C
    rho: int = C.DEFAULT_RHO        # belegter Anteil in Prozent
    tau: int = C.DEFAULT_TAU        # Toleranzschwelle in Prozent
    rule: str = C.R_HAPPY
    radius: int = C.DEFAULT_RADIUS
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    space: Space
    rule: str               # tatsächlich verwendete Regel („nächste“ gibt es nur im Gitter)
    types0: list
    run: dict
    s0: float               # Entmischungsindex am Anfang
    s1: float               # und am Ende
    q0: float               # Modularität der Typen-Partition am Anfang
    q1: float               # und am Ende
    unhappy0: float         # Anteil Unzufriedener am Anfang
    clusters1: tuple        # (Zahl, größter Anteil) am Ende
    nmi1: float             # NMI der Typen mit den Verbünden am Ende (NaN außer im Netz „Verbünde“)

    @property
    def agents(self) -> int:
        return sum(1 for v in self.types0 if v)

    @property
    def free(self) -> int:
        return self.space.n_cells - self.agents

    @property
    def tau(self) -> float:
        return self.settings.tau / 100.0

    @property
    def status(self) -> str:
        return self.run["status"]


def analyse(settings: Settings) -> Analysis:
    sp = build_space(settings.raum, settings.l, settings.n, settings.c, settings.radius, settings.seed, layout=True)
    rule = settings.rule if (settings.rule != C.R_NEAR or sp.positions is not None) else C.R_HAPPY
    types0 = A.initial_types(sp.n_cells, settings.rho / 100.0, C.FRAC_A, _rng(settings.seed, 2))
    tau = settings.tau / 100.0
    run = A.simulate(sp.nbrs, types0, tau, rule, _rng(settings.seed, 3), C.MAX_STEPS, positions=sp.positions, frames=A.frame_schedule(C.MAX_STEPS, C.FRAMES))
    end = run["types"]
    nmi1 = A.nmi(end, sp.labels) if sp.labels is not None else NAN
    return Analysis(settings, sp, rule, types0, run, A.similarity(types0, sp.nbrs), A.similarity(end, sp.nbrs), A.modularity(types0, sp.nbrs), A.modularity(end, sp.nbrs),
                    len(A.unhappy_cells(types0, tau, sp.nbrs)) / max(1, sum(1 for v in types0 if v)), A.clusters(end, sp.nbrs), nmi1)


def verdict_main(an: Analysis) -> tuple[str, str]:
    """Verdikt dieses Laufs: wie stark entmischt das Gebiet, und endet es?"""
    run = an.run
    if an.agents == 0:
        return "info", "Es steht kein Betrieb im Gebiet."
    if an.unhappy0 == 0:
        return "info", f"Alle {an.agents} Betriebe sind von Anfang an zufrieden: bei Schwelle {an.settings.tau} % zieht keiner um."
    gain = f"Der Anteil gleichartiger Nachbarn geht von {pct(an.s0)} % auf {pct(an.s1)} %, die Modularität der Typen von {de(an.q0, 2)} auf {de(an.q1, 2)}"
    if run["status"] == C.ST_DONE:
        text = (f"Nach {run['moves']} Umzügen ({run['steps']} Schritten) sind alle {an.agents} Betriebe zufrieden. {gain}; es bleiben {an.clusters1[0]} Cluster gleichartiger Betriebe, der größte mit {pct(an.clusters1[1])} % der Betriebe.")
        return ("success" if an.s1 - an.s0 >= 0.2 else "info"), text
    if run["status"] == C.ST_BLOCKED:
        why = "es gibt keine freie Fläche" if an.free == 0 else "keiner findet eine freie Fläche, auf der er zufrieden wäre"
        tail = " Mit der Regel „Auf eine beliebige freie Fläche“ würden sie dennoch weiterziehen." if (an.free > 0 and an.rule != C.R_ANY) else ""
        return "warning", f"Nach {run['moves']} Umzügen ({run['steps']} Schritten) blockiert: {pct(run['unhappy'])} % der {an.agents} Betriebe sind unzufrieden, und {why}. {gain}.{tail}"
    return "warning", f"Nach {run['steps']} Schritten (Obergrenze, {run['moves']} Umzüge) sind noch {pct(run['unhappy'])} % der Betriebe unzufrieden. {gain}."


# --- E1: Schwelle und Zugregel ---------------------------------------------------------------------------------------------------------------


def _cell(rows, **keys):
    return next(r for r in rows if all(r[k] == v for k, v in keys.items()))


def tau_rows(l, rho, radius, taus=C.TAU_GRID, rules=C.RULES, runs=C.LIVE_RUNS, max_steps=MAX_STEPS_EXP) -> list[dict]:
    """Je Regel und Schwelle τ auf dem Gitter l × l (belegter Anteil `rho`, Radius `radius`): Entmischungsindex am Ende und am Anfang (Mittel), Anteile der Endstati, Schritte und Umzüge (Median), Anteil Unzufriedener am Ende
    (Mittel) über `runs` feste Starts."""
    sp = build_space(C.T_GRID, l, 0, 0, radius, 0)
    rows = []
    for ri, rule in enumerate(rules):
        for ti, tau in enumerate(taus):
            res = []
            for seed in C.SWEEP_SEEDS[:runs]:
                t0 = A.initial_types(sp.n_cells, rho, C.FRAC_A, _rng(seed, 10))
                out = A.simulate(sp.nbrs, t0, tau, rule, _rng(seed, 11, ri, ti), max_steps, positions=sp.positions)
                res.append((A.similarity(t0, sp.nbrs), A.similarity(out["types"], sp.nbrs), out))
            share = lambda st: float(np.mean([o["status"] == st for _, _, o in res]))
            rows.append({"rule": rule, "tau": tau, "s0": _mean([a for a, _, _ in res]), "s1": _mean([b for _, b, _ in res]), "done": share(C.ST_DONE), "blocked": share(C.ST_BLOCKED), "cap": share(C.ST_CAP),
                         "steps": _median([o["steps"] for _, _, o in res]), "moves": _median([o["moves"] for _, _, o in res]), "unhappy": _mean([o["unhappy"] for _, _, o in res]), "runs": len(res)})
    return rows


def tau_cell(rows, rule, tau):
    return _cell(rows, rule=rule, tau=tau)


def first_tau(rows, rule, predicate):
    """Kleinste Schwelle der Reihe, bei der `predicate(Zeile)` gilt, oder None."""
    hits = [r["tau"] for r in sorted((r for r in rows if r["rule"] == rule), key=lambda r: r["tau"]) if predicate(r)]
    return hits[0] if hits else None


def verdict_tau(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E1: wie stark wirkt eine milde Schwelle, und wann endet es nicht mehr?"""
    if not rows:
        return "warning", "Keine Läufe."
    rules = list(dict.fromkeys(r["rule"] for r in rows))
    taus = sorted({r["tau"] for r in rows})
    mid = 0.3 if 0.3 in taus else taus[len(taus) // 2]
    parts = []
    for rule in rules:
        c0 = tau_cell(rows, rule, mid)
        notall = first_tau(rows, rule, lambda r: r["done"] < 1.0)
        none = first_tau(rows, rule, lambda r: r["done"] == 0.0)
        txt = f"„{C.RULE_LABEL[rule]}“: Entmischungsindex {pct(c0['s0'])} % → {pct(c0['s1'])} % bei τ = {tp(mid)}"
        if notall is None:
            txt += "; jeder Lauf endet zufrieden"
        elif none == notall:
            txt += f"; ab τ = {tp(none)} endet kein Lauf mehr zufrieden"
        else:
            txt += f"; nicht mehr jeder Lauf endet zufrieden ab τ = {tp(notall)}" + (f", keiner ab τ = {tp(none)}" if none is not None else "")
        parts.append(txt)
    return "info", f"Entmischungsindex (mittlerer Anteil gleichartiger Nachbarn) vor und nach den Umzügen, je Regel: " + "; ".join(parts) + "."


# --- E2: freie Flächen und Radius ----------------------------------------------------------------------------------------------------------------


def vacancy_rows(l, tau=C.VACANCY_TAU, radius=1, rhos=C.RHO_GRID, runs=C.LIVE_RUNS, max_steps=MAX_STEPS_EXP) -> list[dict]:
    """Regel „zufrieden“, Schwelle `tau`: Entmischungsindex am Ende, Endstati und Schritte über den belegten Anteil ρ."""
    sp = build_space(C.T_GRID, l, 0, 0, radius, 0)
    rows = []
    for ri, rho in enumerate(rhos):
        res = []
        for seed in C.SWEEP_SEEDS[:runs]:
            t0 = A.initial_types(sp.n_cells, rho, C.FRAC_A, _rng(seed, 20))
            out = A.simulate(sp.nbrs, t0, tau, C.R_HAPPY, _rng(seed, 21, ri), max_steps, positions=sp.positions)
            res.append(out)
        rows.append({"rho": rho, "s1": _mean([A.similarity(o["types"], sp.nbrs) for o in res]), "done": float(np.mean([o["status"] == C.ST_DONE for o in res])),
                     "blocked": float(np.mean([o["status"] == C.ST_BLOCKED for o in res])), "steps": _median([o["steps"] for o in res]), "unhappy": _mean([o["unhappy"] for o in res]), "runs": len(res)})
    return rows


def radius_rows(l, rho, taus=C.RADIUS_TAUS, radii=(1, 2), runs=C.LIVE_RUNS, max_steps=MAX_STEPS_EXP) -> list[dict]:
    """Regel „zufrieden“: Entmischungsindex und Endstati über die Schwelle, je Radius (1 oder 2)."""
    rows = []
    for radius in radii:
        sp = build_space(C.T_GRID, l, 0, 0, radius, 0)
        for ti, tau in enumerate(taus):
            res = []
            for seed in C.SWEEP_SEEDS[:runs]:
                t0 = A.initial_types(sp.n_cells, rho, C.FRAC_A, _rng(seed, 30))
                res.append(A.simulate(sp.nbrs, t0, tau, C.R_HAPPY, _rng(seed, 31, radius, ti), max_steps, positions=sp.positions))
            rows.append({"radius": radius, "tau": tau, "s1": _mean([A.similarity(o["types"], sp.nbrs) for o in res]), "done": float(np.mean([o["status"] == C.ST_DONE for o in res])),
                         "blocked": float(np.mean([o["status"] == C.ST_BLOCKED for o in res])), "unhappy": _mean([o["unhappy"] for o in res]), "runs": len(res)})
    return rows


def space_rows(l, tau=C.VACANCY_TAU, radius=1, rhos=C.RHO_GRID, runs=C.LIVE_RUNS, rho_radius=0.9, taus=C.RADIUS_TAUS, max_steps=MAX_STEPS_EXP) -> dict:
    """Beide Reihen von Experiment 2."""
    return {"vacancy": vacancy_rows(l, tau, radius, rhos, runs, max_steps), "radius": radius_rows(l, rho_radius, taus, (1, 2), runs, max_steps), "tau": tau}


def verdict_space(res: dict) -> tuple[str, str]:
    """Verdikt zu E2: wie wirken freie Flächen und der Radius?"""
    vac, rad = res.get("vacancy"), res.get("radius")
    if not vac or not rad:
        return "warning", "Keine Läufe."
    lo, hi = min(vac, key=lambda r: r["rho"]), max(vac, key=lambda r: r["rho"])
    tmin, tmax = min(r["tau"] for r in rad), max(r["tau"] for r in rad)
    a1, a2 = _cell(rad, radius=1, tau=tmin), _cell(rad, radius=2, tau=tmin)
    taus = sorted({r["tau"] for r in rad})
    tdiff = max(taus, key=lambda t: abs(_cell(rad, radius=1, tau=t)["done"] - _cell(rad, radius=2, tau=t)["done"]))
    d1, d2 = _cell(rad, radius=1, tau=tdiff), _cell(rad, radius=2, tau=tdiff)
    end = (f"bei τ = {tp(tdiff)} enden {pct(d2['done'])} % statt {pct(d1['done'])} % der Läufe zufrieden" if d1["done"] != d2["done"]
           else f"in beiden Fällen enden bei jeder gemessenen Schwelle alle Läufe zufrieden" if all(_cell(rad, radius=k, tau=t)["done"] == d1["done"] for k in (1, 2) for t in taus)
           else "der Anteil zufriedener Enden ist bei beiden Radien gleich")
    text = (f"Bei τ = {tp(res['tau'])} und {pct(hi['rho'])} % belegten Flächen liegt der Entmischungsindex am Ende bei {pct(hi['s1'])} %, bei {pct(lo['rho'])} % belegt bei {pct(lo['s1'])} %; bei {pct(hi['rho'])} % belegt enden "
            f"{pct(hi['done'])} % der Läufe zufrieden und {pct(hi['blocked'])} % blockieren. Radius 2 statt 1: bei τ = {tp(tmin)} {pct(a2['s1'])} % statt {pct(a1['s1'])} %; {end}.")
    return "info", text


# --- E3: exakt auf kleinen Gittern --------------------------------------------------------------------------------------------------------------


def grid_label(rows, cols, na, nb) -> str:
    return f"{rows} × {cols} ({na} A, {nb} B)"


def exact_rows(grids=C.EXACT_GRIDS, taus=C.EXACT_TAUS, rules=(C.R_HAPPY, C.R_ANY), sim_runs=C.EXACT_SIM_RUNS) -> list[dict]:
    """Auf kleinen Gittern: exakte Kette (Zahl der Belegungen, der zufriedenen und blockierten, Wahrscheinlichkeit zufrieden zu enden, erwartete Schritte) gegen eine Simulation mit `sim_runs` zufälligen Starts."""
    rows = []
    for gi, (r, c, na, nb) in enumerate(grids):
        nbrs = A.grid_neighbors(r, c, 1)
        rho, frac = (na + nb) / (r * c), na / (na + nb)
        for ri, rule in enumerate(rules):
            for ti, tau in enumerate(taus):
                ex = A.exact_analysis(r, c, na, nb, tau, rule)
                res = []
                for k in range(sim_runs):
                    t0 = A.initial_types(r * c, rho, frac, _rng(gi, ri, ti, k, 1))
                    res.append(A.simulate(nbrs, t0, tau, rule, _rng(gi, ri, ti, k, 2), C.MAX_STEPS))
                steps = np.array([o["steps"] for o in res], dtype=float)
                rows.append({"grid": grid_label(r, c, na, nb), "rule": rule, "tau": tau, "states": ex["states"], "done": ex["done"], "blocked": ex["blocked"], "p_done": ex["p_done"], "steps": ex["steps"],
                             "sim_p_done": float(np.mean([o["status"] == C.ST_DONE for o in res])), "sim_steps": float(steps.mean()), "sim_se": float(steps.std() / math.sqrt(len(steps))), "runs": sim_runs})
    return rows


def verdict_exact(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E3: wie viele Belegungen blockieren, und wie unterscheiden sich die Zugregeln?"""
    if not rows:
        return "warning", "Keine Rechnung."
    grid = rows[0]["grid"]
    mine = [r for r in rows if r["grid"] == grid]
    tmax = max(r["tau"] for r in mine)
    h = next((r for r in mine if r["rule"] == C.R_HAPPY and r["tau"] == tmax), None)
    a = next((r for r in mine if r["rule"] == C.R_ANY and r["tau"] == tmax), None)
    if h is None or a is None:
        return "info", f"Auf dem Gitter {grid} wurden {len(mine)} Fälle exakt gerechnet."
    return "info", (f"Auf dem Gitter {grid} (alle {h['states']} Belegungen, exakt) sind bei τ = {tp(tmax)} {h['blocked']} Belegungen blockiert; mit der Regel „{C.RULE_LABEL[C.R_HAPPY]}“ endet nur {pct(h['p_done'], 1)} % der Starts "
                    f"zufrieden (Simulation: {pct(h['sim_p_done'], 1)} %), mit „{C.RULE_LABEL[C.R_ANY]}“ {pct(a['p_done'], 1)} % nach im Mittel {de(a['steps'], 1)} Schritten (Simulation: {de(a['sim_steps'], 1)} ± {de(a['sim_se'], 1)}).")


# --- E4: Brücke zu Stück 2 und Netze ---------------------------------------------------------------------------------------------------------------


def bridge_rows(l, spaces=C.BRIDGE_SPACES, taus=C.BRIDGE_TAUS, runs=C.LIVE_RUNS, n=C.BRIDGE_N, c=C.BRIDGE_C, rho=C.BRIDGE_RHO, max_steps=MAX_STEPS_EXP) -> list[dict]:
    """Je Raum und Schwelle (Regel „zufrieden“, belegter Anteil `rho`): Entmischungsindex und Modularität der Typen am Ende, Anteil gleichartiger Kanten, Anteil Unzufriedener, Anteil der Läufe, die zufrieden enden,
    und im Netz „Verbünde“ die NMI der Typen mit den Verbünden. Mittel über `runs` feste Netze und Starts."""
    rows = []
    for si, space in enumerate(spaces):
        for ti, tau in enumerate(taus):
            res = []
            for seed in C.SWEEP_SEEDS[:runs]:
                sp = build_space(space, l, n, c, 1, seed)
                t0 = A.initial_types(sp.n_cells, rho, C.FRAC_A, _rng(seed, 40))
                out = A.simulate(sp.nbrs, t0, tau, C.R_HAPPY, _rng(seed, 41, si, ti), max_steps, positions=sp.positions)
                end = out["types"]
                res.append({"s0": A.similarity(t0, sp.nbrs), "s1": A.similarity(end, sp.nbrs), "q1": A.modularity(end, sp.nbrs), "e1": A.edge_share(end, sp.nbrs), "unhappy": out["unhappy"], "done": out["status"] == C.ST_DONE,
                            "nmi": A.nmi(end, sp.labels) if sp.labels is not None else NAN, "moves": out["moves"]})
            rows.append({"space": space, "tau": tau, "s0": _mean([x["s0"] for x in res]), "s1": _mean([x["s1"] for x in res]), "q1": _mean([x["q1"] for x in res]), "e1": _mean([x["e1"] for x in res]),
                         "unhappy": _mean([x["unhappy"] for x in res]), "done": float(np.mean([x["done"] for x in res])), "nmi": _mean([x["nmi"] for x in res if not math.isnan(x["nmi"])]), "moves": _median([x["moves"] for x in res]), "runs": len(res)})
    return rows


def bridge_cell(rows, space, tau):
    return _cell(rows, space=space, tau=tau)


def _in_space(space) -> str:
    return f"im {space}" if space in (C.T_GRID, C.T_RANDOM) else f"im Netz „{space}“"


def verdict_bridge(rows: list[dict]) -> tuple[str, str]:
    """Verdikt zu E4: stimmt Index mit Modularität überein, und verstärken Verbünde die Entmischung?"""
    if not rows:
        return "warning", "Keine Läufe."
    taus = sorted({r["tau"] for r in rows})
    tmax = taus[-1]
    spaces = list(dict.fromkeys(r["space"] for r in rows))
    text = f"Bei τ = {tp(tmax)} liegt der Entmischungsindex am Ende " + ", ".join(f"{_in_space(sp)} bei {pct(bridge_cell(rows, sp, tmax)['s1'])} %" for sp in spaces)
    if C.T_COMMUNITIES in spaces:
        text += f"; die Typen stimmen mit den Verbünden zu NMI {de(bridge_cell(rows, C.T_COMMUNITIES, tmax)['nmi'], 2)} überein"
    worst = max(abs(r["q1"] - (r["e1"] - 0.5)) for r in rows)
    return "info", text + f". Die Modularität der Typen-Partition liegt höchstens {de(worst, 3)} neben dem Anteil gleichartiger Kanten minus ½."
