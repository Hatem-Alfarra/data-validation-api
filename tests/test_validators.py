import pytest
from app.validators import validate_name, validate_email, validate_phone, validate_contact


# ---------------------------------------------------------------------------
# validate_name
# ---------------------------------------------------------------------------

class TestValidateName:

    def test_valid_simple_name(self):
        assert validate_name("John Doe") is None

    def test_valid_hyphenated_name(self):
        assert validate_name("Mary-Jane Watson") is None

    def test_valid_apostrophe_name(self):
        assert validate_name("O'Brien Smith") is None

    def test_valid_french_accents(self):
        assert validate_name("François Chloë") is None

    def test_valid_middle_name(self):
        assert validate_name("John Michael Doe") is None

    def test_valid_leading_trailing_spaces(self):
        assert validate_name("  John Doe  ") is None

    def test_invalid_single_name(self):
        error = validate_name("John")
        assert error is not None
        assert error.field == "full_name"

    def test_invalid_contains_numbers(self):
        error = validate_name("John123 Doe")
        assert error is not None
        assert error.field == "full_name"

    def test_invalid_special_characters(self):
        error = validate_name("John@ Doe")
        assert error is not None
        assert error.field == "full_name"

    def test_invalid_empty_string(self):
        error = validate_name("")
        assert error is not None
        assert error.field == "full_name"


# ---------------------------------------------------------------------------
# validate_email
# ---------------------------------------------------------------------------

class TestValidateEmail:

    def test_valid_simple_email(self):
        assert validate_email("john.doe@example.com") is None

    def test_valid_email_with_plus(self):
        assert validate_email("john+filter@example.com") is None

    def test_valid_email_subdomain(self):
        assert validate_email("john@mail.example.com") is None

    def test_invalid_missing_at(self):
        error = validate_email("johndoeexample.com")
        assert error is not None
        assert error.field == "email"

    def test_invalid_missing_domain(self):
        error = validate_email("john@")
        assert error is not None
        assert error.field == "email"

    def test_invalid_empty_string(self):
        error = validate_email("")
        assert error is not None
        assert error.field == "email"


# ---------------------------------------------------------------------------
# validate_phone
# ---------------------------------------------------------------------------

class TestValidatePhone:

    def test_valid_plus_one_format(self):
        assert validate_phone("+11234567890") is None

    def test_valid_parentheses_format(self):
        assert validate_phone("(123) 456-7890") is None

    def test_valid_dashes_format(self):
        assert validate_phone("123-456-7890") is None

    def test_valid_dots_format(self):
        assert validate_phone("123.456.7890") is None

    def test_invalid_too_short(self):
        error = validate_phone("123-456-789")
        assert error is not None
        assert error.field == "phone_number"

    def test_invalid_letters(self):
        error = validate_phone("123-abc-7890")
        assert error is not None
        assert error.field == "phone_number"

    def test_invalid_empty_string(self):
        error = validate_phone("")
        assert error is not None
        assert error.field == "phone_number"


# ---------------------------------------------------------------------------
# validate_contact (orchestration)
# ---------------------------------------------------------------------------

class TestValidateContact:

    def test_all_valid_returns_empty_list(self):
        errors = validate_contact(
            full_name="John Doe",
            email="john.doe@example.com",
            phone_number="123-456-7890"
        )
        assert errors == []

    def test_single_invalid_field_returns_one_error(self):
        errors = validate_contact(
            full_name="John",
            email="john.doe@example.com",
            phone_number="123-456-7890"
        )
        assert len(errors) == 1
        assert errors[0].field == "full_name"

    def test_all_invalid_returns_three_errors(self):
        errors = validate_contact(
            full_name="John",
            email="notanemail",
            phone_number="000"
        )
        assert len(errors) == 3

    def test_error_fields_are_correct(self):
        errors = validate_contact(
            full_name="John",
            email="notanemail",
            phone_number="000"
        )
        fields = [e.field for e in errors]
        assert "full_name" in fields
        assert "email" in fields
        assert "phone_number" in fields