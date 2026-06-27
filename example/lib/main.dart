import 'package:flutter/material.dart';
import 'package:muscle_selector/muscle_selector.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Muscle Selector',
      home: HomeView(),
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.lightBlue),
    );
  }
}

class HomeView extends StatefulWidget {
  @override
  _HomeViewState createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  final GlobalKey<MusclePickerMapState> _mapKey = GlobalKey();

  Gender _gender = Gender.male;
  // The highlighted groups, held in app state by *key* so the selection
  // survives a gender switch (re-seeded via initialSelectedGroups on reload).
  Set<String> _groups = {'chest', 'glutes', 'neck', 'lower_back'};

  // Highlight styles the user can switch between: flat colours and premium
  // gradients. The map takes either a `selectedColor` or a `selectedGradient`.
  int _styleIndex = 0;
  static const _begin = Alignment.topCenter, _end = Alignment.bottomCenter;
  final List<HighlightStyle> _styles = [
    HighlightStyle.solid('Blue', Colors.lightBlueAccent),
    HighlightStyle.solid('Green', const Color(0xFF34D399)),
    HighlightStyle.solid('Pink', Colors.pinkAccent),
    HighlightStyle.gradient('Sunset', const LinearGradient(
        begin: _begin, end: _end,
        colors: [Color(0xCCFF7A45), Color(0xCCFF2D78)])),
    HighlightStyle.gradient('Ocean', const LinearGradient(
        begin: _begin, end: _end,
        colors: [Color(0xCC22D3EE), Color(0xCC3B82F6)])),
    HighlightStyle.gradient('Neon', const LinearGradient(
        begin: Alignment.topLeft, end: Alignment.bottomRight,
        colors: [Color(0xCCA855F7), Color(0xCC2563EB)])),
    HighlightStyle.gradient('Lime', const LinearGradient(
        begin: _begin, end: _end,
        colors: [Color(0xCC2DD4BF), Color(0xD9A3E635)])),
  ];

  // Pretty labels for the group keys from Parser.muscleGroups.
  static const _labels = {
    'harmstrings': 'Hamstrings',
    'upper_back': 'Upper back',
    'lower_back': 'Lower back',
    'abductor': 'Abductors',
  };
  String _label(String key) =>
      _labels[key] ?? '${key[0].toUpperCase()}${key.substring(1)}';

  // Map the selected muscles back to their group keys for the chip panel.
  Set<String> _groupKeysFor(Set<Muscle> muscles) => {
        for (final muscle in muscles)
          for (final entry in Parser.muscleGroups.entries)
            if (entry.value.contains(muscle.id)) entry.key,
      };

  @override
  Widget build(BuildContext context) {
    final allGroups = Parser.muscleGroups.keys.toList()
      ..sort((a, b) => _label(a).compareTo(_label(b)));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Muscle Selector'),
        actions: [
          IconButton(
            tooltip: 'Clear selection',
            icon: const Icon(Icons.clear_all),
            onPressed: () => _mapKey.currentState?.clearSelect(),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: SizedBox(
              width: double.infinity,
              child: SegmentedButton<Gender>(
                segments: const [
                  ButtonSegment(
                      value: Gender.male,
                      label: Text('Male'),
                      icon: Icon(Icons.male)),
                  ButtonSegment(
                      value: Gender.female,
                      label: Text('Female'),
                      icon: Icon(Icons.female)),
                ],
                selected: {_gender},
                onSelectionChanged: (s) => setState(() => _gender = s.first),
              ),
            ),
          ),
          Expanded(
            child: LayoutBuilder(
              builder: (context, constraints) => InteractiveViewer(
                minScale: 0.8,
                maxScale: 4,
                child: Center(
                  child: MusclePickerMap(
                    key: _mapKey,
                    width: constraints.maxWidth,
                    height: constraints.maxHeight,
                    gender: _gender,
                    isEditing: false,
                    // Re-seeded on every (re)load, so the highlight is restored
                    // when the body reloads after a gender switch.
                    initialSelectedGroups: _groups.toList(),
                    actAsToggle: true,
                    dotColor: Colors.black,
                    // Highlight styling chosen from the picker below — proves the
                    // colour and gradient are fully controllable from the app.
                    selectedColor: _styles[_styleIndex].color,
                    selectedGradient: _styles[_styleIndex].gradient,
                    overlayOpacity: 0.5,
                    strokeColor: Colors.black54,
                    onChanged: (muscles) =>
                        setState(() => _groups = _groupKeysFor(muscles)),
                  ),
                ),
              ),
            ),
          ),
          _StylePicker(
            styles: _styles,
            selectedIndex: _styleIndex,
            onSelected: (i) => setState(() => _styleIndex = i),
          ),
          _GroupPanel(
            allGroups: allGroups,
            selected: _groups,
            label: _label,
            onToggle: (key, isOn) {
              final state = _mapKey.currentState;
              if (state == null) return;
              isOn ? state.selectGroups([key]) : state.deselectGroups([key]);
            },
          ),
        ],
      ),
    );
  }
}

/// A highlight option: either a flat [color] or a [gradient] (premium look).
class HighlightStyle {
  final String name;
  final Color? color;
  final Gradient? gradient;
  const HighlightStyle.solid(this.name, Color this.color) : gradient = null;
  const HighlightStyle.gradient(this.name, Gradient this.gradient)
      : color = null;

  /// A fully-opaque preview decoration for the swatch (the live highlight is
  /// translucent so the muscle shows through).
  BoxDecoration get swatch => BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        gradient: gradient,
      );
}

/// Horizontal picker of highlight colours and gradients.
class _StylePicker extends StatelessWidget {
  final List<HighlightStyle> styles;
  final int selectedIndex;
  final ValueChanged<int> onSelected;

  const _StylePicker({
    required this.styles,
    required this.selectedIndex,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 84,
      padding: const EdgeInsets.symmetric(vertical: 8),
      color: Theme.of(context).colorScheme.surface,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: styles.length,
        separatorBuilder: (_, __) => const SizedBox(width: 14),
        itemBuilder: (context, i) {
          final style = styles[i];
          final isSelected = i == selectedIndex;
          return GestureDetector(
            onTap: () => onSelected(i),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: style.swatch.copyWith(
                    border: Border.all(
                      color: isSelected
                          ? Theme.of(context).colorScheme.primary
                          : Colors.black12,
                      width: isSelected ? 3 : 1,
                    ),
                  ),
                  child: isSelected
                      ? const Icon(Icons.check, size: 20, color: Colors.white)
                      : null,
                ),
                const SizedBox(height: 4),
                Text(style.name, style: Theme.of(context).textTheme.labelSmall),
              ],
            ),
          );
        },
      ),
    );
  }
}

/// Bottom sheet of filter chips — one per muscle group — kept in two-way sync
/// with the body map: tap the body or a chip, both update.
class _GroupPanel extends StatelessWidget {
  final List<String> allGroups;
  final Set<String> selected;
  final String Function(String) label;
  final void Function(String key, bool isOn) onToggle;

  const _GroupPanel({
    required this.allGroups,
    required this.selected,
    required this.label,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      elevation: 8,
      child: SafeArea(
        top: false,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxHeight: 220),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Highlight groups · ${selected.length} of ${allGroups.length} selected',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                Expanded(
                  child: SingleChildScrollView(
                    child: Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        for (final key in allGroups)
                          FilterChip(
                            label: Text(label(key)),
                            selected: selected.contains(key),
                            onSelected: (isOn) => onToggle(key, isOn),
                          ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
