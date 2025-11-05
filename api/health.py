from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime
from mangum import Mangum

app = FastAPI()

@app.get("/")
@app.get("/health")
def health():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Web Intelligence Platform API"
    })

handler = Mangum(app)

