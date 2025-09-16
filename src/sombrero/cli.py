from logging import getLogger
from pathlib import Path
from shutil import copyfile

import rich_click as click
from rich.logging import RichHandler
from rich.prompt import Confirm, Prompt

from .greyscale import (
    average_greyscales,
    compilation_has_missing_greyscales,
    read_greyscale_from_fixture_config,
    read_greyscales_from_compilation,
    replace_greyscales_in_compilation,
    visualize_graphical,
    visualize_terminal,
)

LOGGER = getLogger(__name__)

BACKUP_TEMPLATE = "{compilation.parent}/{compilation.name}.backup_before_greyscale_fix"
COMPILATION_TEMPLATE = "{project_dir}/{project_dir.name}.project.compilation.original"
FIXTURE_CONFIG_TEMPLATE = "{project_dir}/fixture.config"


@click.group()
@click.argument(
    "project_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
)
@click.pass_context
def cli(ctx: click.Context, project_dir: Path, log_level: str) -> None:
    """All-in-one CLI for post-processing Scan-o-Matic projects."""
    LOGGER.setLevel(log_level.upper())
    LOGGER.addHandler(RichHandler(rich_tracebacks=True, tracebacks_show_locals=True))
    ctx.ensure_object(dict)
    ctx.obj["project_dir"] = project_dir
    ctx.obj["compilation"] = Path(COMPILATION_TEMPLATE.format(project_dir=project_dir))
    ctx.obj["fixture_config"] = Path(FIXTURE_CONFIG_TEMPLATE.format(project_dir=project_dir))
    ctx.obj["backup"] = Path(BACKUP_TEMPLATE.format(compilation=ctx.obj["compilation"]))


@cli.group()
def greyscale() -> None:
    """Commands for greyscale image processing."""
    pass


@click.option(
    "--average/--no-average",
    help=(
        "If greyscale values are only missing from some scans, but not all, "
        "generate and average greyscale value from the available scans and "
        "use that to fill in the missing values."
    ),
    is_flag=True,
    default=True,
)
@click.option(
    "--fixture/--no-fixture",
    help=(
        "If greyscale values are missing from all scans, use the values from "
        "the project fixture config file to fill in the missing values. If combined "
        "with --average, the average values will be used if available, otherwise "
        "the fixture values will be used."
    ),
    is_flag=True,
    default=True,
)
@click.option(
    "--interactive/--no-interactive",
    help=(
        "If missing greyscale values are found, launch an interactive session "
        "to visualize the greyscale values and decide which ones to use to fill "
        "in the missing values."
    ),
    is_flag=True,
    default=False,
)
@click.option(
    "--overwrite/--no-overwrite",
    help="Overwrite any existing backup file without prompting.",
    is_flag=True,
    default=None,
)
@click.option(
    "--replace-all/--replace-missing",
    help=("Replace greyscale values in all scans, or only in scans where they are missing."),
    is_flag=True,
    default=None,
)
@greyscale.command()
@click.pass_context
def interpolate(
    ctx: click.Context,
    average: bool,
    fixture: bool,
    interactive: bool,
    overwrite: bool | None,
    replace_all: bool | None,
) -> None:
    """Interpolate missing greyscale values in project compilations."""
    compilation = ctx.obj["compilation"]
    fixture_config = ctx.obj["fixture_config"]
    backup = ctx.obj["backup"]

    if not (average or fixture or interactive):
        LOGGER.critical("At least one of --average, --fixture, or --interactive must be specified.")
        raise SystemExit(1)

    if not compilation.exists():
        LOGGER.critical("No compilation file found at '%s'.", compilation)
        raise SystemExit(1)

    if interactive and backup.exists() and overwrite is None:
        overwrite = Confirm.ask(f"Found a compilation backup at '{backup}'. Overwrite?", default=False)
    else:
        overwrite = overwrite or False

    if backup.exists() and not overwrite:
        LOGGER.critical("Please restore or remove backup '%s' it before proceeding.", backup)
        raise SystemExit(1)

    if interactive or average:
        greyscales = read_greyscales_from_compilation(compilation)
        if greyscales is None:
            LOGGER.warning("No greyscale values found in compilation '%s'.", compilation.name)
            average_greyscale = None
            stdev = 0.0
        else:
            average_greyscale, stdev = average_greyscales(greyscales)
            LOGGER.info("Average greyscale values generated from compilation '%s'.", compilation.name)
            if stdev > 1:
                LOGGER.warning(
                    "High standard deviation (%.2f) in greyscale values from compilation '%s'.", stdev, compilation.name
                )
    else:
        greyscales = None
        average_greyscale = None
        stdev = 0.0

    if interactive and replace_all is None and greyscales is not None:
        replace_all = Confirm.ask("Replace all greyscale values, even if they are not missing?", default=stdev > 1)
    else:
        replace_all = replace_all or False

    if not (replace_all or compilation_has_missing_greyscales(compilation)):
        LOGGER.info("No missing greyscale values in compilation '%s'.", compilation.name)
        raise SystemExit(0)

    if interactive or fixture:
        if not fixture_config.exists():
            LOGGER.warning("No fixture config file found at '%s'. Continuing without it.", fixture_config)
            fixture = False
        elif (fixture_greyscale := read_greyscale_from_fixture_config(fixture_config)) is None:
            LOGGER.warning("No greyscale values found in fixture config '%s'.", fixture_config)
            fixture = False
        else:
            LOGGER.info("Greyscale values read from fixture config.")
    else:
        fixture_greyscale = None

    if interactive:
        visualize_terminal(greyscales, average_greyscale, fixture_greyscale)
        response = Prompt.ask(
            "Choose greyscale source",
            choices=[name for name, value in [("average", average), ("fixture", fixture)] if value is not None],
            default="average" if (average_greyscale is not None and stdev <= 1) else "fixture",
        )
        greyscale = average_greyscale if response == "average" else fixture_greyscale
    elif average and average_greyscale is not None:
        greyscale = average_greyscale
    elif fixture and fixture_greyscale is not None:
        greyscale = fixture_greyscale

    if greyscale is None:
        LOGGER.critical("No greyscale values available to fill in missing values.")
        raise SystemExit(1)



    try:
        replace_greyscales_in_compilation(compilation, backup, greyscale, replace_all)
    except Exception as exc:
        LOGGER.critical("Failed to replace missing greyscale values: %r", exc, exc_info=False)
        raise SystemExit(1) from exc
    else:
        LOGGER.info("Fixed compilation saved as '%s'", compilation.name)


@greyscale.command()
@click.pass_context
def restore(ctx: click.Context) -> None:
    """Restore original greyscale values in project compilations."""
    compilation = ctx.obj["compilation"]
    backup = ctx.obj["backup"]

    if not backup.exists():
        LOGGER.critical("No backup file found at '%s'. Cannot restore original compilation.", backup)
        raise SystemExit(1)

    try:
        copyfile(backup, compilation)
    except Exception as exc:
        LOGGER.critical("Failed to restore original compilation: %r", exc, exc_info=False)
        raise SystemExit(1) from exc
    else:
        LOGGER.info("Original compilation restored from '%s'", backup)

    try:
        backup.unlink()
    except Exception as exc:
        LOGGER.warning("Failed to delete backup file '%s': %r", backup, exc, exc_info=False)


@greyscale.command()
@click.option(
    "--graphical/--no-graphical",
    help="Use a graphical plot window instead of an ASCII plot in the terminal.",
    is_flag=True,
    default=False,
)
@click.pass_context
def visualize(ctx: click.Context, graphical: bool) -> None:
    """Visualize greyscale values in project compilations."""
    compilation = ctx.obj["compilation"]
    fixture_config = ctx.obj["fixture_config"]

    if not compilation.exists():
        LOGGER.critical("No compilation file found at '%s'.", compilation)
        raise SystemExit(1)

    if not fixture_config.exists():
        LOGGER.warning("No fixture config file found at '%s'. Continuing without it.", fixture_config)
        fixture_greyscale = None
    else:
        fixture_greyscale = read_greyscale_from_fixture_config(fixture_config)

    greyscales = read_greyscales_from_compilation(compilation)
    if greyscales is None:
        LOGGER.critical("No greyscale values found in compilation '%s'.", compilation.name)
        raise SystemExit(1)

    average_greyscale, stdev = average_greyscales(greyscales)

    if graphical:
        visualize_graphical(greyscales, average_greyscale, fixture_greyscale)
    else:
        visualize_terminal(greyscales, average_greyscale, fixture_greyscale)
