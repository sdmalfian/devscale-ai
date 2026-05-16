from dotenv import load_dotenv
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.router import router

load_dotenv()

app = FastAPI()

app.include_router(router)

@app.get("/scalar")
def get_scalar():
    return get_scalar_api_reference(
        title=app.title, openapi_url=app.openapi_url
    )