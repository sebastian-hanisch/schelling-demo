"""Räume: Gitter (Nachbarzahlen, Symmetrie), Netze (gültig, deterministisch auch über Prozesse), Positionen, Verbünde."""

import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

import sch_algorithm as A
import sch_constants as C
import sch_evaluation as ev
import sch_scenario as S

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("radius,corner,edge,inner", [(1, 3, 5, 8), (2, 8, 14, 24)])
def test_grid_neighbour_counts_corner_edge_inner(radius, corner, edge, inner):
    nbrs = A.grid_neighbors(10, 10, radius)
    sizes = [len(nb) for nb in nbrs]
    assert len(nbrs[0]) == corner and len(nbrs[5]) == edge and len(nbrs[5 * 10 + 5]) == inner
    assert max(sizes) == inner and min(sizes) == corner


@pytest.mark.parametrize("radius", [1, 2])
def test_grid_neighbours_are_symmetric_and_exclude_the_cell_itself(radius):
    nbrs = A.grid_neighbors(7, 9, radius)
    for a, nb in enumerate(nbrs):
        assert a not in nb and len(set(nb)) == len(nb)
        for b in nb:
            assert a in nbrs[b]


def test_build_space_grid_has_shape_positions_and_no_labels_or_edges():
    sp = ev.build_space(C.T_GRID, 12, 99, 99, 1, 3)
    assert sp.n_cells == 144 and sp.shape == (12, 12) and sp.labels is None and sp.edges == () and len(sp.pos) == 144
    assert [tuple(p) for p in sp.positions[:3]] == [(0, 0), (0, 1), (0, 2)] and len(sp.positions) == 144
    for x, y in sp.pos:
        assert 0 < x < 1 and 0 < y < 1
    assert ev.build_space(C.T_GRID, 12, 99, 99, 2, 3).nbrs != sp.nbrs


@pytest.mark.parametrize("typ", C.NET_TYPES)
@pytest.mark.parametrize("n,c", [(C.N_MIN, C.C_MIN), (C.N_MIN, C.C_MAX), (C.DEFAULT_N, C.DEFAULT_C), (C.N_MAX, C.C_MAX)])
def test_every_corner_gives_a_valid_network_space(typ, n, c):
    sp = ev.build_space(typ, 10, n, c, 1, 35)
    assert sp.n_cells == n and sp.positions is None and sp.shape is None and len(sp.pos) == n
    for x, y in sp.pos:
        assert math.isfinite(x) and math.isfinite(y) and -1e-9 <= x <= 1 + 1e-9 and -1e-9 <= y <= 1 + 1e-9
    for a, nb in enumerate(sp.nbrs):
        assert a not in nb and len(set(nb)) == len(nb)
        for b in nb:
            assert a in sp.nbrs[b]
    assert len(sp.edges) == sum(len(nb) for nb in sp.nbrs) // 2 and all(i < j for i, j in sp.edges)


def test_only_the_community_network_has_labels_with_equal_blocks():
    for typ in C.NET_TYPES:
        sp = ev.build_space(typ, 10, 240, 8, 1, 35)
        if typ == C.T_COMMUNITIES:
            assert sorted(set(int(v) for v in sp.labels)) == list(range(C.BLOCKS)) and len(sp.labels) == 240
        else:
            assert sp.labels is None


def test_networks_are_deterministic_per_seed_and_differ_between_seeds():
    a = ev.build_space(C.T_COMMUNITIES, 10, 80, 6, 1, 5)
    assert a.nbrs == ev.build_space(C.T_COMMUNITIES, 10, 80, 6, 1, 5).nbrs and a.pos == ev.build_space(C.T_COMMUNITIES, 10, 80, 6, 1, 5).pos
    assert ev.build_space(C.T_COMMUNITIES, 10, 80, 6, 1, 6).nbrs != a.nbrs


def test_layout_false_skips_the_force_layout_and_unknown_space_raises():
    inst = S.make_instance(C.T_RANDOM, 60, 4, 1, layout=False)
    assert set(inst.pos) == {(0.5, 0.5)}
    for bad in ("gibt es nicht", C.T_GRID):
        with pytest.raises(ValueError):
            S.make_instance(bad, 60, 4, 1)
    with pytest.raises(ValueError):
        ev.build_space("gibt es nicht", 10, 60, 4, 1, 1)


def test_the_run_is_independent_of_the_hash_seed_of_the_process():
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import hashlib, sch_constants as C, sch_evaluation as E;"
            "h = hashlib.sha256();"
            "[h.update(repr((lambda a: (a.types0, a.run['steps'], a.run['moves'], a.run['types'], a.status))(E.analyse(E.Settings(sp, 12, 60, 5, 85, 40, rule, 1, 7)))).encode()) for sp in C.ALL_SPACES for rule in C.RULES];"
            "print(h.hexdigest())")
    outs = []
    for hashseed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hashseed)
        outs.append(subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", code, str(ROOT)], capture_output=True, text=True, env=env, check=True).stdout.strip())
    assert outs[0] == outs[1] and len(outs[0]) == 64
