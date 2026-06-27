# Muscle Selector

Interactive Human Body **Muscle Selector** for Flutter — tap muscle groups on an
anatomical SVG body. Supports **male and female** bodies, group selection, toggling,
and pre-seeded selections.

> Fork of [EmilCes/muscle_selector](https://github.com/EmilCes/muscle_selector) adding
> a female body map + `gender` switch, a CI PR builder, and a full test suite.

https://github.com/EmilCes/muscle_selector/assets/50472267/91fa44e9-2962-4ab0-b1cc-58bb59c0e4e1

## Features

- Anterior **and** posterior views in one tappable diagram.
- **Male and female** bodies sharing the exact same muscle ids (`gender:` switch).
- 18 muscle groups / 51 sub-muscles; tapping a sub-muscle selects the whole group.
- Toggle selection, programmatic clear, and initial selection by group or muscle.
- Selection callback returns a `Set<Muscle>`.

## Getting started

```yaml
dependencies:
  muscle_selector:
    git:
      url: https://github.com/alexflav23/muscle_selector.git
```

```dart
import 'package:muscle_selector/muscle_selector.dart';
```

## Usage

```dart
final mapKey = GlobalKey<MusclePickerMapState>();
Gender gender = Gender.female;

MusclePickerMap(
  key: mapKey,
  gender: gender,                       // or: map: Maps.BODY
  initialSelectedGroups: const ['chest', 'glutes'],
  actAsToggle: true,
  selectedColor: Colors.lightBlueAccent,
  strokeColor: Colors.black,
  dotColor: Colors.black,
  onChanged: (Set<Muscle> muscles) {
    // muscles selected
  },
);

// highlight / clear muscle groups programmatically (e.g. from your own buttons)
mapKey.currentState?.selectGroups(['chest', 'glutes']);
mapKey.currentState?.deselectGroups(['glutes']);
mapKey.currentState?.clearSelect();

// which groups are currently highlighted
final Set<String> groups = mapKey.currentState?.selectedGroups ?? {};
// the group keys themselves live in Parser.muscleGroups
```

Switching `gender` (or `map`) on a mounted widget reloads the body automatically.
The [`example/`](example/lib/main.dart) app is a full demo: a Male/Female toggle, the
interactive body, and a chip panel that highlights muscle groups in two-way sync with
the body — with the highlight carried by group key so it survives a gender switch.

### `MusclePickerMap` properties

| prop | type | notes |
|------|------|-------|
| `onChanged` | `Function(Set<Muscle>)` | **required** — selection callback |
| `gender` | `Gender?` | `Gender.male` / `Gender.female` (resolves the asset) |
| `map` | `String?` | asset filename, e.g. `Maps.BODY`; alternative to `gender` |
| `width` / `height` | `double?` | layout size |
| `actAsToggle` | `bool?` | tap toggles a group on/off |
| `isEditing` | `bool?` | when `true`, disables selection |
| `initialSelectedGroups` | `List<String>?` | group keys to pre-select |
| `initialSelectedMuscles` | `Set<Muscle>?` | muscles to pre-select |
| `selectedColor` | `Color?` | **highlight colour** — set from the app; tints the selected muscle |
| `selectedGradient` | `Gradient?` | highlight as a gradient (overrides `selectedColor`); spanned across the whole map so it stays coherent across muscles |
| `overlayOpacity` | `double` | highlight strength on the illustrated maps (0–1, default `0.45`) |
| `strokeColor` / `dotColor` | `Color?` | outline styling (plain vector maps only) |

> The built-in male/female maps are illustrations with the muscles overlaid as an
> invisible hit layer, so only `selectedColor` (+ `overlayOpacity`) affect their look;
> `strokeColor`/`dotColor` apply to plain vector maps you pass via `map:`.

> Provide **either** `gender` or `map` (asserted at construction).

### `MusclePickerMapState` methods (via the `GlobalKey`)

| method | notes |
|--------|-------|
| `selectGroups(List<String> keys)` | highlight whole muscle groups |
| `deselectGroups(List<String> keys)` | clear the highlight from groups |
| `clearSelect()` | clear the whole selection |
| `selectedGroups` | `Set<String>` of currently highlighted group keys |

The muscle group / id catalogue and the full feature list are in [`SPEC.md`](SPEC.md).

## Female body map

The female map (`assets/maps/human_body_female.svg`) shares the identical 52 path ids
with the male map, so it's a drop-in — no selection code changes. The geometry was
derived from the male map by an anatomical proportional warp and is a **tappable
scaffold**, not a finished illustration. To refine it toward the bundled anatomy
reference, see [`tracing/TRACING.md`](tracing/TRACING.md) and validate edits with:

```
python tracing/validate_female_svg.py
```

## Development

```
flutter pub get
flutter analyze --no-fatal-infos
flutter test                 # 34 tests
cd example && flutter test   # example smoke test
```

CI (`.github/workflows/ci.yml`) runs analyze + tests for the package and the example,
and a web smoke build, on every pull request. The feature/test matrix is in
[`SPEC.md`](SPEC.md).

## License

MIT — see [LICENSE](LICENSE). Original work © EmilCes.
