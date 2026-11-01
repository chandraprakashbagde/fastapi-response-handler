# Getting started

Install locally with `pip install -e ".[dev]"`, or install the published distribution when available. Run `pytest` to check the package. The complete application in `examples/basic_app.py` can be started with `uvicorn examples.basic_app:app --reload` after installing Uvicorn. Browse `/docs` for FastAPI's generated OpenAPI UI. To define each success and error message in exactly one place, see [response handling](response_handling.md) and [exception handling](exception_handling.md) for named `ErrorSpec` and `SuccessSpec` definitions.
