"""Batch sentiment analysis for interventions without existing analysis."""

import logging
import os
import sys
import time

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Add parent directory for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.sentiment import SentimentAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

Base = declarative_base()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://democratia:democratia_secret@localhost:5432/democratia",
)

BATCH_SIZE = 10
PAUSE_BETWEEN_BATCHES = 2  # seconds


class Intervention(Base):
    __tablename__ = "interventions"
    id = Column(Integer, primary_key=True)
    depute_id = Column(String)
    texte = Column(Text)


class SentimentCache(Base):
    __tablename__ = "sentiment_cache"
    id = Column(Integer, primary_key=True, autoincrement=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id"), nullable=False)
    theme = Column(String, default="")
    label = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text, default="")


def get_unanalyzed_interventions(session, limit=500):
    """Get interventions that don't have a sentiment analysis yet."""
    analyzed_ids = session.query(SentimentCache.intervention_id).distinct().subquery()
    return (
        session.query(Intervention)
        .filter(Intervention.id.notin_(session.query(analyzed_ids)))
        .filter(Intervention.texte.isnot(None))
        .filter(Intervention.texte != "")
        .limit(limit)
        .all()
    )


def run_batch_analysis():
    """Run sentiment analysis on all unanalyzed interventions."""
    logger.info("=== Batch Sentiment Analysis ===")

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    analyzer = SentimentAnalyzer()

    stats = {
        "total": 0,
        "favorable": 0,
        "defavorable": 0,
        "neutre": 0,
        "errors": 0,
    }

    try:
        interventions = get_unanalyzed_interventions(session)
        total_to_process = len(interventions)
        logger.info(f"Found {total_to_process} interventions to analyze")

        if total_to_process == 0:
            logger.info("No interventions to analyze. Exiting.")
            return

        for batch_start in range(0, total_to_process, BATCH_SIZE):
            batch = interventions[batch_start : batch_start + BATCH_SIZE]
            batch_num = (batch_start // BATCH_SIZE) + 1
            total_batches = (total_to_process + BATCH_SIZE - 1) // BATCH_SIZE

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} interventions)")

            for intervention in batch:
                try:
                    text = intervention.texte[:2000]  # Limit text length
                    result = analyzer.analyze(text)

                    cache_entry = SentimentCache(
                        intervention_id=intervention.id,
                        theme="",
                        label=result["label"],
                        score=result["score"],
                        explanation=result.get("explanation", ""),
                    )
                    session.add(cache_entry)
                    stats["total"] += 1
                    stats[result["label"]] = stats.get(result["label"], 0) + 1

                except Exception as e:
                    logger.warning(f"Failed to analyze intervention {intervention.id}: {e}")
                    stats["errors"] += 1

            session.commit()

            # Pause between batches to respect rate limits
            if batch_start + BATCH_SIZE < total_to_process:
                logger.info(f"Pausing {PAUSE_BETWEEN_BATCHES}s between batches...")
                time.sleep(PAUSE_BETWEEN_BATCHES)

        # Print summary
        logger.info("=== Analysis Complete ===")
        logger.info(f"Total analyzed: {stats['total']}")
        logger.info(f"Errors: {stats['errors']}")

        if stats["total"] > 0:
            pct_fav = (stats["favorable"] / stats["total"]) * 100
            pct_def = (stats["defavorable"] / stats["total"]) * 100
            pct_neu = (stats["neutre"] / stats["total"]) * 100
            logger.info(f"Favorable: {stats['favorable']} ({pct_fav:.1f}%)")
            logger.info(f"Defavorable: {stats['defavorable']} ({pct_def:.1f}%)")
            logger.info(f"Neutre: {stats['neutre']} ({pct_neu:.1f}%)")

    except Exception as e:
        session.rollback()
        logger.error(f"Batch analysis failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_batch_analysis()
