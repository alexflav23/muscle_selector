# muscle_selector — feature spec & test matrix

This document enumerates every feature of the package and the test that guards it,
including the **female muscle selector** added in 1.1.0. It is the contract the CI
PR builder (`.github/workflows/ci.yml`) enforces on every pull request.

## 1. Body maps & gender

The widget renders a body from an SVG asset whose `<path>` elements carry
`id` / `title` / `d`. Two maps ship:

| asset | view content | `Gender` |
|-------|--------------|----------|
| `assets/maps/human_body.svg` | anterior + posterior male | `Gender.male` |
| `assets/maps/human_body_female.svg` | anterior + posterior female | `Gender.female` |

- `Maps.BODY`, `Maps.BODY_FEMALE`, `Maps.forGender(Gender)` resolve the asset name.
- `MusclePickerMap` accepts **either** `map:` (asset filename, backward compatible)
  **or** `gender:`. Exactly one is required (asserted).
- Changing `gender`/`map` on a mounted widget reloads the body (`didUpdateWidget`).

> **Both maps expose the identical 52 path ids.** This is the load-bearing invariant:
> the female map is a drop-in for the male one, so all selection/grouping code is
> gender-agnostic. Guarded by `test/svg_assets_test.dart`.

## 2. Muscle catalogue (18 groups, 51 sub-muscles + silhouette)

Tapping any sub-muscle selects its whole group. Defined in `lib/src/parser.dart`.

| group | ids | view |
|-------|-----|------|
| chest | chest1–2 | front |
| shoulders | shoulder1–4 | front delts (1–2) + rear delts (3–4) |
| obliques | obliques1–2 | front |
| abs | abs1–8 | front (rectus abdominis) |
| abductor | abductor1–2 | front/hip |
| biceps | biceps1–2 | front |
| forearm | forearm1–4 | front (1–2) + back (3–4) |
| quads | quads1–4 | front thigh |
| adductors | adductors1–2 | front inner thigh |
| neck | neck | front |
| trapezius | trapezius1–5 | back (1–3) + front upper (4–5) |
| triceps | triceps1–2 | back |
| upper_back | upper_back1–2 | back |
| lats | lats1–2 | back |
| lower_back | lower_back | back |
| glutes | glutes1–2 | back |
| harmstrings | harmstrings1–2 | back *(original spelling kept)* |
| calves | calves1–4 | back |

Plus `human_body` — the silhouette outline, **not selectable**.

## 3. Feature → test matrix

| # | Feature | Test |
|---|---------|------|
| F1 | `Maps.forGender` / `Gender` resolve correct, distinct assets | `test/maps_test.dart` |
| F2 | `SizeController` accumulates bounds, computes map size & scale | `test/size_controller_test.dart` |
| F3 | `SizeController.reset()` clears bounds before each parse (gender-switch fix) | `test/size_controller_test.dart` |
| F4 | `muscleGroups` = 18 groups / 51 unique ids; expected members | `test/parser_test.dart` |
| F5 | `getMusclesByGroups` resolves groups, spans many, ignores unknown | `test/parser_test.dart` |
| F6 | `MAP_REGEXP` extracts id/title/d for all 52 paths of the real asset | `test/parser_test.dart` |
| F7 | Male & female maps have **identical 52-id sets**, no dupes | `test/svg_assets_test.dart` |
| F8 | Every grouped id (+`human_body`) is drawable in both maps | `test/svg_assets_test.dart` |
| F9 | Female asset is well-formed: every path single-line, self-closed, regex-matched | `test/svg_assets_test.dart` |
| F10 | Widget loads the map and renders without error | `test/muscle_picker_map_test.dart` |
| F11 | `initialSelectedGroups` seeds the whole group | `test/muscle_picker_map_test.dart` |
| F12 | Tapping a muscle selects its group; `actAsToggle` deselects | `test/muscle_picker_map_test.dart` |
| F13 | `clearSelect()` empties the selection | `test/muscle_picker_map_test.dart` |
| F14 | `isEditing` disables selection | `test/muscle_picker_map_test.dart` |
| F15 | `human_body` silhouette is not selectable | `test/muscle_picker_map_test.dart` |
| F16 | Switching `gender` reloads a different map | `test/muscle_picker_map_test.dart` |
| F17 | Example app shows the Male/Female toggle + picker; switching doesn't error | `example/test/widget_test.dart` |

## 4. The female muscle selector (1.1.0)

The female `d=""` geometry was **derived from the male map** by `tracing/derive_female_scaffold.py`
in three reproducible stages:

1. **Proportional warp** about each figure's vertical axis — a global slim (narrow
   shoulders, slimmer limbs) plus a core-only sculpt (pinched waist → wide hips/pelvis)
   that fades out with distance-from-axis so the hands never flare with the hips. Moves
   only `x` (as a function of `x` and `y`), preserving vertical registration.
2. **Breasts** — the flat male pectorals `chest1`/`chest2` are replaced with breast
   shapes (still the *chest* group: tapping a breast selects chest).
3. **Feminine hair** — the male hairstyle is swapped for line-art hair (forehead
   hairline + side-framing locks on the front, a fuller mass on the back), drawn in the
   same thin-band style as the rest of the silhouette.

Every stage reshapes geometry **inside existing paths only** — no id/title/class is
renamed, added, or removed — so **all 52 ids and the registration are preserved** (F7–F9).
An AI-generated female anatomy chart was used to calibrate the proportions and ships as
the refinement reference.

**Fidelity note:** the result is a clearly-female, fully-tappable *scaffold*, not a
finished anatomical illustration — the muscle borders are still inherited from the source.
For publication-grade art, hand-trace the named paths over the reference; see
[`tracing/TRACING.md`](tracing/TRACING.md). Anything edited there must still pass:

```
python tracing/validate_female_svg.py   # 52 ids · one line each · well-formed · renders
```

A real anatomist/illustrator should vet the final artwork.

## 5. Known limitation

Selection is compared by `Muscle` identity; reloading (e.g. a gender flip) rebuilds
`Muscle` instances, so an in-progress highlight clears across the switch. Carry
selection by muscle **id** in app state and re-seed via `initialSelectedGroups` if you
need it to survive a gender change.
