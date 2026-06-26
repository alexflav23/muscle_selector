# Finishing the female muscle map (hand-trace)

The shipped `assets/maps/human_body_female.svg` is a **named scaffold**: it already
contains all 52 paths with the exact `id` / `title` / `class` names the library
needs, reshaped to rough female proportions. Your job is to **node-edit those paths
to match the reference** — not to draw new ones. Never rename, add, or delete a path:
the whole selection + grouping engine keys off these ids.

**Reference (ground truth):** `tracing/female_reference.png`
**Edit this file:** `assets/maps/human_body_female.svg`
**Pristine copy to fall back to:** `tracing/human_body_female.scaffold.svg`

## Coordinate space (keep paths registered)
Two figures share one canvas. Keep each muscle inside its figure's zone or it
will detach from the silhouette:

| view | figure | vertical axis | x-range |
|------|--------|---------------|---------|
| anterior (front) | left  | x ≈ 88  | ~15–155 |
| posterior (back) | right | x ≈ 254 | ~184–330 |

`y` runs ~13 (head) to ~274 (feet). Editing `x` is what creates the female form;
avoid moving `y` much so muscles stay vertically aligned with the body outline.

## Inkscape workflow
1. `File → Open` the scaffold SVG.
2. New layer "ref"; `File → Import` `female_reference.png` onto it. Scale/position so
   its two figures sit over the two SVG figures (match shoulders & feet). Set the layer
   ~40% opacity and **lock** it.
3. Open `Object → Objects…` and the XML editor (`Edit → XML Editor`, Ctrl+Shift+X).
   Each path shows its `id` — select by id, then node-edit (`N`) over the reference.
4. **Do not run "Clean Up Document" or "Vacuum Defs"**, and save as **Plain SVG**
   (`File → Save As → Plain SVG`). Both can rewrite/strip ids and namespaces.
5. After saving, run the validator (below). If it complains that a path isn't matched
   by the library regex, that path got wrapped onto multiple lines — re-save as Plain
   SVG, or join it onto one line.

(Figma works too: place the PNG as a locked background, edit each vector layer, then
export SVG. Keep the layer name = the `id`, and re-apply `id`/`title` if Figma drops
them — the validator will tell you which are missing.)

## Validate after every pass
```
python tracing/validate_female_svg.py
```
Must print `PASS` (well-formed XML · all 52 ids present · 52 one-line regex matches · renders).

## Per-region checklist
Tick a region once it matches the reference. ids come straight from
`lib/src/parser.dart` (`muscleGroups`).

### Anterior figure (left)
- [ ] chest — `chest1`, `chest2`  · pectorals; female chest sits over the pec, keep the pec region
- [ ] shoulders (front delts) — `shoulder1`, `shoulder2`  · narrower than male
- [ ] biceps — `biceps1`, `biceps2`
- [ ] forearms (front) — `forearm1`, `forearm2`
- [ ] neck — `neck`  · slimmer
- [ ] upper traps (front) — `trapezius4`, `trapezius5`
- [ ] abs — `abs1`–`abs8`  · rectus abdominis, 8 segments (present in everyone)
- [ ] obliques — `obliques1`, `obliques2`  · the waist taper lives here
- [ ] hip abductors — `abductor1`, `abductor2`  · wider
- [ ] quads — `quads1`–`quads4`
- [ ] adductors (inner thigh) — `adductors1`, `adductors2`

### Posterior figure (right)
- [ ] rear delts — `shoulder3`, `shoulder4`
- [ ] triceps — `triceps1`, `triceps2`
- [ ] forearms (back) — `forearm3`, `forearm4`
- [ ] traps — `trapezius1`, `trapezius2`, `trapezius3`
- [ ] upper back — `upper_back1`, `upper_back2`
- [ ] lats — `lats1`, `lats2`
- [ ] lower back — `lower_back`  · (erector spinae)
- [ ] glutes — `glutes1`, `glutes2`  · fuller / wider
- [ ] hamstrings — `harmstrings1`, `harmstrings2`  · (note the original's `harmstrings` spelling — keep it)
- [ ] calves — `calves1`–`calves4`  · this map shows calves on the back view only

### Silhouette
- [ ] `human_body` — body outline for BOTH figures (one path, two contours). Not
      selectable; widen hips / narrow shoulders / slim neck so muscles sit inside it.
      The head/hair is just a blob here — feminise it if you like, it carries no muscle.

## How the scaffold was derived
`tracing/derive_female_scaffold.py` warps the male map: a horizontal scale that varies
with height (narrow shoulders → pinched waist → wide hips/pelvis), applied about each
figure's vertical axis. It only moves `x` by `y`, so ids and vertical registration are
untouched. Re-run it to regenerate the scaffold from a fresh `human_body.svg`.
