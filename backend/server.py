from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api import router as api_router
from src.logging import logger

app = FastAPI()

app.include_router(api_router)

origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://0.0.0.0",
    "http://0.0.0.0:80",
    "http://0.0.0.0:8080",
    "http://0.0.0.0:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Needed for K8 health probe or debugging
@app.get("/")
def default():
    return "OK"


def main():
    logger.info("running")
    uvicorn.run("server:app", host="0.0.0.0", port=8080, log_level="info", reload=True)


if __name__ == "__main__":
    main()
