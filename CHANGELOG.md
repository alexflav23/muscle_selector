## 1.0.0

- Muscle Selector for Flutter

## 1.0.1
- Bug fix for muscle deselection.

## 1.0.2
- Now widget accepts a list of initial group of muscles

## 1.0.3
- Neck and Lower Back Implementation

## 1.0.4
- Fix spelling of 'hamstrings', correct 'lats' mapping and add 'upper back'

## 1.1.0
- **Female body map** (`assets/maps/human_body_female.svg`) sharing the identical 52
  muscle ids with the male map, plus a `gender` switch: `Gender`, `Maps.BODY_FEMALE`,
  `Maps.forGender()`, and `MusclePickerMap(gender: …)`. `map:` stays supported and is
  fully backward compatible.
- **Fix:** `SizeController` accumulated bounds across map loads; it now resets before
  each parse, so runtime map/gender switching scales correctly.
- `MusclePickerMap` reloads the body when `gender`/`map` changes (`didUpdateWidget`).
- **CI**: GitHub Actions PR builder (analyze + test + web build for package & example).
- **Tests**: comprehensive suite (34 package + 1 example) — see `SPEC.md` for the matrix.
- **Docs**: `SPEC.md`, and a tracing workflow + SVG validator for refining the female art.