from app.api.routes import router
from app.api.business_routes import router as business_router
from app.api.vector_routes import router as vector_router
from app.api.monetization_routes import router as monetization_router

__all__ = ["router", "business_router", "vector_router", "monetization_router"]