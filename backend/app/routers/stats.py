# DemocratIA - Global platform statistics endpoint

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.depute import Depute
from ..models.groupe import Groupe
from ..models.intervention import Intervention
from ..models.scrutin import Scrutin
from ..models.question import Question
from ..models.amendement import Amendement
from ..models.ia_cache import ResumeCache, SentimentCache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    logger.info("GET /stats")

    nb_deputes = db.query(func.count(Depute.id)).scalar() or 0
    nb_groupes = db.query(func.count(Groupe.id)).scalar() or 0
    nb_interventions = db.query(func.count(Intervention.id)).scalar() or 0
    nb_scrutins = db.query(func.count(Scrutin.id)).scalar() or 0
    nb_questions = db.query(func.count(Question.id)).scalar() or 0
    nb_amendements = db.query(func.count(Amendement.id)).scalar() or 0

    # IA stats
    nb_resumes_generes = db.query(func.count(ResumeCache.id)).scalar() or 0
    nb_sentiments_analyses = db.query(func.count(SentimentCache.id)).scalar() or 0

    return {
        "nb_deputes": nb_deputes,
        "nb_groupes": nb_groupes,
        "nb_interventions": nb_interventions,
        "nb_scrutins": nb_scrutins,
        "nb_questions": nb_questions,
        "nb_amendements": nb_amendements,
        "nb_resumes_generes": nb_resumes_generes,
        "nb_sentiments_analyses": nb_sentiments_analyses,
        "derniere_maj": datetime.utcnow().isoformat(),
    }
