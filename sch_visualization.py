"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import numpy as np
import plotly.graph_objects as go

import sch_algorithm as A
import sch_constants as C
from sch_evaluation import pct, tp

MAX_EDGES = 3000          # größere Netze werden ohne Kanten gezeichnet


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340, bottom=10):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=bottom), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _type_name(t):
    return {0: "frei", 1: "Typ A (Kühlfracht)", 2: "Typ B (Trockenfracht)"}[int(t)]


def build_state(an, step, dark=False):
    """Gebiet im gewählten Schritt: Farbe = Typ (Typ A grün, Typ B orange, frei grau); unzufriedene Betriebe tragen einen Ring (schwarz im hellen, weiß im dunklen Design)."""
    sp = an.space
    types = an.run["frames"][step]
    unh = set(A.unhappy_cells(types, an.tau, sp.nbrs))
    ring = "white" if dark else "black"
    if sp.shape is not None:
        rows, cols = sp.shape
        z = np.array(types, dtype=float).reshape(rows, cols)
        text = [[f"Zeile {i + 1}, Spalte {j + 1}: {_type_name(types[i * cols + j])}" + (", unzufrieden" if i * cols + j in unh else "") for j in range(cols)] for i in range(rows)]
        scale = [[0.0, C.COLOR_EMPTY_SOLID], [0.5, C.COLOR_A], [1.0, C.COLOR_B]]
        fig = go.Figure(go.Heatmap(z=z, zmin=0, zmax=2, colorscale=scale, showscale=False, xgap=1 if cols <= 30 else 0, ygap=1 if rows <= 30 else 0, text=text, hoverinfo="text"))
        if unh:
            ys, xs = zip(*[divmod(c, cols) for c in sorted(unh)])
            fig.add_trace(go.Scatter(x=list(xs), y=list(ys), mode="markers", marker=dict(size=max(3, 200 // max(rows, cols)), color="rgba(0,0,0,0)", line=dict(color=ring, width=1)),
                                     name="unzufrieden", hoverinfo="skip", showlegend=False))
        fig.update_xaxes(visible=False, range=[-0.5, cols - 0.5], constrain="domain")
        fig.update_yaxes(visible=False, range=[rows - 0.5, -0.5], scaleanchor="x", scaleratio=1, constrain="domain")
        fig.update_layout(height=470, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
        return lock_axes(fig)
    pos = sp.pos
    fig = go.Figure()
    if len(sp.edges) <= MAX_EDGES:
        xs, ys = [], []
        for i, j in sp.edges:
            xs += [pos[i][0], pos[j][0], None]
            ys += [pos[i][1], pos[j][1], None]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=C.COLOR_EDGE, width=0.7), hoverinfo="skip", showlegend=False))
    size = 7 if sp.n_cells > 150 else 10
    colors = [C.COLOR_EMPTY_SOLID if t == 0 else (C.COLOR_A if t == 1 else C.COLOR_B) for t in types]
    fig.add_trace(go.Scatter(x=[p[0] for p in pos], y=[p[1] for p in pos], mode="markers", showlegend=False,
                             marker=dict(size=size, color=colors, line=dict(color=[ring if c in unh else "rgba(40,40,40,0.35)" for c in range(sp.n_cells)], width=[2.0 if c in unh else 0.4 for c in range(sp.n_cells)])),
                             hovertext=[f"Fläche {c}: {_type_name(t)}" + (", unzufrieden" if c in unh else "") for c, t in enumerate(types)], hoverinfo="text"))
    fig.update_xaxes(visible=False, autorange=True)
    fig.update_yaxes(visible=False, autorange=True, scaleanchor="x", scaleratio=1)
    fig.update_layout(height=470, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_history(an, step):
    """Entmischungsindex und Anteil Unzufriedener über die Schritte (logarithmisch ab 1); senkrechte Linie = gewählter Schritt."""
    hist = an.run["history"]
    xs = [h[0] + 1 for h in hist]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[100.0 * h[1] for h in hist], mode="lines", line=dict(color=C.COLOR_A, width=3), name="Entmischungsindex",
                             hovertemplate="Schritt %{x}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100.0 * h[2] for h in hist], mode="lines", line=dict(color=C.COLOR_B, width=3, dash="dot"), name="Anteil Unzufriedener",
                             hovertemplate="Schritt %{x}: %{y:.1f} %<extra></extra>"))
    fig.add_vline(x=step + 1, line=dict(color="rgba(120,120,120,0.9)", width=1.5, dash="dot"))
    fig.update_xaxes(title_text="Schritt + 1 (logarithmisch)", type="log")
    fig.update_yaxes(title_text="Prozent", range=[0, 102], ticksuffix=" %")
    return _base(fig, height=320, bottom=60)


def _tick_taus(rows):
    taus = sorted({r["tau"] for r in rows})
    return dict(tickvals=taus, ticktext=[tp(t).replace(" %", "") for t in taus], tickangle=-45)


def build_tau_similarity(rows):
    """Entmischungsindex am Ende über τ, je Zugregel; gestrichelt der Anfangswert."""
    fig = go.Figure()
    for rule in dict.fromkeys(r["rule"] for r in rows):
        mine = sorted((r for r in rows if r["rule"] == rule), key=lambda r: r["tau"])
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[100.0 * r["s1"] for r in mine], mode="lines+markers", name=C.RULE_LABEL[rule], line=dict(color=C.RULE_COLORS[rule], width=3),
                                 hovertemplate="τ = %{x}: %{y:.1f} %<extra></extra>"))
    first = sorted((r for r in rows), key=lambda r: r["tau"])
    base = float(np.mean([r["s0"] for r in first]))
    fig.add_hline(y=100.0 * base, line=dict(color="rgba(120,120,120,0.9)", dash="dash", width=1.5), annotation_text="Anfangswert", annotation_position="bottom right")
    fig.update_xaxes(title_text="Toleranzschwelle τ (%)", **_tick_taus(rows))
    fig.update_yaxes(title_text="Entmischungsindex am Ende", range=[40, 102], ticksuffix=" %")
    return _base(fig, height=340, bottom=110)


def build_tau_status(rows):
    """Anteil der Läufe, die mit allen zufrieden enden, über τ, je Zugregel."""
    fig = go.Figure()
    for rule in dict.fromkeys(r["rule"] for r in rows):
        mine = sorted((r for r in rows if r["rule"] == rule), key=lambda r: r["tau"])
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[100.0 * r["done"] for r in mine], mode="lines+markers", name=C.RULE_LABEL[rule],
                                 line=dict(color=C.RULE_COLORS[rule], width=3, shape="hv"), hovertemplate="τ = %{x}: %{y:.0f} % enden zufrieden<extra></extra>"))
    fig.update_xaxes(title_text="Toleranzschwelle τ (%)", **_tick_taus(rows))
    fig.update_yaxes(title_text="Läufe mit allen zufrieden", range=[-3, 103], ticksuffix=" %")
    return _base(fig, height=320, bottom=100)


def build_vacancy(res):
    """Entmischungsindex am Ende und Anteil der Läufe mit allen zufrieden über den belegten Anteil."""
    rows = sorted(res["vacancy"], key=lambda r: r["rho"])
    xs = [100.0 * r["rho"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[100.0 * r["s1"] for r in rows], mode="lines+markers", name="Entmischungsindex am Ende", line=dict(color=C.COLOR_A, width=3), hovertemplate="%{x:.0f} % belegt: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100.0 * r["done"] for r in rows], mode="lines+markers", name="Läufe mit allen zufrieden", line=dict(color=C.COLOR_B, width=3, dash="dot"), hovertemplate="%{x:.0f} % belegt: %{y:.0f} %<extra></extra>"))
    fig.update_xaxes(title_text="Belegter Anteil der Flächen", ticksuffix=" %", tickvals=xs)
    fig.update_yaxes(title_text="Prozent", range=[0, 103], ticksuffix=" %")
    return _base(fig, height=320, bottom=70)


def build_radius(res):
    """Entmischungsindex am Ende über τ, Radius 1 gegen Radius 2."""
    rows = res["radius"]
    fig = go.Figure()
    for radius, color in ((1, C.COLOR_A), (2, C.COLOR_B)):
        mine = sorted((r for r in rows if r["radius"] == radius), key=lambda r: r["tau"])
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[100.0 * r["s1"] for r in mine], mode="lines+markers", name=f"Radius {radius} ({8 if radius == 1 else 24} Nachbarn)", line=dict(color=color, width=3),
                                 hovertemplate="τ = %{x}: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Toleranzschwelle τ (%)", **_tick_taus(rows))
    fig.update_yaxes(title_text="Entmischungsindex am Ende", range=[40, 102], ticksuffix=" %")
    return _base(fig, height=320, bottom=70)


def build_exact(rows, grid):
    """Wahrscheinlichkeit, dass der Lauf zufrieden endet (Linie: exakt, Rauten: Simulation), über τ, je Regel, für ein Gitter."""
    fig = go.Figure()
    for rule in dict.fromkeys(r["rule"] for r in rows):
        mine = sorted((r for r in rows if r["rule"] == rule and r["grid"] == grid), key=lambda r: r["tau"])
        if not mine:
            continue
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[100.0 * r["p_done"] for r in mine], mode="lines", name=f"{C.RULE_LABEL[rule]} (exakt)", line=dict(color=C.RULE_COLORS[rule], width=3),
                                 hovertemplate="τ = %{x}: %{y:.1f} %<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[100.0 * r["sim_p_done"] for r in mine], mode="markers", name=f"{C.RULE_LABEL[rule]} (Simulation)",
                                 marker=dict(symbol="diamond", size=10, color=C.RULE_COLORS[rule], line=dict(width=1.5, color="white")), hovertemplate="τ = %{x}: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Toleranzschwelle τ (%)", **_tick_taus(rows))
    fig.update_yaxes(title_text="Starts, die zufrieden enden", range=[-3, 103], ticksuffix=" %")
    return _base(fig, height=340, bottom=130)


def build_exact_steps(rows, grid):
    """Erwartete Schritte bis zum Ende (logarithmisch), nur wo jeder Start zufrieden endet; Rauten: Simulation."""
    fig = go.Figure()
    for rule in dict.fromkeys(r["rule"] for r in rows):
        mine = sorted((r for r in rows if r["rule"] == rule and r["grid"] == grid and r["blocked"] == 0 and r["p_done"] > 1 - 1e-9 and not math.isinf(r["steps"])), key=lambda r: r["tau"])
        if not mine:
            continue
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[r["steps"] for r in mine], mode="lines", name=f"{C.RULE_LABEL[rule]} (exakt)", line=dict(color=C.RULE_COLORS[rule], width=3),
                                 hovertemplate="τ = %{x}: %{y:.2f} Schritte<extra></extra>"))
        fig.add_trace(go.Scatter(x=[r["tau"] for r in mine], y=[r["sim_steps"] for r in mine], mode="markers", name=f"{C.RULE_LABEL[rule]} (Simulation)",
                                 marker=dict(symbol="diamond", size=10, color=C.RULE_COLORS[rule], line=dict(width=1.5, color="white")), hovertemplate="τ = %{x}: %{y:.2f} Schritte<extra></extra>"))
    fig.update_xaxes(title_text="Toleranzschwelle τ (%)", **_tick_taus(rows))
    fig.update_yaxes(title_text="Erwartete Schritte (logarithmisch)", type="log")
    return _base(fig, height=340, bottom=130)


def build_bridge_similarity(rows):
    """Entmischungsindex am Ende je Raum und Schwelle (Balken); gestrichelt der Anfangswert."""
    fig = go.Figure()
    taus = sorted({r["tau"] for r in rows})
    spaces = list(dict.fromkeys(r["space"] for r in rows))
    for k, tau in enumerate(taus):
        mine = [next(r for r in rows if r["space"] == sp and r["tau"] == tau) for sp in spaces]
        fig.add_trace(go.Bar(x=spaces, y=[100.0 * r["s1"] for r in mine], name=f"τ = {tp(tau)}", marker_color=["#2F6B65", "#c4623b", "#6b5b95", "#9d755d"][k % 4],
                             text=[f"{pct(r['s1'])} %" for r in mine], textposition="outside"))
    fig.add_hline(y=100.0 * float(np.mean([r["s0"] for r in rows])), line=dict(color="rgba(120,120,120,0.9)", dash="dash", width=1.5))
    fig.update_layout(barmode="group")
    fig.update_xaxes(tickangle=-15)
    fig.update_yaxes(title_text="Entmischungsindex am Ende", range=[0, 110], ticksuffix=" %")
    return _base(fig, height=340, bottom=90)


def build_bridge_identity(rows):
    """Modularität der Typen-Partition gegen Anteil gleichartiger Kanten − ½: die Punkte liegen auf der Diagonalen."""
    fig = go.Figure()
    lim = max(0.5, max(r["e1"] - 0.5 for r in rows) + 0.05)
    fig.add_trace(go.Scatter(x=[0, lim], y=[0, lim], mode="lines", line=dict(color="rgba(120,120,120,0.9)", dash="dash", width=1.5), name="Q = Anteil − ½", hoverinfo="skip"))
    for sp in dict.fromkeys(r["space"] for r in rows):
        mine = [r for r in rows if r["space"] == sp]
        fig.add_trace(go.Scatter(x=[r["e1"] - 0.5 for r in mine], y=[r["q1"] for r in mine], mode="markers", name=sp, marker=dict(size=11, color=C.SPACE_COLORS[sp], line=dict(width=1.5, color="white")),
                                 hovertemplate="Anteil − ½ = %{x:.3f}, Q = %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="Anteil gleichartiger Kanten − ½", range=[0, lim])
    fig.update_yaxes(title_text="Modularität Q der Typen", range=[0, lim])
    return _base(fig, height=340, bottom=100)
