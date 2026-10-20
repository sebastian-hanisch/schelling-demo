"""Orakel-Tests (ORACLE-PLAYBOOK): der Kern wird gegen unabhängige Rechenwege geprüft, nicht gegen sich selbst.

* Maße: Entmischungsindex, Anteil gleichartiger Kanten, Modularität, Cluster und NMI gegen Schleifenfassungen, `networkx` (Modularität, Zusammenhangskomponenten) und die Kontingenztafel (NMI) auf über 100 Belegungen.
* Zufriedenheit: gegen den Vergleich mit einem Bruch (ganzzahlig, ohne Toleranz).
* Kette: gegen eine unabhängig geschriebene Potenziteration der Übergänge auf 2 × 3 Flächen, und gegen die Simulation (Band über Standardfehler).
* Eigenschaften: Erhaltung der Betriebszahlen, Züge nur auf freie Flächen, Endstatus passt zur Definition.
"""

import math
from fractions import Fraction

import networkx as nx
import numpy as np
import pytest
from networkx.algorithms.community import modularity as nx_modularity

import sch_algorithm as A
from conftest import random_nbrs

NETS = 110


def _cases(count=NETS, seed=41):
    rng = np.random.default_rng(seed)
    for _ in range(count):
        n = int(rng.integers(6, 40))
        nbrs = random_nbrs(rng, n, extra=int(rng.integers(0, 2 * n)))
        types = A.initial_types(n, float(rng.choice([0.6, 0.8, 0.95])), 0.5, rng)
        yield rng, nbrs, types


def _graph(types, nbrs):
    g = nx.Graph()
    g.add_nodes_from(c for c, t in enumerate(types) if t)
    for c, t in enumerate(types):
        if t:
            g.add_edges_from((c, q) for q in nbrs[c] if types[q])
    return g


def test_similarity_edge_share_and_modularity_equal_the_loop_versions_and_networkx():
    checked = 0
    for _, nbrs, types in _cases():
        g = _graph(types, nbrs)
        if g.number_of_edges() == 0:
            continue
        per_agent = []
        for c, t in enumerate(types):
            if t:
                nb = [q for q in nbrs[c] if types[q]]
                if nb:
                    per_agent.append(sum(1 for q in nb if types[q] == t) / len(nb))
        assert A.similarity(types, nbrs) == pytest.approx(sum(per_agent) / len(per_agent), abs=1e-12)
        e_in = sum(1 for u, v in g.edges if types[u] == types[v]) / g.number_of_edges()
        assert A.edge_share(types, nbrs) == pytest.approx(e_in, abs=1e-12)
        parts = [{c for c in g.nodes if types[c] == k} for k in (1, 2)]
        parts = [p for p in parts if p]
        assert A.modularity(types, nbrs) == pytest.approx(nx_modularity(g, parts), abs=1e-10)
        d = [sum(dict(g.degree(p)).values()) for p in parts]
        assert A.modularity(types, nbrs) == pytest.approx(e_in - sum((x / (2 * g.number_of_edges())) ** 2 for x in d), abs=1e-12)               # Q = Anteil gleichartiger Kanten − Σ (D / 2m)²
        checked += 1
    assert checked >= 100


def test_clusters_equal_the_connected_components_of_the_same_type_subgraphs():
    for _, nbrs, types in _cases(count=60, seed=42):
        g = nx.Graph()
        g.add_nodes_from(c for c, t in enumerate(types) if t)
        for c, t in enumerate(types):
            g.add_edges_from((c, q) for q in nbrs[c] if types[q] == t and t)
        comps = list(nx.connected_components(g))
        count, largest = A.clusters(types, nbrs)
        assert count == len(comps) and largest == pytest.approx(max(len(x) for x in comps) / sum(1 for t in types if t))


def test_nmi_equals_the_contingency_table_formula():
    rng = np.random.default_rng(43)
    for _ in range(60):
        n = int(rng.integers(8, 60))
        types = A.initial_types(n, 0.9, 0.5, rng)
        labels = rng.integers(0, 4, size=n)
        cells = [c for c, t in enumerate(types) if t]
        a = np.array([types[c] for c in cells])
        b = labels[cells]
        table = np.zeros((a.max() + 1, b.max() + 1))
        for x, y in zip(a, b):
            table[x, y] += 1
        p = table / table.sum()
        pa, pb = p.sum(axis=1), p.sum(axis=0)
        mi = sum(p[i, j] * np.log(p[i, j] / (pa[i] * pb[j])) for i in range(p.shape[0]) for j in range(p.shape[1]) if p[i, j] > 0)
        ha = -sum(x * np.log(x) for x in pa if x > 0)
        hb = -sum(x * np.log(x) for x in pb if x > 0)
        expected = 1.0 if ha + hb == 0 else mi / ((ha + hb) / 2)
        assert A.nmi(types, labels) == pytest.approx(expected, abs=1e-12)


def test_happiness_equals_the_exact_fraction_comparison():
    for rng, nbrs, types in _cases(count=60, seed=44):
        tau = Fraction(int(rng.integers(0, 101)), 100)
        for c, t in enumerate(types):
            if not t:
                continue
            occ = [types[q] for q in nbrs[c] if types[q]]
            same = sum(1 for v in occ if v == t)
            expected = len(occ) == 0 or Fraction(same, len(occ)) >= tau
            assert A.is_happy(types, c, float(tau), nbrs) == expected


def _brute_chain(rows, cols, na, nb, tau, rule):
    """Unabhängige Fassung: Übergänge als Wörterbuch, Verteilung per Potenziteration (P(DONE) und erwartete Schritte aus der Überlebensmasse)."""
    n_cells = rows * cols
    nbrs = []
    for i in range(rows):
        for j in range(cols):
            nbrs.append([a * cols + b for a in range(rows) for b in range(cols) if (a, b) != (i, j) and abs(a - i) <= 1 and abs(b - j) <= 1])
    states = A.enumerate_states(n_cells, na, nb)

    def happy(t, c, tt=None):
        occ = [t[q] for q in nbrs[c] if t[q]]
        return not occ or sum(1 for v in occ if v == t[c]) >= tau * len(occ) - 1e-12

    out = {}
    for s in states:
        unh = [c for c in range(n_cells) if s[c] and not happy(s, c)]
        if not unh:
            out[s] = ("done", {})
            continue
        free = [c for c in range(n_cells) if not s[c]]
        moves, anyone = {}, False
        for a in unh:
            cands = []
            for e in free:
                nxt = list(s)
                nxt[e], nxt[a] = s[a], 0
                if rule == A.ANY or happy(nxt, e):
                    cands.append(tuple(nxt))
            if not cands:
                moves[s] = moves.get(s, 0.0) + 1.0 / len(unh)
            else:
                anyone = True
                for nxt in cands:
                    moves[nxt] = moves.get(nxt, 0.0) + 1.0 / (len(unh) * len(cands))
        out[s] = ("run", moves) if anyone else ("blocked", {})
    dist = {s: 1.0 / len(states) for s in states}
    expected_steps, done, alive = 0.0, 0.0, 0.0
    for _ in range(4000):
        nxt = {}
        alive = 0.0
        for s, mass in dist.items():
            kind, moves = out[s]
            if kind == "run":
                alive += mass
                for t, p in moves.items():
                    nxt[t] = nxt.get(t, 0.0) + mass * p
            elif kind == "done":
                done += mass
        expected_steps += alive
        dist = nxt
    return len(states), sum(1 for k, _ in out.values() if k == "done"), sum(1 for k, _ in out.values() if k == "blocked"), done, expected_steps, alive


@pytest.mark.parametrize("rule", [A.HAPPY, A.ANY])
@pytest.mark.parametrize("tau", [0.0, 0.34, 0.5, 0.67, 0.75])
def test_exact_chain_equals_an_independent_power_iteration_on_a_two_by_three_grid(rule, tau):
    res = A.exact_analysis(2, 3, 2, 2, tau, rule)
    n, done, blocked, p_done, steps, alive = _brute_chain(2, 3, 2, 2, tau, rule)
    assert (res["states"], res["done"], res["blocked"]) == (n, done, blocked) and res["p_done"] == pytest.approx(p_done, abs=1e-6)
    if res["blocked"] == 0 and res["p_done"] > 1 - 1e-9:
        assert res["steps"] == pytest.approx(steps, rel=1e-6)


def test_the_simulation_matches_the_exact_chain_within_the_band():
    for rule in (A.HAPPY, A.ANY):
        for tau in (0.34, 0.6):
            res = A.exact_analysis(3, 3, 3, 3, tau, rule)
            nbrs = A.grid_neighbors(3, 3, 1)
            runs = [A.simulate(nbrs, A.initial_types(9, 6 / 9, 0.5, np.random.default_rng([tau == 0.6, rule == A.ANY, i])), tau, rule, np.random.default_rng([i, 5]), 100_000) for i in range(3000)]
            done = np.array([r["status"] == A.DONE for r in runs], dtype=float)
            assert done.mean() == pytest.approx(res["p_done"], abs=4.5 * (res["p_done"] * (1 - res["p_done"]) / len(runs)) ** 0.5 + 1e-3), (rule, tau)
            if res["blocked"] == 0:
                steps = np.array([r["steps"] for r in runs], dtype=float)
                assert steps.mean() == pytest.approx(res["steps"], abs=4.5 * steps.std() / len(runs) ** 0.5), (rule, tau)


def test_end_status_matches_its_definition_and_counts_are_kept():
    for rng, nbrs, types in _cases(count=40, seed=45):
        tau = float(rng.choice([0.3, 0.5, 0.7]))
        rule = A.HAPPY if rng.random() < 0.5 else A.ANY
        out = A.simulate(nbrs, types, tau, rule, rng, 4000)
        end = out["types"]
        assert [end.count(k) for k in (0, 1, 2)] == [types.count(k) for k in (0, 1, 2)]
        unh = A.unhappy_cells(end, tau, nbrs)
        if out["status"] == A.DONE:
            assert unh == [] and out["unhappy"] == 0.0
        elif out["status"] == A.BLOCKED:
            free = [c for c, t in enumerate(end) if not t]
            assert unh and all(not any(A.happy_if_moved(end, a, e, tau, nbrs) for e in free) for a in unh) and (rule == A.HAPPY or not free)      # „beliebig“ blockiert nur ohne freie Fläche
        else:
            assert out["steps"] == 4000 and unh
        assert out["moves"] <= out["steps"]


@pytest.mark.parametrize("na,nb,rule,tau", [(1, 2, A.ANY, 0.5), (1, 2, A.ANY, 0.34), (1, 2, A.HAPPY, 0.5), (2, 2, A.ANY, 0.5)])
def test_exact_chain_with_cycles_that_never_end_equals_the_power_iteration(na, nb, rule, tau):
    """Bei Regel „beliebig“ gibt es Kreise ohne Ausgang: ein Teil der Masse bleibt für immer im Kreis (erwartete Schritte unendlich), P(zufrieden) ist nur der Teil, der ausläuft."""
    res = A.exact_analysis(2, 3, na, nb, tau, rule)
    n, done, blocked, p_done, steps, alive = _brute_chain(2, 3, na, nb, tau, rule)
    assert (res["states"], res["done"], res["blocked"]) == (n, done, blocked) and res["p_done"] == pytest.approx(p_done, abs=1e-6)
    assert math.isinf(res["steps"]) == (alive > 1e-6)
