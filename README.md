# Schelling-Segregation: Standortwahl im Gewerbegebiet – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-schelling-demo.streamlit.app/)** -->

Zwölftes Stück der **Netzwerkanalyse-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ und viertes und letztes des **Anpassungs-Arms** (Stücke 9 bis 12): in der [Meinungsbildungs-Demo](https://sebastianhanisch-meinungsbildung-demo.streamlit.app/) (Stück 9), der [Voter-Demo](https://sebastianhanisch-voter-modell-demo.streamlit.app/) (Stück 10) und der [Demo zu begrenztem Vertrauen](https://sebastianhanisch-begrenztes-vertrauen-demo.streamlit.app/) (Stück 11) ändern die Betriebe ihre Meinung auf einem festen Netz; hier ändern sie **ihren Standort**, und das Nachbarschaftsnetz **entsteht aus dem Verhalten**. Die Modularität, mit der sich das Ergebnis messen lässt, kommt aus der [Blockmodell-Demo](https://sebastianhanisch-stochastic-block-demo.streamlit.app/) (Stück 2).

Zwei Betriebstypen (zum Beispiel Kühl- und Trockenfracht) sitzen in einem Gewerbegebiet. Jeder Betrieb will mindestens den Anteil τ seiner Nachbarn vom eigenen Typ und zieht sonst auf eine freie Fläche. Die Demo zeigt, **wie stark das Gebiet entmischt, wovon es abhängt, ob die Umzüge zur Ruhe kommen, und wie die Entmischung zur Modularität gehört**. Alles sind Modellbefunde über Betriebe als Punkte, keine Aussagen über Städte oder Bevölkerung.

## Kernfrage

**Wie stark entmischt das Gebiet, und endet das überhaupt?** Der Hook: schon eine **milde Vorliebe** (τ = 30 %) bringt den Anteil gleichartiger Nachbarn von 49,7 % auf 75,6 % (Mittel über 12 Starts, Gitter 30 × 30, 90 % belegt). Ob die Umzüge zur Ruhe kommen, hängt an der **Zugregel**: wer nur auf eine Fläche zieht, auf der er zufrieden wäre, **blockiert** bei hoher Schwelle (ab τ = 70 % in allen 12 Läufen), wer auf eine beliebige freie Fläche zieht, endet bis τ = 70 % in allen Läufen und nicht mehr bei 80 %. Dazu: freie Flächen verstärken die Entmischung, und der **Entmischungsindex ist bis auf eine Konstante die Modularität der Typen-Partition** aus Stück 2. Alle Ergebnisse sind **Modellbefunde**: Betriebe als Punkte, gleiche Schwelle für alle, Standortwahl nur nach Nachbarn.

## Befunde und Korrekturen gegenüber dem Plan

- **Milde Vorlieben erzeugen starke Entmischung, und zwar sprunghaft** (bestätigt, jetzt mit Schwelle gemessen): bei Regel „zufrieden“ steigt der Entmischungsindex von 49,7 % (zufällige Verteilung) auf 58,2 % bei τ = 25 % und auf 75,6 % bei τ = 30 %; bei τ = 50 % sind es 86,9 %, bei 60 % 94,7 %. τ = 30 % und 37,5 % unterscheiden sich nur wenig (75,6 % und 77,0 %), weil bei 8 Nachbarn beide drei gleichartige verlangen (Randflächen haben weniger Nachbarn).
- **Die Zugregel entscheidet, ob es endet** (Plan: „Terminierung nicht voraussetzen“, bestätigt und belegt): Regel „zufrieden“: alle 12 Läufe enden bis τ = 50 % mit allen zufrieden, bei 60 % 8 von 12, ab 70 % **keiner**; dort bleiben im Mittel 71 % (τ = 70 %) bzw. 91 % (τ = 80 %) der Betriebe unzufrieden, und der Lauf steht nach im Median 55 bzw. 15 Umzügen. Regel „beliebig“ endet bis τ = 70 % in allen Läufen (mit 99,3 % Entmischungsindex), braucht dafür aber im Median 5536,5 Schritte gegen 380,5 bei τ = 37,5 %; bei 80 % erreicht kein Lauf das Ende (Obergrenze 60 000 Schritte, 74,6 % unzufrieden).
- **Exakt nachgerechnet auf kleinen Gittern:** auf 3 × 3 Flächen mit 3 + 3 Betrieben (alle 1680 Belegungen als absorbierende Markov-Kette) sind bei τ = 67 % und 75 % 892 Belegungen blockiert und nur 4 zufrieden; die Regel „zufrieden“ endet nur in 13,1 % der gleichverteilten Starts zufrieden, die Regel „beliebig“ in 100 % nach im Mittel 182,4 Schritten (bei τ = 60 %: 29,75). Die Simulation (je 2000 Starts) stimmt überein (Test: innerhalb von 4,5 Standardfehlern).
- **Mehr freie Flächen, mehr Entmischung:** bei τ = 37,5 % sinkt der Entmischungsindex von 84,9 % bei 50 % belegten Flächen auf 76,0 % bei 98 %; bei 98 % belegt enden nur 7 von 12 Läufen mit allen zufrieden, 5 blockieren (mit im Mittel 0,16 % unzufriedenen Betrieben, also nur wenigen einzelnen).
- **Radius 2 wirkt nicht einfach schwächer oder stärker:** bei τ = 30 % entmischt Radius 2 weniger (59,6 % gegen 75,7 %), bei 40 % und 50 % mehr (85,8 % gegen 82,5 % bzw. 89,5 % gegen 87,3 %), und bei 60 % blockieren 4 von 12 Läufen (10,1 % unzufrieden im Mittel), bei Radius 1 keiner. Die Regel „nächste“ entmischt weniger als „zufrieden“ (72,4 % gegen 77,0 % bei τ = 37,5 %).
- **Brücke zu Stück 2 (bestätigt): der Entmischungsindex ist die Modularität der Typen-Partition bis auf eine Konstante.** Die Modularität der Typen im Nachbarschaftsnetz ist *Q* = Anteil gleichartiger Kanten − Σ (*D*<sub>*k*</sub> / 2*m*)<sup>2</sup>; in allen 8 Zellen von Experiment 4 liegt sie höchstens 0,001 neben „Anteil gleichartiger Kanten − ½“.
- **Auf Netzen mit Verbünden entmischt es stärker, und die Typen richten sich an den Verbünden aus:** bei τ = 50 % 82,9 % im Netz „Verbünde“ gegen 72,2 % im Zufallsnetz (Ring: 88,8 %, Gitter: 87,2 %); die NMI der Typen mit den sechs Verbünden steigt von 0,05 (τ = 30 %) auf 0,29 (τ = 50 %).
- **Die Plan-Erwartung „Gemeinschaftserkennung findet die Cluster“ trifft nicht zu:** ein Verfahren, das nur das Nachbarschaftsnetz der belegten Flächen sieht (Greedy-Modularitätsmaximierung), findet 6,2 bis 7,8 **räumliche Blöcke** mit Modularität 0,70 bis 0,75 (schon am zufälligen Start 0,70), nicht die Typen: die NMI mit den Typen ist am Ende höchstens 0,05 bis τ = 50 % und erst bei 60 % 0,43 (Modularität der Typen selbst: 0,05 bis 0,47). Die Messung steht nur in `tests/test_claims.py` (mit `networkx`), nicht in der App.
- **Wortbedeutung:** „Segregation“ meint in `stapelplanung-demo` und `uld-gefahrgut-demo` die Trennung von Gefahrgütern, hier die räumliche Entmischung zweier Typen; der Suchlauf im Portfolio fand keine andere Demo zu Schelling.

## Modell

Gewerbegebiet als **Gitter** (*L* × *L* Flächen, beschränkt, ohne Fortsetzung am Rand; Nachbarn: die 8 Flächen um eine Fläche bei Radius 1, die 24 bei Radius 2) oder als **Netz** (die Betriebe stehen auf den Knoten eines der Netze aus Stück 1, die Nachbarn sind die Netznachbarn). Ein Anteil ρ der Flächen ist belegt, die Hälfte der Betriebe ist Typ A, die andere Typ B, zufällig verteilt; der Rest ist frei. Ein Betrieb ist **zufrieden**, wenn der Anteil seiner belegten Nachbarn vom eigenen Typ mindestens τ ist (Vergleich mit Toleranz 10<sup>−12</sup> gegen die diskreten Anteile); ohne belegte Nachbarn ist er zufrieden. In jedem **Schritt** versucht ein zufälliger unzufriedener Betrieb umzuziehen, nach der **Zugregel**: **zufrieden** (auf eine zufällige freie Fläche, auf der er zufrieden wäre; gibt es keine, bleibt er), **beliebig** (auf eine zufällige freie Fläche) oder **nächste** (auf die nächstgelegene freie Fläche, auf der er zufrieden wäre, im Gitter nach Chebyshev-Abstand, Gleichstand zufällig). **Ende:** alle zufrieden, **blockiert** (es gibt Unzufriedene, aber keiner kann auf eine zulässige Fläche ziehen) oder die **Obergrenze** der Schritte (60 000). **Maße:** Entmischungsindex *S* (mittlerer Anteil gleichartiger Nachbarn über die Betriebe mit mindestens einem Nachbarn), Modularität *Q* der Typen-Partition, Anteil Unzufriedener, Cluster (zusammenhängende Gruppen gleichen Typs) und größter Anteil, Umzüge, Endstatus.

## Methodik

| Baustein | Inhalt |
|---|---|
| **Räume** | Gitter mit Nachbarschaft nach Radius (eigener Code); die Netze aus Stück 1 als Kopie (Zufallsnetz, Potenzgesetz-Netz, skalenfrei (BA), Verbünde = Gewerbeparks, Ring mit Abkürzungen) |
| **Hauptansicht** | Gebiet mit den zwei Typen als Farbe und Ring um die Unzufriedenen, Regler „Schritt“, Verlauf von Entmischungsindex und Anteil Unzufriedener, Kennzahlen (Entmischung, Modularität, Unzufrieden, Cluster, Umzüge, Ende) |
| **Experiment 1** | Entmischungsindex und Endstatus über τ = 10, 20, 25, 30, 37,5, 40, 50, 60, 70, 80 % je Zugregel (Gitter 30 × 30, 90 % belegt, Radius 1; Mittel bzw. Median über 12 feste Starts) |
| **Experiment 2** | Regel „zufrieden“, τ = 37,5 %: Entmischungsindex und Endstatus über den belegten Anteil 50 bis 98 %; Radius 1 gegen Radius 2 über τ = 30 bis 60 % |
| **Experiment 3** | alle Belegungen der Gitter 3 × 3 (3 A, 3 B) und 3 × 4 (2 A, 2 B) als absorbierende Markov-Kette (dichte Rechnung, gleichverteilter Start), je 2000 simulierte Starts als Gegenprobe; τ = 25 bis 75 % |
| **Experiment 4** | Gitter 30 × 30 und Netze mit 240 Flächen (*c* = 8), 85 % belegt, τ = 30 % und 50 %: Entmischungsindex, Modularität der Typen, Anteil gleichartiger Kanten, NMI der Typen mit den Verbünden |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Messreihen: die zwölf festen Starts `SWEEP_SEEDS` je Zelle, Gitter 30 × 30, 90 % belegt, Radius 1, Obergrenze 60 000 Schritte (Experiment 4: Netze mit 240 Flächen, *c* = 8, 85 % belegt); Anteile im Mittel, Schritte und Umzüge im Median. Die App rechnet dieselben Experimente mit fünf Starts und einer Obergrenze von 30 000 Schritten.

| Frage | Befund |
|---|---|
| **Stimmen die Bausteine?** | Entmischungsindex, Anteil gleichartiger Kanten und Modularität gegen Schleifenfassungen und `networkx` auf 110 Zufallsbelegungen (Identität *Q* = Anteil − Σ (*D* / 2*m*)<sup>2</sup>), Cluster gegen Zusammenhangskomponenten, NMI gegen die Kontingenztafel, Zufriedenheit gegen den Bruchvergleich, exakte Kette gegen eine unabhängige Potenziteration auf 2 × 3 Flächen (zwei Regeln, fünf Schwellen) und gegen die Simulation (3 × 3, 3000 Läufe), Endstatus gegen die Definition (`tests/test_oracle_schelling.py`) |
| **Wie stark wirkt die Schwelle, wann blockiert es?** | Tabellen zu Experiment 1 |
| **Freie Flächen und Radius?** | Tabellen zu Experiment 2 |
| **Stimmt die exakte Kette mit der Simulation?** | Tabelle zu Experiment 3 |
| **Brücke zu Stück 2, Netze?** | Tabelle zu Experiment 4 |
| **Gemeinschaftserkennung?** | Tabelle unten (nur in `tests/test_claims.py`) |
| **Standardlauf (Milde Vorliebe, starke Entmischung)** | 810 Betriebe, 90 freie Flächen; Ende „alle zufrieden“ nach 166 Umzügen (166 Schritten): Entmischungsindex 49,9 → 71,1 %, Modularität 0,00 → 0,20, unzufrieden 17,5 → 0,0 %, 11 Cluster (größter 37,9 %) |
| **Preset Hohe Schwelle: die Betriebe blockieren sich** | 810 Betriebe, 90 freie Flächen; Ende „blockiert“ nach 48 Umzügen (3505 Schritten): Entmischungsindex 49,9 → 53,1 %, Modularität 0,00 → 0,04, unzufrieden 83,0 → 73,2 %, 35 Cluster (größter 41,6 %) |
| **Preset Dieselbe Schwelle, beliebige Züge: es endet** | 810 Betriebe, 90 freie Flächen; Ende „alle zufrieden“ nach 4251 Umzügen (4251 Schritten): Entmischungsindex 49,9 → 99,2 %, Modularität 0,00 → 0,49, unzufrieden 83,0 → 0,0 %, 5 Cluster (größter 50,0 %) |
| **Preset Fast kein Platz: einzelne bleiben hängen** | 882 Betriebe, 18 freie Flächen; Ende „blockiert“ nach 201 Umzügen (294 Schritten): Entmischungsindex 49,5 → 76,8 %, Modularität 0,00 → 0,26, unzufrieden 17,0 → 1,0 %, 8 Cluster (größter 48,0 %) |
| **Preset Größerer Radius, mildere Entmischung** | 810 Betriebe, 90 freie Flächen; Ende „alle zufrieden“ nach 63 Umzügen (63 Schritten): Entmischungsindex 49,5 → 55,2 %, Modularität 0,00 → 0,04, unzufrieden 3,7 → 0,0 %, 2 Cluster (größter 50,0 %) |
| **Preset Netz mit Gewerbeparks** | 204 Betriebe, 36 freie Flächen; Ende „alle zufrieden“ nach 94 Umzügen (94 Schritten): Entmischungsindex 50,4 → 84,2 %, Modularität 0,01 → 0,34, unzufrieden 42,6 → 0,0 %, 2 Cluster (größter 50,0 %), NMI der Typen mit den Verbünden 0,35 |

**Experiment 1: Entmischungsindex am Ende** (%, Mittel; Start bei zufälliger Verteilung: 49,7 %):

| Regel | τ = 10 % | τ = 20 % | τ = 25 % | τ = 30 % | τ = 37,5 % | τ = 40 % | τ = 50 % | τ = 60 % | τ = 70 % | τ = 80 % |
|---|---|---|---|---|---|---|---|---|---|---|
| „zufrieden“ | 51,1 | 55,8 | 58,2 | 75,6 | 77,0 | 82,1 | 86,9 | 94,7 | 54,0 | 50,9 |
| „beliebig“ | 51,2 | 55,6 | 57,8 | 75,3 | 76,9 | 83,4 | 87,5 | 97,3 | 99,3 | 60,1 |
| „nächste“ | 50,6 | 54,0 | 55,6 | 70,7 | 72,4 | 78,8 | 83,3 | 96,7 | 53,8 | 50,8 |

**Experiment 1: Läufe, die mit allen zufrieden enden** (von 12; der Rest blockiert, bei „beliebig“ und τ = 80 % erreicht die Obergrenze):

| Regel | τ = 10 % | τ = 20 % | τ = 25 % | τ = 30 % | τ = 37,5 % | τ = 40 % | τ = 50 % | τ = 60 % | τ = 70 % | τ = 80 % |
|---|---|---|---|---|---|---|---|---|---|---|
| „zufrieden“ | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 8 | 0 | 0 |
| „beliebig“ | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 0 |
| „nächste“ | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 11 | 0 | 0 |

**Experiment 1: Schritte bis zum Ende** (Median) und **Umzüge** (Median) in Klammern. Ein Schritt ist der Versuch, einen Unzufriedenen umzusetzen; eine Blockade wird erst festgestellt, wenn jeder Unzufriedene seit dem letzten Umzug einmal vergeblich versucht hat, deshalb liegen die Schritte blockierter Läufe weit über ihren Umzügen. Bei Obergrenze: 60 000:

| Regel | τ = 10 % | τ = 20 % | τ = 25 % | τ = 30 % | τ = 37,5 % | τ = 40 % | τ = 50 % | τ = 60 % | τ = 70 % | τ = 80 % |
|---|---|---|---|---|---|---|---|---|---|---|
| „zufrieden“ | 10,0 (10,0) | 49,0 (49,0) | 70,0 (70,0) | 204,0 (204,0) | 221,5 (221,5) | 276,5 (276,5) | 358,5 (358,5) | 630,5 (571,5) | 3885,0 (55,0) | 5071,0 (15,0) |
| „beliebig“ | 11,0 (11,0) | 57,0 (57,0) | 84,0 (84,0) | 337,5 (337,5) | 380,5 (380,5) | 524,0 (524,0) | 711,5 (711,5) | 2329,0 (2329,0) | 5536,5 (5536,5) | 60000,0 (60000,0) |
| „nächste“ | 9,0 (9,0) | 44,5 (44,5) | 58,5 (58,5) | 181,0 (181,0) | 202,5 (202,5) | 279,0 (279,0) | 364,5 (364,5) | 627,0 (579,5) | 3867,5 (49,0) | 5119,5 (15,0) |

**Experiment 1: Anteil Unzufriedener am Ende** (%, Mittel):

| Regel | τ = 10 % | τ = 20 % | τ = 25 % | τ = 30 % | τ = 37,5 % | τ = 40 % | τ = 50 % | τ = 60 % | τ = 70 % | τ = 80 % |
|---|---|---|---|---|---|---|---|---|---|---|
| „zufrieden“ | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 1,7 | 71,1 | 90,7 |
| „beliebig“ | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 74,6 |
| „nächste“ | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,1 | 71,4 | 91,1 |

**Experiment 2: freie Flächen** (Regel „zufrieden“, τ = 37,5 %, Radius 1):

| belegt (%) | Entmischungsindex am Ende (%) | alle zufrieden (von 12) | blockiert (von 12) | Schritte (Median) | Unzufriedene (%, Mittel) |
|---|---|---|---|---|---|
| 50 | 84,9 | 12 | 0 | 145,5 | 0,00 |
| 60 | 81,6 | 12 | 0 | 170,5 | 0,00 |
| 70 | 80,1 | 12 | 0 | 189,0 | 0,00 |
| 80 | 78,6 | 12 | 0 | 213,0 | 0,00 |
| 90 | 77,0 | 12 | 0 | 213,5 | 0,00 |
| 95 | 76,8 | 12 | 0 | 203,5 | 0,00 |
| 98 | 76,0 | 7 | 5 | 203,0 | 0,16 |

**Experiment 2: Radius** (Regel „zufrieden“, 90 % belegt):

| Radius | τ (%) | Entmischungsindex am Ende (%) | alle zufrieden (von 12) | blockiert (von 12) | Unzufriedene (%, Mittel) |
|---|---|---|---|---|---|
| 1 | 30 | 75,7 | 12 | 0 | 0,0 |
| 1 | 40 | 82,5 | 12 | 0 | 0,0 |
| 1 | 50 | 87,3 | 12 | 0 | 0,0 |
| 1 | 60 | 96,8 | 12 | 0 | 0,0 |
| 2 | 30 | 59,6 | 12 | 0 | 0,0 |
| 2 | 40 | 85,8 | 12 | 0 | 0,0 |
| 2 | 50 | 89,5 | 12 | 0 | 0,0 |
| 2 | 60 | 88,1 | 8 | 4 | 10,1 |

**Experiment 3: exakte Kette** (Belegungen, davon „alle zufrieden“ und blockiert; Wahrscheinlichkeit, zufrieden zu enden, und erwartete Schritte über den gleichverteilten Start; in Klammern die Simulation mit 2000 Starts, Schritte mit Standardfehler. Die Kette absorbiert in einer blockierten Belegung sofort, die Simulation stellt die Blockade erst fest, wenn jeder Unzufriedene einmal vergeblich versucht hat; ihre Schritte sind daher nur ohne Blockaden vergleichbar und sonst mit „–“ bezeichnet):

| Gitter | Regel | τ (%) | Belegungen | zufrieden | blockiert | P(zufrieden) | erwartete Schritte |
|---|---|---|---|---|---|---|---|
| 3 × 3 (3 A, 3 B) | „zufrieden“ | 25 | 1680 | 488 | 0 | 100,0 (100,0) % | 0,96 (1,0 ± 0,0) |
| 3 × 3 (3 A, 3 B) | „zufrieden“ | 34 | 1680 | 144 | 8 | 99,5 (99,5) % | 2,15 (–) |
| 3 × 3 (3 A, 3 B) | „zufrieden“ | 50 | 1680 | 40 | 0 | 100,0 (100,0) % | 3,15 (3,1 ± 0,0) |
| 3 × 3 (3 A, 3 B) | „zufrieden“ | 60 | 1680 | 8 | 160 | 78,8 (79,2) % | 5,28 (–) |
| 3 × 3 (3 A, 3 B) | „zufrieden“ | 67 | 1680 | 4 | 892 | 13,1 (13,2) % | 1,35 (–) |
| 3 × 3 (3 A, 3 B) | „zufrieden“ | 75 | 1680 | 4 | 892 | 13,1 (12,7) % | 1,35 (–) |
| 3 × 3 (3 A, 3 B) | „beliebig“ | 25 | 1680 | 488 | 0 | 100,0 (100,0) % | 1,47 (1,5 ± 0,0) |
| 3 × 3 (3 A, 3 B) | „beliebig“ | 34 | 1680 | 144 | 0 | 100,0 (100,0) % | 4,58 (4,6 ± 0,1) |
| 3 × 3 (3 A, 3 B) | „beliebig“ | 50 | 1680 | 40 | 0 | 100,0 (100,0) % | 6,15 (6,3 ± 0,1) |
| 3 × 3 (3 A, 3 B) | „beliebig“ | 60 | 1680 | 8 | 0 | 100,0 (100,0) % | 29,75 (28,5 ± 0,6) |
| 3 × 3 (3 A, 3 B) | „beliebig“ | 67 | 1680 | 4 | 0 | 100,0 (100,0) % | 182,40 (182,6 ± 4,1) |
| 3 × 3 (3 A, 3 B) | „beliebig“ | 75 | 1680 | 4 | 0 | 100,0 (100,0) % | 182,40 (181,8 ± 4,1) |
| 3 × 4 (2 A, 2 B) | „zufrieden“ | 25 | 2970 | 762 | 0 | 100,0 (100,0) % | 1,09 (1,1 ± 0,0) |
| 3 × 4 (2 A, 2 B) | „zufrieden“ | 34 | 2970 | 454 | 0 | 100,0 (100,0) % | 1,39 (1,4 ± 0,0) |
| 3 × 4 (2 A, 2 B) | „zufrieden“ | 50 | 2970 | 454 | 0 | 100,0 (100,0) % | 1,39 (1,4 ± 0,0) |
| 3 × 4 (2 A, 2 B) | „zufrieden“ | 60 | 2970 | 316 | 4 | 99,9 (99,9) % | 1,84 (–) |
| 3 × 4 (2 A, 2 B) | „zufrieden“ | 67 | 2970 | 316 | 4 | 99,9 (100,0) % | 1,84 (–) |
| 3 × 4 (2 A, 2 B) | „zufrieden“ | 75 | 2970 | 316 | 4 | 99,9 (99,9) % | 1,84 (–) |
| 3 × 4 (2 A, 2 B) | „beliebig“ | 25 | 2970 | 762 | 0 | 100,0 (100,0) % | 1,87 (1,9 ± 0,0) |
| 3 × 4 (2 A, 2 B) | „beliebig“ | 34 | 2970 | 454 | 0 | 100,0 (100,0) % | 2,82 (2,9 ± 0,1) |
| 3 × 4 (2 A, 2 B) | „beliebig“ | 50 | 2970 | 454 | 0 | 100,0 (100,0) % | 2,82 (2,9 ± 0,1) |
| 3 × 4 (2 A, 2 B) | „beliebig“ | 60 | 2970 | 316 | 0 | 100,0 (100,0) % | 5,97 (6,0 ± 0,1) |
| 3 × 4 (2 A, 2 B) | „beliebig“ | 67 | 2970 | 316 | 0 | 100,0 (100,0) % | 5,97 (5,8 ± 0,1) |
| 3 × 4 (2 A, 2 B) | „beliebig“ | 75 | 2970 | 316 | 0 | 100,0 (100,0) % | 5,97 (6,0 ± 0,1) |

**Experiment 4: Brücke zu Stück 2 und Netze** (Regel „zufrieden“, 85 % belegt; Mittel über 12 feste Netze und Starts; *Q*: Modularität der Typen; NMI nur im Netz „Verbünde“):

| Raum | τ (%) | Index am Anfang (%) | Index am Ende (%) | Anteil gleichartiger Kanten (%) | *Q* der Typen | NMI mit den Verbünden | alle zufrieden (von 12) | Umzüge (Median) |
|---|---|---|---|---|---|---|---|---|
| Gitter | 30 | 49,6 | 75,1 | 74,1 | 0,241 | – | 12 | 185,5 |
| Gitter | 50 | 49,6 | 87,2 | 87,1 | 0,370 | – | 12 | 337,0 |
| Zufallsnetz | 30 | 49,5 | 61,3 | 59,9 | 0,098 | – | 12 | 30,5 |
| Zufallsnetz | 50 | 49,5 | 72,2 | 71,1 | 0,211 | – | 12 | 77,0 |
| Verbünde | 30 | 50,0 | 62,9 | 61,5 | 0,115 | 0,05 | 12 | 32,5 |
| Verbünde | 50 | 50,0 | 82,9 | 82,5 | 0,324 | 0,29 | 12 | 100,5 |
| Ring mit Abkürzungen | 30 | 50,2 | 78,7 | 77,6 | 0,275 | – | 12 | 52,5 |
| Ring mit Abkürzungen | 50 | 50,2 | 88,8 | 88,5 | 0,385 | – | 12 | 81,0 |

**Gemeinschaftserkennung** (Greedy-Modularität aus `networkx` auf dem Nachbarschaftsnetz der belegten Flächen, ohne die Typen zu sehen; Gitter 30 × 30, 90 % belegt, Regel „zufrieden“, Mittel über 5 Starts):

| τ (%) | *Q* der Typen am Anfang | *Q* der Typen am Ende | *Q* der Gemeinschaften am Anfang | *Q* der Gemeinschaften am Ende | Gemeinschaften am Ende | NMI mit den Typen am Anfang | NMI mit den Typen am Ende |
|---|---|---|---|---|---|---|---|
| 20 | −0,01 | 0,05 | 0,70 | 0,70 | 6,2 | 0,002 | 0,005 |
| 30 | −0,01 | 0,26 | 0,70 | 0,71 | 6,2 | 0,002 | 0,027 |
| 40 | −0,01 | 0,32 | 0,70 | 0,69 | 6,0 | 0,002 | 0,019 |
| 50 | −0,01 | 0,38 | 0,70 | 0,71 | 5,8 | 0,002 | 0,049 |
| 60 | −0,01 | 0,47 | 0,70 | 0,75 | 7,8 | 0,002 | 0,434 |

### Hypothesen des Einzelplans

|  | Hypothese | Ergebnis |
|---|---|---|
| H1 | Milde Vorlieben erzeugen starke Entmischung, der Übergang ist sprunghaft | ✅ τ = 25 %: 58,2 %, τ = 30 %: 75,6 % (Start 49,7 %) |
| H2 | Ob das Gebiet zur Ruhe kommt, hängt an Zugregel und τ | ✅ „zufrieden“ blockiert ab τ = 60 % (4 von 12) und ab 70 % in allen Läufen; „beliebig“ endet bis 70 %, nicht bei 80 % |
| H3 | Exakt auf kleinen Gittern stimmen Blockaden und Endwahrscheinlichkeit der Kette mit der Simulation überein | ✅ 3 × 3: 892 von 1680 Belegungen blockiert, P(zufrieden) 13,1 % (Simulation 12,7 %) |
| H4 | Mehr freie Flächen erhöhen die Entmischung; ohne freie Fläche blockiert das Gebiet | ✅ 76,0 % → 84,9 % (98 % → 50 % belegt); bei 98 % blockieren 5 von 12 |
| H5 | Größerer Radius und kürzere Zugweite verändern das Ergebnis | ⚠ Radius 2 senkt den Index bei τ = 30 % (59,6 % gegen 75,7 %), hebt ihn bei 40 % und 50 % und blockiert bei 60 %; „nächste“ entmischt weniger |
| H6 | Der Entmischungsindex ist bis auf eine Konstante die Modularität der Typen-Partition | ✅ Abweichung höchstens 0,001 (Orakel: gleich nach der Formel auf 110 Belegungen) |
| H7 | Gemeinschaftserkennung findet die Cluster (Plan) | ❌ findet räumliche Blöcke; NMI mit den Typen höchstens 0,05 bis τ = 50 %, 0,43 bei 60 % |
| H8 | Auf Netzen mit Verbünden entmischt es stärker, die Typen richten sich an den Verbünden aus | ✅ τ = 50 %: 82,9 % gegen 72,2 % im Zufallsnetz, NMI 0,29 (τ = 30 %: 0,05) |

## Ehrliche Grenzen

- **Zwei gleich große Typen, gleiche Schwelle für alle, Standortwahl nur nach Nachbarn:** kein Preis der Fläche, keine Umzugskosten, keine Nähe zu Kunden oder Häfen; mit einem kleinen Typ, mehr als zwei Typen oder verschieden toleranten Betrieben verschieben sich die Schwellen, ab denen es blockiert.
- **Zufällige Auswahl, ein Umzug je Schritt:** mit gleichzeitigen Umzügen oder anderer Reihenfolge ändern sich Dauer und Blockaden. Die Schritte zählen Versuche, einen Unzufriedenen umzusetzen; Umzüge sind die Versuche mit Erfolg. Eine Blockade wird festgestellt, wenn jeder Unzufriedene seit dem letzten Umzug einmal vergeblich versucht hat; die Schritte blockierter Läufe enthalten diese Prüfversuche.
- **Beschränktes Gitter, festes Netz:** das Gitter hat Ränder ohne Fortsetzung (Randflächen haben weniger Nachbarn); in der Netz-Variante sind Flächen und Nachbarschaft vorgegeben, nur die Betriebe wandern. Wie sich das Netz selbst zeitlich ändert, ist Thema des nächsten Stücks (zeitliche Netze).
- **Obergrenze der Schritte:** 60 000 (README-Messreihe) bzw. 30 000 (Experimente der App); „Obergrenze“ heißt nicht „fertig“. Bei „beliebig“ und τ = 80 % erreicht jeder Lauf die Obergrenze, ob er je endet, ist nicht gezeigt.
- **Stichproben:** zwölf feste Starts in der README (fünf in der App), ein Gitter (30 × 30); in Experiment 4 zwölf feste Netze je Typ mit 240 Flächen; die Streuung zwischen den Läufen ist nicht ausgewiesen. Die exakte Kette gilt nur für Gitter bis 4000 Belegungen (3 × 3 und 3 × 4); die Ergebnisse gelten für diese Größen und übertragen sich nicht ohne Weiteres auf große Gitter.
- **Anteile an Typ A fest 50 %, ρ ab 30 %:** andere Anteile sind nicht untersucht.
- **Modellbefund:** die Demo zeigt Verhalten im Modell, keine Wirkung in einer Stadt oder Bevölkerung. Die Betriebstypen sind eine Kulisse für das Modell. Die Einordnung der Blockaden bei Regel „zufrieden“ als „eingefrorene“ Phase (Gauvin, Vannimenus und Nadal 2009) ist eine Vermutung, keine Messung dieser Demo.
- **Literatur (nachgeschlagen am 2026-10-20, nur Zusammenfassungen gesehen):** Schelling, J. Math. Sociol. 1(2), 1971, S. 143–186; Vinković und Kirman, PNAS 103(51), 2006, S. 19261–19265; Gauvin, Vannimenus und Nadal, Eur. Phys. J. B 70, 2009, S. 293–304; Newman und Girvan, Phys. Rev. E 69, 026113 (2004). Die Arbeiten selbst sind nicht vollständig gelesen.

## Verifikation

- **Kern:** Handwerte auf Mini-Instanzen (`tests/conftest.py`, `tests/test_algorithm.py`): Gitter 2 × 2 und 1 × 4 (Index und Modularität), Zeile 1 × 3 (stabile Zustände, erwartete Schritte 8 bzw. 6 aus den Gleichungen der Kette), Nachbarn und Zufriedenheit an den Rändern, Gleichheit an der Schwelle, Cluster und NMI, Endzustände der drei Regeln, die Regel „nächste“ auf einer Zeile, Grenzen und Fehler.
- **Orakel:** `tests/test_oracle_schelling.py` – Maße gegen Schleifenfassungen und `networkx`, Cluster gegen Zusammenhangskomponenten, NMI gegen die Kontingenztafel, Zufriedenheit gegen den Bruchvergleich, exakte Kette gegen eine unabhängige Potenziteration (2 × 3, zwei Regeln × fünf Schwellen) und gegen die Simulation, Erhaltung der Betriebszahlen und Endstatus gegen die Definition.
- **Räume und Läufe:** Nachbarzahlen am Rand und innen, Symmetrie, gültige Netze in allen Ecken der Regler, deterministisch je Seed (auch über Prozesse mit verschiedenem Hash-Seed) (`tests/test_scenario.py`).
- **Verdikte:** jede Schwelle und jede Zahl im Text an von Hand gesetzten Werten (`tests/test_verdicts.py`), Randfälle (Schwelle 0 und 100, volles Gitter, Regel „nächste“ im Netz, Regler-Ecken, kleine Messreihen) in `tests/test_edge_cases.py`.
- **Befunde:** jede Zahl dieser README in `tests/test_claims.py` (Gemeinschaftserkennung mit `networkx` nur dort).
- **Mutationsprüfung des Kerns** (`sch_algorithm.py`, 112 Stellen, ohne die langsamen Aussagen-Tests in der Suite der Überlebenden): 11 Stellen sind durch wortgleiche Zeilen in Nachbar-Demos gesichert, 93 Mutanten gefangen (5 davon erst nach Ergänzung von Tests: die Grenze der exakten Kette, die Konstante bei konstanten Beschriftungen der NMI, das Vorzeichen im Abstand der Regel „nächste“), 6 als äquivalent festgehalten (die Zählung jeder Kante einmal, zwei Nullwächter bei Betrieben ohne Nachbarn, drei Schleifen und eine Verknüpfung in der Behandlung unendlicher Erwartungswerte, die denselben Mittelwert liefern), 2 Zeitüberschreitungen der Simulation (erkannt durch Hängen, im Werkzeug bleiben sie „offen“). Zustand in `tests/mutation_state.json`.
- **Presets:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, jedes Preset zeigt, wofür es benannt ist (Blockade, beliebige Züge, wenige freie Flächen, Radius 2, Netz mit Gewerbeparks).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder aktive Regler am Minimum und Maximum, jeder Raum und jede Zugregel, Schritt-Regler, neuer Lauf, Permalink, alle vier Experimente) und Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `sch_algorithm.py` | Kern: Nachbartabellen, Zufriedenheit, Entmischungsindex, Modularität, Cluster, NMI, Simulation mit drei Zugregeln, exakte Kette |
| `sch_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `sch_evaluation.py` | Analyse, Verdikt-Logik, Messreihen über feste Starts |
| `sch_layout.py` | Fester Kopf (Stylesheet) |
| `sch_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `sch_scenario.py` | Netze: Generatoren (Kopie aus `k-core-demo`), Anordnung |
| `sch_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest, networkx, scipy (nur für die Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen und Handwerte, Orakel, Räume, Verdikte, Randfälle, Presets, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe, Befunde |

## Bewusst nicht umgesetzt

- **Mehr als zwei Typen, ungleiche Anteile, verschieden tolerante Betriebe, Preise und Umzugskosten:** eigene Fragen.
- **Gemeinschaftserkennung in der App:** der Befund steht nur in `tests/test_claims.py`; die App bleibt bei Messgrößen, die sie selbst berechnet.
- **Wohn- oder Bevölkerungskulisse und Daten aus der Wirklichkeit:** nicht Teil der Demo.
- **Gitter über 40 × 40 und exakte Ketten über 4000 Belegungen:** die Läufe wachsen mit der Fläche, die Kette ist dicht.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
