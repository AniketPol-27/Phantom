"""
Data confidence scoring for the patient model.

Scores how trustworthy our model is per system based on:
- Data freshness (how recent is the data?)
- Data completeness (do we have what we need?)
- Trajectory confidence (how many data points for slope?)
"""

from src.model_builder.system_helpers import days_since, get_lab_value_history


def freshness_category(days: int | None) -> str:
    """Classify data freshness."""
    if days is None:
        return "no_data"
    if days <= 90:
        return "fresh"
    if days <= 365:
        return "moderate"
    if days <= 730:
        return "stale"
    return "outdated"


def trajectory_confidence(data_points: int) -> str:
    """Classify trajectory confidence by number of data points."""
    if data_points < 2:
        return "insufficient"
    if data_points < 3:
        return "low"
    if data_points <= 5:
        return "moderate"
    return "high"


def compute_system_confidence(
    required_labs: list[str],
    lab_observations: list[dict],
) -> dict:
    """
    Compute overall confidence for a system based on required labs.

    Args:
        required_labs: Lab keys that this system needs
        lab_observations: All parsed lab observations for the patient

    Returns:
        {
            "completeness": 0.0-1.0,
            "freshness": "fresh|moderate|stale|outdated|no_data",
            "trajectory_confidence": "high|moderate|low|insufficient",
            "missing_labs": [...],
            "stale_labs": [...],
            "overall": "high|moderate|low",
        }
    """
    present_labs = []
    missing_labs = []
    stale_labs = []
    freshness_scores = []
    point_counts = []

    for lab_key in required_labs:
        history = get_lab_value_history(lab_observations, lab_key)
        if not history:
            missing_labs.append(lab_key)
            continue

        present_labs.append(lab_key)
        latest = history[-1]
        days = days_since(latest["date"])
        category = freshness_category(days)

        if category in ("stale", "outdated"):
            stale_labs.append(lab_key)

        freshness_scores.append(category)
        point_counts.append(len(history))

    completeness = len(present_labs) / len(required_labs) if required_labs else 0.0

    # Worst freshness wins
    freshness_priority = ["no_data", "outdated", "stale", "moderate", "fresh"]
    if freshness_scores:
        worst_freshness = min(freshness_scores, key=lambda x: freshness_priority.index(x))
    else:
        worst_freshness = "no_data"

    # Best trajectory among present labs
    if point_counts:
        max_points = max(point_counts)
        traj_conf = trajectory_confidence(max_points)
    else:
        traj_conf = "insufficient"

    # Overall composite
    if completeness >= 0.8 and worst_freshness in ("fresh", "moderate") and traj_conf in ("high", "moderate"):
        overall = "high"
    elif completeness >= 0.5 and worst_freshness != "no_data":
        overall = "moderate"
    else:
        overall = "low"

    return {
        "completeness": round(completeness, 2),
        "freshness": worst_freshness,
        "trajectory_confidence": traj_conf,
        "missing_labs": missing_labs,
        "stale_labs": stale_labs,
        "overall": overall,
    }