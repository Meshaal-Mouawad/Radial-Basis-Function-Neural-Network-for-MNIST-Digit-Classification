# Reproduce the integrated figures

Run from any directory:

```bash
python manuscript/figure_source/create_figures.py
```

In the working tree use `python work/v3/manuscript/figure_source/create_figures.py`.
Dependencies: Python, NumPy, pandas, Matplotlib, and FontTools. The source package bundles the licensed Nimbus source fonts and metric-preserving TrueType derivatives under `fonts/`; no system Nimbus installation is required.
The builder locates the archived analysis CSVs under `work/v2/analysis/` relative to an ancestor directory. It creates PDF/SVG vector files and PNG previews in `manuscript/figures/`, plus `exact_plot_data.json` with source hashes.

Inputs:

- `work/v2/analysis/appendix_certificate_all_grid.csv`
- `work/v2/analysis/appendix_endpoint_all_grid.csv`

Only K=100 and the six scaled endpoints are plotted, matching the source manuscript. Each panel retains every seed (11, 22, 33, 44, 55). The absolute t=1 endpoint is described as zero coverage in the caption. This script reads already completed results; it does not fit or score a model.

The figure design derives from the supplied Visual Scientific Designer vector package. Figure 1 preserves the approved 15 pt question mark and the approved dashed-line gap from the UPDATED PDF geometry. The supplied plotting script did not contain those final manual geometry changes; their point coordinates are encoded explicitly in the integrated source. Its ambiguous prototype-set C is replaced with {c_j}. Figure 2 explicitly includes the positive denominator prerequisite. Main labels have minimum 9.6 pt at the 190 mm source width, yielding 8.044 pt at the current manuscript line width. Mathematical subscripts use normal typographic scaling.


## Valid font embedding

`prepare_fonts.py` converts the bundled CFF OTF source fonts into quadratic TrueType outlines and registers the renamed **RBF Nimbus Sans** faces with Matplotlib. This prevents CFF outlines from being mislabeled as TrueType in PDF font resources. See `fonts/PROVENANCE.md`, `fonts/LICENSE.txt`, and `fonts/conversion_audit.json`. The builder runs the conversion automatically. The approved question mark is anchored by its original PDF baseline; legend anchors compensate for the changed FreeType font-box height, preserving every vector drawing coordinate. All source artwork dimensions, label sizes, and numerical plot data remain unchanged.
