from pydantic import BaseModel
from fastapi_response_handler import success_response


class Payment(BaseModel):
    success: bool
    transaction_id: str
    payment_status: str


def test_success_with_and_without_data():
    assert success_response(data={"id": 1}).model_dump()["data"] == {"id": 1}
    assert success_response().model_dump()["data"] is None


def test_custom_success():
    assert success_response(model=Payment, transaction_id="abc", payment_status="paid").model_dump() == {"success": True, "transaction_id": "abc", "payment_status": "paid"}


def test_native_responses_and_fastapi_serialization():
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
    from fastapi.testclient import TestClient
    from fastapi_response_handler import SuccessResponse, register_handlers
    app = FastAPI()
    register_handlers(app)
    @app.get("/model", response_model=SuccessResponse[list[int]])
    def model():
        return success_response(data=[1, 2])
    @app.get("/custom", response_model=Payment)
    def custom():
        return Payment(success=True, transaction_id="x", payment_status="paid")
    @app.get("/json")
    def native_json():
        return JSONResponse({"native": True}, status_code=202)
    @app.get("/stream")
    def stream():
        return StreamingResponse(iter([b"hello"]))
    @app.get("/redirect")
    def redirect():
        return RedirectResponse("/json")
    client = TestClient(app)
    assert client.get("/model").json()["data"] == [1, 2]
    assert client.get("/custom").json()["transaction_id"] == "x"
    assert client.get("/json").status_code == 202
    assert client.get("/stream").content == b"hello"
    assert client.get("/redirect", follow_redirects=False).status_code == 307
