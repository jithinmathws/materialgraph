## Getting Started

### Prerequisites

Before running MaterialGraph, ensure the following are installed:

* Python 3.11+
* PostgreSQL 15+
* Git
* Materials Project API Key

---

### Clone Repository

```bash
git clone https://github.com/<your-username>/materialgraph.git
cd materialgraph
```

---

### Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost/materialgraph

MP_API_KEY=your_materials_project_api_key
```

---

### Create Database

PostgreSQL:

```sql
CREATE DATABASE materialgraph;
```

---

### Run Database Migrations

```bash
alembic upgrade head
```

---

### Import Battery Material Candidates

MaterialGraph imports a curated set of battery-relevant candidates from Materials Project.

```bash
python scripts/import_materials_project.py
```

Verify import:

```bash
python scripts/check_import_counts.py
```

Example output:

```text
Materials: 28
Elements: 9
MaterialElements: 94
```

---

### Start API Server

```bash
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

### Run Tests

Run all tests:

```bash
pytest
```

Run specific test groups:

```bash
pytest tests/services
```

```bash
pytest tests/api
```

---

## Example Workflows

### Candidate Screening

```text
POST /api/v1/screening/candidates
```

Evaluate battery material candidates under:

* lithium scarcity
* cobalt avoidance
* stability constraints
* supply-risk constraints

---

### Candidate Comparison

```text
POST /api/v1/comparison/materials
```

Compare two candidate materials and receive:

* screening scores
* risk scores
* ranking explanations

---

### Scenario Ranking

```text
POST /api/v1/scenarios/rank
```

Rank candidates under scenarios such as:

* lithium_supply_shock
* cobalt_avoidance
* low_supply_risk

---

### Sensitivity Analysis

```text
POST /api/v1/sensitivity/material
```

Analyze candidate robustness under changing supply-risk conditions.

---

### Substitution Analysis

```text
POST /api/v1/substitutions/analyze
```

Identify alternative candidate materials based on:

* chemistry similarity
* risk profile
* substitution potential

---
