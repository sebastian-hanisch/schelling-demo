"""Gemeinsame Fixtures und Hilfen (DEMO-PLAYBOOK §1b): Mini-Instanzen, an denen jede Einheit von Hand geprüft wird."""

import os
import sys
from pathlib import Path

for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):    # vor dem ersten Import von numpy (siehe sch_algorithm.py)
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402
import pytest  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sch_algorithm as A  # noqa: E402


def random_nbrs(rng, n, extra=None):
    """Zufälliges zusammenhängendes Netz als Nachbartabelle: Baum plus `extra` Zusatzkanten."""
    pairs = {(i, int(rng.integers(i))) for i in range(1, n)}
    for _ in range(n if extra is None else extra):
        i, j = sorted(rng.choice(n, size=2, replace=False).tolist())
        pairs.add((i, j))
    sets = [set() for _ in range(n)]
    for i, j in pairs:
        sets[i].add(j)
        sets[j].add(i)
    return A.adj_neighbors(sets)


@pytest.fixture
def line3():
    """Zeile mit drei Flächen (Radius 1): Nachbarn 0: (1), 1: (0, 2), 2: (1)."""
    return A.grid_neighbors(1, 3, 1)


@pytest.fixture
def square2():
    """Gitter 2 × 2: jede Fläche ist Nachbar jeder anderen."""
    return A.grid_neighbors(2, 2, 1)


@pytest.fixture
def rng():
    return np.random.default_rng(7)
