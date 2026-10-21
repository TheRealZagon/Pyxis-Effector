#!/usr/bin/env python3
# Pyxis Effector - Plugin for Aegisub
# Copyright (C) 2026 @mandholine, @effector2, @pholguinc and Pyxis Effector contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any question you can visit: https://discord.gg/fsxRESeQZN

"""Prueba de humo del motor PyxisNodes (sin interfaz gráfica).

Genera un .ass de karaoke de prueba, lo procesa con el motor de nodos y
verifica que:

1. El análisis karaskel extrae las sílabas esperadas.
2. Se generan líneas de efecto (7 sílabas x 30 iteraciones del buble = 210).
3. Todas las líneas llevan el efecto `pyxis_fx`, el mismo que filtra la macro
   de Aegisub para no confundirlas con el diálogo del usuario.
4. El resultado es determinista: la ejecución con multiproceso coincide
   línea a línea con la secuencial.

Uso:
    python3 tools/smoke_test.py [--keep-ass RUTA]

Sale con código 0 si todo pasa y 1 si falla alguna comprobación. No deja
ficheros temporales salvo que se pida `--keep-ass`.
"""

import argparse
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "PyxisNodes" / "src"

# .ass de karaoke mínimo: 4 + 2 + 1 = 7 sílabas sobre 3 líneas de diálogo.
ASS_TEMPLATE = r"""[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.00,Default,,0,0,0,,{\k20}Ka{\k20}ra{\k20}o{\k20}ke
Dialogue: 0,0:00:02.00,0:00:04.00,Default,,0,0,0,,{\k20}Effe{\k20}ctor
Dialogue: 0,0:00:04.00,0:00:06.00,Default,,0,0,0,,{\k30}Test
"""

# Grafo de estrés: bucle principal por sílabas, 30 iteraciones anidadas,
# cálculo trigonométrico y posicionamiento. Es el mismo que usa
# benchmark_runner.run_performance_diagnostic() como grafo por defecto.
STRESS_GRAPH = {
    "nodes": [
        {"id": 1, "type": "Loops/Main Loop", "properties": {"iterator": "syl"}, "inputs": []},
        {"id": 2, "type": "Loops/MaxLoop", "properties": {"iterations": "30", "var_name": "j"},
         "inputs": [{"name": "Loop In", "link": 1}]},
        {"id": 3, "type": "Math/Calc", "properties": {"expr": "j * 2.5 + sin(j * 0.1) * 10"}, "inputs": []},
        {"id": 4, "type": "Tags/Pos", "properties": {"x": "syl.center", "y": "syl.middle"},
         "inputs": [{"name": "x", "link": 3}, {"name": "y"}]},
        {"id": 5, "type": "System/Output", "properties": {"apply_to": "Sel. Lines"}, "inputs": [
            {"name": "Loop / Domain", "link": 2},
            {"name": "Layer"},
            {"name": "Start Time"},
            {"name": "End Time"},
            {"name": "Tags", "link": 4},
            {"name": "Return"},
        ]},
    ],
    "links": [
        [1, 1, 0, 2, 0, "flow"],
        [2, 2, 0, 5, 0, "flow"],
        [3, 3, 0, 4, 0, "number"],
        [4, 4, 0, 5, 4, "string"],
    ],
}

NUM_DIALOGUES = 3
SYLLABLES_PER_DIALOGUE = (4, 2, 1)
LOOP_ITERATIONS = 30
EXPECTED_FX_LINES = sum(SYLLABLES_PER_DIALOGUE) * LOOP_ITERATIONS  # 210


def check(condition: bool, label: str, failures: list) -> None:
    mark = "OK  " if condition else "FAIL"
    print(f"  [{mark}] {label}")
    if not condition:
        failures.append(label)


def run_smoke(keep_ass: str = None) -> int:
    sys.path.insert(0, str(SRC_DIR))
    import ass_parser
    from node_engine import GraphEngine

    with tempfile.TemporaryDirectory(prefix="pyxis_smoke_") as tmp:
        ass_path = Path(keep_ass) if keep_ass else Path(tmp) / "karaoke_smoke.ass"
        ass_path.write_text(ASS_TEMPLATE, encoding="utf-8")
        print(f"ASS de prueba: {ass_path}")

        styles, dialogues, rx, ry, fd = ass_parser.ASSParser.read_file(str(ass_path))

        failures: list = []
        check(len(dialogues) == NUM_DIALOGUES,
              f"el análisis karaskel encuentra {NUM_DIALOGUES} líneas de diálogo", failures)

        print("Procesando (secuencial)...")
        seq = GraphEngine(STRESS_GRAPH, rx, ry, fd).process(dialogues, styles, use_multiprocessing=False)
        print("Procesando (multiproceso)...")
        mp = GraphEngine(STRESS_GRAPH, rx, ry, fd).process(dialogues, styles, use_multiprocessing=True)

        check(len(seq) == EXPECTED_FX_LINES,
              f"secuencial genera {EXPECTED_FX_LINES} líneas de efecto (obtenidas: {len(seq)})", failures)
        check(all(l.startswith("Dialogue:") for l in seq),
              "todas las líneas generadas son líneas Dialogue válidas", failures)
        check(all(",pyxis_fx," in l for l in seq),
              "todas las líneas generadas llevan el efecto pyxis_fx", failures)
        check(seq == mp,
              f"multiproceso es determinista y coincide con secuencial ({len(mp)} líneas)", failures)

        print("-" * 60)
        if failures:
            print(f"PRUEBA FALLIDA: {len(failures)} comprobación(es) no superada(s)")
            return 1
        print(f"PRUEBA SUPERADA: {len(seq)} líneas FX generadas y verificadas")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba de humo del motor PyxisNodes.")
    parser.add_argument("--keep-ass", metavar="RUTA",
                        help="guarda el .ass de prueba generado en RUTA")
    args = parser.parse_args()
    return run_smoke(keep_ass=args.keep_ass)


if __name__ == "__main__":
    sys.exit(main())
