from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Import route modules
from routes.web_routes import web_router
from routes.api_routes import api_router

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fruit_store")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_RELOAD = os.getenv("APP_RELOAD", "false").lower() == "true"
APP_TITLE = os.getenv("APP_TITLE", "Fruit Store")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")
STATIC_DIR = os.getenv("STATIC_DIR", "static")

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    debug=DEBUG,
    description="A comprehensive fruit store management system with inventory, customers, suppliers, and orders management."
)

# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Static files (if you have a static directory)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include routers
app.include_router(web_router, tags=["Web Routes"])
app.include_router(api_router, prefix="/api", tags=["API Routes"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print(f"🚀 Starting {APP_TITLE} v{APP_VERSION}")
    print(f"📊 MongoDB URL: {MONGODB_URL}")
    print(f"🗃️  Database: {DATABASE_NAME}")
    print(f"🌐 Server: http://{APP_HOST}:{APP_PORT}")
    print(f"🐛 Debug mode: {DEBUG}")
    
    # Test database connection
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🔄 Shutting down application...")
    client.close()
    print("✅ MongoDB connection closed")

# Health check endpoint (keeping this in main for system-level health)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app": APP_TITLE,
            "version": APP_VERSION,
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app": APP_TITLE,
            "version": APP_VERSION,
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=APP_HOST, 
        port=APP_PORT, 
        reload=APP_RELOAD
    )