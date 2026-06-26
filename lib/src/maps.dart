enum Gender { male, female }

class Maps {
  static const BODY = 'human_body.svg';
  static const BODY_FEMALE = 'human_body_female.svg';

  static String forGender(Gender gender) =>
      gender == Gender.female ? BODY_FEMALE : BODY;

  /// Maps whose `.svg` is an invisible hit/highlight layer over a rendered
  /// muscle illustration (the `.png` of the same name). The widget draws the
  /// image and tints only the selected muscles.
  static const _imaged = {BODY, BODY_FEMALE};

  /// The background image asset for [map], or null for plain-vector maps.
  static String? imageForMap(String map) =>
      _imaged.contains(map) ? map.replaceAll('.svg', '.png') : null;
}
