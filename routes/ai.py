from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import ai

router = APIRouter()

class PromptRequest(BaseModel):
    text: str
    target: str  # "title" or "description"

class SummaryRequest(BaseModel):
    text: str

@router.post("/suggest")
async def suggest_text(payload: PromptRequest):
    try:
        if payload.target.lower() == "title":
            suggestion = await ai.suggest_title(payload.text)
        else:
            suggestion = await ai.suggest_description(payload.text)
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_text(payload: SummaryRequest):
    try:
        summary = await ai.summarize_text(payload.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
