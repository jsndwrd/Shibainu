from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import Base, engine

from routers import (
    auth,
    aspirations,
    clusters,
    scores,
    briefs,
    reference,
    policy_level,
)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "This is Vokara.",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(aspirations.router, prefix="/api/aspirations", tags=["Aspirations"])
app.include_router(clusters.router, prefix="/api/clusters", tags=["Clusters"])
app.include_router(scores.router, prefix="/api/scores", tags=["Scores"])
app.include_router(briefs.router, prefix="/api/briefs", tags=["Briefs"])
app.include_router(reference.router, prefix="/api/ref", tags=["Reference"])
app.include_router(policy_level.router, prefix="/api/policy-level", tags=["Policy Level"])