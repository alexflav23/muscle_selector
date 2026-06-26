import 'package:flutter_test/flutter_test.dart';
import 'package:muscle_selector/muscle_selector.dart';

void main() {
  group('Maps.forGender', () {
    test('male resolves to the default body map', () {
      expect(Maps.forGender(Gender.male), Maps.BODY);
      expect(Maps.BODY, 'human_body.svg');
    });

    test('female resolves to the female body map', () {
      expect(Maps.forGender(Gender.female), Maps.BODY_FEMALE);
      expect(Maps.BODY_FEMALE, 'human_body_female.svg');
    });

    test('the two genders map to distinct assets', () {
      expect(Maps.forGender(Gender.male),
          isNot(Maps.forGender(Gender.female)));
    });
  });

  test('Gender has exactly male and female', () {
    expect(Gender.values, [Gender.male, Gender.female]);
  });
}
