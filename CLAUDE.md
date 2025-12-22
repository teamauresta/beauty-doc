# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-Agent AI Growth System (多智能体增长系统) for Chinese medical aesthetics (医美) institutions. Built with LangGraph + FastAPI + PostgreSQL for SaaS deployment with human-in-the-loop approval workflows.

## Development Commands

```bash
# Setup
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Start services (PostgreSQL, Redis, Qdrant)
docker-compose up -d postgres redis qdrant

# Install backend dependencies
pip install -e ".[dev]"

# Run backend
uvicorn backend.app.main:app --reload --port 8000

# Run frontend (in separate terminal)
cd frontend && npm install && npm run dev

# Run with Docker (full stack)
docker-compose up --build

# Lint
ruff check backend/
mypy backend/

# Test
pytest backend/tests/
pytest backend/tests/test_workflow.py -k "test_name"  # single test
```

## Frontend

Next.js 14 web interface at `frontend/` with Vercel-style design (Geist fonts, dark/light mode, shadcn/ui).

**Routes:**
- `/workflows` - List/create workflows
- `/workflows/[id]` - Workflow detail with agent timeline
- `/approvals` - Pending approvals list
- `/approvals/[id]` - Review interface (approve/reject/request changes)
- `/tenants` - Manage institutions

**Key Frontend Files:**
- `frontend/lib/types.ts` - TypeScript types matching backend schemas
- `frontend/lib/api.ts` - API client with fetch wrapper
- `frontend/lib/hooks/` - SWR hooks with auto-polling for running workflows
- `frontend/components/workflows/workflow-timeline.tsx` - Agent execution visualization

## Architecture

```
┌─────────────────────────────────────────────────┐
│              FastAPI Backend (:8000)            │
│  /api/v1/workflows  /api/v1/approvals           │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│          LangGraph Orchestration Layer          │
│  StateGraph with interrupt_before for HITL      │
│  PostgresSaver for persistent checkpoints       │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│              8 Specialist Agents                │
│  Orchestrator → Content → Compliance → Review   │
│  (All use Claude via langchain-anthropic)       │
└─────────────────────────────────────────────────┘
```

**Key Files:**
- `backend/agents/graph/state.py` - LangGraph state definition (`GrowthWorkflowState` TypedDict)
- `backend/agents/graph/workflow.py` - State graph with HITL checkpoints, `run_growth_workflow()` and `resume_workflow_with_approval()` entry points
- `backend/agents/agents/base.py` - `BaseAgent` class all agents extend (uses `ChatAnthropic` with JSON output parsing)
- `backend/app/api/routes/workflows.py` - Workflow CRUD API
- `backend/app/api/routes/approvals.py` - Human approval API

**8 Specialist Agents** (`backend/agents/agents/`):
| Agent | File | Purpose |
|-------|------|---------|
| Orchestrator | `orchestrator.py` | Central coordinator, task planning |
| Global Benchmark | `global_benchmark.py` | US/EU/KR/JP strategy research |
| Product Strategy | `product_strategy.py` | Pricing, bundling, seasonal plans |
| Content Factory | `content_factory.py` | Viral topics, brand columns, scripts |
| Community Ops | `community_ops.py` | Conversation flows, triggers, FAQ |
| Influencer Matching | `influencer_matching.py` | KOL screening, scoring, outreach |
| China Compliance | `china_compliance.py` | 315 regulations, platform rules |
| Data Analyst | `data_analyst.py` | Metrics, A/B tests, dashboards |

**Full Workflow Flow:**
```
Orchestrator → Global Benchmark → Product Strategy → Content Factory
→ Community Ops → Influencer Matching → Compliance Check → Data Analyst
→ Aggregate Results → Human Review → Execute Approved → END
```

## Human-in-the-Loop (HITL) Pattern

Workflows use LangGraph's `interrupt_before` to pause at human review:
1. Workflow runs through agents → hits `human_review` node → pauses
2. State persisted to PostgreSQL via `AsyncPostgresSaver`
3. API returns `awaiting_approval: true` with `pending_approvals` preview
4. Human calls `POST /api/v1/approvals/{workflow_id}` with `approve|reject|request_changes`
5. `resume_workflow_with_approval()` continues the graph

## Adding New Agents

1. Create `backend/agents/agents/new_agent.py` extending `BaseAgent`
2. Implement `async execute(self, state: GrowthWorkflowState)` method
3. Add node wrapper function: `async def new_agent_node(state) -> state`
4. Register in `workflow.py`: add node, add edge, update routing if needed

## Compliance Constraints (Critical)

All content must comply with China's post-315 medical advertising regulations:
- No effect guarantees ("100%有效", "永久保持")
- No doctor personal endorsements for treatment effects
- No real surgery footage
- Patient cases must be anonymized with "个体差异" disclaimer
- Platform-specific rules: Xiaohongshu (标注广告), Douyin (资质认证), WeChat (审核)

See `backend/agents/agents/china_compliance.py` for full compliance ruleset.

## Workflow Types

- `full_growth_plan` - Complete 30/60/90 day growth strategy
- `content_generation` - Generate platform-specific content (uses `create_content_workflow()`)
- `influencer_matching` - KOL discovery and outreach
- `community_strategy` - Social community operations
- `product_strategy` - Product/pricing recommendations
