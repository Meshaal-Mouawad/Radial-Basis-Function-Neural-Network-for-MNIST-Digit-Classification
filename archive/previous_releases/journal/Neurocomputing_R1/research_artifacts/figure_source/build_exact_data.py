"""Build figure coordinates from archived analysis CSVs, without fitting models.

Portable in either the working tree or a release package containing
manuscript/ and work/v2/analysis/ at its root. Uses all five frozen seeds.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd


def find_analysis():
    for parent in Path(__file__).resolve().parents:
        for relative in ("work/v2/analysis", "baseline/work/v2/analysis", "v2/analysis"):
            candidate = parent / relative
            if (candidate / "appendix_certificate_all_grid.csv").is_file():
                return candidate
    raise FileNotFoundError("Place the archived CSVs under work/v2/analysis/ at the package root.")


def build_exact_data():
    source = find_analysis()
    filenames = ("appendix_certificate_all_grid.csv", "appendix_endpoint_all_grid.csv")
    output = {
        "provenance": "Exact per-seed percentages from authoritative v2 frozen-result analysis CSVs; no model refitting or experiment reruns.",
        "seeds": [11, 22, 33, 44, 55], "coverage": [], "agreement_accuracy": [],
        "source_sha256": {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in filenames},
    }
    certificate, endpoint = [pd.read_csv(source / name) for name in filenames]
    for dataset, name in (("mnist", "MNIST"), ("fashion_mnist", "Fashion-MNIST")):
        for floor in (0, 1, 100):
            for kind, frame in (("coverage", certificate), ("agreement_accuracy", endpoint)):
                cell = frame[(frame.dataset == dataset) & (frame.K == 100) &
                             (frame.lambda_lower == floor) & (frame.width_index > 0)]
                record = {"dataset": name, "lambda_floor": floor,
                          "upper_width_over_sC": ["1/16", "1/8", "1/4", "1/2", "1", "2"],
                          "chart_kind": kind}
                if kind == "coverage":
                    sharp = cell[cell.method == "sharp"].sort_values(["width_index", "seed"])
                    basic = cell[cell.method == "basic"].sort_values(["width_index", "seed"])
                    assert list(sharp.certified) == list(basic.certified)
                    metrics = {"sharp_basic": ("sharp", "coverage_percent"),
                               "frobenius": ("cancellation_frobenius", "coverage_percent")}
                else:
                    metrics = {"agreement": (None, "nearest_readout_agree_percent"),
                               "readout_accuracy": (None, "readout_correct_percent"),
                               "nearest_prototype_accuracy": (None, "nearest_correct_percent")}
                for key, (method, column) in metrics.items():
                    subset = cell if method is None else cell[cell.method == method]
                    values = []
                    for width in range(1, 7):
                        rows = subset[subset.width_index == width].sort_values("seed")
                        assert rows.seed.tolist() == output["seeds"]
                        values.append(rows[column].tolist())
                    record[key] = {"mean_percent": [sum(v) / 5 for v in values],
                                   "five_seed_percent": values}
                output[kind].append(record)
    return output


if __name__ == "__main__":
    target = Path(__file__).resolve().with_name("exact_plot_data.json")
    target.write_text(json.dumps(build_exact_data(), indent=2))
    print(target)
