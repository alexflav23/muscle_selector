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
                    selectedColor: Colors.lightBlueAccent,
                    strokeColor: Colors.black54,
                    onChanged: (muscles) =>
                        setState(() => _groups = _groupKeysFor(muscles)),
                  ),
                ),
              ),
            ),
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
