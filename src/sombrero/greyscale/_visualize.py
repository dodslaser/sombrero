from contextlib import suppress

import plotext
from matplotlib import pyplot

from ._common import delta_greyscales


def visualize_graphical(
    greyscales: list[list[float]] | None,
    average_greyscale: list[float] | None,
    fixture_greyscale: list[float] | None,
) -> None:
    plt = pyplot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    ax1, ax2, ax3 = axes

    ax1.set_title("Raw Greyscales")
    if greyscales is not None:
        for gs in greyscales:
            ax1.plot(gs, color="gray", alpha=0.5)
    if fixture_greyscale is not None:
        ax1.plot(fixture_greyscale, label="Fixture", color="blue", linewidth=2)
    if average_greyscale is not None:
        ax1.plot(average_greyscale, label="Average", color="red", linewidth=2)
    ax1.legend()

    ax2.set_title("Delta to Average")
    if average_greyscale is None or greyscales is None:
        ax2.text(0.5, 0.5, "No average greyscale available", ha="center", va="center")
        ax2.axis("off")
    else:
        for gs in greyscales:
            delta = delta_greyscales(gs, average_greyscale)
            ax2.plot(delta, color="gray", alpha=0.5)
        if fixture_greyscale is not None:
            delta_fixture = delta_greyscales(fixture_greyscale, average_greyscale)
            ax2.plot(delta_fixture, label="Fixture", color="blue", linewidth=2)
        ax2.plot([0] * len(average_greyscale), label="Average", color="red", linewidth=2)
        ax2.legend()

    ax3.set_title("Delta to Fixture")
    if fixture_greyscale is None:
        ax3.text(0.5, 0.5, "No fixture greyscale available", ha="center", va="center")
        ax3.axis("off")
    else:
        if greyscales is not None and average_greyscale is not None:
            for gs in greyscales:
                delta = delta_greyscales(gs, fixture_greyscale)
                ax3.plot(delta, color="gray", alpha=0.5)
            delta_average = delta_greyscales(average_greyscale, fixture_greyscale)
        ax3.plot(delta_average, label="Average", color="red", linewidth=2)
        ax3.plot([0] * len(fixture_greyscale), label="Fixture", color="blue", linewidth=2)
        ax3.legend()

    plt.tight_layout()
    with suppress(Exception):
        plt.show()

def visualize_terminal(
    greyscales: list[list[float]] | None,
    average_greyscale: list[float] | None,
    fixture_greyscale: list[float] | None,
) -> None:
    plt = plotext
    plt.clf()
    plt.subplots(1, 3)

    w = plt.tw() // 3 - 2
    h = w // 2

    plt.subplot(1, 1)
    plt.subplot(1, 1).plot_size(w, h)
    plt.subplot(1, 1).theme("clear")
    plt.subplot(1, 1).ylim(0, 255)
    plt.title("Raw Greyscales")
    if greyscales is not None:
        for gs in greyscales:
            plt.plot(gs, color="gray")
    if fixture_greyscale is not None:
        plt.plot(fixture_greyscale, label="Fixture", color="blue")
    if average_greyscale is not None:
        plt.plot(average_greyscale, label="Average", color="red")

    plt.subplot(1, 2)
    plt.subplot(1, 2).plot_size(w, h)
    plt.subplot(1, 2).theme("clear")
    plt.subplot(1, 2).ylim(-255, 255)
    plt.title("Delta to Average")
    if average_greyscale is None or greyscales is None:
        plt.text(0.5, 0.5, "No average greyscale available")
    else:
        for gs in greyscales:
            delta = delta_greyscales(gs, average_greyscale)
            plt.plot(delta, color="gray")
        if fixture_greyscale is not None:
            delta_fixture = delta_greyscales(fixture_greyscale, average_greyscale)
            plt.plot(delta_fixture, label="Fixture", color="blue")
        plt.plot([0] * len(average_greyscale), label="Average", color="red")

    plt.subplot(1, 3)
    plt.subplot(1, 3).plot_size(w, h)
    plt.subplot(1, 3).theme("clear")
    plt.subplot(1, 3).ylim(-255, 255)
    plt.title("Delta to Fixture")
    if fixture_greyscale is None:
        plt.text(0.5, 0.5, "No fixture greyscale available")
    else:
        if greyscales is not None and average_greyscale is not None:
            for gs in greyscales:
                delta = delta_greyscales(gs, fixture_greyscale)
                plt.plot(delta, color="gray")
            delta_average = delta_greyscales(average_greyscale, fixture_greyscale)
            plt.plot(delta_average, label="Average", color="red")
        plt.plot([0] * len(fixture_greyscale), label="Fixture", color="blue")

    plt.show()
