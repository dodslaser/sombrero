from pathlib import Path
from shutil import move


def _format_greyscale_values(greyscales: list[float]) -> str:
    return f"values = S'{', '.join(str(gs) for gs in greyscales)}'"


def replace_missing_greyscales_in_compilation(
    compilation: Path,
    backup: Path,
    greyscales: list[float],
) -> None:
    temp = compilation.parent / (compilation.name + ".tmp")

    new_lines = [
        line if line.strip() != "values" else _format_greyscale_values(greyscales)
        for line in compilation.read_text().splitlines()
    ]
    temp.write_text("\n".join(new_lines))
    temp.chmod(compilation.stat().st_mode)
    move(compilation, backup)
    try:
        move(temp, compilation)
    except Exception as exc:
        move(backup, compilation)
        raise exc
