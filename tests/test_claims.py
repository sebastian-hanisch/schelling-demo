"""Jede Zahl aus der README wird hier über dieselben Auswertungsfunktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4).

Messreihen: die zwölf festen Starts `SWEEP_SEEDS` je Zelle (Mittel bzw. Median, siehe die Funktionen in `sch_evaluation.py`); Gitter 30 × 30, belegter Anteil 0,9, Radius 1, Obergrenze 60 000 Schritte
(Experiment 4: Netze mit 240 Flächen, c = 8, belegter Anteil 0,85). Alle Läufe sind deterministisch (feste Seeds, Zufall nur über `numpy.random.default_rng`); Anteile stehen auf vier, Schritte auf eine
Nachkommastelle, die Bänder fangen die Rundung. Die Gemeinschaftserkennung (Greedy-Modularität) kommt nur hier vor und nutzt `networkx`."""

import math
from functools import lru_cache

import networkx as nx
import numpy as np
import pytest
from networkx.algorithms.community import greedy_modularity_communities
from networkx.algorithms.community import modularity as nx_modularity

import sch_algorithm as A
import sch_constants as C
import sch_evaluation as ev

L, RHO, RADIUS = 30, 0.9, 1
RUNS = len(C.SWEEP_SEEDS)
COMM_TAUS, COMM_RUNS = (0.2, 0.3, 0.4, 0.5, 0.6), 5
EXPECT = {'E1': [{'rule': 'zufrieden', 'tau': 0.1, 's0': 0.4967, 's1': 0.5113, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 10.0, 'moves': 10.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'zufrieden', 'tau': 0.2, 's0': 0.4967, 's1': 0.5578, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 49.0, 'moves': 49.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'zufrieden', 'tau': 0.25, 's0': 0.4967, 's1': 0.5819, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 70.0, 'moves': 70.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'zufrieden', 'tau': 0.3, 's0': 0.4967, 's1': 0.756, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 204.0, 'moves': 204.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'zufrieden',
         'tau': 0.375,
         's0': 0.4967,
         's1': 0.7701,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 221.5,
         'moves': 221.5,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'zufrieden',
         'tau': 0.4,
         's0': 0.4967,
         's1': 0.8207,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 276.5,
         'moves': 276.5,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'zufrieden',
         'tau': 0.5,
         's0': 0.4967,
         's1': 0.8691,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 358.5,
         'moves': 358.5,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'zufrieden',
         'tau': 0.6,
         's0': 0.4967,
         's1': 0.9465,
         'done': 0.6667,
         'blocked': 0.3333,
         'cap': 0.0,
         'steps': 630.5,
         'moves': 571.5,
         'unhappy': 0.0167,
         'runs': 12},
        {'rule': 'zufrieden',
         'tau': 0.7,
         's0': 0.4967,
         's1': 0.5404,
         'done': 0.0,
         'blocked': 1.0,
         'cap': 0.0,
         'steps': 3885.0,
         'moves': 55.0,
         'unhappy': 0.7111,
         'runs': 12},
        {'rule': 'zufrieden',
         'tau': 0.8,
         's0': 0.4967,
         's1': 0.509,
         'done': 0.0,
         'blocked': 1.0,
         'cap': 0.0,
         'steps': 5071.0,
         'moves': 15.0,
         'unhappy': 0.9074,
         'runs': 12},
        {'rule': 'beliebig', 'tau': 0.1, 's0': 0.4967, 's1': 0.5117, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 11.0, 'moves': 11.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'beliebig', 'tau': 0.2, 's0': 0.4967, 's1': 0.5561, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 57.0, 'moves': 57.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'beliebig', 'tau': 0.25, 's0': 0.4967, 's1': 0.5783, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 84.0, 'moves': 84.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'beliebig', 'tau': 0.3, 's0': 0.4967, 's1': 0.7529, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 337.5, 'moves': 337.5, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'beliebig',
         'tau': 0.375,
         's0': 0.4967,
         's1': 0.7691,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 380.5,
         'moves': 380.5,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'beliebig', 'tau': 0.4, 's0': 0.4967, 's1': 0.8336, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 524.0, 'moves': 524.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'beliebig', 'tau': 0.5, 's0': 0.4967, 's1': 0.875, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 711.5, 'moves': 711.5, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'beliebig',
         'tau': 0.6,
         's0': 0.4967,
         's1': 0.9728,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 2329.0,
         'moves': 2329.0,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'beliebig',
         'tau': 0.7,
         's0': 0.4967,
         's1': 0.9926,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 5536.5,
         'moves': 5536.5,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'beliebig',
         'tau': 0.8,
         's0': 0.4967,
         's1': 0.6013,
         'done': 0.0,
         'blocked': 0.0,
         'cap': 1.0,
         'steps': 60000.0,
         'moves': 60000.0,
         'unhappy': 0.7463,
         'runs': 12},
        {'rule': 'nächste', 'tau': 0.1, 's0': 0.4967, 's1': 0.5063, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 9.0, 'moves': 9.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'nächste', 'tau': 0.2, 's0': 0.4967, 's1': 0.5399, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 44.5, 'moves': 44.5, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'nächste', 'tau': 0.25, 's0': 0.4967, 's1': 0.5562, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 58.5, 'moves': 58.5, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'nächste', 'tau': 0.3, 's0': 0.4967, 's1': 0.7065, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 181.0, 'moves': 181.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'nächste',
         'tau': 0.375,
         's0': 0.4967,
         's1': 0.7235,
         'done': 1.0,
         'blocked': 0.0,
         'cap': 0.0,
         'steps': 202.5,
         'moves': 202.5,
         'unhappy': 0.0,
         'runs': 12},
        {'rule': 'nächste', 'tau': 0.4, 's0': 0.4967, 's1': 0.788, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 279.0, 'moves': 279.0, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'nächste', 'tau': 0.5, 's0': 0.4967, 's1': 0.8331, 'done': 1.0, 'blocked': 0.0, 'cap': 0.0, 'steps': 364.5, 'moves': 364.5, 'unhappy': 0.0, 'runs': 12},
        {'rule': 'nächste',
         'tau': 0.6,
         's0': 0.4967,
         's1': 0.9665,
         'done': 0.9167,
         'blocked': 0.0833,
         'cap': 0.0,
         'steps': 627.0,
         'moves': 579.5,
         'unhappy': 0.0005,
         'runs': 12},
        {'rule': 'nächste',
         'tau': 0.7,
         's0': 0.4967,
         's1': 0.5378,
         'done': 0.0,
         'blocked': 1.0,
         'cap': 0.0,
         'steps': 3867.5,
         'moves': 49.0,
         'unhappy': 0.7137,
         'runs': 12},
        {'rule': 'nächste',
         'tau': 0.8,
         's0': 0.4967,
         's1': 0.5083,
         'done': 0.0,
         'blocked': 1.0,
         'cap': 0.0,
         'steps': 5119.5,
         'moves': 15.0,
         'unhappy': 0.9106,
         'runs': 12}],
 'E2': {'vacancy': [{'rho': 0.5, 's1': 0.8492, 'done': 1.0, 'blocked': 0.0, 'steps': 145.5, 'unhappy': 0.0, 'runs': 12},
                    {'rho': 0.6, 's1': 0.8162, 'done': 1.0, 'blocked': 0.0, 'steps': 170.5, 'unhappy': 0.0, 'runs': 12},
                    {'rho': 0.7, 's1': 0.8009, 'done': 1.0, 'blocked': 0.0, 'steps': 189.0, 'unhappy': 0.0, 'runs': 12},
                    {'rho': 0.8, 's1': 0.7864, 'done': 1.0, 'blocked': 0.0, 'steps': 213.0, 'unhappy': 0.0, 'runs': 12},
                    {'rho': 0.9, 's1': 0.77, 'done': 1.0, 'blocked': 0.0, 'steps': 213.5, 'unhappy': 0.0, 'runs': 12},
                    {'rho': 0.95, 's1': 0.7681, 'done': 1.0, 'blocked': 0.0, 'steps': 203.5, 'unhappy': 0.0, 'runs': 12},
                    {'rho': 0.98, 's1': 0.7601, 'done': 0.5833, 'blocked': 0.4167, 'steps': 203.0, 'unhappy': 0.0016, 'runs': 12}],
        'radius': [{'radius': 1, 'tau': 0.3, 's1': 0.7569, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 1, 'tau': 0.4, 's1': 0.8255, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 1, 'tau': 0.5, 's1': 0.873, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 1, 'tau': 0.6, 's1': 0.9684, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 2, 'tau': 0.3, 's1': 0.5961, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 2, 'tau': 0.4, 's1': 0.8576, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 2, 'tau': 0.5, 's1': 0.8951, 'done': 1.0, 'blocked': 0.0, 'unhappy': 0.0, 'runs': 12},
                   {'radius': 2, 'tau': 0.6, 's1': 0.8814, 'done': 0.6667, 'blocked': 0.3333, 'unhappy': 0.1007, 'runs': 12}],
        'tau': 0.375},
 'E3': [{'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'zufrieden',
         'tau': 0.25,
         'states': 1680,
         'done': 488,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 0.962,
         'sim_p_done': 1.0,
         'sim_steps': 0.97,
         'sim_se': 0.02},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'zufrieden',
         'tau': 0.34,
         'states': 1680,
         'done': 144,
         'blocked': 8,
         'p_done': 0.995238,
         'steps': 2.15,
         'sim_p_done': 0.995,
         'sim_steps': 2.21,
         'sim_se': 0.04},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'zufrieden',
         'tau': 0.5,
         'states': 1680,
         'done': 40,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 3.145,
         'sim_p_done': 1.0,
         'sim_steps': 3.15,
         'sim_se': 0.04},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'zufrieden',
         'tau': 0.6,
         'states': 1680,
         'done': 8,
         'blocked': 160,
         'p_done': 0.78836,
         'steps': 5.275,
         'sim_p_done': 0.7925,
         'sim_steps': 7.24,
         'sim_se': 0.12},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'zufrieden',
         'tau': 0.67,
         'states': 1680,
         'done': 4,
         'blocked': 892,
         'p_done': 0.131481,
         'steps': 1.352,
         'sim_p_done': 0.132,
         'sim_steps': 11.67,
         'sim_se': 0.13},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'zufrieden',
         'tau': 0.75,
         'states': 1680,
         'done': 4,
         'blocked': 892,
         'p_done': 0.131481,
         'steps': 1.352,
         'sim_p_done': 0.127,
         'sim_steps': 11.57,
         'sim_se': 0.13},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'beliebig',
         'tau': 0.25,
         'states': 1680,
         'done': 488,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 1.466,
         'sim_p_done': 1.0,
         'sim_steps': 1.48,
         'sim_se': 0.03},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'beliebig',
         'tau': 0.34,
         'states': 1680,
         'done': 144,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 4.581,
         'sim_p_done': 1.0,
         'sim_steps': 4.56,
         'sim_se': 0.11},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'beliebig',
         'tau': 0.5,
         'states': 1680,
         'done': 40,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 6.146,
         'sim_p_done': 1.0,
         'sim_steps': 6.31,
         'sim_se': 0.1},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'beliebig',
         'tau': 0.6,
         'states': 1680,
         'done': 8,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 29.749,
         'sim_p_done': 1.0,
         'sim_steps': 28.49,
         'sim_se': 0.6},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'beliebig',
         'tau': 0.67,
         'states': 1680,
         'done': 4,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 182.397,
         'sim_p_done': 1.0,
         'sim_steps': 182.62,
         'sim_se': 4.09},
        {'grid': '3 × 3 (3 A, 3 B)',
         'rule': 'beliebig',
         'tau': 0.75,
         'states': 1680,
         'done': 4,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 182.397,
         'sim_p_done': 1.0,
         'sim_steps': 181.78,
         'sim_se': 4.11},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'zufrieden',
         'tau': 0.25,
         'states': 2970,
         'done': 762,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 1.087,
         'sim_p_done': 1.0,
         'sim_steps': 1.07,
         'sim_se': 0.02},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'zufrieden',
         'tau': 0.34,
         'states': 2970,
         'done': 454,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 1.391,
         'sim_p_done': 1.0,
         'sim_steps': 1.39,
         'sim_se': 0.02},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'zufrieden',
         'tau': 0.5,
         'states': 2970,
         'done': 454,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 1.391,
         'sim_p_done': 1.0,
         'sim_steps': 1.43,
         'sim_se': 0.02},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'zufrieden',
         'tau': 0.6,
         'states': 2970,
         'done': 316,
         'blocked': 4,
         'p_done': 0.998653,
         'steps': 1.839,
         'sim_p_done': 0.999,
         'sim_steps': 1.87,
         'sim_se': 0.03},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'zufrieden',
         'tau': 0.67,
         'states': 2970,
         'done': 316,
         'blocked': 4,
         'p_done': 0.998653,
         'steps': 1.839,
         'sim_p_done': 0.9995,
         'sim_steps': 1.88,
         'sim_se': 0.03},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'zufrieden',
         'tau': 0.75,
         'states': 2970,
         'done': 316,
         'blocked': 4,
         'p_done': 0.998653,
         'steps': 1.839,
         'sim_p_done': 0.999,
         'sim_steps': 1.84,
         'sim_se': 0.03},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'beliebig',
         'tau': 0.25,
         'states': 2970,
         'done': 762,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 1.874,
         'sim_p_done': 1.0,
         'sim_steps': 1.93,
         'sim_se': 0.04},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'beliebig',
         'tau': 0.34,
         'states': 2970,
         'done': 454,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 2.824,
         'sim_p_done': 1.0,
         'sim_steps': 2.94,
         'sim_se': 0.06},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'beliebig',
         'tau': 0.5,
         'states': 2970,
         'done': 454,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 2.824,
         'sim_p_done': 1.0,
         'sim_steps': 2.86,
         'sim_se': 0.06},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'beliebig',
         'tau': 0.6,
         'states': 2970,
         'done': 316,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 5.968,
         'sim_p_done': 1.0,
         'sim_steps': 6.0,
         'sim_se': 0.14},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'beliebig',
         'tau': 0.67,
         'states': 2970,
         'done': 316,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 5.968,
         'sim_p_done': 1.0,
         'sim_steps': 5.75,
         'sim_se': 0.13},
        {'grid': '3 × 4 (2 A, 2 B)',
         'rule': 'beliebig',
         'tau': 0.75,
         'states': 2970,
         'done': 316,
         'blocked': 0,
         'p_done': 1.0,
         'steps': 5.968,
         'sim_p_done': 1.0,
         'sim_steps': 6.01,
         'sim_se': 0.14}],
 'E4': [{'space': 'Gitter', 'tau': 0.3, 's0': 0.4959, 's1': 0.7511, 'q1': 0.2409, 'e1': 0.7411, 'unhappy': 0.0, 'done': 1.0, 'nmi': None, 'moves': 185.5, 'runs': 12},
        {'space': 'Gitter', 'tau': 0.5, 's0': 0.4959, 's1': 0.8716, 'q1': 0.3705, 'e1': 0.8706, 'unhappy': 0.0, 'done': 1.0, 'nmi': None, 'moves': 337.0, 'runs': 12},
        {'space': 'Zufallsnetz', 'tau': 0.3, 's0': 0.4953, 's1': 0.6126, 'q1': 0.0982, 'e1': 0.5985, 'unhappy': 0.0, 'done': 1.0, 'nmi': None, 'moves': 30.5, 'runs': 12},
        {'space': 'Zufallsnetz', 'tau': 0.5, 's0': 0.4953, 's1': 0.7222, 'q1': 0.2108, 'e1': 0.7112, 'unhappy': 0.0, 'done': 1.0, 'nmi': None, 'moves': 77.0, 'runs': 12},
        {'space': 'Verbünde', 'tau': 0.3, 's0': 0.5005, 's1': 0.6292, 'q1': 0.1145, 'e1': 0.6149, 'unhappy': 0.0, 'done': 1.0, 'nmi': 0.0458, 'moves': 32.5, 'runs': 12},
        {'space': 'Verbünde', 'tau': 0.5, 's0': 0.5005, 's1': 0.8292, 'q1': 0.3244, 'e1': 0.8249, 'unhappy': 0.0, 'done': 1.0, 'nmi': 0.2906, 'moves': 100.5, 'runs': 12},
        {'space': 'Ring mit Abkürzungen',
         'tau': 0.3,
         's0': 0.5017,
         's1': 0.7873,
         'q1': 0.2751,
         'e1': 0.7763,
         'unhappy': 0.0,
         'done': 1.0,
         'nmi': None,
         'moves': 52.5,
         'runs': 12},
        {'space': 'Ring mit Abkürzungen',
         'tau': 0.5,
         's0': 0.5017,
         's1': 0.8884,
         'q1': 0.3847,
         'e1': 0.8851,
         'unhappy': 0.0,
         'done': 1.0,
         'nmi': None,
         'moves': 81.0,
         'runs': 12}],
 'D': [{'tau': 0.2, 'q_types0': -0.006, 'q_types1': 0.051, 'q_greedy0': 0.703, 'q_greedy1': 0.702, 'nmi0': 0.002, 'nmi1': 0.005, 'communities1': 6.2},
       {'tau': 0.3, 'q_types0': -0.006, 'q_types1': 0.26, 'q_greedy0': 0.703, 'q_greedy1': 0.707, 'nmi0': 0.002, 'nmi1': 0.027, 'communities1': 6.2},
       {'tau': 0.4, 'q_types0': -0.006, 'q_types1': 0.323, 'q_greedy0': 0.703, 'q_greedy1': 0.695, 'nmi0': 0.002, 'nmi1': 0.019, 'communities1': 6.0},
       {'tau': 0.5, 'q_types0': -0.006, 'q_types1': 0.378, 'q_greedy0': 0.703, 'q_greedy1': 0.712, 'nmi0': 0.002, 'nmi1': 0.049, 'communities1': 5.8},
       {'tau': 0.6, 'q_types0': -0.006, 'q_types1': 0.471, 'q_greedy0': 0.703, 'q_greedy1': 0.749, 'nmi0': 0.002, 'nmi1': 0.434, 'communities1': 7.8}],
 'presets': {'Milde Vorliebe, starke Entmischung (Voreinstellung)': {'agents': 810,
                                                                     'free': 90,
                                                                     'status': 'zufrieden',
                                                                     'steps': 166,
                                                                     'moves': 166,
                                                                     's0': 0.4987,
                                                                     's1': 0.7113,
                                                                     'q0': -0.0009,
                                                                     'q1': 0.2046,
                                                                     'unhappy0': 0.1753,
                                                                     'unhappy1': 0.0,
                                                                     'clusters': 11,
                                                                     'largest': 0.379,
                                                                     'nmi1': None,
                                                                     'kind': 'success',
                                                                     'verdict': 'Nach 166 Umzügen (166 Schritten) sind alle 810 Betriebe zufrieden. Der Anteil '
                                                                                'gleichartiger Nachbarn geht von 50 % auf 71 %, die Modularität der Typen von 0,00 auf '
                                                                                '0,20; es bleiben 11 Cluster gleichartiger Betriebe, der größte mit 38 % der Betriebe.'},
             'Hohe Schwelle: die Betriebe blockieren sich': {'agents': 810,
                                                             'free': 90,
                                                             'status': 'blockiert',
                                                             'steps': 3505,
                                                             'moves': 48,
                                                             's0': 0.4987,
                                                             's1': 0.5313,
                                                             'q0': -0.0009,
                                                             'q1': 0.0353,
                                                             'unhappy0': 0.8296,
                                                             'unhappy1': 0.7321,
                                                             'clusters': 35,
                                                             'largest': 0.416,
                                                             'nmi1': None,
                                                             'kind': 'warning',
                                                             'verdict': 'Nach 48 Umzügen (3505 Schritten) blockiert: 73 % der 810 Betriebe sind unzufrieden, und keiner '
                                                                        'findet eine freie Fläche, auf der er zufrieden wäre. Der Anteil gleichartiger Nachbarn geht von '
                                                                        '50 % auf 53 %, die Modularität der Typen von 0,00 auf 0,04. Mit der Regel „Auf eine beliebige '
                                                                        'freie Fläche“ würden sie dennoch weiterziehen.'},
             'Dieselbe Schwelle, beliebige Züge: es endet': {'agents': 810,
                                                             'free': 90,
                                                             'status': 'zufrieden',
                                                             'steps': 4251,
                                                             'moves': 4251,
                                                             's0': 0.4987,
                                                             's1': 0.992,
                                                             'q0': -0.0009,
                                                             'q1': 0.494,
                                                             'unhappy0': 0.8296,
                                                             'unhappy1': 0.0,
                                                             'clusters': 5,
                                                             'largest': 0.5,
                                                             'nmi1': None,
                                                             'kind': 'success',
                                                             'verdict': 'Nach 4251 Umzügen (4251 Schritten) sind alle 810 Betriebe zufrieden. Der Anteil gleichartiger '
                                                                        'Nachbarn geht von 50 % auf 99 %, die Modularität der Typen von 0,00 auf 0,49; es bleiben 5 '
                                                                        'Cluster gleichartiger Betriebe, der größte mit 50 % der Betriebe.'},
             'Fast kein Platz: einzelne bleiben hängen': {'agents': 882,
                                                          'free': 18,
                                                          'status': 'blockiert',
                                                          'steps': 294,
                                                          'moves': 201,
                                                          's0': 0.4954,
                                                          's1': 0.7675,
                                                          'q0': -0.0047,
                                                          'q1': 0.2622,
                                                          'unhappy0': 0.1701,
                                                          'unhappy1': 0.0102,
                                                          'clusters': 8,
                                                          'largest': 0.4796,
                                                          'nmi1': None,
                                                          'kind': 'warning',
                                                          'verdict': 'Nach 201 Umzügen (294 Schritten) blockiert: 1 % der 882 Betriebe sind unzufrieden, und keiner '
                                                                     'findet eine freie Fläche, auf der er zufrieden wäre. Der Anteil gleichartiger Nachbarn geht von 50 '
                                                                     '% auf 77 %, die Modularität der Typen von 0,00 auf 0,26. Mit der Regel „Auf eine beliebige freie '
                                                                     'Fläche“ würden sie dennoch weiterziehen.'},
             'Größerer Radius, mildere Entmischung': {'agents': 810,
                                                      'free': 90,
                                                      'status': 'zufrieden',
                                                      'steps': 63,
                                                      'moves': 63,
                                                      's0': 0.4949,
                                                      's1': 0.5516,
                                                      'q0': -0.004,
                                                      'q1': 0.0402,
                                                      'unhappy0': 0.037,
                                                      'unhappy1': 0.0,
                                                      'clusters': 2,
                                                      'largest': 0.5,
                                                      'nmi1': None,
                                                      'kind': 'info',
                                                      'verdict': 'Nach 63 Umzügen (63 Schritten) sind alle 810 Betriebe zufrieden. Der Anteil gleichartiger Nachbarn '
                                                                 'geht von 49 % auf 55 %, die Modularität der Typen von 0,00 auf 0,04; es bleiben 2 Cluster '
                                                                 'gleichartiger Betriebe, der größte mit 50 % der Betriebe.'},
             'Netz mit Gewerbeparks': {'agents': 204,
                                       'free': 36,
                                       'status': 'zufrieden',
                                       'steps': 94,
                                       'moves': 94,
                                       's0': 0.5038,
                                       's1': 0.8421,
                                       'q0': 0.0073,
                                       'q1': 0.3403,
                                       'unhappy0': 0.4265,
                                       'unhappy1': 0.0,
                                       'clusters': 2,
                                       'largest': 0.5,
                                       'nmi1': 0.3464,
                                       'kind': 'success',
                                       'verdict': 'Nach 94 Umzügen (94 Schritten) sind alle 204 Betriebe zufrieden. Der Anteil gleichartiger Nachbarn geht von 50 % auf '
                                                  '84 %, die Modularität der Typen von 0,01 auf 0,34; es bleiben 2 Cluster gleichartiger Betriebe, der größte mit 50 % '
                                                  'der Betriebe.'}},
 'V_E1': 'Entmischungsindex (mittlerer Anteil gleichartiger Nachbarn) vor und nach den Umzügen, je Regel: „Nur auf eine zufriedenstellende Fläche“: Entmischungsindex 50 '
         '% → 76 % bei τ = 30 %; nicht mehr jeder Lauf endet zufrieden ab τ = 60 %, keiner ab τ = 70 %; „Auf eine beliebige freie Fläche“: Entmischungsindex 50 % → 75 % '
         'bei τ = 30 %; ab τ = 80 % endet kein Lauf mehr zufrieden; „Auf die nächste zufriedenstellende Fläche“: Entmischungsindex 50 % → 71 % bei τ = 30 %; nicht mehr '
         'jeder Lauf endet zufrieden ab τ = 60 %, keiner ab τ = 70 %.',
 'V_E2': 'Bei τ = 37,5 % und 98 % belegten Flächen liegt der Entmischungsindex am Ende bei 76 %, bei 50 % belegt bei 85 %; bei 98 % belegt enden 58 % der Läufe '
         'zufrieden und 42 % blockieren. Radius 2 statt 1: bei τ = 30 % 60 % statt 76 %; bei τ = 60 % enden 67 % statt 100 % der Läufe zufrieden.',
 'V_E3': 'Auf dem Gitter 3 × 3 (3 A, 3 B) (alle 1680 Belegungen, exakt) sind bei τ = 75 % 892 Belegungen blockiert; mit der Regel „Nur auf eine zufriedenstellende '
         'Fläche“ endet nur 13,1 % der Starts zufrieden (Simulation: 12,7 %), mit „Auf eine beliebige freie Fläche“ 100,0 % nach im Mittel 182,4 Schritten (Simulation: '
         '181,8 ± 4,1).',
 'V_E4': 'Bei τ = 50 % liegt der Entmischungsindex am Ende im Gitter bei 87 %, im Zufallsnetz bei 72 %, im Netz „Verbünde“ bei 83 %, im Netz „Ring mit Abkürzungen“ bei '
         '89 %; die Typen stimmen mit den Verbünden zu NMI 0,29 überein. Die Modularität der Typen-Partition liegt höchstens 0,001 neben dem Anteil gleichartiger Kanten '
         'minus ½.'}


@lru_cache(maxsize=None)
def _e1():
    return ev.tau_rows(L, RHO, RADIUS, runs=RUNS, max_steps=C.MAX_STEPS)


@lru_cache(maxsize=None)
def _e2():
    return ev.space_rows(L, C.VACANCY_TAU, RADIUS, runs=RUNS, rho_radius=RHO, max_steps=C.MAX_STEPS)


@lru_cache(maxsize=None)
def _e3():
    return ev.exact_rows()


@lru_cache(maxsize=None)
def _e4():
    return ev.bridge_rows(L, runs=RUNS)


@lru_cache(maxsize=None)
def _communities():
    """Greedy-Modularitätsmaximierung auf dem Nachbarschaftsnetz der belegten Flächen: sie sieht nur das Netz, nicht die Typen."""
    sp = ev.build_space(C.T_GRID, L, 0, 0, RADIUS, 0)
    rows = []
    for ti, tau in enumerate(COMM_TAUS):
        acc = {"q_types0": [], "q_types1": [], "q_greedy0": [], "q_greedy1": [], "nmi0": [], "nmi1": [], "communities1": []}
        for seed in C.SWEEP_SEEDS[:COMM_RUNS]:
            t0 = A.initial_types(sp.n_cells, RHO, C.FRAC_A, ev._rng(seed, 10))
            out = A.simulate(sp.nbrs, t0, tau, C.R_HAPPY, ev._rng(seed, 11, 0, ti), C.MAX_STEPS, positions=sp.positions)
            for tag, types in (("0", t0), ("1", out["types"])):
                g = nx.Graph()
                g.add_nodes_from(c for c, t in enumerate(types) if t)
                for c, t in enumerate(types):
                    if t:
                        g.add_edges_from((c, q) for q in sp.nbrs[c] if types[q])
                parts = [set(p) for p in greedy_modularity_communities(g)]
                labels = [0] * sp.n_cells
                for k, p in enumerate(parts):
                    for c in p:
                        labels[c] = k
                acc["q_types" + tag].append(A.modularity(types, sp.nbrs))
                acc["q_greedy" + tag].append(nx_modularity(g, parts))
                acc["nmi" + tag].append(A.nmi(types, labels))
                if tag == "1":
                    acc["communities1"].append(len(parts))
        rows.append({"tau": tau, **{k: float(np.mean(v)) for k, v in acc.items()}})
    return rows


def _band(x, digits):
    return pytest.approx(x, abs=0.6 * 10.0**-digits)


def _e1_cell(rule, tau):
    return ev.tau_cell(_e1(), rule, tau)


# --- E1: Schwelle und Zugregel ------------------------------------------------------------------------------------------------------------------------


def test_threshold_table():
    rows = _e1()
    assert len(rows) == len(EXPECT["E1"]) == len(C.RULES) * len(C.TAU_GRID)
    for got, exp in zip(rows, EXPECT["E1"]):
        assert (got["rule"], got["tau"], got["runs"]) == (exp["rule"], exp["tau"], exp["runs"]), exp
        for key, digits in (("s0", 4), ("s1", 4), ("done", 4), ("blocked", 4), ("cap", 4), ("unhappy", 4), ("steps", 1), ("moves", 1)):
            assert got[key] == _band(exp[key], digits), (exp["rule"], exp["tau"], key)
    assert ev.verdict_tau(rows)[1] == EXPECT["V_E1"]


def test_a_mild_threshold_unmixes_strongly_and_the_jump_sits_between_25_and_30_percent():
    s = {t: _e1_cell(C.R_HAPPY, t)["s1"] for t in C.TAU_GRID}
    start = _e1_cell(C.R_HAPPY, 0.3)["s0"]
    assert 0.49 < start < 0.51 and s[0.25] < 0.6 < 0.75 < s[0.3] and s[0.3] - s[0.25] > 0.15                  # H1: τ = 0,25 kaum, τ = 0,30 stark
    assert all(s[a] <= s[b] for a, b in zip(C.TAU_GRID[:8], C.TAU_GRID[1:8]))                                 # bis τ = 0,6 steigt die Entmischung mit der Schwelle


def test_the_move_rule_decides_whether_the_area_comes_to_rest():
    happy = {t: _e1_cell(C.R_HAPPY, t) for t in C.TAU_GRID}
    anyrule = {t: _e1_cell(C.R_ANY, t) for t in C.TAU_GRID}
    near = {t: _e1_cell(C.R_NEAR, t) for t in C.TAU_GRID}
    assert all(happy[t]["done"] == 1.0 for t in C.TAU_GRID if t <= 0.5) and 0 < happy[0.6]["done"] < 1 and happy[0.7]["blocked"] == happy[0.8]["blocked"] == 1.0   # H2: „zufrieden“ blockiert ab τ = 0,6 bis 0,7
    assert all(anyrule[t]["done"] == 1.0 for t in C.TAU_GRID if t <= 0.7) and anyrule[0.8]["cap"] == 1.0 and anyrule[0.8]["done"] == 0.0 and anyrule[0.8]["blocked"] == 0.0
    assert 0 < near[0.6]["done"] < 1 and near[0.7]["blocked"] == near[0.8]["blocked"] == 1.0
    assert anyrule[0.7]["s1"] > 0.99 and happy[0.7]["s1"] < 0.6 and happy[0.7]["unhappy"] > 0.5 and happy[0.8]["unhappy"] > 0.8        # Blockade: die meisten bleiben unzufrieden
    assert anyrule[0.7]["steps"] > 10 * anyrule[0.375]["steps"] > 10 * happy[0.375]["steps"] / 2


def test_the_blockade_really_occurs_and_each_rule_has_a_threshold_where_its_ending_differs_from_the_others():
    rows = _e1()
    assert any(r["blocked"] > 0 for r in rows) and any(r["cap"] > 0 for r in rows) and any(r["done"] == 1.0 for r in rows)               # keine Nullspalte: alle drei Endstati kommen vor
    for rule in C.RULES:
        others = [r for r in C.RULES if r != rule]
        assert any((_e1_cell(rule, t)["done"], _e1_cell(rule, t)["blocked"], _e1_cell(rule, t)["cap"]) != (_e1_cell(o, t)["done"], _e1_cell(o, t)["blocked"], _e1_cell(o, t)["cap"]) for o in others for t in C.TAU_GRID), rule


def test_the_nearest_rule_unmixes_less_than_the_happy_rule_at_a_moderate_threshold():
    assert all(_e1_cell(C.R_NEAR, t)["s1"] < _e1_cell(C.R_HAPPY, t)["s1"] for t in (0.2, 0.3, 0.375, 0.4, 0.5))


# --- E2: freie Flächen und Radius --------------------------------------------------------------------------------------------------------------------


def test_vacancy_and_radius_tables():
    res = _e2()
    assert len(res["vacancy"]) == len(EXPECT["E2"]["vacancy"]) == len(C.RHO_GRID) and len(res["radius"]) == len(EXPECT["E2"]["radius"]) == 8
    for got, exp in zip(res["vacancy"], EXPECT["E2"]["vacancy"]):
        assert got["rho"] == exp["rho"] and got["runs"] == exp["runs"]
        for key, digits in (("s1", 4), ("done", 4), ("blocked", 4), ("unhappy", 4), ("steps", 1)):
            assert got[key] == _band(exp[key], digits), (exp["rho"], key)
    for got, exp in zip(res["radius"], EXPECT["E2"]["radius"]):
        assert (got["radius"], got["tau"], got["runs"]) == (exp["radius"], exp["tau"], exp["runs"])
        for key in ("s1", "done", "blocked", "unhappy"):
            assert got[key] == _band(exp[key], 4), (exp["radius"], exp["tau"], key)
    assert ev.verdict_space(res)[1] == EXPECT["V_E2"]


def test_more_vacancies_unmix_more_and_a_nearly_full_area_blocks():
    vac = _e2()["vacancy"]
    s = [r["s1"] for r in vac]
    assert s == sorted(s, reverse=True) and s[0] - s[-1] > 0.08                                                  # H4: je mehr freie Flächen, desto stärker die Entmischung
    assert all(r["done"] == 1.0 for r in vac[:-1]) and vac[-1]["rho"] == 0.98 and 0 < vac[-1]["done"] < 1 and vac[-1]["blocked"] > 0.3


def test_the_larger_radius_unmixes_less_at_the_mild_and_the_high_threshold_and_more_in_between():
    by = {(r["radius"], r["tau"]): r for r in _e2()["radius"]}
    assert by[(2, 0.3)]["s1"] < by[(1, 0.3)]["s1"] - 0.1 and by[(2, 0.4)]["s1"] > by[(1, 0.4)]["s1"] and by[(2, 0.5)]["s1"] > by[(1, 0.5)]["s1"] and by[(2, 0.6)]["s1"] < by[(1, 0.6)]["s1"] - 0.05
    assert by[(1, 0.6)]["done"] == 1.0 and 0 < by[(2, 0.6)]["done"] < 1 and by[(2, 0.6)]["unhappy"] > 0.05                  # H5: bei Radius 2 blockiert τ = 0,6 schon


# --- E3: exakte Kette ----------------------------------------------------------------------------------------------------------------------------------


def test_exact_table_and_simulation():
    rows = _e3()
    assert len(rows) == len(EXPECT["E3"]) == len(C.EXACT_GRIDS) * 2 * len(C.EXACT_TAUS)
    for got, exp in zip(rows, EXPECT["E3"]):
        assert (got["grid"], got["rule"], got["tau"], got["states"], got["done"], got["blocked"]) == (exp["grid"], exp["rule"], exp["tau"], exp["states"], exp["done"], exp["blocked"]), exp
        assert got["p_done"] == _band(exp["p_done"], 4) and got["sim_p_done"] == _band(exp["sim_p_done"], 4) and got["sim_steps"] == _band(exp["sim_steps"], 2) and got["sim_se"] == _band(exp["sim_se"], 2)
        if exp["steps"] is None:
            assert math.isinf(got["steps"])
        else:
            assert got["steps"] == _band(exp["steps"], 3)
    assert ev.verdict_exact(rows)[1] == EXPECT["V_E3"]


def test_the_exact_chain_blocks_892_of_1680_states_at_high_thresholds_and_the_simulation_agrees():
    for rule in (C.R_HAPPY, C.R_ANY):
        for tau in (0.67, 0.75):
            r = next(x for x in _e3() if x["grid"] == "3 × 3 (3 A, 3 B)" and x["rule"] == rule and x["tau"] == tau)
            assert r["states"] == 1680 and r["done"] == 4
            if rule == C.R_HAPPY:
                assert r["blocked"] == 892 and r["p_done"] == pytest.approx(0.1315, abs=1e-4)                                      # H3
            else:
                assert r["blocked"] == 0 and r["p_done"] == pytest.approx(1.0) and r["steps"] == pytest.approx(182.4, abs=0.05)
            p = r["p_done"]
            assert abs(r["sim_p_done"] - p) <= 4.5 * math.sqrt(max(p * (1 - p), 1e-12) / r["runs"]) + 1e-3
            if r["blocked"] == 0:
                assert abs(r["sim_steps"] - r["steps"]) <= 4.5 * r["sim_se"]


# --- E4: Brücke zu Stück 2 und Netze ----------------------------------------------------------------------------------------------------------------


def test_bridge_table():
    rows = _e4()
    assert len(rows) == len(EXPECT["E4"]) == len(C.BRIDGE_SPACES) * len(C.BRIDGE_TAUS)
    for got, exp in zip(rows, EXPECT["E4"]):
        assert (got["space"], got["tau"], got["runs"]) == (exp["space"], exp["tau"], exp["runs"]), exp
        for key in ("s0", "s1", "q1", "e1", "unhappy", "done"):
            assert got[key] == _band(exp[key], 4), (exp["space"], exp["tau"], key)
        assert got["moves"] == _band(exp["moves"], 1)
        if exp["nmi"] is None:
            assert math.isnan(got["nmi"])
        else:
            assert got["nmi"] == _band(exp["nmi"], 4)
    assert ev.verdict_bridge(rows)[1] == EXPECT["V_E4"]


def test_the_unmixing_index_is_the_modularity_of_the_types_up_to_a_constant():
    for r in _e4():
        assert abs(r["q1"] - (r["e1"] - 0.5)) < 0.002                                                               # H6: Q = Anteil gleichartiger Kanten − Σ (D / 2m)²
    assert all(r["done"] == 1.0 and r["unhappy"] == 0.0 for r in _e4())


def test_communities_unmix_more_and_the_types_line_up_with_them_only_at_a_high_threshold():
    by = {(r["space"], r["tau"]): r for r in _e4()}
    assert by[(C.T_COMMUNITIES, 0.5)]["s1"] > by[(C.T_RANDOM, 0.5)]["s1"] + 0.08 and by[(C.T_COMMUNITIES, 0.5)]["nmi"] > 0.25 > 0.1 > by[(C.T_COMMUNITIES, 0.3)]["nmi"]                   # H8
    assert by[(C.T_RING, 0.5)]["s1"] > by[(C.T_RANDOM, 0.5)]["s1"] and all(by[(sp, 0.5)]["s1"] > by[(sp, 0.3)]["s1"] for sp in C.BRIDGE_SPACES)


# --- Gemeinschaftserkennung (nur hier, mit networkx) ---------------------------------------------------------------------------------------------------


def test_community_detection_finds_spatial_blocks_not_the_types():
    rows = _communities()
    assert len(rows) == len(EXPECT["D"]) == len(COMM_TAUS)
    for got, exp in zip(rows, EXPECT["D"]):
        assert got["tau"] == exp["tau"]
        for key in ("q_types0", "q_types1", "q_greedy0", "q_greedy1", "nmi0", "nmi1"):
            assert got[key] == pytest.approx(exp[key], abs=0.0016), (exp["tau"], key)
        assert got["communities1"] == pytest.approx(exp["communities1"], abs=0.06)
    by = {r["tau"]: r for r in rows}
    assert all(by[t]["nmi1"] < 0.05 for t in (0.2, 0.3, 0.4)) and by[0.5]["nmi1"] <= 0.05 and by[0.6]["nmi1"] > 0.3                                  # H7: die Gemeinschaften sind keine Typen (bis τ = 0,5)
    assert all(r["q_greedy0"] > 0.69 and r["q_greedy1"] > 0.69 for r in rows) and all(r["q_greedy1"] > r["q_types1"] + 0.2 for r in rows)          # die Gemeinschaften haben die höhere Modularität


# --- Presets ---------------------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_preset_numbers(name):
    an = ev.analyse(ev.Settings(**C.PRESETS[name]))
    exp = EXPECT["presets"][name]
    assert (an.agents, an.free, an.status, an.run["steps"], an.run["moves"], an.clusters1[0]) == (exp["agents"], exp["free"], exp["status"], exp["steps"], exp["moves"], exp["clusters"])
    for got, key in ((an.s0, "s0"), (an.s1, "s1"), (an.q0, "q0"), (an.q1, "q1"), (an.unhappy0, "unhappy0"), (an.run["unhappy"], "unhappy1"), (an.clusters1[1], "largest")):
        assert got == _band(exp[key], 4), (name, key)
    if exp["nmi1"] is None:
        assert math.isnan(an.nmi1)
    else:
        assert an.nmi1 == _band(exp["nmi1"], 4)
    assert ev.verdict_main(an) == (exp["kind"], exp["verdict"])
