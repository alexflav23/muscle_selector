import 'dart:ui';
import 'package:muscle_selector/src/models/map_area.dart';

class SizeController {
  static SizeController? _instance;

  static SizeController get instance {
    _instance ??= SizeController._init();
    return _instance!;
  }

  SizeController._init();

  final MapArea _mapArea = MapArea();
  Size mapSize = Size.zero;

  void addBounds(Rect bound) {
    if (_mapArea.anyEmpty) {
      _mapArea
        ..minX = bound.left
        ..maxX = bound.right
        ..minY = bound.top
        ..maxY = bound.bottom;
    } else {
      if (bound.left < _mapArea.minX!) _mapArea.minX = bound.left;
      if (bound.right > _mapArea.maxX!) _mapArea.maxX = bound.right;
      if (bound.top < _mapArea.minY!) _mapArea.minY = bound.top;
      if (bound.bottom > _mapArea.maxY!) _mapArea.maxY = bound.bottom;
    }
    calculateArea();
  }

  void reset() {
    _mapArea
      ..minX = null
      ..maxX = null
      ..minY = null
      ..maxY = null;
    mapSize = Size.zero;
  }

  void calculateArea() {
    if (_mapArea.anyEmpty) mapSize = Size.zero;

    double width = _mapArea.maxX! - _mapArea.minX!;
    double height = _mapArea.maxY! - _mapArea.minY!;

    mapSize = Size(width, height);
  }

  double calculateScale(Size? containerSize) {
    if (containerSize == null) {
      return 1.0;
    }

    double newWidth = containerSize.width, newHeight = containerSize.height;
    if (containerSize.width > containerSize.height) {
      newHeight = 1 /(mapSize.aspectRatio / containerSize.width);
    }
    else {
      newHeight = containerSize.width / mapSize.aspectRatio;
    }
    containerSize = Size(newWidth, newHeight);

    double scale1 = containerSize.width / mapSize.width;
    double scale2 = containerSize.height / mapSize.height;
    double mapScale = scale1 > scale2 ? scale1 : scale2;

    return mapScale;
  }

  double inverseOfScale(double scale) => 1.0/scale;
}