import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:muscle_selector/src/constant.dart';
import 'package:muscle_selector/src/parser.dart';

final _regExp = RegExp(Constants.MAP_REGEXP,
    multiLine: true, caseSensitive: false, dotAll: false);

List<String> _idsOf(String svg) =>
    _regExp.allMatches(svg).map((m) => m.group(1)!).toList();

void main() {
  final male = File('assets/maps/human_body.svg').readAsStringSync();
  final female = File('assets/maps/human_body_female.svg').readAsStringSync();

  test('female asset exists and is non-trivial', () {
    expect(File('assets/maps/human_body_female.svg').existsSync(), isTrue);
    expect(female.length, greaterThan(1000));
  });

  group('male / female parity (the contract the selection engine relies on)',
      () {
    test('both expose exactly 52 named paths', () {
      expect(_idsOf(male).length, 52);
      expect(_idsOf(female).length, 52);
    });

    test('the female map has the identical id set to the male map', () {
      expect(_idsOf(female).toSet(), _idsOf(male).toSet());
    });

    test('no duplicate ids in either map', () {
      expect(_idsOf(male).toSet().length, 52);
      expect(_idsOf(female).toSet().length, 52);
    });
  });

  group('every muscleGroups member is drawable in both maps', () {
    final required = Parser.muscleGroups.values.expand((g) => g).toSet()
      ..add('human_body');

    test('male covers every grouped id (+ human_body)', () {
      expect(_idsOf(male).toSet(), containsAll(required));
    });

    test('female covers every grouped id (+ human_body)', () {
      expect(_idsOf(female).toSet(), containsAll(required));
    });
  });

  group('female asset is tool-clean (valid for Inkscape/Figma round-trips)',
      () {
    final pathLines = female
        .split('\n')
        .where((l) => l.contains('<path '))
        .toList();

    test('every path element is a single self-closed line', () {
      expect(pathLines.length, 52);
      for (final line in pathLines) {
        expect(line.trimRight().endsWith('/>'), isTrue,
            reason: 'not self-closed: $line');
      }
    });

    test('every path line still matches the library regex', () {
      for (final line in pathLines) {
        expect(_regExp.hasMatch(line), isTrue, reason: 'no id/title/d: $line');
      }
    });
  });
}
