"""
scoring.py
----------
Intelligent scoring mechanisms that combine semantic similarity and
audio/fluency metrics into an overall score (0-100) and structured
qualitative feedback.
"""

from typing import Dict, List, Optional, Tuple


def _fluency_subscore(fluency_metrics: Dict) -> float:
    """
    Convert raw fluency metrics into a 0-100 sub-score.
    Rewards moderate pace, low filler usage, and low pause ratio.
    """
    wpm = fluency_metrics.get("words_per_minute", 0)
    filler_count = fluency_metrics.get("filler_word_count", 0)
    pause_ratio = fluency_metrics.get("pause_ratio", 0)
    duration = max(fluency_metrics.get("duration_seconds", 1), 1)

    # Ideal conversational speech rate: ~110-160 wpm
    if 110 <= wpm <= 160:
        pace_score = 100
    elif wpm == 0:
        pace_score = 0
    else:
        deviation = min(abs(wpm - 135), 135)
        pace_score = max(0, 100 - (deviation / 135) * 100)

    # Filler words per minute (normalize by duration)
    fillers_per_min = filler_count / (duration / 60.0)
    filler_score = max(0, 100 - fillers_per_min * 12)

    # Lower pause ratio is generally better, up to a point (some pausing
    # for thought is natural)
    pause_score = max(0, 100 - max(0, pause_ratio - 0.15) * 200)

    fluency_score = (pace_score * 0.4) + (filler_score * 0.35) + (pause_score * 0.25)
    return round(max(0, min(100, fluency_score)), 2)


def compute_overall_score(
    similarity_score: Optional[float],
    fluency_metrics: Dict,
    mode: str = "understanding",
) -> Tuple[float, Dict]:
    """
    Compute an overall 0-100 score.

    mode == "understanding": weighted blend of semantic similarity (70%)
        and fluency (30%).
    mode == "fluency": pure fluency scoring (100%).
    """
    fluency_score = _fluency_subscore(fluency_metrics)

    if mode == "understanding" and similarity_score is not None:
        semantic_score = round(similarity_score * 100, 2)
        overall = round(semantic_score * 0.7 + fluency_score * 0.3, 2)
        breakdown = {
            "semantic_similarity_score": semantic_score,
            "fluency_score": fluency_score,
            "weights": {"semantic": 0.7, "fluency": 0.3},
            "overall_score": overall,
        }
    else:
        overall = fluency_score
        breakdown = {
            "fluency_score": fluency_score,
            "weights": {"fluency": 1.0},
            "overall_score": overall,
        }

    return overall, breakdown


def generate_feedback(
    mode: str,
    similarity_score: Optional[float],
    understanding_label: Optional[str],
    fluency_metrics: Dict,
) -> List[str]:
    """
    Generate structured, human-readable feedback strings based on the
    computed metrics.
    """
    feedback = []

    if mode == "understanding":
        if understanding_label == "Strong Understanding":
            feedback.append(
                "Excellent! Your explanation closely matches the core concept "
                "and covers the key ideas accurately."
            )
        elif understanding_label == "Moderate Understanding":
            feedback.append(
                "Good attempt — you captured several key ideas, but some "
                "important points may be missing or underdeveloped."
            )
        elif understanding_label == "Weak Understanding":
            feedback.append(
                "Your explanation touches on the topic but misses several "
                "core ideas. Review the reference definition and try again."
            )
        else:
            feedback.append(
                "Your explanation deviates significantly from the expected "
                "concept. Consider revisiting the fundamentals before re-attempting."
            )

    wpm = fluency_metrics.get("words_per_minute", 0)
    filler_count = fluency_metrics.get("filler_word_count", 0)
    pause_ratio = fluency_metrics.get("pause_ratio", 0)

    if wpm and wpm < 100:
        feedback.append("Your speaking pace is a bit slow; try to speak a little more fluidly.")
    elif wpm and wpm > 170:
        feedback.append("Your speaking pace is quite fast; slowing down could improve clarity.")
    else:
        feedback.append("Your speaking pace is within a comfortable conversational range.")

    if filler_count > 5:
        feedback.append(
            f"You used filler words (e.g. 'um', 'like', 'uh') {filler_count} times — "
            "try to reduce these for a more polished delivery."
        )
    else:
        feedback.append("Minimal use of filler words — great job staying articulate.")

    if pause_ratio > 0.35:
        feedback.append(
            "There are noticeably long pauses in your delivery; practicing the "
            "explanation beforehand may help you speak more continuously."
        )
    else:
        feedback.append("Your pacing shows good continuity with natural, well-placed pauses.")

    return feedback
