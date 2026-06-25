import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:muscle_selector/muscle_selector.dart';

import 'helpers/asset_mock.dart';

Widget _host(Widget child) => MaterialApp(
      home: Scaffold(
        body: Center(
          child: SizedBox(width: 200, height: 300, child: child),
        ),
      ),
    );

Set<String> _selectedIds(GlobalKey<MusclePickerMapState> key) =>
    key.currentState!.selectedMuscles.map((m) => m.id).toSet();

void main() {
  testWidgets('loads the map and renders without error', (tester) async {
    mockMuscleAssets(tester);
    await tester.pumpWidget(_host(MusclePickerMap(
      width: 200,
      height: 300,
      gender: Gender.male,
      onChanged: (_) {},
    )));
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(CustomPaint), findsWidgets);
  });

  testWidgets('initialSelectedGroups seeds the whole group', (tester) async {
    mockMuscleAssets(tester);
    final key = GlobalKey<MusclePickerMapState>();
    Set<Muscle>? changed;

    await tester.pumpWidget(_host(MusclePickerMap(
      key: key,
      width: 200,
      height: 300,
      gender: Gender.male,
      initialSelectedGroups: const ['chest'],
      onChanged: (m) => changed = m,
    )));
    await tester.pumpAndSettle();

    expect(_selectedIds(key), containsAll(<String>['chest1', 'chest2']));
    expect(changed, isNotNull);
  });

  testWidgets('clearSelect empties the selection', (tester) async {
    mockMuscleAssets(tester);
    final key = GlobalKey<MusclePickerMapState>();

    await tester.pumpWidget(_host(MusclePickerMap(
      key: key,
      width: 200,
      height: 300,
      gender: Gender.male,
      initialSelectedGroups: const ['chest'],
      onChanged: (_) {},
    )));
    await tester.pumpAndSettle();
    expect(_selectedIds(key), isNotEmpty);

    key.currentState!.clearSelect();
    await tester.pump();
    expect(key.currentState!.selectedMuscles, isEmpty);
  });

  testWidgets('tapping a muscle selects its whole group; toggle deselects',
      (tester) async {
    // full-area chest1 last in document -> topmost -> a centre tap lands on it
    mockMuscleAssets(tester, male: svgOf([humanPath, fullChest1]));
    final key = GlobalKey<MusclePickerMapState>();

    await tester.pumpWidget(_host(MusclePickerMap(
      key: key,
      width: 200,
      height: 300,
      gender: Gender.male,
      actAsToggle: true,
      onChanged: (_) {},
    )));
    await tester.pumpAndSettle();

    await tester.tap(find.byType(GestureDetector).last, warnIfMissed: false);
    await tester.pump();
    expect(_selectedIds(key), <String>{'chest1', 'chest2'});

    await tester.tap(find.byType(GestureDetector).last, warnIfMissed: false);
    await tester.pump();
    expect(key.currentState!.selectedMuscles, isEmpty);
  });

  testWidgets('isEditing disables selection', (tester) async {
    // full-area chest1 would be hit at the centre -> proves isEditing blocks it
    mockMuscleAssets(tester, male: svgOf([humanPath, fullChest1]));
    final key = GlobalKey<MusclePickerMapState>();

    await tester.pumpWidget(_host(MusclePickerMap(
      key: key,
      width: 200,
      height: 300,
      gender: Gender.male,
      isEditing: true,
      onChanged: (_) {},
    )));
    await tester.pumpAndSettle();

    await tester.tap(find.byType(GestureDetector).last, warnIfMissed: false);
    await tester.pump();
    expect(key.currentState!.selectedMuscles, isEmpty);
  });

  testWidgets('the human_body silhouette is not selectable', (tester) async {
    // selectable chest underneath, human_body full-area on top -> tap hits the
    // silhouette (topmost) but it must not select anything
    mockMuscleAssets(tester, male: svgOf([fullChest1, humanPath]));
    final key = GlobalKey<MusclePickerMapState>();

    await tester.pumpWidget(_host(MusclePickerMap(
      key: key,
      width: 200,
      height: 300,
      gender: Gender.male,
      onChanged: (_) {},
    )));
    await tester.pumpAndSettle();

    await tester.tap(find.byType(GestureDetector).last, warnIfMissed: false);
    await tester.pump();
    expect(key.currentState!.selectedMuscles, isEmpty);
  });

  testWidgets('switching gender reloads a different map', (tester) async {
    mockMuscleAssets(tester); // female fixture additionally has the biceps group
    final key = GlobalKey<MusclePickerMapState>();
    var gender = Gender.male;
    late StateSetter setOuter;

    await tester.pumpWidget(_host(StatefulBuilder(
      builder: (context, setState) {
        setOuter = setState;
        return MusclePickerMap(
          key: key,
          width: 200,
          height: 300,
          gender: gender,
          initialSelectedGroups: const ['biceps'],
          onChanged: (_) {},
        );
      },
    )));
    await tester.pumpAndSettle();
    // male map has no biceps -> nothing to seed
    expect(_selectedIds(key).where((id) => id.startsWith('biceps')), isEmpty);

    setOuter(() => gender = Gender.female);
    await tester.pumpAndSettle();
    // female map has biceps -> the group is now present and seeded
    expect(_selectedIds(key), containsAll(<String>['biceps1', 'biceps2']));
  });
}
