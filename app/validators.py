import re
from email_validator import validate_email as _validate_email, EmailNotValidError
from app.models import FieldError


NAME_PATTERN = re.compile(
    r"^[a-zA-ZÀ-ÖØ-öø-ÿ]+([-'\s][a-zA-ZÀ-ÖØ-öø-ÿ]+)+$"
)

PHONE_PATTERN = re.compile(
    r"^(\+1[-.\s]?)?"           # optional country code
    r"(\(\d{3}\)|(\d{3}))"      # area code: either (123) or 123
    r"[-.\s]?"                  # optional separator
    r"\d{3}"                    # first 3 digits
    r"[-.\s]?"                  # optional separator
    r"\d{4}$"                   # last 4 digits
)


def validate_name(name: str) -> FieldError | None:
    if not NAME_PATTERN.match(name.strip()):
        return FieldError(
            field="full_name",
            message="Must be a valid North American name with at least a first and last name. "
                    "Only letters, hyphens, and apostrophes are allowed."
        )
    return None


def validate_email(email: str) -> FieldError | None:
    try:
        _validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        return FieldError(
            field="email",
            message="Must be a valid email address format."
        )
    return None


def validate_phone(phone: str) -> FieldError | None:
    if not PHONE_PATTERN.match(phone.strip()):
        return FieldError(
            field="phone_number",
            message="Must be a valid North American phone number format "
                    "(e.g. +1-234-567-8900, (234) 567-8900, or 234-567-8900)."
        )
    return None


def validate_contact(full_name: str, email: str, phone_number: str) -> list[FieldError]:
    errors = []

    name_error = validate_name(full_name)
    if name_error:
        errors.append(name_error)

    email_error = validate_email(email)
    if email_error:
        errors.append(email_error)

    phone_error = validate_phone(phone_number)
    if phone_error:
        errors.append(phone_error)

    return errors