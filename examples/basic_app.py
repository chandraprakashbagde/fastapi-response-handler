"""Run with: uvicorn examples.basic_app:app --reload"""
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_response_handler import (
    NotFoundException,
    ResponseHandlerConfig,
    SuccessResponse,
    api_responses,
    register_handlers,
    success_response,
)

app = FastAPI()
register_handlers(app, ResponseHandlerConfig())


class User(BaseModel):
    id: int
    name: str


@app.get("/users/{user_id}", response_model=SuccessResponse[User], responses=api_responses(404))
def get_user(user_id: int) -> SuccessResponse[User]:
    if user_id != 1:
        raise NotFoundException("User not found", error_code="USER_NOT_FOUND")
    return SuccessResponse[User](message="User found", data=User(id=1, name="Ada"))


@app.post("/users", status_code=201, response_model=SuccessResponse[User], responses=api_responses(400, 409))
def create_user(user: User) -> SuccessResponse:
    return success_response("User created successfully", user)
