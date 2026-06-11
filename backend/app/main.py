from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.business_routes import router as business_router
from app.api.vector_routes import router as vector_router
from app.api.monetization_routes import router as monetization_router
from app.api.workflow_routes import router as workflow_router
from app.core.config import settings

app = FastAPI(
    title="创业帮 API",
    description="从消费者抱怨中发现新价值需求，辅助商业模式设计",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["分析"])
app.include_router(business_router, prefix="/api", tags=["商业模式"])
app.include_router(vector_router, prefix="/api", tags=["向量分析"])
app.include_router(monetization_router, prefix="/api", tags=["变现模式"])
app.include_router(workflow_router, prefix="/api", tags=["工作流"])

@app.get("/")
def root():
    return {"message": "欢迎使用创业帮 API", "docs": "/docs"}