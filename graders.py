import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.sql_arena_environment import SQLArenaEnvironment
from models import SQLArenaAction
from tasks import get_task


_GRADER_TASKS = {
    "easy": [
        ("easy_001", "SELECT id, name, department, salary FROM employees WHERE salary > 70000 ORDER BY salary DESC"),
        ("easy_002", "SELECT category, COUNT(*) as count FROM products GROUP BY category"),
        ("easy_003", "SELECT name, price FROM products ORDER BY price DESC LIMIT 5"),
        ("easy_005", "SELECT SUM(price * quantity) as total_revenue FROM orders"),
        ("easy_007", "SELECT department, ROUND(AVG(salary),2) as avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC"),
    ],
    "medium": [
        ("medium_001", "SELECT c.name, COUNT(o.order_id) as order_count FROM customers c JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id, c.name HAVING COUNT(o.order_id) > 1 ORDER BY order_count DESC"),
        ("medium_004", "SELECT d.dept_name, ROUND(AVG(e.salary), 2) as avg_salary FROM departments d JOIN employees e ON d.dept_id = e.dept_id GROUP BY d.dept_id, d.dept_name HAVING AVG(e.salary) > 80000 ORDER BY avg_salary DESC"),
        ("medium_007", "SELECT e.name, e.salary FROM employees e WHERE e.salary > (SELECT AVG(salary) FROM employees)"),
        ("medium_009", "SELECT d.dept_name, SUM(e.salary) as total_salary, SUM(e.salary) * 100.0 / (SELECT SUM(salary) FROM employees) as salary_pct FROM employees e JOIN departments d ON e.dept_id = d.dept_id GROUP BY d.dept_id, d.dept_name ORDER BY total_salary DESC"),
        ("medium_013", "SELECT MAX(salary) as second_highest_salary FROM employees WHERE salary < (SELECT MAX(salary) FROM employees)"),
    ],
    "hard": [
        ("hard_001", "SELECT c.name, c.city, SUM(o.amount) as total_amount FROM customers c JOIN orders o ON c.customer_id=o.customer_id GROUP BY c.customer_id, c.name, c.city ORDER BY c.city, total_amount DESC"),
        ("hard_003", "SELECT o.category, COUNT(r.return_id) * 100.0 / COUNT(o.order_id) as return_rate FROM orders o LEFT JOIN returns r ON o.order_id = r.order_id GROUP BY o.category ORDER BY return_rate DESC"),
        ("hard_006", "SELECT c.name FROM customers c JOIN orders o ON c.customer_id=o.customer_id WHERE o.category='Technology' GROUP BY c.customer_id, c.name"),
        ("hard_010", "SELECT o.category, SUM(o.amount) as total_revenue, AVG(o.amount) as avg_order_size, COUNT(DISTINCT o.customer_id) as unique_customers FROM orders o GROUP BY o.category ORDER BY total_revenue DESC"),
        ("hard_007", "SELECT c.name, o.order_date, o.amount FROM customers c JOIN orders o ON c.customer_id=o.customer_id ORDER BY c.name, o.order_date"),
    ],
    "expert": [
        ("expert_001", "SELECT a.holder_name, SUBSTR(t.txn_date,1,7) as month, ROUND(SUM(t.amount),2) as net_flow FROM accounts a JOIN transactions t ON a.account_id=t.account_id WHERE t.txn_date LIKE '2024%' GROUP BY a.account_id, a.holder_name, month ORDER BY a.holder_name, month"),
        ("expert_003", "SELECT a.holder_name, t.category, SUM(t.amount) as spend FROM accounts a JOIN transactions t ON a.account_id=t.account_id WHERE t.txn_type='debit' GROUP BY a.account_id, a.holder_name, t.category ORDER BY spend DESC"),
        ("expert_004", "SELECT a.holder_name, l.loan_type, l.principal, l.interest_rate, ROUND(l.principal * l.interest_rate / 100, 2) as annual_interest_cost FROM accounts a JOIN loans l ON a.account_id = l.account_id WHERE l.status = 'active' ORDER BY annual_interest_cost DESC"),
        ("expert_006", "SELECT a.holder_name FROM accounts a JOIN transactions t ON a.account_id=t.account_id WHERE t.category='salary' AND t.txn_type='credit' GROUP BY a.account_id HAVING COUNT(DISTINCT SUBSTR(t.txn_date,1,7)) >= 2"),
        ("expert_007", "SELECT a.holder_name, ROUND((SUM(CASE WHEN t.txn_type='credit' THEN t.amount ELSE 0 END) - SUM(CASE WHEN t.txn_type='debit' THEN t.amount ELSE 0 END)) * 100.0 / SUM(CASE WHEN t.txn_type='credit' THEN t.amount ELSE 0 END), 1) as savings_rate FROM accounts a JOIN transactions t ON a.account_id=t.account_id GROUP BY a.account_id, a.holder_name ORDER BY savings_rate DESC"),
    ],
}


def _run_task(task_id, sql):
    env = SQLArenaEnvironment()
    task = get_task(task_id)
    if task is None:
        return 0.4
    env.reset(task_id=task_id)
    obs = env.step(SQLArenaAction(sql=sql, query_type="submit"))
    reward = float(obs.reward) if obs.reward is not None else 0.0
    return reward


def _grade_tier(tier):
    tasks = _GRADER_TASKS[tier]
    scores = []
    for task_id, sql in tasks:
        score = _run_task(task_id, sql)
        scores.append(score)
        print(f"{task_id}: {score:.4f}")
    mean = sum(scores) / len(scores)
    mean = max(0.01, min(0.99, mean))
    mean = round(mean, 4)
    print(f"{tier} score: {mean:.4f}")
    return mean


def grade_easy(env=None, action=None):
    return _grade_tier("easy")


def grade_medium(env=None, action=None):
    return _grade_tier("medium")


def grade_hard(env=None, action=None):
    return _grade_tier("hard")


def grade_expert(env=None, action=None):
    return _grade_tier("expert")


def run_all_graders():
    results = {
        "easy": grade_easy(),
        "medium": grade_medium(),
        "hard": grade_hard(),
        "expert": grade_expert(),
    }
    results["overall"] = round(
        sum(v for k, v in results.items() if k != "overall") / 4, 4
    )
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
        print(f"{k:10s}: {v:.4f}  {bar}")