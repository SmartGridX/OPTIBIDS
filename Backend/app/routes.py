from fastapi import FastAPI

from .routes_auth import router as auth_router
from .routes_admin import router as admin_router
from .routes_applicant import router as applicant_router
from .routes_public import router as public_router


def register_all_routes(app: FastAPI):
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    app.include_router(applicant_router, prefix="/applicant", tags=["Applicant"])
    app.include_router(public_router, tags=["Public"])
