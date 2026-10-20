"""Kern: Schelling-Segregation mit zwei Betriebstypen auf einem Gitter oder einem Netz (Python, numpy für Zufall und die exakte Kette).

Flächen sind die Zellen des Gitters (beschränkt, 8 Nachbarn bei Radius 1) oder die Knoten eines Netzes; jede Fläche ist leer (0) oder von einem Betrieb des Typs 1 oder 2 belegt. Ein Betrieb ist zufrieden, wenn der
Anteil gleichartiger unter seinen belegten Nachbarn mindestens τ ist (ohne Nachbarn ist er zufrieden). In jedem Schritt wird ein zufälliger unzufriedener Betrieb gewählt und zieht nach der Zugregel auf eine freie Fläche:
„zufrieden“ (zufällige freie Fläche, auf der er zufrieden wäre; gibt es keine, bleibt er), „beliebig“ (zufällige freie Fläche), „nächste“ (nächstgelegene zufriedenstellende freie Fläche, nur im Gitter).

Zufall nur über `numpy.random.default_rng(Seed)` in Blöcken fester Größe (`BATCH`); der Strom hängt von Seed, Regel und Lauf ab, nicht von der Plattform."""

import itertools
import math
import os

# Dichte Kette bis etwa 3 000 Zustände: ein BLAS-Thread genügt. Mehrere Threads machen kleine Lösungen auf ausgelasteten Rechnern hundertfach langsamer.
for _var in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np

TOL = 1e-12               # Toleranz beim Vergleich der Anteile mit der Schwelle (Anteile sind Brüche mit kleinem Nenner)
BATCH = 2048              # Zufallszahlen je Block; legt den Strom fest (die Messreihen hängen daran: nicht ändern, ohne sie neu zu rechnen)
HAPPY, ANY, NEAR = "zufrieden", "beliebig", "nächste"
RULES = (HAPPY, ANY, NEAR)
DONE, BLOCKED, CAP = "zufrieden", "blockiert", "Obergrenze"
EXACT_LIMIT = 4000        # Obergrenze der Zustandszahl der exakten Kette (dichte Rechnung)

# --- Flächen ---------------------------------------------------------------------------------------------------------------------------------------


def grid_neighbors(rows, cols, radius=1):
    """Nachbartabelle des beschränkten Gitters (Flächen zeilenweise nummeriert): alle Flächen mit Abstand höchstens `radius` im Maximumsabstand, ohne die Fläche selbst."""
    out = []
    for i in range(rows):
        for j in range(cols):
            out.append(tuple(a * cols + b for a in range(max(0, i - radius), min(rows, i + radius + 1)) for b in range(max(0, j - radius), min(cols, j + radius + 1)) if (a, b) != (i, j)))
    return tuple(out)


def grid_positions(rows, cols):
    return tuple((i, j) for i in range(rows) for j in range(cols))


def adj_neighbors(adj):
    """Nachbartabelle eines Netzes aus Nachbarlisten."""
    return tuple(tuple(sorted(a)) for a in adj)


def initial_types(n_cells, rho, frac, rng):
    """Zufällige Belegung: round(ρ · n) Flächen belegt, davon round(frac · Betriebe) mit Typ 1, der Rest Typ 2; Reihenfolge und Flächen zufällig."""
    agents = int(round(rho * n_cells))
    n1 = int(round(frac * agents))
    types = [0] * n_cells
    for k, c in enumerate(rng.permutation(n_cells)[:agents].tolist()):
        types[c] = 1 if k < n1 else 2
    return types


# --- Zufriedenheit und Maße ----------------------------------------------------------------------------------------------------------------------


def is_happy(types, cell, tau, nbrs):
    """Zufrieden: kein belegter Nachbar oder Anteil gleichartiger Nachbarn ≥ τ."""
    typ = types[cell]
    occ = same = 0
    for q in nbrs[cell]:
        tq = types[q]
        if tq:
            occ += 1
            if tq == typ:
                same += 1
    return occ == 0 or same >= tau * occ - TOL


def happy_if_moved(types, origin, dest, tau, nbrs):
    """Wäre der Betrieb auf `origin` auf der freien Fläche `dest` zufrieden? (Die Fläche `origin` ist dann leer.)"""
    typ = types[origin]
    occ = same = 0
    for q in nbrs[dest]:
        if q == origin:
            continue
        tq = types[q]
        if tq:
            occ += 1
            if tq == typ:
                same += 1
    return occ == 0 or same >= tau * occ - TOL


def unhappy_cells(types, tau, nbrs):
    return [c for c, t in enumerate(types) if t and not is_happy(types, c, tau, nbrs)]


def similarity(types, nbrs):
    """Entmischungsindex: Mittel über alle Betriebe mit mindestens einem Nachbarn vom Anteil gleichartiger Nachbarn (NaN ohne solche Betriebe)."""
    vals = []
    for c, typ in enumerate(types):
        if not typ:
            continue
        occ = same = 0
        for q in nbrs[c]:
            if types[q]:
                occ += 1
                if types[q] == typ:
                    same += 1
        if occ:
            vals.append(same / occ)
    return float(np.mean(vals)) if vals else float("nan")


def _edge_counts(types, nbrs):
    """(Zahl der Kanten zwischen Betrieben, davon gleichartige, Gradsumme je Typ 1 und 2) im Nachbarschaftsnetz der belegten Flächen."""
    m = same = 0
    degree = [0, 0, 0]
    for c, typ in enumerate(types):
        if not typ:
            continue
        for q in nbrs[c]:
            if types[q]:
                degree[typ] += 1
                if q > c:
                    m += 1
                    same += types[q] == typ
    return m, same, degree[1], degree[2]


def edge_share(types, nbrs):
    """Anteil der Kanten zwischen Betrieben, die zwei gleichartige verbinden (NaN ohne Kanten)."""
    m, same, _, _ = _edge_counts(types, nbrs)
    return same / m if m else float("nan")


def modularity(types, nbrs):
    """Modularität der Typen-Partition im Nachbarschaftsnetz der belegten Flächen: Anteil gleichartiger Kanten minus Σ (D_k / 2m)² mit der Gradsumme D_k des Typs k (NaN ohne Kanten)."""
    m, same, d1, d2 = _edge_counts(types, nbrs)
    return same / m - (d1 / (2.0 * m)) ** 2 - (d2 / (2.0 * m)) ** 2 if m else float("nan")


def clusters(types, nbrs):
    """(Zahl der zusammenhängenden Gruppen gleichartiger Betriebe, Anteil der Betriebe in der größten)."""
    seen = set()
    sizes = []
    for c, typ in enumerate(types):
        if typ and c not in seen:
            comp = [c]
            seen.add(c)
            for x in comp:
                for q in nbrs[x]:
                    if types[q] == typ and q not in seen:
                        seen.add(q)
                        comp.append(q)
            sizes.append(len(comp))
    agents = sum(1 for t in types if t)
    return (len(sizes), max(sizes) / agents) if sizes else (0, float("nan"))


def nmi(types, labels):
    """Normierte gegenseitige Information (Mittel der Entropien im Nenner) zwischen den Typen der Betriebe und vorgegebenen Gruppen der Flächen (1 = gleiche Aufteilung, 0 = unabhängig)."""
    cells = [c for c, t in enumerate(types) if t]
    n = len(cells)
    if n == 0:
        return float("nan")
    joint = {}
    for c in cells:
        key = (types[c], int(labels[c]))
        joint[key] = joint.get(key, 0) + 1
    pa, pb = {}, {}
    for (a, b), k in joint.items():
        pa[a] = pa.get(a, 0) + k
        pb[b] = pb.get(b, 0) + k
    mi = sum(k / n * math.log(k * n / (pa[a] * pb[b])) for (a, b), k in joint.items())
    ha = -sum(k / n * math.log(k / n) for k in pa.values())
    hb = -sum(k / n * math.log(k / n) for k in pb.values())
    return 1.0 if ha + hb == 0 else mi / ((ha + hb) / 2.0)


# --- Lauf ----------------------------------------------------------------------------------------------------------------------------------------------


class _RandomSet:
    """Menge mit Zufallszugriff in O(1)."""

    def __init__(self):
        self.items, self.pos = [], {}

    def add(self, x):
        if x not in self.pos:
            self.pos[x] = len(self.items)
            self.items.append(x)

    def discard(self, x):
        if x in self.pos:
            i = self.pos.pop(x)
            last = self.items.pop()
            if i < len(self.items):
                self.items[i] = last
                self.pos[last] = i

    def __len__(self):
        return len(self.items)


def frame_schedule(max_steps, frames):
    """Schritte, deren Zustände aufgehoben werden: 0, 1, 2, … und danach geometrisch bis `max_steps` (höchstens etwa `frames` Stück)."""
    steps = {0, 1}
    steps |= {int(round(v)) for v in np.geomspace(1, max(1, max_steps), frames)}
    return sorted(s for s in steps if 0 <= s <= max_steps)


def simulate(nbrs, types0, tau, rule, rng, max_steps, positions=None, frames=None):
    """Ein Lauf bis alle zufrieden sind, nichts mehr geht oder `max_steps` erreicht sind. Ein Schritt ist der Versuch, einen zufälligen unzufriedenen Betrieb umzusetzen (bei fehlender zulässiger Fläche bleibt er).
    Rückgabe: status (DONE, BLOCKED, CAP), steps, moves (tatsächliche Umzüge), types (Endzustand), unhappy (Anteil unzufriedener Betriebe am Ende), frames (Schritt -> Belegung für die Schritte aus `frames` und den letzten),
    history (Liste (Schritt, Entmischungsindex, Anteil Unzufriedener) zu denselben Schritten)."""
    if rule not in RULES:
        raise ValueError(f"unbekannte Regel: {rule}")
    if rule == NEAR and positions is None:
        raise ValueError("die Regel „nächste“ braucht Positionen (nur im Gitter)")
    t = list(types0)
    agents = sum(1 for v in t if v)
    empties, unh = _RandomSet(), _RandomSet()
    for c, v in enumerate(t):
        if not v:
            empties.add(c)
    for c in unhappy_cells(t, tau, nbrs):
        unh.add(c)
    wanted = set(frames or ())
    kept, hist = {}, []

    def snap(step):
        kept[step] = t.copy()
        hist.append((step, similarity(t, nbrs), len(unh) / agents if agents else 0.0))

    steps = moves = 0
    if 0 in wanted:
        snap(0)
    failed = set()
    status = CAP
    idx = BATCH
    buf = None
    while True:
        if len(unh) == 0:
            status = DONE
            break
        if steps >= max_steps:
            break
        if idx >= BATCH:
            buf = rng.random((2, BATCH)).tolist()
            idx = 0
        u1, u2 = buf[0][idx], buf[1][idx]
        idx += 1
        a = unh.items[int(u1 * len(unh))]
        steps += 1
        if rule == ANY:
            cand = empties.items
        else:
            cand = [e for e in empties.items if happy_if_moved(t, a, e, tau, nbrs)]
            if cand and rule == NEAR:
                ai, aj = positions[a]
                dist = [max(abs(positions[e][0] - ai), abs(positions[e][1] - aj)) for e in cand]
                dmin = min(dist)
                cand = [e for e, d in zip(cand, dist) if d == dmin]
        if not cand:
            failed.add(a)
            if len(failed) == len(unh):
                if steps in wanted:
                    snap(steps)
                status = BLOCKED
                break
        else:
            b = cand[int(u2 * len(cand))]
            t[b], t[a] = t[a], 0
            empties.discard(b)
            empties.add(a)
            moves += 1
            failed.clear()
            for c in set(nbrs[a]) | set(nbrs[b]) | {a, b}:
                if t[c] and not is_happy(t, c, tau, nbrs):
                    unh.add(c)
                else:
                    unh.discard(c)
        if steps in wanted:
            snap(steps)
    if steps not in kept:
        snap(steps)
    return {"status": status, "steps": steps, "moves": moves, "types": t, "unhappy": len(unh) / agents if agents else 0.0, "frames": kept, "history": hist}



# --- Exakte Kette ----------------------------------------------------------------------------------------------------------------------------------


def enumerate_states(n_cells, na, nb):
    """Alle Belegungen mit na Betrieben des Typs 1 und nb des Typs 2 (Reihenfolge fest)."""
    out = []
    for first in itertools.combinations(range(n_cells), na):
        rest = [c for c in range(n_cells) if c not in first]
        for second in itertools.combinations(rest, nb):
            t = [0] * n_cells
            for c in first:
                t[c] = 1
            for c in second:
                t[c] = 2
            out.append(tuple(t))
    return out


def exact_analysis(rows, cols, na, nb, tau, rule, radius=1):
    """Absorbierende Markov-Kette über alle Belegungen eines kleinen Gitters (Zustände: alle zufrieden = DONE, kein Unzufriedener hat eine zulässige Fläche = BLOCKED; beide absorbierend). Ein Schritt wählt einen
    zufälligen Unzufriedenen und setzt ihn nach der Regel um; gibt es keine zulässige Fläche, bleibt der Zustand (Schleife). Rückgabe: Zahl der Zustände, der zufriedenen, der blockierten, P(DONE) und erwartete Schritte
    bis zur Absorption, jeweils als Mittel über den gleichverteilten Start (erwartete Schritte unendlich, wenn irgendein Start nicht sicher absorbiert wird)."""
    if rule == NEAR:
        raise ValueError("die exakte Kette kennt die Regeln „zufrieden“ und „beliebig“")
    n_cells = rows * cols
    nbrs = grid_neighbors(rows, cols, radius)
    states = enumerate_states(n_cells, na, nb)
    if len(states) > EXACT_LIMIT:
        raise ValueError(f"exakte Kette nur bis {EXACT_LIMIT} Zustände")
    index = {s: k for k, s in enumerate(states)}
    kind = {}
    trans = {}
    for s in states:
        unh = unhappy_cells(s, tau, nbrs)
        if not unh:
            kind[s] = DONE
            continue
        empt = [c for c in range(n_cells) if not s[c]]
        moves = {}
        blocked = True
        for a in unh:
            cand = empt if rule == ANY else [e for e in empt if happy_if_moved(s, a, e, tau, nbrs)]
            if not cand:
                moves[s] = moves.get(s, 0.0) + 1.0 / len(unh)
                continue
            blocked = False
            for e in cand:
                nxt = list(s)
                nxt[e], nxt[a] = nxt[a], 0
                nxt = tuple(nxt)
                moves[nxt] = moves.get(nxt, 0.0) + 1.0 / (len(unh) * len(cand))
        if blocked:
            kind[s] = BLOCKED
        else:
            trans[s] = moves
    inner = [s for s in states if s in trans]
    p_done = np.zeros(len(states))
    steps = np.zeros(len(states))
    for s in states:
        if kind.get(s) == DONE:
            p_done[index[s]] = 1.0
    if inner:
        pos = {s: k for k, s in enumerate(inner)}
        q = np.zeros((len(inner), len(inner)))
        r = np.zeros(len(inner))
        reach = [set() for _ in inner]                           # Vorgänger je Zustand (für die Erreichbarkeit rückwärts)
        for s in inner:
            for nxt, p in trans[s].items():
                if nxt in pos:
                    q[pos[s], pos[nxt]] += p
                    if nxt != s:
                        reach[pos[nxt]].add(pos[s])
                elif kind[nxt] == DONE:
                    r[pos[s]] += p
        absorbing = [pos[s] for s in inner if any((nxt not in pos) for nxt in trans[s])]
        can_absorb = _backward(reach, absorbing)
        stuck = [k for k in range(len(inner)) if k not in can_absorb]
        leaky = _backward(reach, stuck) if stuck else set()
        keep = [k for k in range(len(inner)) if k in can_absorb]
        if keep:
            qk = q[np.ix_(keep, keep)]
            sol = np.linalg.solve(np.eye(len(keep)) - qk, r[keep])
            for k, v in zip(keep, sol):
                p_done[index[inner[k]]] = v
            safe = [k for k in keep if k not in leaky]
            if safe:
                qs = q[np.ix_(safe, safe)]
                tsol = np.linalg.solve(np.eye(len(safe)) - qs, np.ones(len(safe)))
                for k, v in zip(safe, tsol):
                    steps[index[inner[k]]] = v
        for k in range(len(inner)):
            if k not in can_absorb or k in leaky:
                steps[index[inner[k]]] = float("inf")
    return {"states": len(states), "done": sum(1 for s in states if kind.get(s) == DONE), "blocked": sum(1 for s in states if kind.get(s) == BLOCKED),
            "p_done": float(np.mean(p_done)), "steps": float(np.mean(steps))}


def _backward(preds, targets):
    """Alle Zustände, von denen aus ein Zustand aus `targets` erreichbar ist (Rückwärtssuche; die Ziele gehören dazu)."""
    seen = set(targets)
    stack = list(targets)
    while stack:
        x = stack.pop()
        for p in preds[x]:
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen
