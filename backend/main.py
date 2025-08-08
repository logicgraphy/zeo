import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import auth, users, analysis, hire

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI(title="Force Vector AI Backend", description="Backend API with email verification")

# Debug middleware to log requests
@app.middleware("http")
async def debug_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",  # Alternative localhost        
        "*",  # Allow all origins in development
    ],
    allow_credentials=False,  # Set to False when using "*" for origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analysis.router)
app.include_router(hire.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "SG AI Backend is running", "status": "healthy"}

@app.options("/analyze/quick")
async def analyze_quick_options():
    """Handle OPTIONS request for CORS preflight"""
    return {"message": "OK"}

@app.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working"""
    return {"message": "CORS test successful", "timestamp": "2024-01-01T00:00:00Z"}

@app.post("/test-analyze")
async def test_analyze():
    """Test endpoint to verify analysis endpoint is accessible"""
    return {"message": "Analysis endpoint is accessible", "test": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)