from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import BusinessModelService, AnalysisService

router = APIRouter()

class CanvasGenerateRequest(BaseModel):
    analysis_id: str = None
    keyword: str = None
    canvas_type: str = "lean"

@router.post("/canvas/generate")
def generate_canvas(request: CanvasGenerateRequest):
    """基于分析结果生成商业模式画布"""
    if not request.keyword and not request.analysis_id:
        raise HTTPException(status_code=400, detail="需要提供keyword或analysis_id")
    
    if request.keyword:
        analysis_service = AnalysisService()
        analysis_result = analysis_service.analyze_industry(request.keyword)
        if not analysis_result:
            raise HTTPException(status_code=404, detail=f"未找到「{request.keyword}」的分析结果")
    else:
        analysis_result = {}
    
    service = BusinessModelService()
    if request.canvas_type == "lean":
        canvas = service.generate_lean_canvas(analysis_result)
    elif request.canvas_type == "business_model":
        canvas = service.generate_business_model_canvas(analysis_result)
    elif request.canvas_type == "value_proposition":
        canvas = service.generate_value_proposition_canvas(analysis_result)
    else:
        raise HTTPException(status_code=400, detail="canvas_type必须是lean|business_model|value_proposition")
    
    score = service.calculate_model_score(canvas)
    
    return {
        "canvas_type": request.canvas_type,
        "canvas": canvas,
        "completeness_score": score,
        "suggestions": service._get_improvement_suggestions(canvas)
    }

@router.get("/canvas/types")
def get_canvas_types():
    """获取支持的画布类型"""
    return {
        "types": [
            {"id": "lean", "name": "精益画布", "source": "《精益创业》", "description": "适合创业者快速验证商业模式"},
            {"id": "business_model", "name": "商业模式画布", "source": "《商业模式新生代》", "description": "9宫格商业模式设计工具"},
            {"id": "value_proposition", "name": "价值主张画布", "source": "《商业模式新生代》", "description": "聚焦价值主张与客户需求的匹配"}
        ]
    }

@router.get("/canvas/template/{canvas_type}")
def get_canvas_template(canvas_type: str):
    """获取空白画布模板"""
    service = BusinessModelService()
    if canvas_type == "lean":
        template = service._get_lean_canvas_template()
    elif canvas_type == "business_model":
        template = service._get_business_model_template()
    elif canvas_type == "value_proposition":
        template = service._get_value_proposition_template()
    else:
        raise HTTPException(status_code=400, detail="不支持的canvas_type")
    return {"canvas_type": canvas_type, "template": template}