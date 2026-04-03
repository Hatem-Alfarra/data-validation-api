from fastapi import FastAPI
from app.models import ContactRequest, SuccessResponse, ErrorResponse
from app.validators import validate_contact


app = FastAPI()


@app.post("/validate", response_model=SuccessResponse | ErrorResponse)
def validate(request: ContactRequest) -> SuccessResponse | ErrorResponse:
    errors = validate_contact(
        full_name = request.full_name,
        email = request.email,
        phone_number = request.phone_number,
    )

    if errors:
        return ErrorResponse(errors=errors)

    return SuccessResponse()