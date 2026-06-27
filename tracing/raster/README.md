# Raster muscle maps (illustration + invisible hit-map)

The female map ships as a **rendered illustration** (`assets/maps/human_body_female.png`)
with the 52 named SVG paths (`human_body_female.svg`) overlaid as an **invisible
hit / highlight layer**. The widget draws the image and tints only the muscles that
are selected (see `MusclePainter`'s `overlay` mode, enabled via `Maps.imageForMap`).
This gives a premium illustrated look while keeping every muscle tappable.

## How the assets were produced

1. **Silhouette** — render the source map as a solid grey body silhouette to capture
   the exact pose and layout → `female_silhouette_ref.png`.
2. **Illustration** — generate a clean flat female muscular-system chart *conditioned
   on that silhouette* (image-to-image), so the result keeps the same pose, size and
   limb angles → `female_source_2k.png`. Because the pose matches the source map, the
   muscles line up with our paths.
3. **Align** — `python tracing/raster/align_hitmap.py female` maps every muscle path
   onto the image with a per-figure bbox→bbox affine (shapes match → clean alignment,
   no smear), anchors `human_body` to the image corners so the coordinate frame equals
   the image, and writes `assets/maps/human_body_female.svg` + `.png`.

4. **Seat the legs** — `python tracing/raster/leg_correct.py <gender>` nudges the
   leg muscles down onto the illustration (the torso aligns from step 3, but the
   AI draws thighs/calves slightly lower). Run it once, after `align_hitmap.py`.

5. **Reshape the calves** — `python tracing/raster/calf_shapes.py <gender>` swaps
   the scattered inherited calf paths for clean leaf shapes seated on each
   gastrocnemius. Run once, after `leg_correct.py`.

6. **Female fixups** — `python tracing/raster/female_fixups.py` repositions the
   female neck (was on the chin) and deltoids (were inboard) onto the muscle.
   Run once, after the steps above.

The hit-map only needs to *approximately* cover each muscle — the highlight is a
translucent tint — so small mismatches are invisible.

## Invariants (still enforced)

`python tracing/validate_female_svg.py` → 52 ids · one line each · well-formed.
The PNG must stay 1:1 with the SVG `viewBox` (`align_hitmap.py` guarantees this).
