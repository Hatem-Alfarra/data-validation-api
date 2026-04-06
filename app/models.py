from pydantic import BaseModel


class ContactRequest(BaseModel):
    full_name: str
    email: str
    phone_number: str


class FieldError(BaseModel):
    field: str
    message: str


class SuccessResponse(BaseModel):
    status: str = "valid"


class ErrorResponse(BaseModel):
    status: str = "invalid"
    errors: list[FieldError]