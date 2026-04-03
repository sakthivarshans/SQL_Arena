"""
SQLArenaEnv Graders.

Four deterministic graders, one per difficulty tier.
Each grader runs 3 fixed tasks using a heuristic agent
and returns a score in [0.0, 1.0].
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.sql_arena_environment import SQLArenaEnvironment
from models import SQLArenaAction
from tasks import get_task


# Heuristic agents per difficulty — realistic but imperfect SQL attempts
_HEURISTIC_AGENT = {
    "easy_001": "SELECT name, salary FROM employees WHERE salary > 70000",  # missing id, dept, wrong order
    "easy_002": "SELECT category, COUNT(*) as count FROM products GROUP BY category",  # correct
    "easy_005": "SELECT SUM(price * quantity) as total_revenue FROM orders",  # missing ROUND
    "medium_001": "SELECT c.name, COUNT(*) as order_count FROM customers c JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.name HAVING COUNT(*)>1",  # missing status filter
    "medium_004": "SELECT d.dept_name, AVG(e.salary) as avg_salary FROM departments d JOIN employees e ON d.dept_id=e.dept_id GROUP BY d.dept_name HAVING AVG(e.salary)>80000",  # correct
    "medium_007": "SELECT e.name, e.salary FROM employees e WHERE e.salary > (SELECT AVG(salary) FROM employees)",  # missing dept_name
    "hard_001": "SELECT c.name, c.city, SUM(o.amount) as total_amount FROM customers c JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id",  # missing window rank
    "hard_003": "SELECT o.category, COUNT(r.return_id)*100.0/COUNT(o.order_id) as return_rate FROM orders o LEFT JOIN returns r ON o.order_id=r.order_id GROUP BY o.category",  # missing ROUND
    "hard_006": "SELECT c.name FROM customers c JOIN orders o ON c.customer_id=o.customer_id WHERE o.category='Technology' GROUP BY c.customer_id",  # wrong logic
    "expert_001": "SELECT a.holder_name, SUBSTR(t.txn_date,1,7) as month, SUM(t.amount) as net_flow FROM accounts a JOIN transactions t ON a.account_id=t.account_id GROUP BY a.holder_name, month",  # missing credit/debit logic
    "expert_003": "SELECT a.holder_name, t.category, SUM(t.amount) as spend FROM accounts a JOIN transactions t ON a.account_id=t.account_id WHERE t.txn_type='debit' GROUP BY a.holder_name, t.category",  # missing RANK, returns all not top
    "expert_007": "SELECT a.holder_name, SUM(t.amount) as total FROM accounts a JOIN transactions t ON a.account_id=t.account_id WHERE t.txn_type='credit' GROUP BY a.holder_name",  # wrong formula
}


def _grade_task(task_id: str) -> float:
    env = SQLArenaEnvironment()
    task = get_task(task_id)
    if task is None:
        return 0.0
    env.reset(task_id=task_id)
    sql = _HEURISTIC_AGENT.get(task_id, "SELECT 1")
    obs = env.step(SQLArenaAction(sql=sql, query_type="submit"))
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