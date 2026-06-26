import 'package:flutter/material.dart';
import 'package:muscle_selector/muscle_selector.dart';
import 'package:muscle_selector/src/size_controller.dart';

class MusclePainter extends CustomPainter {
  final Muscle muscle;
  final Set<Muscle> selectedMuscles;
  final Color? strokeColor;
  final Color? selectedColor;
  final Color? dotColor;

  /// When true the map is rendered over a background illustration: muscles are
  /// invisible until selected, and a selection is drawn as a translucent tint.
  final bool overlay;

  /// Strength of the selection tint in [overlay] mode (0 = invisible, 1 = solid).
  final double overlayOpacity;

  final sizeController = SizeController.instance;

  double _scale = 1.0;

  MusclePainter({
    required this.muscle,
    required this.selectedMuscles,
    this.selectedColor,
    this.strokeColor,
    this.dotColor,
    this.overlay = false,
    this.overlayOpacity = 0.45,
  });

  @override
  void paint(Canvas canvas, Size size) {
    _scale = sizeController.calculateScale(size);
    canvas.scale(_scale);

    final isSelected =
        selectedMuscles.any((selected) => selected.id == muscle.id);

    if (overlay) {
      // The illustration carries the muscle outlines; only tint a selection.
      if (muscle.id == 'human_body') return;
      if (isSelected) {
        canvas.drawPath(
          muscle.path,
          Paint()
            ..color = (selectedColor ?? Colors.blue).withOpacity(overlayOpacity)
            ..style = PaintingStyle.fill,
        );
      }
      return;
    }

    final pen = Paint()
      ..color = strokeColor ?? Colors.white60
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    final selectedPen = Paint()
      ..color = selectedColor ?? Colors.blue
      ..strokeWidth = 1.0
      ..style = PaintingStyle.fill;

    if (isSelected) {
      canvas.drawPath(muscle.path, selectedPen);
    }

    canvas.drawPath(muscle.path, pen);
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;

  @override
  bool hitTest(Offset position) {
    double inverseScale = sizeController.inverseOfScale(_scale);
    return muscle.path.contains(position.scale(inverseScale, inverseScale));
  }
}
