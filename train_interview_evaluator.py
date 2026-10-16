#!/usr/bin/env python3
"""
Train the interview evaluator from datasets under data/interview.
Produces:
 - data/interview_evaluator.joblib
 - data/interview_keywords.json
"""

import sys
import logging

from interview_evaluator import InterviewEvaluator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main() -> int:
    try:
        logger.info("🚀 Training interview evaluator from data/interview ...")
        ev = InterviewEvaluator()
        stats = ev.train_from_directory(base_dir="data/interview", json_sample_limit=20000)
        ev.save()
        logger.info("✅ Training complete")
        logger.info(f"Roles discovered: {stats['roles']}")
        logger.info(f"Total questions analyzed: {stats['total_questions']}")
        logger.info(f"Global keyword size: {stats['global_keywords']}")
        return 0
    except Exception as e:
        logger.exception("❌ Training failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())


