"""Schelling-Segregation: Standortwahl im Gewerbegebiet - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zwölftes Stück der Reihe „Netzwerkanalyse“ und viertes des Anpassungs-Arms: zwei Betriebstypen sitzen in einem Gewerbegebiet, und ein Betrieb zieht um, wenn ihm zu wenige Nachbarn
vom eigenen Typ sind. Die Demo zeigt, wie stark eine milde Vorliebe entmischt, dass die Zugregel entscheidet, ob es endet, und wie die Entmischung zur Modularität aus Stück 2 gehört.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sch_constants as C
from sch_evaluation import (
    Settings,
    analyse,
    bridge_rows,
    de,
    exact_rows,
    grid_label,
    pct,
    space_rows,
    tau_rows,
    tp,
    verdict_bridge,
    verdict_exact,
    verdict_main,
    verdict_space,
    verdict_tau,
)
from sch_layout import dunkles_design, kopf_css
from sch_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sch_visualization import (
    build_bridge_identity,
    build_bridge_similarity,
    build_exact,
    build_exact_steps,
    build_history,
    build_radius,
    build_state,
    build_tau_similarity,
    build_tau_status,
    build_vacancy,
)

MAX_STEPS_TXT = f"{C.MAX_STEPS:,}".replace(",", " ")    # 60 000

st.set_page_config(page_title="Schelling-Segregation – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _tau(l, rho, radius):
    return tau_rows(l, rho, radius)


@st.cache_data(show_spinner=False)
def _space(l, rho, radius):
    return space_rows(l, C.VACANCY_TAU, radius, rho_radius=rho)


@st.cache_data(show_spinner=False)
def _exact():
    return exact_rows()


@st.cache_data(show_spinner=False)
def _bridge(l):
    return bridge_rows(l)


def experiment(name, label, key, compute, show, hint):
    """Teure Zusatzansicht erst auf Klick; das Ergebnis bleibt nur für genau diese Einstellungen stehen (Session State)."""
    state_key = f"exp_{name}"
    if st.button(label, key=f"run_{name}", help=hint):
        with st.spinner("Rechne …"):
            result = compute()
        st.session_state[state_key] = (key, result)
    state = st.session_state.get(state_key)
    if state is None:
        st.caption(f"Noch nicht gerechnet. {hint}")
        return
    if state[0] != key:
        st.info("Die Einstellungen haben sich seit der letzten Rechnung geändert. Bitte neu starten.")
        return
    show(state[1])


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sch_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🏭 Schelling-Segregation: Standortwahl im Gewerbegebiet")
st.markdown(
    """
**Zwölftes Stück** der Reihe „Netzwerkanalyse“ und viertes und letztes des **Anpassungs-Arms**: in Stück 9 bis 11 ändern die Betriebe ihre Meinung, hier ändern sie **ihren Standort**. Zwei Betriebstypen (zum Beispiel Kühl- und Trockenfracht) sitzen in einem Gewerbegebiet; ein Betrieb zieht um, wenn ihm zu wenige Nachbarn vom eigenen Typ sind. Das Nachbarschaftsnetz ist damit nicht vorgegeben, sondern **entsteht aus dem Verhalten** (anders als in Stück 11, wo das Netz fest war).

Die Kernfrage: **Wie stark entmischt das Gebiet, und endet das überhaupt?** Der Hook: schon eine **milde Vorliebe** (Schwelle τ = 30 %: ein Betrieb will mindestens drei von zehn Nachbarn vom eigenen Typ) entmischt das Gebiet stark. Ob die Umzüge zur Ruhe kommen, hängt dagegen an der **Zugregel**: wer nur auf eine Fläche zieht, auf der er zufrieden wäre, **blockiert** bei hoher Schwelle, wer auf eine beliebige freie Fläche zieht, endet. Dazu: freie Flächen verstärken die Entmischung, und der Anteil gleichartiger Kanten ist bis auf eine Konstante die **Modularität** der Typen-Partition aus Stück 2 (der Entmischungsindex liegt nahe daran). Alle Ergebnisse sind **Modellbefunde** über Betriebe als Punkte mit gleicher Schwelle, keine Aussagen über Städte oder Bevölkerung.

Weiter unten: vier Experimente (**🔬**), der Abschnitt **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Standortwahl", expanded=True):
    st.markdown(
        """
1. **Gebiet:** ein Gitter aus Flächen (oder ein Netz aus Stück 1); ein Anteil ρ der Flächen ist mit Betrieben belegt, die Hälfte davon Typ A, die andere Typ B, zufällig verteilt. Der Rest ist frei.
2. **Zufrieden:** ein Betrieb ist zufrieden, wenn mindestens der Anteil τ seiner belegten Nachbarn zu seinem Typ gehört. Hat er keine Nachbarn, ist er zufrieden.
3. **Ein Schritt:** ein zufälliger **unzufriedener** Betrieb versucht umzuziehen, nach der gewählten **Zugregel** (Tabelle unten).
4. **Ende:** **alle zufrieden**, oder **blockiert** (kein Unzufriedener hat noch eine zulässige Fläche), oder die **Obergrenze** der Schritte ist erreicht.
        """
    )
    st.markdown(
        """
| Begriff | Bedeutung hier |
|---|---|
| **Toleranzschwelle τ** | Mindestanteil gleichartiger Nachbarn, bei dem ein Betrieb bleibt |
| **Entmischungsindex** | mittlerer Anteil gleichartiger Nachbarn über alle Betriebe mit mindestens einem Nachbarn (0,5 bei zufälliger Verteilung, 1 bei vollständiger Trennung) |
| **Regel „zufrieden“** | zieht auf eine zufällige freie Fläche, auf der er zufrieden wäre; gibt es keine, bleibt er |
| **Regel „beliebig“** | zieht auf eine zufällige freie Fläche, ob er dort zufrieden wäre oder nicht |
| **Regel „nächste“** | zieht auf die nächstgelegene freie Fläche, auf der er zufrieden wäre (nur im Gitter) |
| **Blockiert** | es gibt noch Unzufriedene, aber keiner kann auf eine zulässige Fläche ziehen; festgestellt, wenn jeder Unzufriedene einmal vergeblich versucht hat |
| **Radius** | 1: die 8 Flächen um eine Fläche zählen als Nachbarn; 2: die 24 Flächen |
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um einen Lauf zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Gebiet**")
    raum = st.selectbox("Gebiet", C.ALL_SPACES, key="raum_select", help="Gitter aus Flächen oder eines der Netze aus Stück 1 (Verbünde: die Gewerbeparks).")
    grid = raum == C.T_GRID
    l = st.slider("Kantenlänge L des Gitters", *bounds("l_slider"), key="l_slider", disabled=not grid, help="Das Gitter hat L × L Flächen, ohne Rand-Fortsetzung.")
    n = st.slider("Flächen im Netz n", *bounds("n_slider"), key="n_slider", disabled=grid, help="Zahl der Flächen im Netz (Knoten).")
    c = st.slider("Nachbarn je Fläche c", *bounds("c_slider"), key="c_slider", disabled=grid, help="Was c bedeutet, hängt vom Netztyp ab (siehe darunter).")
    st.caption(C.C_MEANING[raum])
    rho = st.slider("Belegter Anteil ρ (%)", *bounds("rho_slider"), key="rho_slider", help="Anteil der Flächen mit einem Betrieb; der Rest ist frei und der Platz zum Umziehen.")
    radius = st.slider("Radius der Nachbarschaft", *bounds("radius_slider"), key="radius_slider", disabled=not grid, help="1: die 8 Flächen um eine Fläche; 2: die 24 Flächen. Im Netz sind die Nachbarn vorgegeben.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt das Netz, die Anfangsverteilung und die Auswahl der Umzüge.")
    st.button("🎲 Neuer Lauf", width="stretch", on_click=randomize_seed)
    st.markdown("**Standortwahl**")
    tau = st.slider("Toleranzschwelle τ (%)", *bounds("tau_slider"), key="tau_slider", help="Mindestanteil gleichartiger Nachbarn, damit ein Betrieb zufrieden ist.")
    rule = st.selectbox("Zugregel", C.RULES, key="rule_select", format_func=lambda r: C.RULE_LABEL[r], help="Wohin ein unzufriedener Betrieb zieht.")
    st.caption(C.RULE_HELP[rule])
    if rule == C.R_NEAR and not grid:
        st.caption("Im Netz gibt es keine Entfernung zwischen Flächen: dort gilt die Regel „zufrieden“.")

sync_query_params({"raum_select": raum, "l_slider": int(l), "n_slider": int(n), "c_slider": int(c), "rho_slider": int(rho), "tau_slider": int(tau), "rule_select": rule, "radius_slider": int(radius), "seed_input": int(seed)})

settings = Settings(raum, int(l), int(n), int(c), int(rho), int(tau), rule, int(radius), int(seed))
with st.spinner("Lasse die Betriebe umziehen …"):
    an = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Wie stark entmischt das Gebiet?")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Entmischung", f"{pct(an.s1)} %", delta=f"{'+' if an.s1 >= an.s0 else '−'}{pct(abs(an.s1 - an.s0))} Punkte", delta_color="off", help=f"Entmischungsindex am Ende (mittlerer Anteil gleichartiger Nachbarn); am Anfang {pct(an.s0)} %.")
m2.metric("Modularität", de(an.q1, 2), help="Modularität der Aufteilung in Typ A und Typ B im Nachbarschaftsnetz der Betriebe (am Anfang: " + de(an.q0, 2) + ").")
m3.metric("Unzufrieden", f"{pct(an.run['unhappy'])} %", help=f"Anteil der Betriebe am Ende; am Anfang {pct(an.unhappy0)} %.")
m4.metric("Cluster", f"{an.clusters1[0]}", help=f"Zusammenhängende Gruppen gleichen Typs; die größte hat {pct(an.clusters1[1])} % der Betriebe.")
m5.metric("Umzüge", f"{an.run['moves']}", help=f"Schritte insgesamt: {an.run['steps']} (ein Schritt ist der Versuch, einen unzufriedenen Betrieb umzusetzen).")
st.caption(f"**Ende des Laufs:** {C.STATUS_LABEL[an.status]}. Ein Schritt ist der Versuch, einen unzufriedenen Betrieb umzusetzen; ein Lauf endet, wenn alle zufrieden sind, wenn keiner der Unzufriedenen mehr ziehen kann (blockiert) oder bei der Obergrenze von {MAX_STEPS_TXT} Schritten.")
steps = sorted(an.run["frames"])
step_key = "step_" + "_".join(str(v) for v in (raum, l, n, c, rho, tau, rule, radius, seed))
step = st.select_slider("Schritt", options=steps, value=steps[0], key=step_key, help="Blättert durch den Lauf: ganz links die zufällige Anfangsverteilung, ganz rechts das Ende.")
st.markdown("**Das Gebiet im Lauf** (Farbe: Typ A grün, Typ B orange, frei grau; Ring: unzufrieden)")
if an.space.edges and len(an.space.edges) > 3000:
    st.caption("Das Netz hat zu viele Kanten für die Zeichnung; sie werden weggelassen.")
st.plotly_chart(build_state(an, step, dunkles_design()), width="stretch", key="state_chart")
st.markdown("**Entmischungsindex und Anteil Unzufriedener über die Schritte**")
st.plotly_chart(build_history(an, step), width="stretch", key="history_chart")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie stark entmischt es, und endet es?")
kind, text = verdict_main(an)
getattr(st, kind)(text)
st.caption("Ein einzelner Lauf ist ein Beispiel; die Experimente rechnen über feste Starts.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

l_exp, rho_exp, radius_exp = settings.l, settings.rho / 100.0, settings.radius
st.subheader("🔬 Experiment 1: Schwelle und Zugregel")
st.caption(f"Gitter {l_exp} × {l_exp}, belegter Anteil {settings.rho} %, Radius {radius_exp}: Entmischungsindex am Ende und Anteil der Läufe, die zufrieden enden, über die Schwelle τ = {', '.join(tp(t) for t in C.TAU_GRID)}, je Zugregel. Mittel über {C.LIVE_RUNS} feste Starts.")


def show_tau(rows):
    st.markdown("**Entmischungsindex am Ende** (gestrichelt: Anfangswert)")
    st.plotly_chart(build_tau_similarity(rows), width="stretch", key="tau_sim_chart")
    st.markdown("**Läufe, die mit allen zufrieden enden**")
    st.plotly_chart(build_tau_status(rows), width="stretch", key="tau_status_chart")
    kind_, text_ = verdict_tau(rows)
    getattr(st, kind_)(text_)


experiment("tau", "Schwellen messen", (l_exp, rho_exp, radius_exp), lambda: _tau(l_exp, rho_exp, radius_exp), show_tau, "Rechnet 3 Regeln bei 10 Schwellen mit je 5 Starts, einige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 2: Freie Flächen und Radius")
st.caption(f"Gitter {l_exp} × {l_exp}. Links: Regel „zufrieden“, τ = {tp(C.VACANCY_TAU)}, Radius {radius_exp}, belegter Anteil von {pct(C.RHO_GRID[0])} % bis {pct(C.RHO_GRID[-1])} %. Rechts: belegter Anteil {settings.rho} %, Radius 1 gegen Radius 2 über τ = {', '.join(tp(t) for t in C.RADIUS_TAUS)}. Mittel über {C.LIVE_RUNS} feste Starts.")


def show_space(res):
    left, right = st.columns(2)
    with left:
        st.markdown("**Über den belegten Anteil**")
        st.plotly_chart(build_vacancy(res), width="stretch", key="vacancy_chart")
    with right:
        st.markdown("**Radius 1 gegen Radius 2**")
        st.plotly_chart(build_radius(res), width="stretch", key="radius_chart")
    kind_, text_ = verdict_space(res)
    getattr(st, kind_)(text_)


experiment("space", "Flächen und Radius messen", (l_exp, rho_exp, radius_exp), lambda: _space(l_exp, rho_exp, radius_exp), show_space, "Rechnet 7 belegte Anteile und 2 Radien, wenige Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 3: Exakt auf kleinen Gittern")
st.caption(f"Alle Belegungen der Gitter {', '.join(grid_label(*g) for g in C.EXACT_GRIDS)} bei Radius 1 als Markov-Kette, gleichverteilter Start; Zustände „alle zufrieden“ und „blockiert“ sind absorbierend. Dazu je {C.EXACT_SIM_RUNS} simulierte Starts als Gegenprobe. Schwellen τ = {', '.join(tp(t) for t in C.EXACT_TAUS)}.")


def show_exact(rows):
    for g in C.EXACT_GRIDS:
        label = grid_label(*g)
        st.markdown(f"**Gitter {label}**")
        left, right = st.columns(2)
        with left:
            st.caption("Starts, die zufrieden enden (Linie: exakt, Rauten: Simulation)")
            st.plotly_chart(build_exact(rows, label), width="stretch", key=f"exact_p_{label}")
        with right:
            st.caption("Erwartete Schritte, wo jeder Start endet")
            st.plotly_chart(build_exact_steps(rows, label), width="stretch", key=f"exact_t_{label}")
    kind_, text_ = verdict_exact(rows)
    getattr(st, kind_)(text_)


experiment("exact", "Exakt rechnen", "fest", _exact, show_exact, f"Rechnet 2 Gitter mit 2 Regeln bei 6 Schwellen exakt und je {C.EXACT_SIM_RUNS} Starts, etwa zwanzig Sekunden.")

st.markdown("---")

st.subheader("🔬 Experiment 4: Brücke zu Stück 2 und Netze")
st.caption(f"Regel „zufrieden“, belegter Anteil {pct(C.BRIDGE_RHO)} %, Schwellen τ = {', '.join(tp(t) for t in C.BRIDGE_TAUS)}; Gitter {l_exp} × {l_exp} (Radius 1) und Netze mit {C.BRIDGE_N} Flächen, c = {C.BRIDGE_C}. Mittel über {C.LIVE_RUNS} feste Netze und Starts.")


def show_bridge(rows):
    st.markdown("**Entmischungsindex am Ende** (gestrichelt: Anfangswert)")
    st.plotly_chart(build_bridge_similarity(rows), width="stretch", key="bridge_sim_chart")
    st.markdown("**Anteil gleichartiger Kanten bis auf eine Konstante gleich Modularität:** Modularität der Typen gegen Anteil gleichartiger Kanten − ½")
    st.plotly_chart(build_bridge_identity(rows), width="stretch", key="bridge_id_chart")
    kind_, text_ = verdict_bridge(rows)
    getattr(st, kind_)(text_)


experiment("bridge", "Räume vergleichen", l_exp, lambda: _bridge(l_exp), show_bridge, "Rechnet 4 Räume bei 2 Schwellen mit je 5 festen Netzen, wenige Sekunden.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Zwei gleich große Typen** | Der Anteil von Typ A ist fest 50 %. Mit einem kleinen Typ oder mehr als zwei Typen verschieben sich die Schwellen, ab denen es blockiert. | – |
| **Gleiche Schwelle für alle** | Alle Betriebe haben dasselbe τ. Mit verschieden toleranten Betrieben verändert sich die Entmischung. | – |
| **Standortwahl nur nach Nachbarn** | Kein Preis der Fläche, keine Umzugskosten, keine Nähe zu Kunden oder Häfen. Ein Betrieb zieht, wenn ihm die Nachbarn nicht passen, sonst nie. | – |
| **Zufällige Auswahl, ein Umzug je Schritt** | Ein zufälliger Unzufriedener versucht einen Umzug. Mit gleichzeitigen Umzügen oder einer anderen Reihenfolge ändern sich Dauer und Blockaden. | – |
| **Beschränktes Gitter** | Das Gitter hat Ränder ohne Fortsetzung; Randflächen haben weniger Nachbarn. Am Rand ist Zufriedenheit leichter oder schwerer als innen. | – |
| **Festes Netz in der Netz-Variante** | Die Flächen und ihre Nachbarschaft sind vorgegeben; nur die Betriebe wandern. Wie sich das Netz zeitlich selbst ändert, zeigt das nächste Stück. | Stück 13 (zeitliche Netze) |
| **Obergrenze der Schritte** | Läufe enden spätestens nach 60 000 Schritten (in der App nach 30 000 in den Experimenten); „Obergrenze“ heißt nicht „fertig“. | – |
| **Stichproben** | Mittel über fünf feste Starts in der App (zwölf in der README); die Streuung ist nicht ausgewiesen. Das exakte Ergebnis gilt nur für die kleinen Gitter. | – |
| **Modellbefund** | Die Demo zeigt Verhalten im Modell, keine Wirkung in einer Stadt oder Bevölkerung. Die Betriebstypen sind eine Kulisse für das Modell, kein Befund über Standortentscheidungen. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Zufrieden.** Mit der Nachbarmenge $N(i)$ der Fläche $i$, den Typen $\theta_j \in \{0, 1, 2\}$ (0 = frei) und der Toleranzschwelle $\tau$ ist der Betrieb auf $i$ zufrieden, wenn

$$\bigl|\{\, j \in N(i) : \theta_j = \theta_i \,\}\bigr| \;\ge\; \tau \cdot \bigl|\{\, j \in N(i) : \theta_j \neq 0 \,\}\bigr|$$

gilt; ohne belegte Nachbarn ist er zufrieden. Verglichen wird mit der Toleranz $10^{-12}$ gegen die diskreten Anteile.

**Entmischungsindex.** Mit dem Anteil $s_i / o_i$ gleichartiger unter den belegten Nachbarn des Betriebs $i$ und der Menge $V'$ der Betriebe mit mindestens einem Nachbarn ist

$$S = \frac{1}{|V'|} \sum_{i \in V'} \frac{s_i}{o_i}$$

**Brücke zu Stück 2 (Modularität der Typen).** Im Nachbarschaftsnetz der belegten Flächen mit $m$ Kanten, dem Anteil $e_{\text{in}}$ gleichartiger Kanten und den Gradsummen $D_k$ der Typen $k \in \{A, B\}$ ist die Modularität der Typen-Partition

$$Q = e_{\text{in}} - \sum_{k \in \{A, B\}} \left( \frac{D_k}{2m} \right)^2$$

Sind die Gradsummen etwa gleich, ist $Q \approx e_{\text{in}} - \tfrac{1}{2}$; der Entmischungsindex und die Modularität messen dasselbe bis auf diese Konstante und die Gewichtung der Betriebe.

**Exakte Kette.** Auf einem kleinen Gitter ist jede Belegung ein Zustand. Mit der Übergangsmatrix $Q_T$ zwischen den nicht absorbierenden Zuständen und den Übergängen $R$ in die absorbierenden Zustände („alle zufrieden“, „blockiert“) sind die Endwahrscheinlichkeiten

$$B = (I - Q_T)^{-1} R$$

und die erwarteten Schritte bis zum Ende

$$t = (I - Q_T)^{-1} \mathbf{1}$$

Die Demo mittelt über den gleichverteilten Start.

**Übereinstimmung mit den Verbünden.** Die normalisierte gegenseitige Information der Typen $X$ mit den Verbünden $Y$ ist

$$\mathrm{NMI}(X, Y) = \frac{I(X; Y)}{\tfrac{1}{2}\bigl(H(X) + H(Y)\bigr)}$$

**Literatur.**
- Schelling, T. C. (1971): *Dynamic Models of Segregation.* Journal of Mathematical Sociology 1(2), 143–186.
- Vinković, D., Kirman, A. (2006): *A physical analogue of the Schelling model.* Proceedings of the National Academy of Sciences 103(51), 19261–19265.
- Gauvin, L., Vannimenus, J., Nadal, J.-P. (2009): *Phase diagram of a Schelling segregation model.* European Physical Journal B 70, 293–304.
- Newman, M. E. J., Girvan, M. (2004): *Finding and evaluating community structure in networks.* Physical Review E 69, 026113.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
