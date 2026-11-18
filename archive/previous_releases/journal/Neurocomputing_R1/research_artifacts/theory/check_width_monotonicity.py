"""Independent random-geometry audit of archived constants and guarded masks."""
import importlib.util
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "archived_certificate", BASE / "baseline/work/v2/experiment/certificate.py"
)
certificate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(certificate)
rng = np.random.default_rng(772911)
result = {"seed": 772911, "geometries": 80, "widths_per_geometry": 61,
          "ridge_floors": [0, 1, 100], "constant_order_violations": 0,
          "mask_order_violations": 0, "applicability_order_violations": 0,
          "certified_query_width_method_cases": 0,
          "comparison_scope": "independent synthetic geometries; archived implementation"}
for rep in range(result["geometries"]):
    N, K, C, M = 33, 7, 3, 29
    X = rng.normal(size=(N, 4))
    if rep % 10 == 0:
        X[1] = X[0]  # Retain duplicate inputs, including duplicate prototypes.
    y = rng.integers(C, size=N)
    Y = np.eye(C)[y]
    rows = np.arange(K)
    centers = X[rows]
    queries = rng.normal(size=(M, 4))
    if rep % 5 == 0:
        queries[0] = (centers[0] + centers[1]) / 2
    Dtrain = ((X[:, None] - centers[None]) ** 2).sum(axis=2)
    Dquery = ((queries[:, None] - centers[None]) ** 2).sum(axis=2)
    previous = {}
    for width in np.geomspace(0.01, 10, result["widths_per_geometry"]):
        H = np.exp(-Dtrain / (2 * width * width))
        terms = certificate.training_terms(H, Y, rows)
        for floor in result["ridge_floors"]:
            bounds, applicable = certificate.constants(terms, floor)
            masks, _, _, _ = certificate.query_certificate(Dquery, terms["Yc"], width, bounds)
            result["certified_query_width_method_cases"] += int(masks.sum())
            if floor in previous:
                old_bounds, old_masks, old_applicable = previous[floor]
                finite = np.isfinite(bounds) & np.isfinite(old_bounds)
                result["constant_order_violations"] += int(
                    np.count_nonzero(bounds[finite] + 1e-12 * (1 + old_bounds[finite]) < old_bounds[finite])
                )
                result["mask_order_violations"] += int(np.count_nonzero(masks & ~old_masks))
                result["applicability_order_violations"] += int(applicable and not old_applicable)
            previous[floor] = bounds, masks, applicable
destination = Path(__file__).with_name("width_monotonicity_results.json")
destination.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
assert all(result[name] == 0 for name in ("constant_order_violations", "mask_order_violations", "applicability_order_violations"))
