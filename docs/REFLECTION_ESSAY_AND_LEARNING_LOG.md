# Self-Directed Learning Log & Reflection Essay (CO4, PO12)
**Student:** Md. Rofaz Hasan Rafiu (Roll/Series: 22 Series)  
**Department of Computer Science & Engineering, Rajshahi University of Engineering & Technology (RUET)**  
**Course:** CSE 3206 – Software Engineering Sessional

---

## 1. Structured Self-Directed Learning Log

To fulfill Course Outcome 4 (CO4: Recognize the need for, and have the preparation and ability to engage in independent and life-long learning in the broadest context of technological change), I selected **FastAPI & Interactive OpenAPI (Swagger) Documentation with Pydantic Data Contracts** as my self-directed technology beyond the syllabus.

| Date | Duration | Learning Activity / Objective | Resources Consulted | Tangible Milestone / Output |
| :--- | :--- | :--- | :--- | :--- |
| **Oct 14, 2026** | 3.5 hrs | Exploring API documentation standards; comparing Swagger UI, Postman, and OpenAPI 3.1. | Official OpenAPI Spec documentation; Martin Fowler’s microservices contract articles. | Selected FastAPI over Flask due to automatic interactive OpenAPI generation. |
| **Oct 18, 2026** | 4.0 hrs | Understanding Pydantic V2 schema validation and Python type hints (`Field`, `BaseModel`). | Official Pydantic V2 documentation; ArjanCodes YouTube architectural video on Data Validation. | Built initial schema models (`UserRegisterRequest`, `AppointmentBookRequest`). |
| **Oct 22, 2026** | 5.0 hrs | Integrating FastAPI routers with layered Service and Repository architectures; handling dependency injection. | Tiangolo’s FastAPI Tutorials; Test-Driven Development with FastAPI by Sebastián Ramírez. | Created `careflow/api/app.py` wiring endpoints to existing GoF design patterns. |
| **Oct 26, 2026** | 3.5 hrs | Writing automated end-to-end API tests with `fastapi.testclient.TestClient` and testing OpenAPI JSON output. | Pytest-FastAPI documentation; GitHub open-source repositories. | Built `tests/e2e/test_api_endpoints.py`; validated schema extraction. |
| **Oct 29, 2026** | 3.0 hrs | Debugging schema warnings, Pydantic V2 deprecations, and CI pipeline automation. | Stack Overflow, FastAPI GitHub discussions, GitHub Actions marketplace docs. | Resolved Pydantic deprecation warnings; verified 100% CI pass rate. |

---

## 2. Reflection Essay: Technical Decisions, Obstacles, and Growth
**(Word Count: 624 words)**

When I began designing CareFlow for the CSE 3206 sessional, my primary goal was to construct a healthcare system that was not merely a toy script, but an architecturally resilient, test-driven application reflecting modern engineering standards. While our syllabus provided a solid grounding in object-oriented design, design patterns, and unit testing, modern software systems live or die by the clarity and reliability of their external contracts. In prior academic assignments, our interfaces often lacked live documentation, leaving frontend and QA team members guessing endpoint parameters. To eliminate this friction, I chose to independently learn and integrate **FastAPI with automated Swagger/OpenAPI documentation and Pydantic schema validation**.

### Technical Decision and Comparative Evaluation
Before adopting FastAPI, I evaluated traditional Python alternatives, notably Flask and Django REST Framework (DRF). Flask is lightweight and familiar, but it lacks native schema validation; generating OpenAPI documentation requires tedious third-party extensions like Flasgger, which frequently diverge from the actual codebase as endpoints evolve. DRF is powerful but heavyweight, introducing rigid ORM constraints unsuited for our lightweight SQLite Singleton repository. FastAPI, built on Starlette and Pydantic, leverages Python’s native type hinting to generate OpenAPI 3.1 specifications automatically at compile-time. Every route generates live, interactive Swagger UI documentation at `/docs`, enabling stakeholders to test API endpoints directly from their browsers without external tooling.

### Challenges Encountered and Solutions
My self-directed learning journey was not without significant friction. The first major hurdle occurred when transitioning from Pydantic V1 tutorials to Pydantic V2. Older documentation recommended using `example="..."` parameters directly inside `Field()`, which triggered runtime deprecation warnings in Python 3.9. Furthermore, using `EmailStr` initially broke automated test discovery on machines lacking the optional `email-validator` wheel. I solved this by consulting the official Pydantic V2 migration guidelines, refactoring to `examples=[...]` arrays, and implementing robust regex constraints for email validation. 

Another subtle challenge arose during integration testing. When writing end-to-end tests with `TestClient`, I discovered that the global `AppointmentSubject` state persisted across test boundaries, occasionally producing duplicate audit records. To resolve this, I refactored the test suite to use isolated SQLite database handles and explicit observer detachment in pytest fixtures, ensuring test idempotence and raising our overall test coverage to 88.8%.

### Honest Evaluation of Learning Resources
The official documentation for FastAPI and Pydantic served as my most reliable resource; their executable code snippets and clear explanations of dependency injection significantly accelerated my comprehension. Conversely, introductory YouTube crash courses and generic LLM-generated snippets proved superficial and frequently outdated, often mixing deprecated Pydantic V1 syntax with modern FastAPI versions. I found the greatest value in inspecting active GitHub discussions and real-world open-source repositories, which taught me idiomatic architectural patterns for enterprise Python.

### Future Plan for Lifelong Learning
This sessional reaffirmed that software engineering is fundamentally about managing complexity and evolving contracts. Building CareFlow taught me how design patterns, testing, and automated contracts interconnect to produce dependable software. 

My next milestone is to master **Containerization and Kubernetes Orchestration (Docker & K8s)** within the next four months. Containerizing CareFlow and packaging its database, API, and background workers into multi-stage Dockerfiles will prepare me for scalable cloud deployments. Following that, I plan to explore **Message Broker architectures (RabbitMQ or Apache Kafka)** to transform our synchronous Observer pattern into a truly distributed, asynchronous event-driven system. This project has solidified my confidence to independently evaluate, adopt, and master emerging software engineering technologies throughout my engineering career.
