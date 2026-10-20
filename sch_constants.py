"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# --- Räume ---------------------------------------------------------------------------------------------------------------------------------------
T_GRID = "Gitter"                                   # eigenes Gitter mit Nachbarschaft nach Radius (nicht das Gitter-Netz aus Stück 1)
T_RANDOM = "Zufallsnetz"
T_POWER = "Potenzgesetz-Netz"
T_BA = "Skalenfreies Netz (BA)"
T_COMMUNITIES = "Verbünde"
T_RING = "Ring mit Abkürzungen"
NET_TYPES = (T_RANDOM, T_POWER, T_BA, T_COMMUNITIES, T_RING)
ALL_SPACES = (T_GRID,) + NET_TYPES
BLOCKS = 6

C_MEANING = {
    T_GRID: "ohne Wirkung: im Gitter bestimmt der Radius die Nachbarn",
    T_RANDOM: "mittlerer Grad des Zufallsnetzes",
    T_POWER: "mittlerer Grad (Gradfolge mit Potenzgesetz-Exponent 2,5, Konfigurationsmodell)",
    T_BA: "zwei Kanten je neuem Knoten, also m = c / 2 gerundet (jeder Knoten hat mindestens m Nachbarn)",
    T_COMMUNITIES: "mittlerer Grad; 80 % der Kanten bleiben im eigenen Verbund (6 Verbünde, die Gewerbeparks)",
    T_RING: "Nachbarn auf dem Ring (c gerade gerundet), dazu Abkürzungen mit 5 % je Ringkante",
}

L_MIN, L_MAX, DEFAULT_L = 10, 40, 30               # Kantenlänge des Gitters
N_MIN, N_MAX, DEFAULT_N = 60, 400, 240             # Flächen im Netz
C_MIN, C_MAX, DEFAULT_C = 3, 12, 8
RHO_MIN, RHO_MAX, DEFAULT_RHO = 30, 100, 90        # belegter Anteil der Flächen in Prozent
TAU_MIN, TAU_MAX, DEFAULT_TAU = 0, 100, 30         # Toleranzschwelle in Prozent (Mindestanteil gleichartiger Nachbarn)
RADIUS_MIN, RADIUS_MAX, DEFAULT_RADIUS = 1, 2, 1
SEED_MAX, DEFAULT_SEED = 999999, 35
SWEEP_SEEDS = tuple(range(100000, 100012))          # feste Läufe für alle Messreihen (zwölf Starts je Zelle)
FRAC_A = 0.5                                        # Anteil des Typs A an den Betrieben (fest)

# --- Zugregeln und Ende --------------------------------------------------------------------------------------------------------------------------
R_HAPPY, R_ANY, R_NEAR = "zufrieden", "beliebig", "nächste"
RULES = (R_HAPPY, R_ANY, R_NEAR)
RULE_LABEL = {R_HAPPY: "Nur auf eine zufriedenstellende Fläche", R_ANY: "Auf eine beliebige freie Fläche", R_NEAR: "Auf die nächste zufriedenstellende Fläche"}
RULE_HELP = {
    R_HAPPY: "Ein unzufriedener Betrieb zieht auf eine zufällige freie Fläche, auf der er zufrieden wäre; gibt es keine, bleibt er.",
    R_ANY: "Ein unzufriedener Betrieb zieht auf eine zufällige freie Fläche, ob er dort zufrieden wäre oder nicht.",
    R_NEAR: "Ein unzufriedener Betrieb zieht auf die nächstgelegene freie Fläche, auf der er zufrieden wäre (nur im Gitter; Gleichstand zufällig).",
}
ST_DONE, ST_BLOCKED, ST_CAP = "zufrieden", "blockiert", "Obergrenze"
STATUS_LABEL = {ST_DONE: "alle zufrieden", ST_BLOCKED: "blockiert", ST_CAP: "Obergrenze der Schritte"}

# --- Messungen -----------------------------------------------------------------------------------------------------------------------------------
MAX_STEPS = 60000                                   # Schutz: Obergrenze der Schritte (Versuche, einen unzufriedenen Betrieb umzusetzen)
FRAMES = 120                                        # Zahl der Bilder im Schritt-Regler
TAU_GRID = (0.1, 0.2, 0.25, 0.3, 0.375, 0.4, 0.5, 0.6, 0.7, 0.8)    # Toleranzschwellen in Experiment 1
LIVE_RUNS = 5                                       # Starts je Zelle in der App (die README-Zahlen nutzen alle zwölf)
RHO_GRID = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98)    # belegte Anteile in Experiment 2
RADIUS_TAUS = (0.3, 0.4, 0.5, 0.6)
VACANCY_TAU = 0.375
EXACT_GRIDS = ((3, 3, 3, 3), (3, 4, 2, 2))          # (Zeilen, Spalten, Betriebe Typ A, Betriebe Typ B) für die exakte Kette
EXACT_TAUS = (0.25, 0.34, 0.5, 0.6, 0.67, 0.75)
EXACT_SIM_RUNS = 2000
BRIDGE_SPACES = (T_GRID, T_RANDOM, T_COMMUNITIES, T_RING)
BRIDGE_TAUS = (0.3, 0.5)
BRIDGE_N, BRIDGE_C, BRIDGE_RHO = 240, 8, 0.85

# --- Darstellung ---------------------------------------------------------------------------------------------------------------------------------
COLOR_EDGE = "rgba(120,120,120,0.30)"
COLOR_A = "#2F6B65"                                 # Typ A (Kühlfracht)
COLOR_B = "#c4623b"                                 # Typ B (Trockenfracht)
COLOR_EMPTY = "rgba(160,160,160,0.18)"
COLOR_EMPTY_SOLID = "#d9d9d9"                       # freie Fläche (deckend, damit die Heatmap keine Transparenz braucht)
COLOR_C = "#6b5b95"
RULE_COLORS = {R_HAPPY: "#2F6B65", R_ANY: "#c4623b", R_NEAR: "#6b5b95"}
SPACE_COLORS = {T_GRID: "#333333", T_RANDOM: "#2F6B65", T_POWER: "#c4623b", T_BA: "#6b5b95", T_COMMUNITIES: "#9d755d", T_RING: "#4c78a8"}

PRESETS = {
    "Milde Vorliebe, starke Entmischung (Voreinstellung)": {"raum": T_GRID, "l": DEFAULT_L, "n": DEFAULT_N, "c": DEFAULT_C, "rho": DEFAULT_RHO, "tau": DEFAULT_TAU, "rule": R_HAPPY, "radius": DEFAULT_RADIUS, "seed": DEFAULT_SEED},
    "Hohe Schwelle: die Betriebe blockieren sich": {"raum": T_GRID, "l": DEFAULT_L, "n": DEFAULT_N, "c": DEFAULT_C, "rho": DEFAULT_RHO, "tau": 70, "rule": R_HAPPY, "radius": DEFAULT_RADIUS, "seed": DEFAULT_SEED},
    "Dieselbe Schwelle, beliebige Züge: es endet": {"raum": T_GRID, "l": DEFAULT_L, "n": DEFAULT_N, "c": DEFAULT_C, "rho": DEFAULT_RHO, "tau": 70, "rule": R_ANY, "radius": DEFAULT_RADIUS, "seed": DEFAULT_SEED},
    "Fast kein Platz: einzelne bleiben hängen": {"raum": T_GRID, "l": DEFAULT_L, "n": DEFAULT_N, "c": DEFAULT_C, "rho": 98, "tau": 37, "rule": R_HAPPY, "radius": DEFAULT_RADIUS, "seed": 42},
    "Größerer Radius, mildere Entmischung": {"raum": T_GRID, "l": DEFAULT_L, "n": DEFAULT_N, "c": DEFAULT_C, "rho": DEFAULT_RHO, "tau": 30, "rule": R_HAPPY, "radius": 2, "seed": DEFAULT_SEED},
    "Netz mit Gewerbeparks": {"raum": T_COMMUNITIES, "l": DEFAULT_L, "n": DEFAULT_N, "c": DEFAULT_C, "rho": 85, "tau": 50, "rule": R_HAPPY, "radius": DEFAULT_RADIUS, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Milde Vorliebe, starke Entmischung (Voreinstellung)": "Jeder Betrieb will nur 30 % gleichartige Nachbarn, und doch entmischt das Gebiet stark.",
    "Hohe Schwelle: die Betriebe blockieren sich": "Bei Schwelle 70 % findet keiner mehr eine zufriedenstellende Fläche: die meisten bleiben unzufrieden, es geht nichts mehr.",
    "Dieselbe Schwelle, beliebige Züge: es endet": "Mit beliebigen Zügen findet das Gebiet auch bei Schwelle 70 % einen Zustand, in dem alle zufrieden sind: es ist fast vollständig entmischt.",
    "Fast kein Platz: einzelne bleiben hängen": "Nur 2 % der Flächen sind frei: schon bei einer mittleren Schwelle bleiben einzelne Betriebe unzufrieden, weil keine freie Fläche für sie passt.",
    "Größerer Radius, mildere Entmischung": "Bei Radius 2 zählen 24 Nachbarn; dieselbe Schwelle 30 % entmischt hier schwächer als bei Radius 1.",
    "Netz mit Gewerbeparks": "Die Betriebe stehen auf den Knoten eines Netzes mit sechs Gewerbeparks: die Typen richten sich an den Parks aus.",
}
DEFAULT_PRESET_NAME = "Milde Vorliebe, starke Entmischung (Voreinstellung)"
