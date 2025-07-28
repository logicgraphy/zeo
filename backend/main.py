from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, users, analysis, hire

app = FastAPI(title="SG AI Backend", description="Backend API with email verification")

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)