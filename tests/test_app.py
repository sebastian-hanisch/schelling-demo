"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, fährt jeden Slider an seine Grenzen,
prüft Permalink, Räume, Regeln, den Schritt-Regler und alle vier Experimente; es darf kein Python-Fehler auftreten."""

import os

import pytest
from streamlit.testing.v1 import AppTest

import sch_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
EXPERIMENTS = ("tau", "space", "exact", "bridge")
METRICS = ["Entmischung", "Modularität", "Unzufrieden", "Cluster", "Umzüge"]


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _metric(at, label):
    return next(m.value for m in at.metric if m.label == label)


def test_app_loads_without_exception():
    at = _fresh_app()
    assert [m.label for m in at.metric] == METRICS
    assert [_metric(at, k) for k in METRICS] == ["71 %", "0,20", "0 %", "11", "166"]
    assert not at.error and not at.warning
    assert any(s.value.startswith("Nach 166 Umzügen (166 Schritten) sind alle 810 Betriebe zufrieden.") for s in at.success)
    assert any("**Ende des Laufs:** alle zufrieden." in c.value and "60 000 Schritten" in c.value for c in at.caption)


def test_every_preset_click_does_not_raise():
    for name in C.PRESETS:
        at = _fresh_app()
        at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])


def test_the_presets_show_their_numbers():
    at = _fresh_app()
    at.sidebar.button(key="preset_Hohe Schwelle: die Betriebe blockieren sich").click().run(timeout=TIMEOUT)
    assert [_metric(at, k) for k in ("Entmischung", "Unzufrieden", "Cluster", "Umzüge")] == ["53 %", "73 %", "35", "48"] and any("blockiert" in w.value for w in at.warning)
    at.sidebar.button(key="preset_Dieselbe Schwelle, beliebige Züge: es endet").click().run(timeout=TIMEOUT)
    assert _metric(at, "Entmischung") == "99 %" and _metric(at, "Umzüge") == "4251" and any("alle 810 Betriebe zufrieden" in s.value for s in at.success)
    at.sidebar.button(key="preset_Netz mit Gewerbeparks").click().run(timeout=TIMEOUT)
    assert _metric(at, "Entmischung") == "84 %" and _metric(at, "Cluster") == "2" and at.selectbox(key="raum_select").value == C.T_COMMUNITIES


SLIDERS = {"l_slider": C.T_GRID, "radius_slider": C.T_GRID, "rho_slider": C.T_GRID, "tau_slider": C.T_GRID, "n_slider": C.T_COMMUNITIES, "c_slider": C.T_COMMUNITIES}      # ein deaktivierter Regler lässt sich nicht bedienen: der Raum bestimmt, welche aktiv sind


def test_the_sidebar_has_exactly_these_sliders_in_this_order():
    assert [s.label for s in _fresh_app().sidebar.slider] == ["Kantenlänge L des Gitters", "Flächen im Netz n", "Nachbarn je Fläche c", "Belegter Anteil ρ (%)", "Radius der Nachbarschaft", "Toleranzschwelle τ (%)"]
    assert [s.key for s in _fresh_app().sidebar.slider] == ["l_slider", "n_slider", "c_slider", "rho_slider", "radius_slider", "tau_slider"]


@pytest.mark.parametrize("key", list(SLIDERS))
@pytest.mark.parametrize("edge", ["min", "max"])
def test_every_slider_at_its_min_and_max_does_not_raise(key, edge):
    at = _fresh_app()
    at.selectbox(key="raum_select").set_value(SLIDERS[key]).run(timeout=TIMEOUT)
    slider = at.sidebar.slider(key=key)
    slider.set_value(int(slider.min if edge == "min" else slider.max)).run(timeout=TIMEOUT)
    assert not at.exception, (key, edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("raum", [C.T_GRID, C.T_BA])
def test_all_active_sliders_at_their_minimum_and_all_at_their_maximum_do_not_raise(raum):
    for edge in ("min", "max"):
        at = _fresh_app()
        at.selectbox(key="raum_select").set_value(raum).run(timeout=TIMEOUT)
        for slider in at.sidebar.slider:
            if not slider.disabled:
                slider.set_value(int(slider.min if edge == "min" else slider.max))
        at.run(timeout=TIMEOUT)
        assert not at.exception, (raum, edge, [str(e) for e in at.exception])


@pytest.mark.parametrize("raum", C.ALL_SPACES)
def test_every_space_renders(raum):
    at = _fresh_app()
    at.selectbox(key="raum_select").set_value(raum).run(timeout=TIMEOUT)
    assert not at.exception, (raum, [str(e) for e in at.exception])


@pytest.mark.parametrize("rule", C.RULES)
def test_every_rule_renders_on_the_grid_and_in_a_network(rule):
    at = _fresh_app()
    at.selectbox(key="rule_select").set_value(rule).run(timeout=TIMEOUT)
    assert not at.exception, (rule, [str(e) for e in at.exception])
    at.selectbox(key="raum_select").set_value(C.T_RING).run(timeout=TIMEOUT)
    assert not at.exception, (rule, [str(e) for e in at.exception])


def test_the_step_slider_moves_through_the_frames_and_resets_with_the_settings():
    at = _fresh_app()
    slider = at.select_slider[0]
    last = int(slider.options[-1])
    assert slider.label == "Schritt" and slider.value == 0 and last == 166
    slider.set_value(last).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == last
    at.sidebar.slider(key="tau_slider").set_value(35).run(timeout=TIMEOUT)
    assert not at.exception and at.select_slider[0].value == 0                                       # neue Einstellungen: neuer Regler, zurück auf Schritt 0


def test_a_new_run_changes_the_seed_and_the_result():
    at = _fresh_app()
    before = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index("🎲 Neuer Lauf")].click().run(timeout=TIMEOUT)
    assert not at.exception and at.number_input(key="seed_input").value != before


def test_permalink_values_are_clamped_and_unknown_choices_ignored():
    at = AppTest.from_file(APP_PATH)
    at.query_params["l"] = "5"
    at.query_params["belegt"] = "999"
    at.query_params["radius"] = "99"
    at.query_params["regel"] = "gibt es nicht"
    at.query_params["raum"] = "gibt es nicht"
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.slider(key="l_slider").value == C.L_MIN and at.slider(key="rho_slider").value == C.RHO_MAX and at.slider(key="radius_slider").value == C.RADIUS_MAX
    assert at.selectbox(key="rule_select").value == C.R_HAPPY and at.selectbox(key="raum_select").value == C.T_GRID


def test_permalink_selects_space_and_rule_and_the_address_mirrors_the_settings():
    at = AppTest.from_file(APP_PATH)
    at.query_params["raum"] = C.T_COMMUNITIES
    at.query_params["regel"] = C.R_ANY
    at.query_params["schwelle"] = "50"
    at.run(timeout=TIMEOUT)
    assert not at.exception and at.selectbox(key="raum_select").value == C.T_COMMUNITIES and at.selectbox(key="rule_select").value == C.R_ANY and at.slider(key="tau_slider").value == 50
    assert dict(at.query_params) == {"raum": C.T_COMMUNITIES, "l": "30", "n": "240", "c": "8", "belegt": "90", "schwelle": "50", "regel": C.R_ANY, "radius": "1", "seed": "35"}


def test_every_experiment_runs_and_is_invalidated_by_a_setting_change():
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    at.sidebar.slider(key="l_slider").set_value(C.L_MIN).run(timeout=TIMEOUT)         # kleines Gitter: schnell
    for name in EXPERIMENTS:
        at.button(key=f"run_{name}").click().run(timeout=TIMEOUT)
        assert not at.exception, (name, [str(e) for e in at.exception])
    texts = " ".join(x.value for x in list(at.info) + list(at.warning) + list(at.success))
    for fragment in ("Entmischungsindex (mittlerer Anteil gleichartiger Nachbarn) vor und nach den Umzügen, je Regel", "Bei τ = 37,5 % und 98 % belegten Flächen", "Auf dem Gitter 3 × 3 (3 A, 3 B) (alle 1680 Belegungen, exakt)", "Die Modularität der Typen-Partition liegt höchstens"):
        assert fragment in texts, fragment
    at.sidebar.slider(key="l_slider").set_value(C.L_MIN + 2).run(timeout=TIMEOUT)
    assert not at.exception
    assert sum("neu starten" in i.value for i in at.info) == 3                                    # Experiment 1, 2 und 4 hängen an L; 3 an nichts
