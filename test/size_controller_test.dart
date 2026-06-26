import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:muscle_selector/src/size_controller.dart';

void main() {
  final controller = SizeController.instance;

  setUp(controller.reset);

  test('is a singleton', () {
    expect(SizeController.instance, same(controller));
  });

  group('addBounds', () {
    test('seeds the map size from the first bound', () {
      controller.addBounds(const Rect.fromLTRB(10, 20, 40, 80));
      expect(controller.mapSize, const Size(30, 60));
    });

    test('grows to the union of all bounds', () {
      controller.addBounds(const Rect.fromLTRB(10, 10, 20, 20));
      controller.addBounds(const Rect.fromLTRB(0, 5, 50, 100));
      // union is (0,5)->(50,100)
      expect(controller.mapSize, const Size(50, 95));
    });
  });

  test('reset clears accumulated bounds (the gender-switch fix)', () {
    controller.addBounds(const Rect.fromLTRB(0, 0, 100, 200));
    expect(controller.mapSize, isNot(Size.zero));
    controller.reset();
    expect(controller.mapSize, Size.zero);
    // a fresh, smaller map after reset must NOT inherit the old larger bounds
    controller.addBounds(const Rect.fromLTRB(0, 0, 10, 10));
    expect(controller.mapSize, const Size(10, 10));
  });

  group('calculateScale', () {
    setUp(() {
      controller.reset();
      controller.addBounds(const Rect.fromLTRB(0, 0, 100, 200)); // 100x200 map
    });

    test('returns 1.0 for a null container', () {
      expect(controller.calculateScale(null), 1.0);
    });

    test('scales up to a larger container (portrait branch)', () {
      final scale = controller.calculateScale(const Size(200, 600));
      expect(scale, greaterThan(1.0));
    });

    test('landscape container takes the width>height branch', () {
      final scale = controller.calculateScale(const Size(400, 100));
      expect(scale, greaterThan(0));
    });
  });

  test('inverseOfScale is the reciprocal', () {
    expect(controller.inverseOfScale(2.0), 0.5);
    expect(controller.inverseOfScale(0.5), 2.0);
  });
}
