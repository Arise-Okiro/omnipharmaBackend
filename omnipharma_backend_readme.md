# OmniPharma 🏥⚡

> High-throughput, multi-tenant pharmacy inventory & POS backend built for enterprise pharmacy chains (simulating 38 MedNova retail outlets).

OmniPharma is designed to resolve core operational challenges in multi-location retail pharmacies: race conditions during peak checkout hours, inventory spoilage, stockout substitution, and cross-tenant data isolation.

---

## 📌 Architecture Highlights

- **Shared-Database, Shared-Schema Multi-Tenancy**: Data separation across 38 retail outlets enforced logically via `tenant_id` / `store_id` indexing and zero-trust query filtering.
- **Resilient Connection Pooling**: SQLAlchemy connection pool tuned (base size: 10, overflow: 20) with FastAPI generator-based session dependencies (`yield db`) to prevent connection starvation under concurrent cashier load.
- **FEFO Batch Allocation**: First-Expired, First-Out inventory tracking to mitigate drug expiration losses.
- **Reproducible Development**: Containerized PostgreSQL via Docker Compose, isolated from local OS conflicts (port-mapped `5433:5432`).

---

## 🏗️ System Overview

```text
       [ Cashier / Auditor / Store Staff ]
                       │ (HTTP / JSON)
                       ▼
             [ Uvicorn ASGI Server ]
                       │
             [ FastAPI Application ]
      ┌────────────────┴────────────────┐
      │  Dependency Injection: yield db │
      ▼                                 ▼
[ SQLAlchemy ORM ]            [ JWT Auth & Scoping ]
 (Pool: 10+20)                 (store_id + role)
      │
      ▼ (Port 5433 -> 5432)
┌────────────────────────────────────────────────────────┐
│           Docker: postgres:16-alpine                   │
│                                                        │
│  ├── tenants       ├── products      ├── sales         │
│  ├── users         ├── inventory     ├── sale_items    │
│  └── audit_logs                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🗄️ Relational Data Model

OmniPharma utilizes a 6-core relational entity structure:

| Entity | Table Name | Purpose / Boundary |
| :--- | :--- | :--- |
| **Stores / Outlets** | `tenants` | Represents pharmacy branches (e.g., MedNova Banjara Hills, Hitec City). |
| **Staff & Roles** | `users` | Scoped by `tenant_id`; supports `pharmacist`, `inventory_controller`, `auditor`, and `head_office`. |
| **Global Master Catalog** | `products` | Master SKU catalog containing generic molecular composition for AI substitution. |
| **Batches & Stock** | `inventory` | Scoped by `store_id` and `product_id`; tracks `batch_number`, `expiry_date`, and `quantity`. |
| **Invoicing & Ledger** | `sales` & `sale_items` | Transaction ledger recording bills, line items, and quantities. |
| **Governance Trail** | `audit_logs` | Immutable audit log tracking operational diffs, user actions, and anomaly flags. |

---

## 🛠️ Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Server:** [Uvicorn](https://www.uvicorn.org/) (ASGI)
- **ORM & DB Driver:** [SQLAlchemy](https://www.sqlalchemy.org/) & `psycopg2-binary`
- **Database:** [PostgreSQL 16](https://www.postgresql.org/) (Containerized with Alpine Linux)
- **Containerization:** Docker & Docker Compose

---

## 📂 Project Directory Structure

```text
omnipharma/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application & base routes
│   ├── database.py      # Engine, connection pooling & SessionLocal
│   ├── models.py        # SQLAlchemy schema definitions
│   └── seed.py          # Seed script for MedNova outlets & drug data
├── docker-compose.yml   # PostgreSQL container configuration
├── requirements.txt     # Python project dependencies
├── .env.example         # Environment template
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running)
- [Python 3.10+](https://www.python.org/downloads/)

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/<your-username>/OmniPharma.git
cd OmniPharma

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/omnipharma_db
PORT=8000
```

> **Note:** The host port `5433` is mapped to container port `5432` in `docker-compose.yml` to prevent authentication and port collisions with any existing local PostgreSQL service.

### 3. Start Database Container

```bash
docker compose up -d
```

Verify that the container is healthy:

```bash
docker ps
```

### 4. Run Migrations & Seed Sample Data

Initialize the tables and populate test records (MedNova outlets, users, and molecular inventory):

```bash
python -m app.seed
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Access the interactive API documentation at:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

---
