enum Gender { male, female }

class Maps {
  static const BODY = 'human_body.svg';
  static const BODY_FEMALE = 'human_body_female.svg';

  static String forGender(Gender gender) =>
      gender == Gender.female ? BODY_FEMALE : BODY;
}
