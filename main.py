from loguru import logger
import uvicorn

if __name__ == "__main__":
    

    logger.info("Starting uvicorn in reload mode")
    uvicorn.run(
        "app.app:app",
        host="127.0.0.1",
        reload=True,
        port=8080,
    )
