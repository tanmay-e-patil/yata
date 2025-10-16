from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models import user, todo, oauth_client, oauth_token, personal_token
from app.api.v1 import auth, todos, oauth, oauth_todos, personal_tokens, personal_todos

# Create database tables
user.Base.metadata.create_all(bind=engine)
todo.Base.metadata.create_all(bind=engine)
oauth_client.Base.metadata.create_all(bind=engine)
oauth_token.Base.metadata.create_all(bind=engine)
personal_token.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])
app.include_router(oauth_todos.router, prefix="/api/v1/oauth-todos", tags=["oauth-todos"])
app.include_router(personal_tokens.router, prefix="/api/v1/personal-tokens", tags=["personal-tokens"])
app.include_router(personal_todos.router, prefix="/api/v1/personal-todos", tags=["personal-todos"])


@app.get("/")
async def root():
    return {"message": "Yata Todo API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}