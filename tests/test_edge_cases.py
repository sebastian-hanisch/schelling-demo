"""Randfälle der Auswertung: Grenzen aller Regler, ohne freie Fläche, Schwelle 0 und 100, Regel „nächste“ im Netz, Seeds, Messreihen mit kleinen Läufen."""

import dataclasses

import pytest

import sch_algorithm as A
import sch_constants as C
import sch_evaluation as ev


def _an(**kw):
    return ev.analyse(ev.Settings(**kw))


@pytest.mark.parametrize("rule", C.RULES)
@pytest.mark.parametrize("radius", [1, 2])
@pytest.mark.parametrize("rho,tau", [(C.RHO_MIN, C.TAU_MIN), (C.RHO_MIN, 100), (100, C.TAU_MIN), (100, 100), (C.RHO_MAX, 50), (C.RHO_MIN, 50)])
def test_smallest_grid_with_every_corner_of_density_and_threshold(rule, radius, rho, tau):
    an = _an(l=C.L_MIN, rho=rho, tau=tau, rule=rule, radius=radius)
    assert an.status in (C.ST_DONE, C.ST_BLOCKED, C.ST_CAP) and an.run["moves"] <= an.run["steps"]
    kind, text = ev.verdict_main(an)
    assert kind in ("success", "info", "warning") and text
    assert an.run["types"].count(1) == an.types0.count(1) and an.run["types"].count(2) == an.types0.count(2)


def test_threshold_zero_means_nobody_moves_and_threshold_one_hundred_is_the_strictest():
    zero = _an(tau=0)
    assert zero.unhappy0 == 0.0 and zero.status == C.ST_DONE and zero.run["steps"] == 0 and zero.run["types"] == zero.types0
    hundred = _an(l=10, tau=100)
    assert hundred.unhappy0 > 0.5                                                                           # nur ein Betrieb ohne Nachbarn oder mit lauter gleichartigen ist zufrieden
    assert hundred.status in (C.ST_DONE, C.ST_BLOCKED)


def test_a_full_grid_has_no_free_cell_and_is_blocked_for_every_rule_with_unhappy_agents():
    for rule in C.RULES:
        an = _an(l=10, rho=100, tau=60, rule=rule)
        assert an.free == 0 and an.status == C.ST_BLOCKED and an.run["moves"] == 0 and an.run["unhappy"] == an.unhappy0


def test_the_nearest_rule_is_replaced_by_the_happy_rule_in_a_network_but_kept_in_the_grid():
    net = _an(raum=C.T_RING, rule=C.R_NEAR)
    assert net.rule == C.R_HAPPY and net.run == _an(raum=C.T_RING, rule=C.R_HAPPY).run
    grid = _an(l=12, rule=C.R_NEAR)
    assert grid.rule == C.R_NEAR


def test_seeds_zero_and_maximum_run_and_differ():
    a, b = _an(l=12, seed=0), _an(l=12, seed=C.SEED_MAX)
    assert a.status == b.status == C.ST_DONE and a.types0 != b.types0


def test_the_same_settings_give_the_same_run_and_other_seeds_other_runs():
    base = ev.Settings(l=12)
    assert ev.analyse(base).run == ev.analyse(base).run
    assert ev.analyse(dataclasses.replace(base, seed=36)).run != ev.analyse(base).run


def test_the_start_distribution_is_the_same_for_every_rule_and_threshold():
    base = ev.Settings(l=12)
    starts = {(rule, tau): ev.analyse(dataclasses.replace(base, rule=rule, tau=tau)).types0 for rule in C.RULES for tau in (10, 50, 90)}
    assert len({tuple(v) for v in starts.values()}) == 1                                                    # Start hängt nur an Seed, Raum und ρ: Vergleiche zwischen Regeln sind Vergleiche am selben Start


def test_unhappy_share_at_the_start_and_end_are_shares_of_the_agents():
    an = _an(tau=70)
    assert 0.0 <= an.unhappy0 <= 1.0 and 0.0 <= an.run["unhappy"] <= 1.0
    assert an.unhappy0 == pytest.approx(len(A.unhappy_cells(an.types0, an.tau, an.space.nbrs)) / an.agents)


def test_the_network_runs_report_nmi_only_for_the_community_network():
    for typ in C.NET_TYPES:
        an = _an(raum=typ, rho=85, tau=50)
        assert (an.nmi1 == an.nmi1) == (typ == C.T_COMMUNITIES), typ


def test_measurement_rows_with_one_run_and_tiny_grids_are_well_formed():
    rows = ev.tau_rows(8, 0.9, 1, taus=(0.3, 0.8), rules=(C.R_HAPPY, C.R_ANY), runs=1, max_steps=2000)
    assert len(rows) == 4 and all(r["runs"] == 1 and abs(r["done"] + r["blocked"] + r["cap"] - 1.0) < 1e-12 for r in rows)
    res = ev.space_rows(8, 0.375, 1, rhos=(0.5, 0.98), runs=1, taus=(0.3, 0.6), max_steps=2000)
    assert [r["rho"] for r in res["vacancy"]] == [0.5, 0.98] and {(r["radius"], r["tau"]) for r in res["radius"]} == {(1, 0.3), (1, 0.6), (2, 0.3), (2, 0.6)}
    bridge = ev.bridge_rows(8, spaces=(C.T_GRID, C.T_COMMUNITIES), taus=(0.5,), runs=1, n=60, c=6, max_steps=2000)
    assert [r["space"] for r in bridge] == [C.T_GRID, C.T_COMMUNITIES] and bridge[0]["nmi"] != bridge[0]["nmi"] and 0 <= bridge[1]["nmi"] <= 1


def test_exact_rows_on_a_tiny_grid_agree_between_chain_and_simulation():
    rows = ev.exact_rows(grids=((2, 3, 2, 2),), taus=(0.5,), rules=(C.R_HAPPY, C.R_ANY), sim_runs=300)
    assert [r["grid"] for r in rows] == ["2 × 3 (2 A, 2 B)"] * 2
    for r in rows:
        assert r["states"] == 90 and abs(r["sim_p_done"] - r["p_done"]) < 0.1


def test_grid_label_names_the_cells_and_agents():
    assert ev.grid_label(3, 4, 2, 2) == "3 × 4 (2 A, 2 B)"
