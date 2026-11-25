"""Join code generation."""

from app.services.join_codes import ALPHABET, CODE_LENGTH, generate_join_code


def test_codes_have_the_right_length_and_characters():
    for _ in range(1000):
        code = generate_join_code()
        assert len(code) == CODE_LENGTH
        assert all(char in ALPHABET for char in code)


def test_codes_are_not_all_the_same():
    codes = {generate_join_code() for _ in range(100)}
    assert len(codes) > 1
