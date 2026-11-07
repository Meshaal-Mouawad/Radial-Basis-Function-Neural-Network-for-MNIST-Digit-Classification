# Nimbus Sans font provenance and conversion

Upstream: URW Base35 fonts, <https://github.com/ArtifexSoftware/urw-base35-fonts>.
Source distribution: Debian `fonts-urw-base35`, the installed OpenType files under `/usr/share/fonts/opentype/urw-base35/`. Both source fonts identify themselves as Version 1.00 and retain the upstream copyright `(URW)++, Copyright 2014 by (URW)++ Design & Development`.

Bundled source files:

- `NimbusSans-Regular.otf`, SHA256 `7c25be4d78155523080ab85b10277150657ff7dabbcad7037bdd536c9b6d0d08`
- `NimbusSans-Bold.otf`, SHA256 `7f33328e6b4d4cd21b45fa625791928c9407dc702db6780e56b09ca9a3ecaa67`

License: GNU Affero General Public License version 3 with the upstream font embedding exception. `LICENSE.txt` includes the full license and exception. `UPSTREAM_DEBIAN_COPYRIGHT.txt` preserves the complete distribution notice. The exception permits embedding these fonts in a PostScript/PDF document regardless of the document's own license.

Modified 6 November 2026 for the RBF figure package: `prepare_fonts.py` uses FontTools FontBuilder, Cu2QuPen and TTGlyphPen to convert the CFF cubic outlines to genuine quadratic TrueType outlines. The renamed derivative family is **RBF Nimbus Sans**, with faces **RBFNimbusSans-Regular** and **RBFNimbusSans-Bold**. Both derivative fonts remain under AGPL-3 with the font exception. Source OTFs and the complete conversion script accompany the derivatives. No warranty is provided.

All 855 glyph advance widths/sidebearings and source vertical metrics are copied exactly. Glyph order, Unicode mappings, and GPOS/GSUB layout tables are retained. The cubic-to-quadratic approximation target is 0.1 font units before integer coordinate rounding; units per em are 1000. Names identify the modified fonts to avoid collisions with installed CFF faces. Conversion is deterministic, with original font header timestamps retained. `conversion_audit.json` records source/output hashes and metric checks.

The figure builder registers these TTFs explicitly with Matplotlib. It never passes CFF outlines to the PDF backend's type-42 embedding path. The supplied OTFs are conversion inputs and are not embedded in the resulting PDF. PDF font resources are valid CIDFontType2 fonts with actual glyf-based FontFile2 streams. DejaVu mathematical glyphs are supplied by Matplotlib's existing TrueType fonts.
