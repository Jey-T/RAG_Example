from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
import uvicorn
import logging
import time

logging.basicConfig(
    filename='logs/embedding_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Recipe Embedding Service",
    description="Text embedding service using e5-small-v2 for recipe RAG system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

try:
    logger.info("Loading embedding model...")
    model = SentenceTransformer("intfloat/e5-small-v2")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

class TextInput(BaseModel):
    text: str = Field(description="The text to embed")

@app.get("/", summary="Service information")
def read_root():
    """Root endpoint with service information."""
    return {
        "service": "Recipe Embedding Service",
        "model": "intfloat/e5-small-v2",
        "version": "1.0.0",
        "health_check": "/health",
        "embed_endpoint": "/embed"
    }

@app.post("/embedding")
def embed(input: TextInput):
    """Generate an embedding for the given text."""
    start_time = time.time()
    emb = model.encode(input.text).tolist()
    end_time = time.time()
    logger.info(f"Embedding successfully generated in {end_time - start_time} seconds")
    return {"embedding": emb, "processing_time": round(end_time - start_time, 2)}

@app.get("/health", summary="Health check")
def health_check():
    """Health check endpoint."""
    try:
        test_embedding = model.encode("healthy")
        return {
            "status": "healthy",
            "model": "intfloat/e5-small-v2",
            "model_loaded": True,
            "embedding_dimension": len(test_embedding)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy: model not responding"
        )

if __name__ == "__main__":
    logger.info("Starting Recipe Embedding Service...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )