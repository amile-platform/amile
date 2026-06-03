# AMILE — Adaptive Mathematics Intelligence & Learning Ecosystem

> **AI-native educational data analytics platform** engineered to eliminate persistent mathematics achievement gaps in U.S. high schools serving underserved populations.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![React 18](https://img.shields.io/badge/react-18-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![TensorFlow 2.13](https://img.shields.io/badge/TensorFlow-2.13-FF6F00.svg)](https://tensorflow.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://postgresql.org/)

---

## What is AMILE?

AMILE is not a content delivery system like Khan Academy or DreamBox. It is a closed-loop instructional intelligence infrastructure that:

-  **Monitors** thousands of discrete student mathematical interactions in real-time using Deep Knowledge Tracing (DKT) ensembles
-  **Identifies** specific cognitive misconceptions at the sub-skill level using Explainable AI (XAI)
-  **Generates** standards-aligned, project-based learning modules tailored to each student's cultural context and reading level
-  **Provides** reinforcement-trainable AI teaching assistants that improve through student and educator feedback
-  **Produces** predictive equity dashboards for school districts to proactively allocate resources before achievement gaps manifest

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        AMILE Platform                         │
├─────────────┬─────────────────────────────┬─────────────────┤
│   Frontend  │         Backend (API)        │   ML Pipeline   │
│  React 18   │      FastAPI + PostgreSQL    │  TF/PyTorch DKT │
│  TypeScript │      Redis + Apache Kafka    │  LLaMA-3-8B     │
│  Tailwind   │      Oracle Cloud OCI        │  XAI + RLHF     │
└─────────────┴─────────────────────────────┴─────────────────┘
```

---

## 📁 Repository Structure

```
amile/
├── backend/                    # FastAPI backend service
│   ├── app/
│   │   ├── api/routes/         # REST API endpoints
│   │   ├── core/               # Config, security, dependencies
│   │   ├── db/                 # Database session and migrations
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── ai/             # DKT, BKT, LLM inference services
│   │   │   ├── analytics/      # Equity dashboards, reporting
│   │   │   └── auth/           # Authentication & authorization
│   │   └── utils/              # Shared utilities
│   ├── alembic/                # Database migrations
│   └── tests/                  # Unit and integration tests
├── frontend/                   # React 18 + TypeScript
│   └── src/
│       ├── components/         # Reusable UI components
│       ├── pages/              # Route-level page components
│       ├── hooks/              # Custom React hooks
│       ├── services/           # API client layer
│       └── store/              # Zustand global state
├── ml/                         # Machine learning models & training
│   ├── models/dkt/             # Deep Knowledge Tracing
│   ├── models/bkt/             # Bayesian Knowledge Tracing
│   ├── models/llm/             # Fine-tuned LLaMA mathematics tutor
│   ├── models/xai/             # Explainable AI misconception detector
│   ├── training/               # Training scripts
│   └── evaluation/             # Model evaluation and benchmarks
├── infrastructure/             # DevOps & deployment
│   ├── docker/                 # Docker configurations
│   ├── k8s/                    # Kubernetes manifests
│   └── terraform/              # Oracle OCI infrastructure as code
├── mvp/                        # ⚡ Standalone MVP prototype
│   ├── backend/                # Lightweight FastAPI MVP
│   └── frontend/               # React MVP dashboard
├── docs/                       # Architecture and API documentation
└── .github/workflows/          # CI/CD pipelines
```

---

## Quick Start (MVP)

The fastest way to run AMILE locally:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/amile.git
cd amile

# Run MVP with Docker Compose
cd mvp
docker-compose up --build

# Access:
# Student Dashboard:  http://localhost:3000
# Teacher Dashboard:  http://localhost:3000/teacher
# Admin Dashboard:    http://localhost:3000/admin
# API Docs:           http://localhost:8000/docs
```

---

##  Full Platform Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit with your config
alembic upgrade head            # Run database migrations
uvicorn app.main:app --reload   # Start API server
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local      # Edit with your API URL
npm run dev                     # Start development server
```

### ML Pipeline
```bash
cd ml
pip install -r requirements.txt
python training/train_dkt.py    # Train DKT model
python training/train_bkt.py    # Train BKT model
```

---

##  Running Tests

```bash
# Backend tests
cd backend && pytest tests/ -v --cov=app

# Frontend tests
cd frontend && npm run test

# ML model evaluation
cd ml && python evaluation/evaluate_models.py
```

---

##  Key Metrics Tracked

| Metric | Target | Measurement |
|--------|--------|-------------|
| Math proficiency improvement | +25 percentage points | Pre/post standardized assessment |
| Achievement gap reduction | -30% | Comparative cohort analysis |
| STEM course enrollment increase | +40% | District enrollment records |
| AI prediction accuracy | ≥85% | Cross-validated on holdout set |
| System uptime | 99.9% | Oracle OCI monitoring |

---

##  Compliance & Privacy

- **FERPA compliant**: All student data encrypted at rest (AES-256) and in transit (TLS 1.3)
- **COPPA compliant**: Parental consent workflows for students under 13
- **Data minimization**: Only educationally relevant data collected
- **Audit logging**: All data access logged with immutable audit trail

---

##  Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

---

##  License

MIT License — see [LICENSE](LICENSE) for details.

---

##  Author

**Gordon Nsiah**  
MS Applied Mathematics, Ohio University  
Data Analyst & STEM Education Specialist  
gordon.nsiah@amile.io
