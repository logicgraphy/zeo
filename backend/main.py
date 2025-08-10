import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import auth, users, analysis, hire
from fastapi import Body
from api.models import ContactRequest, MessageResponse
from api.database import DatabaseService
import uuid

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI(title="Force Vector AI Backend", description="Backend API with email verification")

# Consent extraction middleware (reads consent headers/cookies and attaches to request.state)
def _parse_bool(value):
    try:
        return str(value).lower() in {"1", "true", "yes", "y", "on"}
    except Exception:
        return False

@app.middleware("http")
async def consent_middleware(request: Request, call_next):
    headers = request.headers
    consent = {
        "do_not_sell": _parse_bool(headers.get("x-consent-do-not-sell")),
        "functional": _parse_bool(headers.get("x-consent-functional")),
        "analytics": _parse_bool(headers.get("x-consent-analytics")),
        "marketing": _parse_bool(headers.get("x-consent-marketing")),
        "gpc": headers.get("x-gpc") == "1" or headers.get("sec-gpc") == "1",
        "dnt": headers.get("dnt") == "1",
    }
    # Fallback to cookies if present
    try:
        cookie_header = headers.get("cookie", "")
        pairs = [c.strip().split("=", 1) for c in cookie_header.split(";") if "=" in c]
        cookies = {k: v for k, v in pairs if k}
        if "do_not_sell" in cookies:
            consent["do_not_sell"] = cookies.get("do_not_sell") == "1" or consent["do_not_sell"]
        usp = cookies.get("usprivacy")
        if usp and len(usp) >= 3:
            # crude interpretation: character 3 indicates sale opt-out in some variants
            if "y" in usp.lower():
                consent["do_not_sell"] = True
    except Exception:
        pass

    # Enforce opt-out on GPC/DNT
    if consent["gpc"] or consent["dnt"]:
        consent["do_not_sell"] = True
        consent["analytics"] = False
        consent["marketing"] = False

    request.state.consent = consent
    response = await call_next(request)
    try:
        response.headers["X-Consent-Ack"] = ";".join([f"{k}={int(bool(v))}" for k, v in consent.items()])
    except Exception:
        pass
    return response

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

@app.post("/contact", response_model=MessageResponse)
async def contact_submit(payload: ContactRequest = Body(...)):
    request_id = str(uuid.uuid4())
    DatabaseService.create_contact_request(request_id, payload.dict())
    return MessageResponse(message="Thanks! We'll get back to you shortly.")

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