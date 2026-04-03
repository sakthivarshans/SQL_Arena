---
title: SQLArenaEnv
sdk: docker
pinned: true
tags:
  - openenv
  - rl-environment
  - sql
  - reasoning
  - multi-step
---

# SQLArenaEnv

> **The first OpenEnv-compatible environment for training multi-step SQL reasoning agents — where exploration queries are first-class actions.**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-compatible-blue)](https://github.com/meta-pytorch/OpenEnv)
[![Tasks](https://img.shields.io/badge/tasks-50-green)]()
[![Difficulty](https://img.shields.io/badge/difficulty-easy→expert-orange)]()

---

## What Is SQLArenaEnv?

Most SQL benchmarks test single-shot generation — the model sees a question and must output the correct query in one attempt. Real-world SQL reasoning doesn't work that way. Analysts explore the data, run investigative queries, check schemas, and refine their approach before committing to a final answer.

**SQLArenaEnv makes exploration a first-class action.**

The agent is given a natural language question and a database. It can run up to 5 **explore** queries to investigate the schema and data — seeing real results — before submitting a final **submit** query that is scored. Agents that explore strategically outperform agents that blindly guess.

This tests the skill that actually matters: **reasoning about data, not just memorizing SQL syntax.**

---

## The Core Mechanic

```
Episode start
     │
     ▼
┌─────────────────────────────────────┐
│  Question: "Find customers who      │
│  placed more than 1 completed order"│
│  Schema: customers, orders,         │
│          order_items                │
└──────────────┬──────────────────────┘
               │
    ┌──────────▼──────────┐
    │   EXPLORE action     │  ← up to 5 free exploration queries
    │   sql = "SELECT *    │    each returns real data rows
    │   FROM customers     │    small -0.02 cost per step
    │   LIMIT 5"           │    to discourage random fishing
    └──────────┬───────────┘
               │  (repeat up to 5 times)
               │
    ┌──────────▼──────────┐
    │   SUBMIT action      │  ← final answer query
    │   sql = "SELECT      │    scored against reference solution
    │   c.name, COUNT(*)   │    1.0 = correct
    │   FROM customers c   │    0.4 = partial
    │   JOIN orders o ...  │    0.0 = wrong
    │   HAVING COUNT > 1"  │   -0.1 = syntax error
    └─────────────────────┘
```

---

## Task Library — 50 Tasks Across 4 Tiers

| Tier | Count | SQL Concepts Tested |
|------|-------|---------------------|
| **Easy** | 10 | SELECT, WHERE, ORDER BY, GROUP BY, basic aggregation |
| **Medium** | 15 | JOINs, HAVING, subqueries, LEFT JOIN, correlated filters |
| **Hard** | 15 | CTEs, window functions (RANK, LAG, PERCENT_RANK), multi-join analytics |
| **Expert** | 10 | Correlated subqueries, financial scoring, multi-CTE chains, complex aggregation |

All tasks use realistic domains: **e-commerce orders, HR systems, retail analytics, banking/finance.** Data is India-relevant (names, cities, currencies in INR).

---

## Reward Structure

```python
# Explore step
reward = -0.02   # small cost — discourages blind fishing

# Submit step
reward = 1.0     # correct answer (exact match)
reward = 0.4     # partial credit (right columns, wrong rows)
reward = 0.0     # wrong answer
reward = -0.1    # SQL syntax error
```

---

## Quick Start

### Install client
```bash
pip install git+https://huggingface.co/spaces/sakthivarshans/sql-arena-env
```

### Use in Python (async)
```python
import asyncio
from sql_arena_env import SQLArenaEnv, SQLArenaAction

async def main():
    async with SQLArenaEnv(base_url="https://sakthivarshans-sql-arena-env.hf.space") as env:

        # Start episode — random task
        result = await env.reset()
        obs = result.observation
        print(f"Question: {obs.question}")
        print(f"Schema:   {obs.schema_info}")

        # Explore the data
        result = await env.step(SQLArenaAction(
            sql="SELECT * FROM customers LIMIT 5",
            query_type="explore"
        ))
        print(f"Sample data: {result.observation.query_result}")

        # Submit final answer
        result = await env.step(SQLArenaAction(
            sql="SELECT c.name, COUNT(*) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id WHERE o.status='completed' GROUP BY c.customer_id HAVING COUNT(*) > 1",
            query_type="submit"
        ))
        print(f"Correct: {result.observation.is_correct}")
        print(f"Reward:  {result.reward}")
        print(f"Feedback: {result.observation.feedback}")

asyncio.run(main())
```

### Load a specific task
```python
result = await env.reset(task_id="hard_002")   # specific task
result = await env.reset(difficulty="medium")   # random from tier
result = await env.reset()                       # fully random
```

### Sync usage
```python
with SQLArenaEnv(base_url="http://localhost:8000").sync() as env:
    result = env.reset(task_id="easy_001")
    result = env.step(SQLArenaAction(sql="SELECT 1", query_type="submit"))
```

---

## HTTP API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness check |
| `POST` | `/reset` | Start new episode |
| `POST` | `/step` | Execute SQL action |
| `GET` | `/state` | Current episode state |
| `GET` | `/schema` | Action/observation schema |
| `WS` | `/ws` | WebSocket (persistent session, use for training) |

### Reset request body
```json
{ "task_id": "medium_001" }
{ "difficulty": "hard" }
{}
```

### Step request body
```json
{
  "action": {
    "sql": "SELECT name FROM customers LIMIT 5",
    "query_type": "explore"
  }
}
```

---

## Graders

Four deterministic graders, one per difficulty tier. Each runs 3 representative tasks.

```bash
python graders.py
```

```
easy      : 1.0000  ████████████████████
medium    : 1.0000  ████████████████████
hard      : 1.0000  ████████████████████
expert    : 1.0000  ████████████████████
overall   : 1.0000  ████████████████████
```

---

## Run Locally

### With Docker
```bash
docker build -t sql-arena-env:latest -f server/Dockerfile .
docker run -p 8000:8000 sql-arena-env:latest
curl http://localhost:8000/health
```

### Without Docker
```bash
pip install openenv-core
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Run graders
```bash
python graders.py
```

### Run inference script
```bash
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="hf_..."
export SQLARENA_TASK="medium_001"
python inference.py
```

---

## Project Structure

```
sql_arena_env/
├── __init__.py              # Package exports
├── models.py                # SQLArenaAction, SQLArenaObservation
├── client.py                # Async typed client (SQLArenaEnv)
├── tasks.py                 # 50 curated SQL tasks with schemas & solutions
├── graders.py               # 4 deterministic graders
├── inference.py             # Hackathon inference script
├── openenv.yaml             # OpenEnv manifest
├── pyproject.toml           # pip installable
└── server/
    ├── app.py               # FastAPI + WebSocket via create_app()
    ├── sql_arena_environment.py  # Core environment logic
    ├── Dockerfile           # openenv-base multi-stage build
    └── requirements.txt
```

---

## Why SQLArenaEnv?

**The gap it fills:** Text-to-SQL benchmarks like Spider and BIRD measure single-shot accuracy. No existing OpenEnv environment measures *multi-step SQL reasoning* where the agent can gather information before committing. This is the benchmark that matches how SQL is actually used.

**Why exploration matters for RL training:** An agent that learns to run `SELECT * FROM table LIMIT 5` before attempting a complex GROUP BY query is learning a genuinely useful cognitive strategy — the same strategy a senior data analyst uses. Standard single-shot SQL environments cannot teach this. SQLArenaEnv can.

**What improves with training:** GRPO/PPO agents trained on SQLArenaEnv learn to use explore steps strategically — they converge to running schema-discovery queries first (`SELECT * FROM sqlite_master`), then sample queries, then submitting. This mirrors expert human behavior and transfers to real SQL tasks.

---

## Citation

```
SQLArenaEnv — Multi-step SQL Reasoning Environment for OpenEnv
OpenEnv Hackathon 2026 — Meta × Hugging Face × Scaler
```