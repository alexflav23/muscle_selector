import 'dart:io';
import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:muscle_selector/muscle_selector.dart';
import 'package:muscle_selector/src/constant.dart';
import 'package:muscle_selector/src/parser.dart';

Muscle _m(String id) => Muscle(id: id, title: id, path: Path());

void main() {
  group('muscleGroups catalogue', () {
    test('defines 18 groups covering 51 sub-muscle ids', () {
      expect(Parser.muscleGroups.length, 18);
      final allIds =
          Parser.muscleGroups.values.expand((g) => g).toList();
      expect(allIds.length, 51);
      expect(allIds.toSet().length, 51, reason: 'no id belongs to two groups');
    });

    test('key groups have the expected members', () {
      expect(Parser.muscleGroups['chest'], ['chest1', 'chest2']);
      expect(Parser.muscleGroups['abs']!.length, 8);
      expect(Parser.muscleGroups['trapezius']!.length, 5);
      expect(Parser.muscleGroups['neck'], ['neck']);
      expect(Parser.muscleGroups['lower_back'], ['lower_back']);
    });
  });

  group('getMusclesByGroups', () {
    final muscles = [
      _m('chest1'),
      _m('chest2'),
      _m('neck'),
      _m('biceps1'),
      _m('biceps2'),
    ];

    test('returns every present member of the requested group', () {
      final got = Parser.instance.getMusclesByGroups(['chest'], muscles);
      expect(got.map((m) => m.id).toSet(), {'chest1', 'chest2'});
    });

    test('spans multiple groups', () {
      final got =
          Parser.instance.getMusclesByGroups(['chest', 'biceps'], muscles);
      expect(got.map((m) => m.id).toSet(),
          {'chest1', 'chest2', 'biceps1', 'biceps2'});
    });

    test('ignores unknown group keys', () {
      expect(Parser.instance.getMusclesByGroups(['nope'], muscles), isEmpty);
    });

    test('only returns members actually present in the list', () {
      final got = Parser.instance.getMusclesByGroups(['abs'], muscles);
      expect(got, isEmpty);
    });
  });

  group('MAP_REGEXP against the real male asset', () {
    final regExp = RegExp(Constants.MAP_REGEXP,
        multiLine: true, caseSensitive: false, dotAll: false);
    final svg = File('assets/maps/human_body.svg').readAsStringSync();

    test('extracts id/title/d for every path', () {
      final matches = regExp.allMatches(svg).toList();
      expect(matches.length, 52);
      final ids = matches.map((m) => m.group(1)).toSet();
      expect(ids, containsAll(<String>['chest1', 'lower_back', 'human_body']));
    });
  });
}
