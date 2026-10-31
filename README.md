# CareFlow - Smart Clinic Appointment & Billing System
**RUET CSE 3206 - Software Engineering Sessional Project**
**Course Outcome:** CO4, PO12 | **Student:** Md. Rofaz Hasan Rafiu (22 Series)

---

## 📌 Project Overview
CareFlow is a modular, extensible, and enterprise-ready Clinic Management and Healthcare Billing application developed adhering to the complete Software Development Life Cycle (SDLC) using the Agile Scrum framework.

The system encapsulates appointment scheduling, medical records management, polymorphic billing with dynamic discounts, multi-channel event notifications, and persistent SQLite storage.

### 🌟 Key Highlights
- **5 Core Functional Modules**: Authentication & Roles, Appointment Scheduling, Medical Consultations & Prescriptions, Dynamic Billing & Invoicing, and Event-Driven Notifications.
- **Enterprise Design Patterns**:
  - **Singleton**: Thread-safe `DatabaseManager` connection pool.
  - **Factory Method**: Decoupled `NotificationFactory` for multi-channel dispatch.
  - **Adapter Pattern**: Structural integration of third-party payment gateways (bKash & Stripe).
  - **Observer Pattern**: Loose coupling of clinic state changes with SMS/Email/Audit observers.
  - **Strategy Pattern**: Interchangeable fee computation algorithms (Standard, Insurance Waiver, RUET Student Subsidy).
- **Test-Driven Development (TDD)**: Comprehensive unit tests with mocks for external dependencies (>90% test coverage).
- **Self-Directed Learning (Beyond Syllabus)**: FastAPI RESTful architecture with automated interactive Swagger / OpenAPI documentation & Pydantic data contract validation.
- **CI/CD Automation**: GitHub Actions pipeline for automated static analysis, test execution, and coverage thresholds.
