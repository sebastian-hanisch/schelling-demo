"""Verdikte (reine Funktionen: Art und Text) und Formatierung: jede Zahl im Text kommt aus der Rechnung, Grenzfälle und leere Eingaben."""

import math

import pytest

import sch_constants as C
import sch_evaluation as ev


def _an(**kw):
    return ev.analyse(ev.Settings(**kw))


def test_formatting_helpers_use_comma_and_typographic_minus():
    assert ev.de(1.234, 2) == "1,23" and ev.de(-0.5, 1) == "−0,5" and ev.de(-0.0004, 2) == "0,00" and ev.de(-0.004, 2) == "0,00" and ev.de(float("nan")) == "–" and ev.de(None) == "–"
    assert ev.pct(0.714) == "71" and ev.pct(0.0714, 1) == "7,1"
    assert ev.tp(0.3) == "30 %" and ev.tp(0.375) == "37,5 %" and ev.tp(0.25) == "25 %" and ev.tp(1.0) == "100 %" and ev.tp(0.0) == "0 %" and ev.tp(0.67) == "67 %"


def test_main_verdict_done_blocked_and_the_all_happy_case():
    done = ev.verdict_main(_an())
    assert done[0] == "success" and done[1].startswith("Nach 166 Umzügen (166 Schritten) sind alle 810 Betriebe zufrieden. Der Anteil gleichartiger Nachbarn geht von 50 % auf 71 %")
    blocked = ev.verdict_main(_an(tau=70))
    assert blocked[0] == "warning" and "blockiert" in blocked[1] and "keiner findet eine freie Fläche, auf der er zufrieden wäre" in blocked[1] and "„Auf eine beliebige freie Fläche“ würden sie dennoch weiterziehen" in blocked[1]
    anyrule = ev.verdict_main(_an(tau=70, rule=C.R_ANY))
    assert anyrule[0] == "success" and "Nach 4251 Umzügen (4251 Schritten)" in anyrule[1] and "auf 99 %" in anyrule[1]
    happy = ev.verdict_main(_an(tau=0))
    assert happy == ("info", "Alle 810 Betriebe sind von Anfang an zufrieden: bei Schwelle 0 % zieht keiner um.")


def test_main_verdict_without_a_free_cell_says_so():
    an = _an(l=10, rho=100, tau=60)
    assert an.free == 0 and an.status == C.ST_BLOCKED
    kind, text = ev.verdict_main(an)
    assert kind == "warning" and "es gibt keine freie Fläche" in text and "dennoch weiterziehen" not in text                                      # ohne freie Fläche hilft auch die andere Regel nicht


def test_main_verdict_at_the_cap_names_the_step_limit(monkeypatch):
    monkeypatch.setattr(C, "MAX_STEPS", 5)
    an = _an(tau=70, rule=C.R_ANY)
    kind, text = ev.verdict_main(an)
    assert an.status == C.ST_CAP and kind == "warning" and text.startswith("Nach 5 Schritten (Obergrenze,") and "unzufrieden" in text


def test_main_verdict_kind_is_info_when_the_gain_is_small():
    an = _an(tau=10)
    kind, text = ev.verdict_main(an)
    assert an.status == C.ST_DONE and an.s1 - an.s0 < 0.2 and kind == "info"


def _tau_rows(done_by_rule):
    rows = []
    for rule, dones in done_by_rule.items():
        for tau, d in zip((0.1, 0.3, 0.6, 0.8), dones):
            rows.append({"rule": rule, "tau": tau, "s0": 0.5, "s1": 0.5 + tau / 2, "done": d, "blocked": 1 - d, "cap": 0.0, "steps": 10.0, "moves": 9.0, "unhappy": 1 - d, "runs": 5})
    return rows


def test_tau_verdict_names_the_first_thresholds_without_full_and_without_any_ending():
    rows = _tau_rows({C.R_HAPPY: (1, 1, 0.8, 0.0), C.R_ANY: (1, 1, 1, 1)})
    kind, text = ev.verdict_tau(rows)
    assert kind == "info" and "„Nur auf eine zufriedenstellende Fläche“: Entmischungsindex 50 % → 65 % bei τ = 30 %; nicht mehr jeder Lauf endet zufrieden ab τ = 60 %, keiner ab τ = 80 %" in text
    assert "„Auf eine beliebige freie Fläche“: Entmischungsindex 50 % → 65 % bei τ = 30 %; jeder Lauf endet zufrieden" in text and text.count("keiner ab") == 1
    assert ev.verdict_tau([]) == ("warning", "Keine Läufe.")
    same = ev.verdict_tau(_tau_rows({C.R_ANY: (1, 1, 1, 0.0)}))[1]
    assert "ab τ = 80 % endet kein Lauf mehr zufrieden" in same and "nicht mehr jeder" not in same


def test_first_tau_and_tau_cell_pick_the_right_rows():
    rows = _tau_rows({C.R_HAPPY: (1, 1, 0.8, 0.0)})
    assert ev.first_tau(rows, C.R_HAPPY, lambda r: r["done"] < 1.0) == 0.6 and ev.first_tau(rows, C.R_ANY, lambda r: True) is None
    assert ev.tau_cell(rows, C.R_HAPPY, 0.3)["s1"] == pytest.approx(0.65)
    with pytest.raises(StopIteration):
        ev.tau_cell(rows, C.R_HAPPY, 0.99)


def _space_res(done_equal=True):
    vac = [{"rho": rho, "s1": 0.85 - 0.2 * (rho - 0.5), "done": 1.0 if rho < 0.95 else 0.6, "blocked": 0.0 if rho < 0.95 else 0.4, "steps": 100.0, "unhappy": 0.0, "runs": 5} for rho in (0.5, 0.9, 0.98)]
    rad = [{"radius": k, "tau": t, "s1": 0.7 if k == 1 else 0.6, "done": 1.0 if done_equal or k == 1 else 0.6, "blocked": 0.0, "unhappy": 0.0, "runs": 5} for k in (1, 2) for t in (0.3, 0.6)]
    return {"vacancy": vac, "radius": rad, "tau": 0.375}


def test_space_verdict_reports_vacancy_and_radius_and_both_radius_endings():
    kind, text = ev.verdict_space(_space_res())
    assert kind == "info" and text.startswith("Bei τ = 37,5 % und 98 % belegten Flächen liegt der Entmischungsindex am Ende bei 75 %, bei 50 % belegt bei 85 %") and "bei 98 % belegt enden 60 % der Läufe zufrieden und 40 % blockieren" in text
    assert text.endswith("Radius 2 statt 1: bei τ = 30 % 60 % statt 70 %; in beiden Fällen enden bei jeder gemessenen Schwelle alle Läufe zufrieden.")
    assert "bei τ = 30 % enden 60 % statt 100 % der Läufe zufrieden" in ev.verdict_space(_space_res(done_equal=False))[1] or "bei τ = 60 % enden 60 % statt 100 % der Läufe zufrieden" in ev.verdict_space(_space_res(done_equal=False))[1]
    assert ev.verdict_space({}) == ("warning", "Keine Läufe.") and ev.verdict_space({"vacancy": [], "radius": [1]}) == ("warning", "Keine Läufe.")


def test_space_verdict_with_unequal_but_not_all_full_endings():
    res = _space_res()
    for r in res["radius"]:
        if r["radius"] == 2 and r["tau"] == 0.6:
            r["done"] = 1.0
        if r["radius"] == 1 and r["tau"] == 0.6:
            r["done"] = 1.0
    res["radius"][0]["done"] = 0.8       # Radius 1, τ = 0,3: nicht alle Läufe; Radius 2 gleich überall 1,0
    res["radius"][2]["done"] = 0.8
    assert "der Anteil zufriedener Enden ist bei beiden Radien gleich" in ev.verdict_space(res)[1]


def test_exact_verdict_names_blocked_states_and_both_rules():
    rows = [
        {"grid": "3 × 3 (3 A, 3 B)", "rule": C.R_HAPPY, "tau": 0.75, "states": 1680, "done": 4, "blocked": 892, "p_done": 0.1314, "steps": 1.35, "sim_p_done": 0.127, "sim_steps": 1.4, "sim_se": 0.05, "runs": 2000},
        {"grid": "3 × 3 (3 A, 3 B)", "rule": C.R_ANY, "tau": 0.75, "states": 1680, "done": 4, "blocked": 0, "p_done": 1.0, "steps": 182.4, "sim_p_done": 1.0, "sim_steps": 181.8, "sim_se": 4.1, "runs": 2000},
    ]
    kind, text = ev.verdict_exact(rows)
    assert kind == "info" and "alle 1680 Belegungen, exakt) sind bei τ = 75 % 892 Belegungen blockiert" in text and "endet nur 13,1 % der Starts zufrieden (Simulation: 12,7 %)" in text
    assert "„Auf eine beliebige freie Fläche“ 100,0 % nach im Mittel 182,4 Schritten (Simulation: 181,8 ± 4,1)" in text
    assert ev.verdict_exact([]) == ("warning", "Keine Rechnung.")
    only_one = ev.verdict_exact(rows[:1])
    assert only_one == ("info", "Auf dem Gitter 3 × 3 (3 A, 3 B) wurden 1 Fälle exakt gerechnet.")


def _bridge_rows():
    rows = []
    for sp, s in ((C.T_GRID, 0.88), (C.T_RANDOM, 0.72), (C.T_COMMUNITIES, 0.84)):
        for tau in (0.3, 0.5):
            rows.append({"space": sp, "tau": tau, "s0": 0.5, "s1": s, "q1": 0.3, "e1": 0.8, "unhappy": 0.0, "done": 1.0, "nmi": 0.3 if sp == C.T_COMMUNITIES else float("nan"), "moves": 90.0, "runs": 5})
    return rows


def test_bridge_verdict_lists_the_spaces_and_the_nmi_and_the_identity_gap():
    kind, text = ev.verdict_bridge(_bridge_rows())
    assert kind == "info" and text.startswith("Bei τ = 50 % liegt der Entmischungsindex am Ende im Gitter bei 88 %, im Zufallsnetz bei 72 %, im Netz „Verbünde“ bei 84 %; die Typen stimmen mit den Verbünden zu NMI 0,30 überein.")
    assert text.endswith("Die Modularität der Typen-Partition liegt höchstens 0,000 neben dem Anteil gleichartiger Kanten minus ½.")
    assert ev.verdict_bridge([]) == ("warning", "Keine Läufe.")
    no_comm = [r for r in _bridge_rows() if r["space"] != C.T_COMMUNITIES]
    assert "NMI" not in ev.verdict_bridge(no_comm)[1]


def test_nan_inputs_never_leak_into_the_text():
    for text in (ev.verdict_bridge(_bridge_rows())[1], ev.verdict_main(_an(raum=C.T_COMMUNITIES, rho=85, tau=50))[1]):
        assert "nan" not in text.lower()
    assert not math.isnan(_an(raum=C.T_COMMUNITIES, rho=85, tau=50).nmi1) and math.isnan(_an().nmi1)
