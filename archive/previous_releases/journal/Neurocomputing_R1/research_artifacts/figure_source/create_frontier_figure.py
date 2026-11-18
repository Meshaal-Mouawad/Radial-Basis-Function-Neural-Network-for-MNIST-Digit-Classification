"""Figure 05: exact supplementary certificate frontier and endpoint accuracy.

This script never reruns the experiment or modifies Figures 01--04. It requires
completed frontier CSV outputs. Run with --help for explicit paths; defaults
follow the v4 working tree. All plotted numeric values are archived verbatim in
frontier_plot_data.json, together with input SHA256 checksums.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.lines import Line2D
import numpy as np


SOURCE = Path(__file__).resolve().parent
PROJECT = next((p for p in SOURCE.parents if (p / "frontier/results").is_dir()),
               SOURCE.parents[1])
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--results", type=Path, default=PROJECT / "frontier/results")
parser.add_argument("--output", type=Path, default=SOURCE.parent / "figures")
args = parser.parse_args()

for font in (SOURCE / "fonts").glob("RBFNimbusSans-*.ttf"):
    font_manager.fontManager.addfont(str(font))
rcParams.update({
    "font.family": "RBF Nimbus Sans", "font.size": 8.5,
    "text.color": "#0F172A", "axes.labelcolor": "#1E293B",
    "axes.edgecolor": "#CBD5E1", "xtick.color": "#64748B",
    "ytick.color": "#64748B", "pdf.fonttype": 42, "ps.fonttype": 42,
    "svg.fonttype": "none", "path.simplify": False,
    "svg.hashsalt": "rbf-v4-exact-frontier-20261107",
    "savefig.facecolor": "white", "figure.facecolor": "white",
})
COLORS = {0: "#0284C7", 100: "#F43F5E"}
DATASETS = [("mnist", "MNIST"), ("fashion_mnist", "Fashion-MNIST")]
SEEDS = [11, 22, 33, 44, 55]


def read_csv(name):
    path = args.results / name
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return path, rows


grid_path, grid = read_csv("grid_coverage.csv")
endpoint_path, endpoints = read_csv("endpoint_metrics.csv")
record = {"sources": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in [grid_path, endpoint_path]},
          "K": 100, "lambda_floors": [0, 100],
          "coverage_summary": "unweighted mean and min/max across five seeds",
          "accuracy_points": "individual seeds; lines pair same seed and floor",
          "grid_rows": [], "endpoint_rows": []}

fig, axes = plt.subplots(2, 2, figsize=(159.2 / 25.4, 125 / 25.4))
fig.subplots_adjust(left=.105, right=.975, bottom=.11, top=.855,
                    hspace=.52, wspace=.26)

for col, (dataset, label) in enumerate(DATASETS):
    top, bottom = axes[:, col]
    for ax in (top, bottom):
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_linewidth(.6)
        ax.tick_params(labelsize=8.5, width=.6, length=2.4, pad=2.5)
        ax.grid(axis="y", color="#E2E8F0", lw=.65)
        ax.set_axisbelow(True)
        ax.set_xscale("log", base=2)
    top.set_title(f"{chr(65+col)}   {label} | K = 100", loc="left",
                  fontsize=9, fontweight="bold", pad=8)
    bottom.set_title(f"{chr(67+col)}   {label} | endpoint readouts", loc="left",
                     fontsize=9, fontweight="bold", pad=8)
    top.set_xlim(1/32, 1/4)
    top.set_xticks([1/32, 1/16, 1/8, 1/4], ["1/32", "1/16", "1/8", "1/4"])
    top.set_ylim(-3, 103)
    top.set_yticks([0, 25, 50, 75, 100])
    top.set_xlabel("Scaled upper bandwidth", fontsize=8.5, labelpad=4)
    bottom.set_xlim(.028, 2.3)
    bottom.set_xticks([1/32, 1/16, 1/8, 1/4, 1/2, 1, 2],
                     ["1/32", "1/16", "1/8", "1/4", "1/2", "1", "2"])
    bottom.set_xlabel("Scaled fitted bandwidth", fontsize=8.5, labelpad=4)
    if col == 0:
        top.set_ylabel("Certified queries (%)", fontsize=8.5)
        bottom.set_ylabel("All-query accuracy (%)", fontsize=8.5)

    accuracy_values = []
    for floor in [0, 100]:
        color = COLORS[floor]
        selected_grid = [r for r in grid if r["dataset"] == dataset
                         and int(r["K"]) == 100 and float(r["lambda_floor"]) == floor
                         and r["method"] == "sharp"]
        record["grid_rows"].extend(selected_grid)
        by_seed = {}
        for seed in SEEDS:
            rs = sorted([r for r in selected_grid if int(r["seed"]) == seed],
                        key=lambda r: int(r["grid_index"]))
            if len(rs) != 67:
                raise ValueError(f"Expected67 complete grid rows, found {len(rs)}: {dataset}/{seed}/{floor}")
            by_seed[seed] = rs
        x = np.array([float(r["sigma_over_sC"]) for r in by_seed[SEEDS[0]]])
        y = np.array([[100 * float(r["coverage"]) for r in by_seed[s]] for s in SEEDS])
        if y.max() > 100.001:
            raise ValueError("Coverage must be a fraction, not a percentage")
        top.fill_between(x, y.min(axis=0), y.max(axis=0), color=color, alpha=.13, lw=0)
        top.plot(x, y.mean(axis=0), color=color, lw=1.45,
                 linestyle="-" if floor == 0 else "--")
        rs = [r for r in endpoints if r["dataset"] == dataset and int(r["K"]) == 100
              and float(r["lambda_floor"]) == floor and r["target"] == "any"]
        if len(rs) != 5:
            raise ValueError("Missing seedwise any-coverage endpoint rows")
        record["endpoint_rows"].extend(rs)
        for r in sorted(rs, key=lambda r: int(r["seed"])):
            if str(r["available"]).lower() not in ["true", "1"]:
                raise ValueError("Unavailable any-coverage endpoint")
            x1, x2 = float(r["sigma_over_sC"]), float(r["best_frozen_sampled_ratio"])
            y1, y2 = 100*float(r["accuracy"]), 100*float(r["best_frozen_sampled_accuracy"])
            accuracy_values.extend([y1, y2])
            bottom.plot([x1, x2], [y1, y2], color=color, alpha=.25, lw=.7, zorder=1)
            bottom.plot(x1, y1, "o", color=color, markersize=4.2, markeredgewidth=.75,
                        markerfacecolor="white", zorder=3)
            bottom.plot(x2, y2, "D", color=color, markersize=3.9, markeredgewidth=.65,
                        markerfacecolor=color, alpha=.8, zorder=3)
    bottom.set_ylim(np.floor(min(accuracy_values)/5)*5-1,
                    np.ceil(max(accuracy_values)/5)*5+1)

fig.legend(handles=[
    Line2D([], [], color=COLORS[0], lw=1.6, label="Penalty floor 0"),
    Line2D([], [], color=COLORS[100], lw=1.6, ls="--", label="Penalty floor 100"),
], loc="upper center", bbox_to_anchor=(.53, .995), ncol=2,
           frameon=False, fontsize=8.5, handlelength=2.2, columnspacing=1.8)
fig.legend(handles=[
    Line2D([], [], color="#64748B", marker="o", markerfacecolor="white", lw=0,
           markersize=4, label="Largest certified grid width"),
    Line2D([], [], color="#64748B", marker="D", lw=0, markersize=4,
           label="Best frozen sampled accuracy"),
], loc="upper center", bbox_to_anchor=(.53, .945), ncol=2,
           frameon=False, fontsize=8.5, handlelength=1.0, columnspacing=1.1)

args.output.mkdir(parents=True, exist_ok=True)
slug = "Figure_05_Certified_Frontier_Accuracy"
for fmt in ["pdf", "svg", "png"]:
    destination = args.output / (slug + ("_preview" if fmt == "png" else "") + "." + fmt)
    metadata = {"Creator": "Exact archived frontier CSVs"}
    if fmt == "pdf":
        metadata.update(CreationDate=datetime(2026, 11, 7, tzinfo=timezone.utc),
                        ModDate=datetime(2026, 11, 7, tzinfo=timezone.utc))
    elif fmt == "svg":
        metadata["Date"] = "2026-11-07"
    fig.savefig(destination, dpi=220, metadata=metadata)
plt.close(fig)
(SOURCE / "frontier_plot_data.json").write_text(json.dumps(record, indent=2) + "\n")
print(args.output / (slug + ".pdf"))
