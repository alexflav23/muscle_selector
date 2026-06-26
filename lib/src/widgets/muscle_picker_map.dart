import 'package:flutter/material.dart';
import 'package:muscle_selector/muscle_selector.dart';
import 'package:muscle_selector/src/widgets/muscle_painter.dart';
import '../constant.dart';
import '../size_controller.dart';

class MusclePickerMap extends StatefulWidget {
  final double? width;
  final double? height;
  final String? map;
  final Gender? gender;
  final Function(Set<Muscle> muscles) onChanged;
  final Color? strokeColor;

  /// Colour used to highlight a selected muscle. On the illustrated (image)
  /// maps it is drawn as a translucent tint over the muscle; on plain vector
  /// maps it fills the muscle. Set this from the app to theme the highlight.
  final Color? selectedColor;
  final Color? dotColor;

  /// Strength of the highlight tint on the illustrated maps (0–1, default 0.45).
  final double overlayOpacity;
  final bool? actAsToggle;
  final bool? isEditing;
  final Set<Muscle>? initialSelectedMuscles;
  final List<String>? initialSelectedGroups;

  const MusclePickerMap({
    Key? key,
    required this.onChanged,
    this.map,
    this.gender,
    this.width,
    this.height,
    this.strokeColor,
    this.selectedColor,
    this.dotColor,
    this.overlayOpacity = 0.45,
    this.actAsToggle,
    this.isEditing = false,
    this.initialSelectedMuscles,
    this.initialSelectedGroups
  })  : assert(map != null || gender != null,
            'Provide either a map asset or a gender'),
        super(key: key);

  String get resolvedMap => map ?? Maps.forGender(gender ?? Gender.male);

  @override
  MusclePickerMapState createState() => MusclePickerMapState();
}

class MusclePickerMapState extends State<MusclePickerMap> {
  final List<Muscle> _muscleList = [];
  final Set<Muscle> selectedMuscles = {};

  final _sizeController = SizeController.instance;
  Size? mapSize;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadMuscleList();
    });
  }

  @override
  void didUpdateWidget(covariant MusclePickerMap oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.resolvedMap != widget.resolvedMap) {
      _loadMuscleList();
    }
  }

  _loadMuscleList() async {
    final list = await Parser.instance.svgToMuscleList(widget.resolvedMap);
    _muscleList.clear();
    setState(() {
      _muscleList.addAll(list);
      mapSize = _sizeController.mapSize;
      _initializeSelectedMuscles();
    });
  }

  void _initializeSelectedMuscles() {
    if (widget.initialSelectedMuscles != null) {
      selectedMuscles.addAll(widget.initialSelectedMuscles!);
    } else if (widget.initialSelectedGroups != null && widget.initialSelectedGroups!.isNotEmpty) {
      final groupMuscles = Parser.instance.getMusclesByGroups(widget.initialSelectedGroups!, _muscleList);
      selectedMuscles.addAll(groupMuscles);
    }
    widget.onChanged.call(selectedMuscles);
  }

  void clearSelect() {
    setState(() {
      selectedMuscles.clear();
    });
    widget.onChanged.call(selectedMuscles);
  }

  /// Highlight whole muscle groups (e.g. `['chest', 'glutes']`) programmatically.
  void selectGroups(List<String> groupKeys) {
    final muscles = Parser.instance.getMusclesByGroups(groupKeys, _muscleList);
    setState(() => selectedMuscles.addAll(muscles));
    widget.onChanged.call(selectedMuscles);
  }

  /// Clear the highlight from whole muscle groups.
  void deselectGroups(List<String> groupKeys) {
    final muscles = Parser.instance.getMusclesByGroups(groupKeys, _muscleList);
    setState(() => selectedMuscles.removeAll(muscles));
    widget.onChanged.call(selectedMuscles);
  }

  /// The group keys (from [Parser.muscleGroups]) currently highlighted.
  Set<String> get selectedGroups => {
        for (final muscle in selectedMuscles)
          for (final entry in Parser.muscleGroups.entries)
            if (entry.value.contains(muscle.id)) entry.key,
      };

  /// When the resolved map has a companion illustration, the silhouette is an
  /// invisible hit/highlight layer drawn over that image.
  String? get _imageAsset => Maps.imageForMap(widget.resolvedMap);

  @override
  Widget build(BuildContext context) {
    final image = _imageAsset;
    final size = mapSize;
    if (image != null && size != null && size != Size.zero) {
      // Overlay mode: the illustration and the (transparent) hit/highlight paths
      // live in one mapSize box and are scaled together by the FittedBox, so the
      // tints line up with the image exactly regardless of the available space.
      return Center(
        child: FittedBox(
          fit: BoxFit.contain,
          child: SizedBox(
            width: size.width,
            height: size.height,
            child: Stack(
              children: [
                Image.asset(
                  '${Constants.ASSETS_PATH}/$image',
                  width: size.width,
                  height: size.height,
                  fit: BoxFit.fill,
                  errorBuilder: (context, error, stack) =>
                      const SizedBox.shrink(),
                ),
                // Skip human_body: it only exists to anchor the coordinate frame
                // to the image (its rect spans the whole map) and must not eat taps.
                for (var muscle in _muscleList)
                  if (muscle.id != 'human_body') _buildStackItem(muscle, true),
              ],
            ),
          ),
        ),
      );
    }
    return Stack(
      children: [
        for (var muscle in _muscleList) _buildStackItem(muscle, false),
      ],
    );
  }

  Widget _buildStackItem(Muscle muscle, bool overlay) {

    final bool isSelectable = muscle.id != 'human_body' && !widget.isEditing!;

    return GestureDetector(
      behavior: HitTestBehavior.deferToChild,
      onTap: () => {
        if (isSelectable) {
          (widget.actAsToggle ?? false) ? _toggleButton(muscle) : _useButton(muscle)
        }
      },
      child: CustomPaint(
        isComplex: true,
        foregroundPainter: MusclePainter(
          muscle: muscle,
          selectedMuscles: selectedMuscles,
          dotColor: widget.dotColor,
          selectedColor: widget.selectedColor,
          strokeColor: widget.strokeColor,
          overlay: overlay,
          overlayOpacity: widget.overlayOpacity,
        ),
        // In overlay mode the canvas is exactly mapSize (so the painter's scale
        // is 1 and paths sit in image-pixel space); otherwise fill the widget.
        child: overlay
            ? SizedBox(width: mapSize?.width, height: mapSize?.height)
            : Container(
                width: widget.width ?? double.infinity,
                height: widget.height ?? double.infinity,
                constraints: BoxConstraints(
                  maxWidth: mapSize?.width ?? 0,
                  maxHeight: mapSize?.height ?? 0,
                ),
                alignment: Alignment.center,
              ),
      ),
    );
  }

  void _toggleButton(Muscle muscle) {
    setState(() {
      final group = Parser.muscleGroups.entries.firstWhere(
            (entry) => entry.value.contains(muscle.id),
        orElse: () => const MapEntry('', []),
      );

      if (group.key.isNotEmpty) {
        final relatedMuscles = _muscleList.where((m) => group.value.contains(m.id)).toList();
        if (relatedMuscles.every((m) => selectedMuscles.contains(m))) {
          selectedMuscles.removeAll(relatedMuscles);
        } else {
          selectedMuscles.addAll(relatedMuscles);
        }
      } else {
        if (selectedMuscles.contains(muscle)) {
          selectedMuscles.remove(muscle);
        } else {
          selectedMuscles.add(muscle);
        }
      }
      widget.onChanged.call(selectedMuscles);
    });
  }

  void _useButton(Muscle muscle) {
    setState(() {
      final group = Parser.muscleGroups.entries.firstWhere(
            (entry) => entry.value.contains(muscle.id),
        orElse: () => const MapEntry('', []),
      );

      if (group.key.isNotEmpty) {
        final relatedMuscles = _muscleList.where((m) => group.value.contains(m.id)).toList();
        selectedMuscles.addAll(relatedMuscles);
      } else {
        selectedMuscles.add(muscle);
      }
      widget.onChanged.call(selectedMuscles);
    });
  }
}
