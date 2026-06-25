#!/usr/bin/env python3
"""
Validate a (hand-edited) female muscle SVG against the contract the
muscle_selector library and Forge's selection logic depend on.

It checks the things that actually break the app if you get them wrong while
tracing over the reference:

  1. XML is well-formed (so Inkscape/Figma round-trips cleanly).
  2. Every required muscle id from the canonical male map is still present
     -- nothing renamed, deleted, or dropped.
  3. Every <path> is on a SINGLE line and matches the library's own
     line-based regex (lib/src/constant.dart MAP_REGEXP). This is the one
     that silently bites you: Inkscape sometimes wraps long attributes.
  4. The file actually renders (needs cairosvg; skipped with a warning if
     it isn't installed).

Usage:
    python tracing/validate_female_svg.py
    python tracing/validate_female_svg.py path/to/edited.svg
"""
import os
import re
import sys
import xml.dom.minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MALE = os.path.join(ROOT, "assets", "maps", "human_body.svg")
DEFAULT_FEMALE = os.path.join(ROOT, "assets", "maps", "human_body_female.svg")

# exact regex the Dart library uses, per line (lib/src/constant.dart)
MAP_REGEXP = re.compile(r'.* id="(.*)" title="(.*)" .* d="(.*)"')
# tolerant element scan, independent of line breaks / self-closing style
ANY_PATH = re.compile(r'<path\b[^>]*?\bid="([^"]*)"', re.DOTALL)


def ids_tolerant(text):
    return [m.group(1) for m in ANY_PATH.finditer(text)]


def ids_library(text):
    return [m.group(1) for line in text.splitlines()
            if (m := MAP_REGEXP.search(line))]


def main():
    female = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FEMALE
    fsrc = open(female).read()
    msrc = open(MALE).read()
    required = ids_tolerant(msrc)            # 52: 50 muscles + lower_back-ish + human_body
    ok = True

    def fail(msg):
        nonlocal ok
        ok = False
        print("  FAIL:", msg)

    print(f"Validating {os.path.relpath(female, ROOT)}")

    # 1. well-formed XML
    try:
        xml.dom.minidom.parseString(fsrc)
        print("  ok  : well-formed XML")
    except Exception as e:
        fail(f"not well-formed XML ({e}). Inkscape can usually re-save to fix this.")

    # 2. required ids present (the library keys EVERYTHING off these names)
    present = set(ids_tolerant(fsrc))
    missing = [i for i in required if i not in present]
    extra = [i for i in present if i not in required]
    if missing:
        fail(f"missing {len(missing)} required id(s): {missing}")
    else:
        print(f"  ok  : all {len(required)} required ids present")
    if extra:
        print(f"  warn: {len(extra)} id(s) not in the male map (fine if intentional): {extra}")

    # 3. library regex: each path single-line and matched
    lib = ids_library(fsrc)
    lib_missing = [i for i in required if i not in lib]
    if lib_missing:
        fail("these ids are NOT matched by the library's line regex -- the path is "
             f"probably wrapped onto multiple lines: {lib_missing}")
    else:
        print(f"  ok  : {len(lib)} paths match the library MAP_REGEXP (one line each)")

    # 4. renders
    try:
        import cairosvg
        out = os.path.join(HERE, "_validate_render.png")
        cairosvg.svg2png(url=female, write_to=out, output_width=360, background_color="white")
        print(f"  ok  : renders -> {os.path.relpath(out, ROOT)}")
    except ImportError:
        print("  warn: cairosvg not installed; skipped render check "
              "(pip install cairosvg to enable)")
    except Exception as e:
        fail(f"failed to render ({e})")

    print("PASS" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
