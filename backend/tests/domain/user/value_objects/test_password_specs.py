import pytest

from src.backend.domain.user.value_objects.HashedPassword.password import (
    PasswordDifferenceSpecification,
    PasswordDigitSpecification,
    PasswordLengthSpecification,
    PasswordLowerLetterSpecification,
    PasswordSpecialCharacterSpecification,
    PasswordUpperLetterSpecification,
)


class TestPasswordLengthSpecification:
    def test_exactly_8_chars_is_valid(self):
        assert PasswordLengthSpecification().is_satisfied_by("abcdefgh") is True

    def test_more_than_8_chars_is_valid(self):
        assert PasswordLengthSpecification().is_satisfied_by("abcdefghij") is True

    def test_7_chars_is_invalid(self):
        assert PasswordLengthSpecification().is_satisfied_by("abcdefg") is False

    def test_empty_string_is_invalid(self):
        assert PasswordLengthSpecification().is_satisfied_by("") is False


class TestPasswordUpperLetterSpecification:
    def test_has_uppercase_is_valid(self):
        assert PasswordUpperLetterSpecification().is_satisfied_by("Password") is True

    def test_all_uppercase_is_valid(self):
        assert PasswordUpperLetterSpecification().is_satisfied_by("PASSWORD") is True

    def test_no_uppercase_is_invalid(self):
        assert PasswordUpperLetterSpecification().is_satisfied_by("password") is False

    def test_empty_string_is_invalid(self):
        assert PasswordUpperLetterSpecification().is_satisfied_by("") is False


class TestPasswordLowerLetterSpecification:
    def test_has_lowercase_is_valid(self):
        assert PasswordLowerLetterSpecification().is_satisfied_by("Password") is True

    def test_all_lowercase_is_valid(self):
        assert PasswordLowerLetterSpecification().is_satisfied_by("password") is True

    def test_no_lowercase_is_invalid(self):
        assert PasswordLowerLetterSpecification().is_satisfied_by("PASSWORD") is False

    def test_empty_string_is_invalid(self):
        assert PasswordLowerLetterSpecification().is_satisfied_by("") is False


class TestPasswordDigitSpecification:
    def test_has_digit_is_valid(self):
        assert PasswordDigitSpecification().is_satisfied_by("pass1word") is True

    def test_only_digits_is_valid(self):
        assert PasswordDigitSpecification().is_satisfied_by("12345678") is True

    def test_no_digit_is_invalid(self):
        assert PasswordDigitSpecification().is_satisfied_by("password") is False

    def test_empty_string_is_invalid(self):
        assert PasswordDigitSpecification().is_satisfied_by("") is False


class TestPasswordSpecialCharacterSpecification:
    @pytest.mark.parametrize("char", list("!@#$%^&*()-_+=/{}[];:'\"\\|`~?,."))
    def test_known_special_char_is_valid(self, char):
        assert PasswordSpecialCharacterSpecification().is_satisfied_by(f"pass{char}word") is True

    def test_no_special_char_is_invalid(self):
        assert PasswordSpecialCharacterSpecification().is_satisfied_by("Password1") is False

    def test_empty_string_is_invalid(self):
        assert PasswordSpecialCharacterSpecification().is_satisfied_by("") is False


class TestPasswordDifferenceSpecification:
    def test_different_passwords_is_valid(self):
        spec = PasswordDifferenceSpecification()
        assert spec.is_satisfied_by(("OldPass1!", "NewPass2!")) is True

    def test_same_passwords_is_invalid(self):
        spec = PasswordDifferenceSpecification()
        assert spec.is_satisfied_by(("SamePass1!", "SamePass1!")) is False

    def test_empty_both_same_is_invalid(self):
        spec = PasswordDifferenceSpecification()
        assert spec.is_satisfied_by(("", "")) is False


class TestCombinedPasswordSpecifications:
    def test_strong_password_passes_all(self):
        password = "StrongPass1!"
        assert PasswordLengthSpecification().is_satisfied_by(password) is True
        assert PasswordUpperLetterSpecification().is_satisfied_by(password) is True
        assert PasswordLowerLetterSpecification().is_satisfied_by(password) is True
        assert PasswordDigitSpecification().is_satisfied_by(password) is True
        assert PasswordSpecialCharacterSpecification().is_satisfied_by(password) is True

    def test_and_combination(self):
        strong_spec = (
            PasswordLengthSpecification()
            & PasswordUpperLetterSpecification()
            & PasswordLowerLetterSpecification()
            & PasswordDigitSpecification()
            & PasswordSpecialCharacterSpecification()
        )
        assert strong_spec.is_satisfied_by("StrongPass1!") is True
        assert strong_spec.is_satisfied_by("weakpass") is False
