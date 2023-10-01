
from fastapi import FastAPI
from loguru import logger

app = FastAPI()

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting uvicorn in reload mode")
    uvicorn.run(
        "app.app:app",
        host="127.0.0.1",
        reload=True,
        port=8080,
    )