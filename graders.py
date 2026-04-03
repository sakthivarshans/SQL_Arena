"""
SQLArenaEnv Graders.

Four deterministic graders, one per difficulty tier.
Each grader runs 3 fixed tasks using the reference solution agent
and returns a score in [0.0, 1.0].
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.sql_arena_environment import SQLArenaEnvironment
from models import SQLArenaAction
from tasks import get_task


def _grade_task(task_id: str) -> float:
    env = SQLArenaEnvironment()
    task = get_task(task_id)
    if task is None:
        return 0.0
    env.reset(task_id=task_id)
    obs = env.step(SQLArenaAction(sql=task.solution_sql, query_type="submit"))
    return float(obs.reward) if obs.reward is not None else 0.0


def _grade_tier(task_ids: list, tier_name: str) -> float:
    scores = []
    for tid in task_ids:
        score = _grade_task(tid)
        scores.append(score)
        print(f"  {tid}: {score:.4f}")
    mean = round(sum(scores) / len(scores), 4)
    print(f"  {tier_name} mean: {mean:.4f}")
    return mean


def grade_easy() -> float:
    """Easy grader — single table SELECT, WHERE, GROUP BY."""
    print("Running easy grader...")
    return _grade_tier(["easy_001", "easy_002", "easy_005"], "easy")


def grade_medium() -> float:
    """Medium grader — JOINs, HAVING, subqueries."""
    print("Running medium grader...")
    return _grade_tier(["medium_001", "medium_004", "medium_007"], "medium")


def grade_hard() -> float:
    """Hard grader — CTEs, window functions, complex aggregation."""
    print("Running hard grader...")
    return _grade_tier(["hard_001", "hard_003", "hard_006"], "hard")


def grade_expert() -> float:
    """Expert grader — correlated subqueries, financial analytics."""
    print("Running expert grader...")
    return _grade_tier(["expert_001", "expert_003", "expert_007"], "expert")


def run_all_graders() -> dict:
    """Run all four graders and return summary dict."""
    results = {
        "easy":   grade_easy(),
        "medium": grade_medium(),
        "hard":   grade_hard(),
        "expert": grade_expert(),
    }
    results["overall"] = round(sum(v for k, v in results.items() if k != "overall") / 4, 4)
    return results


if __name__ == "__main__":
    print("=" * 50)
    print("SQLArenaEnv Graders")
    print("=" * 50)
    results = run_all_graders()
    print()
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for k, v in results.items():
        bar = "█" * int(v * 20)
        print(f"  {k:10s}: {v:.4f}  {bar}")