# DemocratIA - IA endpoints with caching

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from groq import Groq
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.ia_cache import ResumeCache, SentimentCache
from ..models.intervention import Intervention
from ..config import settings

router = APIRouter()

LLM_MODEL = "llama-3.3-70b-versatile"

# En dessous de ce nombre de mots, resumer n'a pas de sens (le resume serait
# plus long que la source) : on renvoie le texte tel quel sans appeler le LLM.
MIN_SUMMARY_WORDS = 40


class ResumeRequest(BaseModel):
    intervention_id: Optional[str] = None
    text: Optional[str] = None
    context: str = ""


class SentimentRequest(BaseModel):
    text: Optional[str] = None
    intervention_id: Optional[str] = None
    theme: str = ""


def _get_llm_client():
    """Create Groq LLM client instance."""
    return Groq(api_key=settings.GROQ_API_KEY)


@router.post("/ia/resume")
def generate_resume(req: ResumeRequest, db: Session = Depends(get_db)):
    text = req.text
    intervention_id = req.intervention_id

    if not text and not intervention_id:
        raise HTTPException(status_code=400, detail="Provide intervention_id or text")

    # Check cache if intervention_id provided
    if intervention_id:
        cached = db.query(ResumeCache).filter(
            ResumeCache.intervention_id == intervention_id
        ).first()
        if cached:
            return {"resume": cached.resume_text, "cached": True}

        # Fetch text from intervention
        if not text:
            intervention = db.query(Intervention).filter(
                Intervention.id == intervention_id
            ).first()
            if not intervention:
                raise HTTPException(status_code=404, detail="Intervention not found")
            text = intervention.texte

    if not text:
        raise HTTPException(status_code=400, detail="No text available")

    # Garde-fou : texte deja court -> pas de resume (plus rapide, pas d'appel LLM)
    if len(text.split()) < MIN_SUMMARY_WORDS:
        return {"resume": text.strip(), "cached": False, "short": True}

    # Call LLM
    client = _get_llm_client()
    system_prompt = (
        "Tu es un assistant specialise dans la vulgarisation de l'activite "
        "parlementaire francaise. Ton role est de rendre les textes legislatifs "
        "et les debats accessibles a tous les citoyens."
    )
    user_prompt = (
        "Resume le texte parlementaire suivant en 1 a 2 phrases claires et "
        "accessibles, plus courtes que le texte d'origine. Donne uniquement le "
        "resume, sans phrase d'introduction.\n\n"
    )
    if req.context:
        user_prompt += f"Contexte : {req.context}\n\n"
    user_prompt += f"Texte :\n{text}"

    response = client.chat.completions.create(
        model=LLM_MODEL,
        max_tokens=160,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    resume_text = response.choices[0].message.content

    # Store in cache
    if intervention_id:
        cache_entry = ResumeCache(
            intervention_id=intervention_id,
            resume_text=resume_text,
        )
        db.add(cache_entry)
        db.commit()

    return {"resume": resume_text, "cached": False}


@router.post("/ia/sentiment")
def analyze_sentiment(req: SentimentRequest, db: Session = Depends(get_db)):
    text = req.text
    intervention_id = req.intervention_id

    if not text and not intervention_id:
        raise HTTPException(status_code=400, detail="Provide intervention_id or text")

    # Check cache if intervention_id provided
    if intervention_id:
        cached = db.query(SentimentCache).filter(
            SentimentCache.intervention_id == intervention_id,
            SentimentCache.theme == req.theme,
        ).first()
        if cached:
            return {
                "label": cached.label,
                "score": cached.score,
                "explanation": cached.explanation,
                "cached": True,
            }

        # Fetch text from intervention
        if not text:
            intervention = db.query(Intervention).filter(
                Intervention.id == intervention_id
            ).first()
            if not intervention:
                raise HTTPException(status_code=404, detail="Intervention not found")
            text = intervention.texte

    if not text:
        raise HTTPException(status_code=400, detail="No text available")

    # Call LLM
    client = _get_llm_client()
    system_prompt = (
        "Tu es un analyste politique objectif. Tu analyses le sentiment "
        "des textes parlementaires par rapport a un sujet donne."
    )
    user_prompt = "Analyse le sentiment du texte suivant"
    if req.theme:
        user_prompt += f' par rapport au theme "{req.theme}"'
    user_prompt += ".\n\n"
    user_prompt += f"Texte :\n{text}\n\n"
    user_prompt += (
        "Reponds UNIQUEMENT avec un objet JSON valide au format suivant :\n"
        '{"label": "favorable|defavorable|neutre", "score": 0.0-1.0, '
        '"explanation": "explication courte en francais"}\n\n'
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        max_tokens=300,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    response_text = response.choices[0].message.content.strip()
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(response_text[start:end])
        else:
            result = {"label": "neutre", "score": 0.5, "explanation": "Analyse non disponible"}

    # Store in cache
    if intervention_id:
        cache_entry = SentimentCache(
            intervention_id=intervention_id,
            theme=req.theme,
            label=result["label"],
            score=result["score"],
            explanation=result.get("explanation", ""),
        )
        db.add(cache_entry)
        db.commit()

    return {
        "label": result["label"],
        "score": result["score"],
        "explanation": result.get("explanation", ""),
        "cached": False,
    }
