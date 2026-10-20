"""Einheiten des Kerns an Mini-Instanzen mit von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import math

import numpy as np
import pytest

import sch_algorithm as A

# --- Flächen ------------------------------------------------------------------------------------------------------------------------------------


def test_grid_neighbors_radius_one_and_two_with_borders():
    nb = A.grid_neighbors(3, 3, 1)
    assert nb[4] == (0, 1, 2, 3, 5, 6, 7, 8) and nb[0] == (1, 3, 4) and nb[1] == (0, 2, 3, 4, 5) and nb[8] == (4, 5, 7)
    assert A.grid_neighbors(1, 3, 1) == ((1,), (0, 2), (1,)) and A.grid_neighbors(1, 1, 1) == ((),)
    big = A.grid_neighbors(5, 5, 2)
    assert len(big[12]) == 24 and len(big[0]) == 8 and 6 in big[0] and 12 in big[0] and 13 not in big[0]
    assert A.grid_positions(2, 3) == ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2))


def test_adj_neighbors_sorts_and_initial_types_counts():
    assert A.adj_neighbors([{2, 1}, {0}, {0}]) == ((1, 2), (0,), (0,))
    types = A.initial_types(100, 0.9, 0.5, np.random.default_rng(3))
    assert len(types) == 100 and types.count(0) == 10 and types.count(1) == 45 and types.count(2) == 45
    assert A.initial_types(100, 0.9, 0.5, np.random.default_rng(3)) == types and A.initial_types(100, 0.9, 0.5, np.random.default_rng(4)) != types
    assert A.initial_types(10, 1.0, 0.3, np.random.default_rng(1)).count(1) == 3 and A.initial_types(10, 0.0, 0.5, np.random.default_rng(1)) == [0] * 10


# --- Zufriedenheit und Maße ---------------------------------------------------------------------------------------------------------------------


def test_happiness_by_hand(line3):
    assert A.is_happy([1, 2, 1], 1, 0.5, line3) is False and A.is_happy([1, 1, 2], 1, 0.5, line3) is True           # Mitte: 0 von 2 gleich, bzw. 1 von 2 gleich (Gleichheit zählt)
    assert A.is_happy([1, 2, 0], 0, 0.5, line3) is False and A.is_happy([1, 0, 2], 0, 0.5, line3) is True            # ohne Nachbarn zufrieden
    assert A.is_happy([1, 1, 2], 1, 0.0, line3) is True and A.is_happy([1, 2, 1], 1, 1.0, line3) is False
    assert A.is_happy([1, 1, 2], 1, 0.5000001, line3) is False                                                       # knapp über dem Anteil 1 / 2
    assert A.unhappy_cells([1, 2, 1], 0.5, line3) == [0, 1, 2] and A.unhappy_cells([1, 1, 2], 0.5, line3) == [2]


def test_happy_if_moved_ignores_the_origin(line3):
    assert A.happy_if_moved([1, 2, 0], 0, 2, 0.5, line3) is False                                                    # Ziel 2 hat Nachbar 1 (Typ 2): 0 von 1 gleich
    assert A.happy_if_moved([2, 0, 1], 0, 1, 0.5, line3) is False                                                    # Ziel 1: Nachbar 0 ist der Ursprung (leer), Nachbar 2 ist Typ 1: ungleich
    assert A.happy_if_moved([1, 0, 0], 0, 1, 0.5, line3) is True                                                     # Ziel 1 hat nur den Ursprung als Nachbarn: keiner, also zufrieden
    assert A.happy_if_moved([1, 1, 0], 0, 2, 0.5, line3) is True                                                     # Ziel 2: Nachbar 1 gleich


def test_similarity_edge_share_and_modularity_by_hand(square2):
    t = [1, 1, 2, 2]
    assert A.similarity(t, square2) == pytest.approx(1 / 3) and A.edge_share(t, square2) == pytest.approx(1 / 3) and A.modularity(t, square2) == pytest.approx(1 / 3 - 1 / 2)   # K4, 2 von 6 Kanten gleichartig
    line4 = A.grid_neighbors(1, 4, 1)
    t = [1, 1, 2, 2]
    assert A.similarity(t, line4) == pytest.approx(0.75) and A.edge_share(t, line4) == pytest.approx(2 / 3) and A.modularity(t, line4) == pytest.approx(2 / 3 - 1 / 2)           # Q = 1/6
    mixed = [1, 2, 1, 2]
    assert A.similarity(mixed, line4) == 0.0 and A.modularity(mixed, line4) == pytest.approx(0.0 - 0.5)
    assert math.isnan(A.similarity([1, 0, 0, 0], line4)) and math.isnan(A.edge_share([1, 0, 2, 0], line4)) and math.isnan(A.modularity([0, 0, 0, 0], line4))


def test_clusters_and_nmi_by_hand():
    line6 = A.grid_neighbors(1, 6, 1)
    assert A.clusters([1, 1, 2, 2, 1, 0], line6) == (3, 0.4) and A.clusters([1, 0, 1, 0, 2, 0], line6) == (3, 1 / 3) and A.clusters([0] * 6, line6)[0] == 0
    assert A.nmi([1, 1, 2, 2], [0, 0, 1, 1]) == pytest.approx(1.0) and A.nmi([1, 2, 1, 2], [0, 0, 1, 1]) == pytest.approx(0.0, abs=1e-12)
    assert A.nmi([1, 1, 2, 0], [0, 0, 1, 9]) == pytest.approx(1.0) and math.isnan(A.nmi([0, 0], [0, 1])) and A.nmi([1, 1, 1], [0, 1, 2]) == pytest.approx(0.0)


# --- Lauf ---------------------------------------------------------------------------------------------------------------------------------------


def test_simulate_the_three_cell_line_ends_with_the_stable_states(line3):
    for rule in (A.HAPPY, A.ANY):
        for seed in range(20):
            out = A.simulate(line3, [1, 2, 0], 0.5, rule, np.random.default_rng(seed), 1000)
            assert out["status"] == A.DONE and out["types"] in ([1, 0, 2], [2, 0, 1]) and out["unhappy"] == 0.0 and out["moves"] >= 1 and out["steps"] >= out["moves"]


def test_simulate_without_unhappy_agents_stops_at_once(line3):
    out = A.simulate(line3, [1, 1, 2], 0.0, A.HAPPY, np.random.default_rng(1), 100)
    assert out["status"] == A.DONE and out["steps"] == 0 and out["moves"] == 0 and out["types"] == [1, 1, 2] and out["frames"] == {0: [1, 1, 2]} and out["history"][0][0] == 0


def test_simulate_blocked_and_step_limit():
    full = A.grid_neighbors(2, 2, 1)
    out = A.simulate(full, [1, 2, 2, 1], 0.9, A.HAPPY, np.random.default_rng(1), 100)                              # keine freie Fläche: sofort blockiert
    assert out["status"] == A.BLOCKED and out["moves"] == 0 and out["unhappy"] == 1.0
    out = A.simulate(full, [1, 2, 2, 1], 0.9, A.ANY, np.random.default_rng(1), 100)                                # auch „beliebig“ findet keine Fläche
    assert out["status"] == A.BLOCKED
    nb = A.grid_neighbors(6, 6, 1)
    types = A.initial_types(36, 0.8, 0.5, np.random.default_rng(2))
    capped = A.simulate(nb, types, 0.8, A.ANY, np.random.default_rng(3), 7)
    assert capped["status"] == A.CAP and capped["steps"] == 7 and capped["unhappy"] > 0.0


def test_simulate_keeps_the_numbers_of_each_type_and_only_moves_to_free_cells():
    nb = A.grid_neighbors(5, 5, 1)
    types = A.initial_types(25, 0.8, 0.5, np.random.default_rng(5))
    out = A.simulate(nb, types, 0.5, A.HAPPY, np.random.default_rng(6), 5000, frames=list(range(0, 400)))
    seq = [out["frames"][k] for k in sorted(out["frames"])]
    assert seq[0] == types
    for before, after in zip(seq, seq[1:]):
        changed = [c for c in range(25) if before[c] != after[c]]
        assert changed == [] or (len(changed) == 2 and sorted((before[changed[0]], before[changed[1]])) == [0, after[changed[0]] or after[changed[1]]])     # ein Betrieb wandert auf eine freie Fläche
        assert [after.count(k) for k in (0, 1, 2)] == [types.count(k) for k in (0, 1, 2)]


def test_simulate_is_deterministic_per_seed_and_the_history_matches_the_frames(line3):
    nb = A.grid_neighbors(5, 5, 1)
    types = A.initial_types(25, 0.8, 0.5, np.random.default_rng(5))
    one = A.simulate(nb, types, 0.4, A.HAPPY, np.random.default_rng(9), 5000, frames=[0, 5, 50])
    two = A.simulate(nb, types, 0.4, A.HAPPY, np.random.default_rng(9), 5000, frames=[0, 5, 50])
    assert one["steps"] == two["steps"] and one["types"] == two["types"] and one["history"] == two["history"]
    for step, s, u in one["history"]:
        t = one["frames"][step]
        assert s == pytest.approx(A.similarity(t, nb), nan_ok=True) and u == pytest.approx(len(A.unhappy_cells(t, 0.4, nb)) / sum(1 for v in t if v))
    assert set(one["frames"]) <= {0, 5, 50, one["steps"]} and 0 in one["frames"]


def test_nearest_rule_needs_positions_and_unknown_rule_raises(line3):
    with pytest.raises(ValueError):
        A.simulate(line3, [1, 2, 0], 0.5, A.NEAR, np.random.default_rng(1), 10)
    with pytest.raises(ValueError):
        A.simulate(line3, [1, 2, 0], 0.5, "gibt es nicht", np.random.default_rng(1), 10)
    nb = A.grid_neighbors(1, 7, 1)
    out = A.simulate(nb, [1, 2, 1, 2, 0, 0, 0], 0.5, A.NEAR, np.random.default_rng(4), 2000, positions=A.grid_positions(1, 7))
    assert out["status"] in (A.DONE, A.BLOCKED)


def test_nearest_rule_moves_to_the_closest_satisfying_cell():
    nb = A.grid_neighbors(1, 6, 1)
    t0 = [1, 2, 0, 0, 0, 2]                                          # bei τ = 1 sind Betrieb 0 und 1 unzufrieden, Betrieb 5 hat keinen Nachbarn
    seen = set()
    for seed in range(30):
        out = A.simulate(nb, t0, 1.0, A.NEAR, np.random.default_rng(seed), 1, positions=A.grid_positions(1, 6), frames=[1])
        seen.add(tuple(out["frames"][1]))
    assert seen == {(0, 2, 0, 1, 0, 2), (1, 0, 2, 0, 0, 2)}                                                         # Betrieb 0 auf Fläche 3 (Fläche 2 und 4 enttäuschen), Betrieb 1 auf die nächste Fläche 2


def test_frame_schedule_is_sorted_unique_and_bounded():
    sched = A.frame_schedule(5000, 120)
    assert sched == sorted(set(sched)) and sched[0] == 0 and sched[1] == 1 and sched[-1] == 5000 and len(sched) <= 125
    assert A.frame_schedule(0, 10) == [0] and A.frame_schedule(3, 120) == [0, 1, 2, 3]


# --- Exakte Kette ----------------------------------------------------------------------------------------------------------------------------------


def test_exact_chain_of_the_three_cell_line_by_hand():
    for rule in (A.HAPPY, A.ANY):
        res = A.exact_analysis(1, 3, 1, 1, 0.5, rule)
        assert res["states"] == 6 and res["done"] == 2 and res["blocked"] == 0 and res["p_done"] == pytest.approx(1.0) and res["steps"] == pytest.approx(8 / 6)


def test_exact_chain_counts_blocked_and_done_states_on_the_three_by_three_grid():
    happy = A.exact_analysis(3, 3, 3, 3, 0.67, A.HAPPY)
    assert (happy["states"], happy["done"], happy["blocked"]) == (1680, 4, 892) and 0.1 < happy["p_done"] < 0.2 and happy["steps"] == pytest.approx(1.35, abs=0.01)
    anyr = A.exact_analysis(3, 3, 3, 3, 0.67, A.ANY)
    assert (anyr["done"], anyr["blocked"]) == (4, 0) and anyr["p_done"] == pytest.approx(1.0) and anyr["steps"] == pytest.approx(182.4, abs=0.1)
    easy = A.exact_analysis(3, 3, 3, 3, 0.25, A.HAPPY)
    assert easy["blocked"] == 0 and easy["done"] == 488 and easy["p_done"] == pytest.approx(1.0)


def test_exact_chain_limits_and_errors():
    with pytest.raises(ValueError):
        A.exact_analysis(1, 3, 1, 1, 0.5, A.NEAR)
    with pytest.raises(ValueError):
        A.exact_analysis(4, 4, 5, 5, 0.5, A.HAPPY)                                                                   # zu viele Zustände
    trivial = A.exact_analysis(1, 2, 1, 1, 0.0, A.HAPPY)
    assert trivial["done"] == trivial["states"] == 2 and trivial["p_done"] == 1.0 and trivial["steps"] == 0.0         # τ = 0: alle zufrieden
    assert len(A.enumerate_states(4, 1, 2)) == 12 and all(s.count(1) == 1 and s.count(2) == 2 for s in A.enumerate_states(4, 1, 2))


def test_exact_limit_is_inclusive(monkeypatch):
    states = len(A.enumerate_states(4, 1, 2))
    monkeypatch.setattr(A, "EXACT_LIMIT", states)
    assert A.exact_analysis(1, 4, 1, 2, 0.5, A.HAPPY)["states"] == states                 # genau am Limit: erlaubt
    monkeypatch.setattr(A, "EXACT_LIMIT", states - 1)
    with pytest.raises(ValueError):
        A.exact_analysis(1, 4, 1, 2, 0.5, A.HAPPY)


def test_exact_chain_with_closed_classes_that_never_absorb():
    """Regel „beliebig“ kann in Zyklen laufen, die nie enden: dann ist die erwartete Zahl der Schritte unendlich, und P(zufrieden) zählt nur die Starts, die sicher enden (von Hand: 1 × 4 mit A, B, B, zwei Kreise)."""
    res = A.exact_analysis(1, 4, 1, 2, 0.5, A.ANY)
    assert (res["states"], res["done"], res["blocked"]) == (12, 2, 0) and res["p_done"] == pytest.approx(10 / 12) and math.isinf(res["steps"])
    everywhere = A.exact_analysis(2, 2, 1, 1, 0.5, A.ANY)                                    # 2 × 2: nie alle zufrieden, jeder Zustand läuft ewig weiter
    assert (everywhere["states"], everywhere["done"], everywhere["blocked"]) == (12, 0, 0) and everywhere["p_done"] == 0.0 and math.isinf(everywhere["steps"])


def test_nmi_of_two_constant_labelings_is_one_and_never_nan():
    types = [1, 1, 1, 0, 1]
    assert A.nmi(types, [0, 0, 0, 0, 0]) == 1.0
    assert A.nmi(types, [3, 3, 3, 3, 3]) == 1.0


def test_nearest_rule_always_picks_a_closest_satisfying_cell_on_random_grids():
    rng = np.random.default_rng(11)
    nbrs = A.grid_neighbors(4, 5, 1)
    pos = A.grid_positions(4, 5)
    checked = 0
    for _ in range(300):
        types = A.initial_types(20, 0.7, 0.5, rng)
        out = A.simulate(nbrs, types, 0.5, A.NEAR, np.random.default_rng(int(rng.integers(10**6))), 1, positions=pos)
        if out["moves"] != 1:
            continue
        end = out["types"]
        origin = next(c for c in range(20) if types[c] and not end[c])
        dest = next(c for c in range(20) if not types[c] and end[c])
        happy = [e for e in range(20) if not types[e] and A.happy_if_moved(types, origin, e, 0.5, nbrs)]
        dist = lambda e: max(abs(pos[e][0] - pos[origin][0]), abs(pos[e][1] - pos[origin][1]))
        assert dest in happy and dist(dest) == min(dist(e) for e in happy)
        checked += 1
    assert checked >= 100
