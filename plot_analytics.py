#!/usr/bin/env python3
"""Plot keyword and builtin frequency from keyword_analytics.json."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl

# Style: dark-ish background, readable fonts
mpl.rcParams["figure.facecolor"] = "#1a1b26"
mpl.rcParams["axes.facecolor"] = "#24283b"
mpl.rcParams["axes.edgecolor"] = "#565f89"
mpl.rcParams["axes.labelcolor"] = "#c0caf5"
mpl.rcParams["xtick.color"] = "#a9b1d6"
mpl.rcParams["ytick.color"] = "#a9b1d6"
mpl.rcParams["text.color"] = "#c0caf5"

DATA_PATH = Path(__file__).resolve().parent / "keyword_analytics.json"
TOP_N = 25


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def main():
    data = load_data()
    kw = list(data["keyword_freq"].items())[:TOP_N]
    blt = list(data["builtin_freq"].items())[:TOP_N]
    dnd = list(data.get("dunder_freq", {}).items())[:TOP_N]
    ncols = 3 if dnd else 2
    fig, axes = plt.subplots(1, ncols, figsize=(6 * ncols, 8))
    if ncols == 2:
        ax1, ax2 = axes
    else:
        ax1, ax2, ax3 = axes
    fig.suptitle(
        data.get("meta", {}).get("language_reference", "CPython") + " — keyword, built-in & dunder frequency",
        fontsize=14, color="#c0caf5",
    )

    # Keywords
    labels_kw = [x[0] for x in reversed(kw)]
    vals_kw = [x[1] for x in reversed(kw)]
    colors_kw = plt.cm.Blues([0.3 + 0.6 * (i / max(len(vals_kw), 1)) for i in range(len(vals_kw))])
    ax1.barh(labels_kw, vals_kw, color=colors_kw, edgecolor="#565f89", linewidth=0.5)
    ax1.set_xlabel("Count")
    ax1.set_title("Top keywords")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Built-ins
    labels_blt = [x[0] for x in reversed(blt)]
    vals_blt = [x[1] for x in reversed(blt)]
    colors_blt = plt.cm.Greens([0.3 + 0.6 * (i / max(len(vals_blt), 1)) for i in range(len(vals_blt))])
    ax2.barh(labels_blt, vals_blt, color=colors_blt, edgecolor="#565f89", linewidth=0.5)
    ax2.set_xlabel("Count")
    ax2.set_title("Top built-ins")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Dunder (optional)
    if dnd:
        labels_dnd = [x[0] for x in reversed(dnd)]
        vals_dnd = [x[1] for x in reversed(dnd)]
        colors_dnd = plt.cm.Purples([0.3 + 0.6 * (i / max(len(vals_dnd), 1)) for i in range(len(vals_dnd))])
        ax3.barh(labels_dnd, vals_dnd, color=colors_dnd, edgecolor="#565f89", linewidth=0.5)
        ax3.set_xlabel("Count")
        ax3.set_title("Top dunder methods")
        ax3.spines["top"].set_visible(False)
        ax3.spines["right"].set_visible(False)

    plt.tight_layout()
    out = Path(__file__).resolve().parent / "keyword_analytics_plot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1b26")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
