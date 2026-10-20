"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt, wofür es benannt ist."""

import sch_algorithm as A
import sch_constants as C
import sch_evaluation as ev
import sch_presets as P


def _settings(name):
    return ev.Settings(**C.PRESETS[name])


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["raum"] in C.ALL_SPACES and C.L_MIN <= p["l"] <= C.L_MAX and C.N_MIN <= p["n"] <= C.N_MAX and C.C_MIN <= p["c"] <= C.C_MAX and 0 <= p["seed"] <= C.SEED_MAX, name
        assert C.RHO_MIN <= p["rho"] <= C.RHO_MAX and C.TAU_MIN <= p["tau"] <= C.TAU_MAX and C.RADIUS_MIN <= p["radius"] <= C.RADIUS_MAX and p["rule"] in C.RULES, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[C.DEFAULT_PRESET_NAME]) == ev.Settings()
    assert next(iter(C.PRESETS)) == C.DEFAULT_PRESET_NAME


def test_setting_specs_cover_every_preset_key_and_defaults_match():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for key, state_key in P.PRESET_KEYS.items():
        assert P.SETTING_SPECS[state_key].default == C.PRESETS[C.DEFAULT_PRESET_NAME][key], key


def test_every_preset_differs_from_the_default_in_something_besides_the_space():
    default = C.PRESETS[C.DEFAULT_PRESET_NAME]
    for name, p in C.PRESETS.items():
        if name != C.DEFAULT_PRESET_NAME:
            assert any(p[k] != default[k] for k in p if k != "raum"), name


def test_each_preset_shows_what_its_name_says():
    an = {name: ev.analyse(_settings(name)) for name in C.PRESETS}
    mild = an[C.DEFAULT_PRESET_NAME]
    assert mild.status == C.ST_DONE and mild.run["unhappy"] == 0.0 and mild.s1 - mild.s0 >= 0.2 and mild.q1 > mild.q0 + 0.15
    high = an["Hohe Schwelle: die Betriebe blockieren sich"]
    assert high.status == C.ST_BLOCKED and high.run["unhappy"] > 0.5 and high.run["moves"] < high.run["steps"] and high.s1 < 0.6
    anyrule = an["Dieselbe Schwelle, beliebige Züge: es endet"]
    assert anyrule.status == C.ST_DONE and anyrule.s1 > 0.95 and anyrule.run["moves"] > 10 * high.run["moves"]
    assert anyrule.settings.tau == high.settings.tau and anyrule.settings.seed == high.settings.seed and anyrule.types0 == high.types0                   # nur die Regel ist anders
    full = an["Fast kein Platz: einzelne bleiben hängen"]
    assert full.status == C.ST_BLOCKED and 0 < full.run["unhappy"] <= 0.05 and full.free == 18 and full.agents == 882
    radius = an["Größerer Radius, mildere Entmischung"]
    assert radius.status == C.ST_DONE and radius.settings.radius == 2 and radius.s1 < mild.s1 - 0.1
    net = an["Netz mit Gewerbeparks"]
    assert net.settings.raum == C.T_COMMUNITIES and net.status == C.ST_DONE and net.s1 > 0.8 and net.nmi1 > 0.2


def test_every_preset_runs_and_the_verdict_is_a_known_kind():
    for name in C.PRESETS:
        an = ev.analyse(_settings(name))
        kind, text = ev.verdict_main(an)
        assert kind in ("success", "info", "warning") and text
        frames = an.run["frames"]
        assert set(frames) >= {0, an.run["steps"]} and frames[an.run["steps"]] == an.run["types"] and frames[0] == an.types0
        assert all(f.count(1) == an.types0.count(1) and f.count(2) == an.types0.count(2) for f in frames.values())          # die Zahl der Betriebe je Typ bleibt erhalten
        if an.status == C.ST_DONE:
            assert A.unhappy_cells(an.run["types"], an.tau, an.space.nbrs) == []
