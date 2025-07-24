from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.api import database
from src.api.routes import users, notes, tags

app = FastAPI(
    title="Smart Notes Organizer API",
    description="Backend API for the Smart Notes Organizer app. Handles notes CRUD, tagging, user authentication, and search capabilities.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"], summary="Health Check", response_description="API healthy response")
def health_check():
    """
    Health check route to verify service availability.
    """
    return {"message": "Healthy"}

# Register API routers
app.include_router(users.router)
app.include_router(auth_router := users.auth_router, prefix="/auth")
app.include_router(notes.router)
app.include_router(tags.router)

@app.on_event("startup")
def on_startup():
    database.init_db()

# Customize OpenAPI settings for docs
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Smart Notes Organizer API",
        version="1.0.0",
        description="RESTful API for notes CRUD, tagging, search, and user authentication.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
