from ast import literal_eval
from pathlib import Path


def _read_greyscales(path: Path) -> list[list[float]]:
    return [
        [float(value) for value in literal_eval(line.removeprefix("values = ").strip("S'"))]
        for line in path.read_text().splitlines()
        if line.startswith("values = ")
    ]


def read_greyscale_from_fixture_config(fixture_config: Path) -> list[float] | None:
    if not (values := _read_greyscales(fixture_config)):
        return None

    return values[0]


def read_greyscales_from_compilation(compilation: Path) -> list[list[float]] | None:
    if not (values := _read_greyscales(compilation)):
        return None
    return values


def average_greyscales(greyscales: list[list[float]]) -> tuple[list[float], float]:
    average = []
    variance = 0.0
    for value_set in zip(*greyscales):
        value = sum(value_set) / len(value_set)
        variance += sum((x - value) ** 2 for x in value_set) / len(value_set)
        average.append(value)

    stdev = (variance / len(average)) ** 0.5
    return average, stdev

def delta_greyscales(greyscale: list[float], reference: list[float]) -> list[float]:
    return [g - r for g, r in zip(greyscale, reference)]


def compilation_has_missing_greyscales(compilation: Path) -> bool:
    # If "values" exists on a line on its own, greyscale values for that scan are missing
    return "values" in compilation.read_text().splitlines()
