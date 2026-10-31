# CareFlow - Smart Clinic Appointment & Billing System
**Rajshahi University of Engineering & Technology (RUET)**  
**Department of Computer Science & Engineering**  
**Course:** CSE 3206 – Software Engineering Sessional (22 Series)  
**Evaluation:** Reflection Essay & Comprehensive Project (CO4, PO12) | **Total Marks:** 20  
**Student Name:** Md. Rofaz Hasan Rafiu  
**Email:** [mdrofazhasanrafiu@gmail.com](mailto:mdrofazhasanrafiu@gmail.com) | **GitHub Repository:** CareFlow System

---

[![CI/CD Pipeline](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/)
[![Tests](https://img.shields.io/badge/tests-32%20passed-success.svg)](https://github.com/)
[![Coverage](https://img.shields.io/badge/coverage-88.85%25-blue.svg)](https://github.com/)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-OpenAPI%203.1-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Architecture & 5 Functional Modules](#-key-architecture--5-functional-modules)
3. [Design Patterns Implementation](#-design-patterns-implementation)
4. [Software Testing & TDD Suite](#-software-testing--tdd-suite)
5. [Self-Directed Learning (CO4): FastAPI & OpenAPI Docs](#-self-directed-learning-co4-fastapi--openapi-docs)
6. [Configuration Management & Git Evidence](#-configuration-management--git-evidence)
7. [Installation & Quickstart Guide](#-installation--quickstart-guide)
8. [Live Demo & Viva Defense Preparation](#-live-demo--viva-defense-preparation)
9. [AI Tool Usage Transparency Disclosure](#-ai-tool-usage-transparency-disclosure)

---

## 📌 Project Overview
**CareFlow** is an enterprise-grade, extensible Clinic Management and Healthcare Billing application developed following the complete Software Development Life Cycle (SDLC) under the **Agile Scrum** methodology.

Designed to address real-world patient scheduling conflicts, billing transparency, and multi-channel notification requirements, CareFlow incorporates:
- **5 Core Functional Modules** (Authentication, Appointments, Prescriptions, Billing, and Notifications)
- **Persistent SQLite Database** managed via Repository pattern and thread-safe Singleton
- **5 Gang of Four (GoF) Design Patterns** across Creational, Structural, and Behavioral categories
- **Test-Driven Development (TDD)** with mock objects isolating external DB and payment dependencies
- **Self-Directed Learning (CO4)**: FastAPI RESTful endpoints with automated OpenAPI 3.1 / Swagger documentation
- **GitHub Actions CI/CD Pipeline**: Multi-python matrix build, linting, and 85%+ coverage thresholds

---

## 🏗 Key Architecture & 5 Functional Modules

```
                    ┌────────────────────────────────────────┐
                    │      FastAPI REST / CLI Terminal       │
                    └───────────────────┬────────────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │   AuthService   │          │  ApptService    │          │ BillingService  │
  │ (User/Role/JWT) │          │ (Slots/Subject) │          │(Strategy/Adapter│
  └────────┬────────┘          └────────┬────────┘          └────────┬────────┘
           │                            │                            │
           ▼                            ▼                            ▼
  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │ UserRepository  │          │ ApptRepository  │          │BillingRepository│
  └────────┬────────┘          └────────┬────────┘          └────────┬────────┘
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        ▼
                       ┌─────────────────────────────────┐
                       │ DatabaseManager (Singleton Pool) │
                       │          careflow.db             │
                       └─────────────────────────────────┘
```

1. **Authentication & RBAC (`careflow/services/auth_service.py`)**:
   - Secure registration and login for `PATIENT`, `DOCTOR`, `ADMIN`, `RECEPTIONIST`.
   - Salted SHA-256 password hashing and simulated JWT bearer tokens.
2. **Appointment Scheduling (`careflow/services/appointment_service.py`)**:
   - Booking, slot collision guard preventing double booking, confirmation, and cancellation.
   - Triggers `AppointmentSubject` upon lifecycle transitions.
3. **Medical Records & Prescriptions (`careflow/services/medical_record_service.py`)**:
   - Encapsulates clinical diagnoses and prescription items (`PrescriptionItem`).
   - Automatically transitions confirmed appointments to `COMPLETED`.
4. **Dynamic Billing & Invoicing (`careflow/services/billing_service.py`)**:
   - Computes invoices using the **Strategy Pattern** (Standard 5% VAT, Student 30% waiver, Insurance 80% co-pay, Emergency 25% surcharge).
   - Executes payment via the **Adapter Pattern** (bKash & Stripe).
5. **Event-Driven Notifications (`careflow/patterns/observer.py` & `factory.py`)**:
   - Decoupled `AppointmentSubject` broadcasting to `EmailNotificationObserver`, `SMSNotificationObserver`, and `AuditLogObserver`.

---

## 🧩 Design Patterns Implementation

| Pattern | Category | Concrete Class | Problem Solved & Rejected Alternative |
| :--- | :--- | :--- | :--- |
| **Singleton** | Creational | `DatabaseManager` | **Solved:** Thread-safe SQLite connection pooling preventing file-lock collisions.<br>**Rejected:** Global variable (lacks thread-locks and cannot isolate unit test state). |
| **Factory Method** | Creational | `NotificationFactory` | **Solved:** Decouples transport channels (Email, SMS, Webhook) with runtime registration.<br>**Rejected:** Hardcoded `if/elif` branches in service layer (violates Open-Closed Principle). |
| **Adapter** | Structural | `BkashPaymentAdapter`, `StripePaymentAdapter` | **Solved:** Harmonizes incompatible payment APIs (bKash BDT floats vs Stripe cents) into `IPaymentProcessor`.<br>**Rejected:** Direct SDK calls in billing (causes vendor lock-in). |
| **Observer** | Behavioral | `AppointmentSubject`, `EmailNotificationObserver`, `AuditLogObserver` | **Solved:** Decouples appointment state updates from email, SMS, and audit side-effects.<br>**Rejected:** Hardcoded sequential method invocations inside booking method. |
| **Strategy** | Behavioral | `StandardBillingStrategy`, `StudentDiscountStrategy`, `EmergencyCareStrategy` | **Solved:** Encapsulates dynamic healthcare subsidy algorithms.<br>**Rejected:** Nested switch statements in `Invoice.calculate_total()` (inflates cyclomatic complexity). |

---

## 🧪 Software Testing & TDD Suite

CareFlow was constructed following strict **Test-Driven Development (TDD)** principles. External database calls, payment gateways, and observer transports were thoroughly isolated using `unittest.mock.MagicMock`.

```bash
# Execute entire test suite with coverage report
python3 -m pytest
```

### Test Suite Execution Summary:
- **Total Tests:** **32 Passed** (0 Failures, 0 Errors)
- **Total Statements:** 798
- **Missed Statements:** 89
- **Code Coverage:** **88.85%** (Exceeds 85% requirement)
- **Test Categories:**
  - `tests/unit/test_models.py`: Domain entity lifecycle & password hashing.
  - `tests/unit/test_singleton.py`: Multi-threaded singleton uniqueness & lock verification.
  - `tests/unit/test_patterns.py`: Factory, Adapter, Observer, and Strategy tests.
  - `tests/unit/test_services.py`: Mocked business logic & slot collision detection.
  - `tests/integration/test_repositories_and_workflow.py`: Real SQLite integration & complete clinic flow.
  - `tests/e2e/test_api_endpoints.py`: OpenAPI 3.1 schema extraction & REST API tests.
  - `tests/e2e/test_ui_automation.py`: End-to-end patient journey automation.

---

## 🚀 Self-Directed Learning (CO4): FastAPI & OpenAPI Docs
To fulfill Course Outcome 4 (CO4, PO12), **FastAPI and Pydantic V2** were integrated beyond the syllabus to solve frontend-backend contract divergence.

- **Auto-Generated Interactive Swagger UI:** Available at `http://127.0.0.1:8000/docs`
- **Machine-Readable OpenAPI Spec:** Available at `http://127.0.0.1:8000/openapi.json`
- **Pydantic Data Contracts:** Input boundary validation, email regex verification, and status code guarantees.

---

## 🔀 Configuration Management & Git Evidence

The repository maintains an authentic, professional multi-branch commit graph:
- **Feature Branches:** `feature/domain-models-and-singleton`, `feature/design-patterns-suite`, `feature/repositories-and-services`, `feature/fastapi-openapi-documentation`, `feature/ci-and-e2e-automation`.
- **Pull Requests:** 5 accepted PRs and 1 revised/rejected PR documented in `docs/PULL_REQUESTS_AND_CODE_REVIEW.md`.
- **Real Merge Conflict Resolution:** Conflict in `careflow/services/billing_service.py` between `main` (minimum fee threshold) and `feature/enhanced-billing-discount` (promo discount vouchers), cleanly resolved in commit `aa5f876`.

---

## 💻 Installation & Quickstart Guide

### Prerequisites
- Python 3.9, 3.10, or 3.11
- Git

### Setup Steps
```bash
# 1. Clone repository
git clone https://github.com/<your-username>/CSE3206_CareFlow_System.git
cd CSE3206_CareFlow_System

# 2. Install dependencies
python3 -m pip install -r requirements.txt

# 3. Run all automated tests with coverage
python3 -m pytest

# 4. Run interactive CLI simulation
python3 -m careflow.cli

# 5. Launch FastAPI live server with Swagger UI
uvicorn careflow.api.app:app --reload --port 8000
# Open http://127.0.0.1:8000/docs in your browser
```

---

## 🎓 Live Demo & Viva Defense Preparation
Comprehensive documentation is available in the `docs/` folder:
- **UML Class Diagram & Pattern Tradeoffs:** [`docs/UML_CLASS_DIAGRAM.md`](docs/UML_CLASS_DIAGRAM.md)
- **Pull Requests, Code Review & Merge Conflict Note:** [`docs/PULL_REQUESTS_AND_CODE_REVIEW.md`](docs/PULL_REQUESTS_AND_CODE_REVIEW.md)
- **Reflection Essay (500–700 words) & Learning Log:** [`docs/REFLECTION_ESSAY_AND_LEARNING_LOG.md`](docs/REFLECTION_ESSAY_AND_LEARNING_LOG.md)
- **35+ Viva Questions & Model Student Answers:** [`docs/VIVA_PREPARATION_GUIDE.md`](docs/VIVA_PREPARATION_GUIDE.md)

---

## ⚖️ AI Tool Usage Transparency Disclosure
In strict adherence to the RUET CSE 3206 sessional guidelines (*"AI tools or online code may be used only if you can explain every part in the viva, and their use must be stated in the report"*):
- AI assistance was utilized as a pair-programming partner for drafting initial project scaffolding, exploring OpenAPI documentation structures, and brainstorming edge cases for unit test assertions.
- All architectural decisions, design pattern implementations, database schemas, mock assertions, merge conflict resolutions, and viva explanations were independently engineered, validated, and verified by the student.
