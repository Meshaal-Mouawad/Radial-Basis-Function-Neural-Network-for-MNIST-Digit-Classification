"""Create valid TrueType Nimbus derivatives for Matplotlib's PDF backend.

Modified 6 November 2026: cubic CFF outlines are approximated by quadratic
TrueType outlines; original character widths and layout metrics are retained.
The bundled source fonts and these derivatives carry AGPL-3 with the upstream
font embedding exception; see fonts/LICENSE.txt and fonts/PROVENANCE.md.
"""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


FONT_DIR = Path(__file__).resolve().parent / "fonts"
FONT_FAMILY = "RBF Nimbus Sans"


def convert_font(source, target, style):
    original = TTFont(source)
    glyph_set = original.getGlyphSet()
    glyph_order = original.getGlyphOrder()
    glyphs = {}
    for name in glyph_order:
        pen = TTGlyphPen(glyph_set)
        # 0.1 units at 1000 units/em is 0.0015 pt at the approved 15 pt mark.
        glyph_set[name].draw(Cu2QuPen(pen, max_err=0.1, reverse_direction=True))
        glyphs[name] = pen.glyph()
    builder = FontBuilder(original["head"].unitsPerEm, isTTF=True)
    builder.setupGlyphOrder(glyph_order)
    builder.setupCharacterMap(original.getBestCmap())
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(dict(original["hmtx"].metrics))
    builder.setupHorizontalHeader(ascent=original["hhea"].ascent,
                                  descent=original["hhea"].descent)
    builder.font["hhea"] = deepcopy(original["hhea"])
    builder.font["OS/2"] = deepcopy(original["OS/2"])
    builder.font["name"] = deepcopy(original["name"])
    replacements = {
        1: FONT_FAMILY, 2: style, 3: f"RBF-NimbusSans-{style}-TT-20261106",
        4: f"{FONT_FAMILY} {style}", 5: "Version 1.00; quadratic outline conversion 2026-11-06",
        6: f"RBFNimbusSans-{style}", 16: FONT_FAMILY, 17: style,
        13: "AGPL-3 with font embedding exception; see accompanying LICENSE.txt",
        14: "https://github.com/ArtifexSoftware/urw-base35-fonts",
    }
    for name_id, value in replacements.items():
        builder.font["name"].removeNames(nameID=name_id)
        builder.font["name"].setName(value, name_id, 3, 1, 0x409)
    builder.setupPost(italicAngle=original["post"].italicAngle,
                      underlinePosition=original["post"].underlinePosition,
                      underlineThickness=original["post"].underlineThickness,
                      isFixedPitch=original["post"].isFixedPitch)
    for table in ("GPOS", "GSUB"):
        if table in original:
            builder.font[table] = deepcopy(original[table])
    # Preserve global metrics used for text placement, rather than replacing
    # them by bounding boxes of the newly rounded quadratic control points.
    for field in ("xMin", "yMin", "xMax", "yMax", "macStyle", "lowestRecPPEM", "created", "modified"):
        setattr(builder.font["head"], field, getattr(original["head"], field))
    builder.font.recalcBBoxes = False
    builder.font.recalcTimestamp = False
    builder.font.save(target)
    result = TTFont(target)
    assert result.sfntVersion == "\x00\x01\x00\x00" and "glyf" in result and "CFF " not in result
    assert result["hmtx"].metrics == original["hmtx"].metrics
    assert result["hhea"].ascent == original["hhea"].ascent
    assert result["hhea"].descent == original["hhea"].descent
    return {
        "source": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output": target.name, "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "glyph_count": len(glyph_order), "all_horizontal_metrics_identical": True,
        "vertical_metrics_identical": True, "units_per_em": original["head"].unitsPerEm,
        "cubic_to_quadratic_max_error_font_units": 0.1,
    }


def prepare_fonts():
    records = []
    outputs = []
    for style in ("Regular", "Bold"):
        source = FONT_DIR / f"NimbusSans-{style}.otf"
        target = FONT_DIR / f"RBFNimbusSans-{style}.ttf"
        records.append(convert_font(source, target, style))
        outputs.append(target)
    (FONT_DIR / "conversion_audit.json").write_text(json.dumps(records, indent=2))
    return outputs


if __name__ == "__main__":
    for font in prepare_fonts():
        print(font)
