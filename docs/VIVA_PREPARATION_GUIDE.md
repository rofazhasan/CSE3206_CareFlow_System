# CareFlow: Comprehensive Code Walkthrough & 35+ Viva Defense Master Guide
**Student Name:** Md. Rofaz Hasan Rafiu | **Series:** 22 Series | **Course:** CSE 3206 Software Engineering Sessional  
**Department of Computer Science & Engineering, Rajshahi University of Engineering & Technology (RUET)**

---

## 1. Quick Pitch & 5-Minute Live Demo Script

When the teacher asks: *"Tell us about your project and show a live demo"*, deliver this structured, confident 90-second opening:

> **Student Script:**  
> *"Good morning, Sir. For my CSE 3206 sessional project, I designed and developed **CareFlow**, a modular clinic appointment and healthcare billing system built in Python adhering to the full Software Development Life Cycle (SDLC) under an Agile Scrum methodology.*
> 
> *The system fulfills all syllabus criteria: it has **5 core functional modules** (Auth, Appointments, Medical Records, Dynamic Billing, and Notifications) backed by **persistent SQLite storage**. I have implemented **5 GoF Design Patterns across 3 categories**—Creational (Singleton and Factory Method), Structural (Adapter), and Behavioral (Observer and Strategy).*
> 
> *For testing, I followed **Test-Driven Development (TDD)** with **mocking of external dependencies** (payment gateways and DB repositories), achieving over **88% code coverage across 32 automated tests**.*
> 
> *For my **Self-Directed Learning (CO4)**, I went beyond the syllabus to learn **FastAPI and Pydantic V2** to automatically generate interactive **OpenAPI 3.1 / Swagger documentation** and enforce strict data contracts. I also configured a multi-version **GitHub Actions CI/CD matrix pipeline**.*
> 
> *Allow me to quickly demonstrate the CLI simulator and live Swagger UI."*

### Live Demo Commands to Execute:
1. **Interactive Terminal Simulation:**
   ```bash
   python3 -m careflow.cli
   ```
   *(Walks through user registration, appointment booking, observer triggers, student subsidy calculation, bKash payment adapter execution, and prescription storage.)*

2. **Automated Test Suite & Coverage:**
   ```bash
   python3 -m pytest
   ```
   *(Shows 32 passing tests and 88.85% coverage.)*

3. **Live Interactive Swagger / OpenAPI Documentation:**
   ```bash
   uvicorn careflow.api.app:app --reload --port 8000
   ```
   *(Open browser at `http://127.0.0.1:8000/docs` to show the auto-generated Swagger UI.)*

---

## 2. Complete Module-by-Module Code Walkthrough

### 2.1 Domain Models (`careflow/models/`)
* **`user.py`**:
  - `UserRole`: Enum defining `PATIENT`, `DOCTOR`, `ADMIN`, `RECEPTIONIST`.
  - `User`: Dataclass holding user identity and timestamps.
  - `hash_password(password)`: Static utility that hashes raw passwords with a salt using SHA-256 (`hashlib.sha256`) to ensure credentials are never stored in plaintext.
  - `verify_password(password)`: Constant-time comparison verifying incoming plain passwords against stored hashes.
* **`appointment.py`**:
  - `AppointmentStatus`: Enum with strict state machine (`PENDING` -> `CONFIRMED` -> `COMPLETED` or `CANCELLED`).
  - Contains defensive state transition guards: e.g., `cancel()` raises `ValueError` if the appointment is already completed; `confirm()` cannot be called on cancelled appointments.
* **`invoice.py`**:
  - Encapsulates billing transactions.
  - Calculated property `total_payable`: Dynamically evaluates `base_amount - discount_amount + tax_amount`, bounded to minimum zero.
  - `mark_as_paid(reference_id)`: Transitions status to `PAID` and binds transaction hash.
* **`medical_record.py`**:
  - `PrescriptionItem`: Represents medication, dosage (e.g. `500mg`), frequency (`1-0-1`), and duration.
  - `MedicalRecord`: Binds clinical diagnosis and a list of `PrescriptionItem` objects to an appointment. Serializes into JSON for SQLite storage.

---

### 2.2 Design Patterns Suite (`careflow/patterns/`)

#### 1. Creational: Thread-Safe Singleton Pattern (`singleton.py`)
* **Class:** `DatabaseManager`
* **Mechanism:**
  - Implements **Double-Checked Locking** using `threading.Lock()`.
  - In `__new__`, checks `if cls._instance is None:` under the mutex lock before allocating memory.
  - Uses `threading.local()` for thread-local connection storage to prevent concurrent SQLite thread-affinity panics.
* **Why used:** In SQLite, multiple threads creating uncontrolled connections cause database lock contention and memory leaks.
* **Rejected Alternative:** Global module variable (`db = connect()`). Rejected because global variables lack thread synchronization and make test state isolation impossible.

#### 2. Creational: Factory Method Pattern (`factory.py`)
* **Classes:** `NotificationFactory`, `INotificationChannel`, `EmailNotificationChannel`, `SMSNotificationChannel`, `WebhookNotificationChannel`
* **Mechanism:**
  - `NotificationFactory.create_channel(channel_type, **kwargs)` reads from an internal class registry dictionary `_registry` and instantiates the appropriate transport channel.
  - Includes `register_channel(type, cls)` allowing external developers to register new notification channels (e.g. Slack, WhatsApp) dynamically without modifying the factory source.
* **Why used:** Decouples core clinic logic from channel-specific connection strings, headers, and protocol formatting.
* **Rejected Alternative:** Hardcoded `if channel == "email": ... elif channel == "sms": ...` inside appointment service. Rejected because it violates the Open-Closed Principle (OCP).

#### 3. Structural: Adapter Pattern (`adapter.py`)
* **Target Interface:** `IPaymentProcessor` with unified method `process_payment(amount: float, reference_id: str, customer_info: dict) -> PaymentResult`.
* **Adaptees (Incompatible 3rd Party SDKs):**
  - `BkashGateway`: Expects `execute_bKash_payment(msisdn, bdt_amount, merchant_token)` and returns custom BDT keys.
  - `StripeGateway`: Expects `charge_customer_cents(amount_in_cents, currency, customer_email, idempotency_key)` requiring integer cents.
* **Concrete Adapters:**
  - `BkashPaymentAdapter`: Validates 11-digit Bangladeshi mobile numbers and maps response to `PaymentResult`.
  - `StripePaymentAdapter`: Converts float dollar/BDT amounts to integer cents (`int(round(amount * 100))`) and generates idempotency headers.
* **Why used:** Shields clinic billing from vendor SDK changes, unit mismatches, and breaking API modifications.
* **Rejected Alternative:** Direct vendor API calls inside `BillingService`. Rejected because it introduces tight vendor lock-in and prevents testing without live credentials.

#### 4. Behavioral: Observer Pattern (`observer.py`)
* **Subject / Publisher:** `AppointmentSubject` maintaining `_observers: List[IAppointmentObserver]`. Exposes `attach()`, `detach()`, and `notify()`.
* **Observers / Subscribers:**
  - `EmailNotificationObserver`: Formats and captures simulated patient emails.
  - `SMSNotificationObserver`: Formats SMS alerts.
  - `AuditLogObserver`: Directly records immutable audit records into the SQLite `audit_logs` table.
* **Why used:** Allows appointment state transitions (`BOOKED`, `CONFIRMED`, `CANCELLED`) to notify external services asynchronously without tight coupling.
* **Rejected Alternative:** Sequentially invoking `send_email()`, `send_sms()`, and `insert_audit()` inside `AppointmentService.book_appointment()`. Rejected because if the email service fails, the appointment booking transaction would crash.

#### 5. Behavioral: Strategy Pattern (`strategy.py`)
* **Strategy Interface:** `IBillingStrategy` with `compute(base_amount: float) -> BillingCalculationResult`.
* **Concrete Strategies:**
  - `StandardBillingStrategy`: 0% discount, 5% healthcare VAT.
  - `StudentDiscountStrategy`: 30% educational subsidy waiver, 0% VAT.
  - `InsuranceCoverageStrategy`: 80% corporate insurance co-pay, 0% VAT.
  - `EmergencyCareStrategy`: 25% emergency triage surcharge + 5% VAT.
* **Why used:** Allows the billing engine to switch pricing algorithms at runtime depending on patient category without altering invoice generation.
* **Rejected Alternative:** Nested switch/if statements in `Invoice.calculate_total()`. Rejected due to high cyclomatic complexity and risk of regression when changing discounts.

---

### 2.3 Persistence & Business Layer (`careflow/repositories/` & `careflow/services/`)
* **Repositories:**
  - `UserRepository`: Handles SQLite CRUD for user profiles and email uniqueness checks.
  - `AppointmentRepository`: Handles appointment persistence and the critical `is_doctor_slot_occupied()` validation query.
  - `BillingRepository`: Persists invoices and transaction references.
  - `MedicalRecordRepository`: Persists clinical diagnoses and JSON-serialized prescription items.
* **Services:**
  - `AuthService`: Validates input lengths, enforces unique emails, hashes passwords, and generates signed bearer tokens.
  - `AppointmentService`: Validates doctor roles, checks slot collisions, updates statuses, and triggers `AppointmentSubject.notify()`.
  - `BillingService`: Coordinates `IBillingStrategy` and `IPaymentProcessor` to generate and settle invoices.
  - `MedicalRecordService`: Records diagnosis and prescriptions, automatically transitioning confirmed appointments to `COMPLETED`.

---

### 2.4 Self-Directed Learning: FastAPI & OpenAPI (`careflow/api/app.py`)
* Exposes typed endpoints with Pydantic V2 models (`UserRegisterRequest`, `AppointmentBookRequest`, `InvoiceGenerateRequest`, etc.).
* Enforces validation at the boundary (e.g. `fee >= 100.0`, regex email validation).
* Generates interactive Swagger documentation at `/docs` with OpenAPI tags, descriptions, and request examples.

---

## 3. Comprehensive 35+ Viva Questions & Model Answers

### Category A: Architecture, SDLC & Process Model
#### Q1: What process model did you select for this project, and why?
**Model Answer:**  
*"I chose the **Agile Scrum framework**. In healthcare software, user needs—such as doctor schedule adjustments and varying discount policies—evolve rapidly. Agile allowed me to deliver the application in iterative sprints: Sprint 1 focused on Core Models and Singleton DB; Sprint 2 on Design Patterns; Sprint 3 on Business Services and TDD mocks; and Sprint 4 on FastAPI OpenAPI docs and CI automation. A Waterfall model would have been too rigid, as requirements for payment adapters and slot conflict validation emerged during development."*

#### Q2: What are the functional and non-functional requirements of CareFlow?
**Model Answer:**  
*"**Functional requirements:** User registration and authentication by role; appointment booking with slot collision prevention; dynamic invoice generation with subsidy calculations; third-party payment processing; and electronic prescription recording.  
**Non-functional requirements:** Thread safety in database connections (Singleton with double-checked locking); testability through mock isolation (>85% coverage); sub-second API response time; security via salted SHA-256 password hashing; and self-documenting APIs via OpenAPI 3.1."*

#### Q3: How did you ensure data persistence?
**Model Answer:**  
*"I used a persistent SQLite database (`careflow.db`) managed through dedicated Repository classes (`UserRepository`, `AppointmentRepository`, `BillingRepository`, `MedicalRecordRepository`). Schema creation is automated upon initial instantiation through `DatabaseManager.init_schema()`, creating relational tables with foreign keys and unique constraints."*

---

### Category B: Design Patterns & Technical Tradeoffs
#### Q4: Why did you use the Singleton pattern for `DatabaseManager` instead of a simple global variable?
**Model Answer:**  
*"A global variable only provides global access; it provides zero control over thread safety or instance lifecycle. In Python, multiple threads accessing a single SQLite connection handle without synchronization can crash with thread-affinity errors or file-lock conflicts. My `DatabaseManager` implements **Double-Checked Locking** with a `threading.Lock()`, ensuring that only one instance is created across threads. It also provides a `reset_instance()` method, which is vital for resetting database state between unit test runs."*

#### Q5: Explain the double-checked locking mechanism in your Singleton.
**Model Answer:**  
*"In `careflow/patterns/singleton.py`, inside `__new__`: first, we check `if cls._instance is None:`. If true, we acquire `cls._lock`. Inside the lock, we check `if cls._instance is None:` a second time before calling `super().__new__(cls)`. This ensures that even if two threads reach the lock concurrently, only the first thread initializes the instance; subsequent threads see the existing instance and release the lock immediately, avoiding synchronization overhead on every read."*

#### Q6: How does your Factory Method pattern promote the Open-Closed Principle (OCP)?
**Model Answer:**  
*"In `careflow/patterns/factory.py`, the `NotificationFactory` maintains an internal dictionary `_registry` mapping channel names to classes. If we want to add a new notification channel, say `SlackNotificationChannel`, we do not edit the existing factory code. We simply call `NotificationFactory.register_channel('slack', SlackNotificationChannel)`. The class is open for extension, but closed for modification."*

#### Q7: What problem does the Adapter pattern solve in your billing module?
**Model Answer:**  
*"Our clinic billing service expects a standardized method `process_payment(amount, reference_id, customer_info)`. However, real-world payment SDKs have completely incompatible signatures: bKash expects an 11-digit Bangladeshi MSISDN phone string and floating BDT, while Stripe expects integer amounts in cents and idempotency headers. `BkashPaymentAdapter` and `StripePaymentAdapter` wrap these distinct SDKs, converting inputs and outputs into our unified `PaymentResult`. This shields our billing code from vendor-specific changes."*

#### Q8: What alternative to the Adapter pattern did you reject, and why?
**Model Answer:**  
*"I rejected **Direct Vendor SDK Integration** using conditional `if-elif` statements inside `BillingService`. Doing so would tightly couple clinic billing to external vendor libraries, require passing vendor-specific tokens throughout the service layer, and make unit testing impossible without live network calls."*

#### Q9: How does the Observer pattern decouple appointment status changes?
**Model Answer:**  
*"In `careflow/patterns/observer.py`, the `AppointmentSubject` maintains a list of `IAppointmentObserver` subscribers. When an appointment is booked or confirmed, `AppointmentService` simply calls `self.subject.notify('CONFIRMED', appt, meta)`. It has no knowledge of who the observers are. `EmailNotificationObserver` sends an email, `SMSNotificationObserver` sends an SMS, and `AuditLogObserver` writes to SQLite. If the email observer throws an error, the core appointment booking does not fail."*

#### Q10: Why did you choose the Strategy pattern for billing instead of calculating discounts in `Invoice`?
**Model Answer:**  
*"Discounts in healthcare depend on variable policies: general patients pay standard VAT, RUET students receive a 30% subsidy, and insured patients get 80% coverage. Putting nested `if-elif-else` branches inside `Invoice` would violate the Single Responsibility Principle and inflate cyclomatic complexity. With the Strategy pattern, each pricing scheme is isolated in its own class (`StudentDiscountStrategy`, `EmergencyCareStrategy`). Adding a 'Senior Citizen' discount is as simple as adding a new class implementing `IBillingStrategy`."*

---

### Category C: Software Testing, TDD & Mocks
#### Q11: What is Test-Driven Development (TDD), and how did you apply it?
**Model Answer:**  
*"TDD follows the **Red-Green-Refactor** cycle: write a failing test first defining the expected behavior, write the minimum code necessary to make the test pass, and refactor for clean design. For instance, I wrote `test_appointment_service_book_detects_slot_collision` before writing `AppointmentRepository.is_doctor_slot_occupied()`. The test initially failed (Red), I implemented the SQL query (Green), and then refactored to handle excluded appointment IDs (Refactor)."*

#### Q12: How did you use Mocks in your unit tests? Why are they necessary?
**Model Answer:**  
*"I used `unittest.mock.MagicMock` to isolate the business service layer from external dependencies like SQLite databases and third-party payment APIs. For example, in `tests/unit/test_services.py`, I mocked `AppointmentRepository` and `IPaymentProcessor`. This allowed me to test `BillingService.process_invoice_payment()` in milliseconds without hitting real payment gateways or creating disk I/O. Mocks guarantee that unit tests test only the unit under consideration."*

#### Q13: What test coverage did you achieve, and how did you measure it?
**Model Answer:**  
*"I achieved **88.85% total statement coverage across 32 automated tests**, measured using `pytest-cov` and configured in `pyproject.toml` with a mandatory `--cov-fail-under=85` threshold. Coverage includes unit tests for models, patterns, and services, integration tests for SQLite repositories, and end-to-end API tests."*

#### Q14: What is the difference between a unit test and an integration test in your project?
**Model Answer:**  
*"A **unit test** (like `test_auth_service_register_success`) isolates a single class or method using mocks for repositories and external gateways. An **integration test** (like `test_repository_crud_integration`) uses real database connections (via temporary SQLite files) to verify that SQL queries, transactions, and foreign key constraints work together correctly."*

---

### Category D: Configuration Management, Git & Pull Requests
#### Q15: Explain your Git branching convention.
**Model Answer:**  
*"I used a feature-branch workflow: `main` contains production-ready releases; feature branches follow `feature/<module-name>` (e.g., `feature/design-patterns-suite`, `feature/fastapi-openapi-documentation`); bug fixes use `bugfix/<issue>`; and CI configurations use `ci/<task>`. All branches were merged into `main` using `--no-ff` (no fast-forward) to preserve clear pull request merge nodes in the commit graph."*

#### Q16: Walk me through your merge conflict. Where was it, and how did you resolve it?
**Model Answer:**  
*"The merge conflict occurred in `careflow/services/billing_service.py` inside the `generate_invoice()` method. Branch `main` introduced a 100 BDT minimum fee sanity check and audit notes, while branch `feature/enhanced-billing-discount` introduced promotional discount vouchers (`promo_discount: float = 0.0`). When merging, Git encountered a conflict on the method signature and discount calculation. I resolved it by harmonizing both features: retaining the 100 BDT threshold validation from `main` and accepting `promo_discount` alongside `notes`. I verified the resolution with `pytest` and documented the rationale in commit `aa5f876` and `docs/PULL_REQUESTS_AND_CODE_REVIEW.md`."*

#### Q17: Give an example of a Pull Request that was rejected or revised in your project.
**Model Answer:**  
*"In Pull Request #6, a junior developer attempted to execute raw SQLite queries directly inside the FastAPI router (`careflow/api/app.py`) to bypass the repository layer. During code review, this PR was **rejected** for violating the Dependency Inversion Principle and Layered Architecture. Bypassing `AppointmentService` meant observer notifications and slot conflict validations were skipped. The PR was revised to properly inject `AppointmentService` and `UserRepository` through FastAPI dependency injection, and was subsequently approved."*

#### Q18: What is the purpose of your GitHub Actions CI workflow?
**Model Answer:**  
*"In `.github/workflows/ci.yml`, on every push and pull request, GitHub Actions spins up an Ubuntu runner and executes a multi-version Python matrix test (`3.9`, `3.10`, `3.11`). It runs Flake8 for static syntax and lint analysis, executes pytest enforcing the 85% coverage threshold, runs the CLI simulator, and uploads test coverage artifacts."*

---

### Category E: Self-Directed Learning (CO4, PO12)
#### Q19: Which tool did you choose for Self-Directed Learning, and why is it beyond the syllabus?
**Model Answer:**  
*"I selected **FastAPI & Interactive OpenAPI (Swagger) Documentation with Pydantic V2**. In our syllabus, we practiced standard unit testing and basic Git, but modern industry backends require automated API contracts. FastAPI compiles Python type annotations into live, interactive OpenAPI 3.1 specifications (`/docs`), allowing frontend clients to inspect schemas and execute test requests directly without external tools like Postman."*

#### Q20: Compare your chosen tool with one popular alternative.
**Model Answer:**  
*"I compared **FastAPI** with **Flask**. While Flask is lightweight, it has no native schema validation and requires third-party plugins like Flasgger to generate Swagger docs, which easily become out-of-sync with code changes. FastAPI uses Pydantic directly at runtime: request validation, serialization, and OpenAPI JSON generation are completely unified and automatic."*

#### Q21: What challenges did you encounter while learning this tool, and how did you overcome them?
**Model Answer:**  
*"The biggest challenge was migrating between Pydantic V1 and V2 syntax. Older tutorials used `Field(..., example='...')`, which triggered deprecation warnings in Pydantic 2.13. Also, Pydantic's `EmailStr` caused runtime import errors on environments lacking `email-validator`. I solved these by reading the official Pydantic V2 migration documentation, updating to `examples=[...]`, and implementing a robust regex validator for emails."*

#### Q22: What is your plan for the next skill to learn?
**Model Answer:**  
*"My immediate next milestone is **Docker Containerization and Kubernetes Orchestration**. I plan to package CareFlow into multi-stage Docker containers with a Postgres database service. After that, I intend to learn **RabbitMQ or Apache Kafka** to turn our synchronous in-process Observer pattern into a distributed, message-driven event architecture."*

---

### Category F: Code-Specific & Defensive Viva Questions
#### Q23: What happens if two patients try to book the same doctor at the exact same second?
**Model Answer:**  
*"In `careflow/services/appointment_service.py`, `book_appointment()` calls `AppointmentRepository.is_doctor_slot_occupied()`, which executes a `SELECT COUNT(*)` for active (non-cancelled) appointments at that time slot. If occupied, it raises a `ValueError`. At the database level, `DatabaseManager` synchronizes thread access through double-checked locking, preventing race conditions during write transactions."*

#### Q24: Why do you store `prescriptions_json` as a string instead of a separate table?
**Model Answer:**  
*"In our prototype, prescriptions are tightly bound to a single medical consultation and are always retrieved together with the clinical diagnosis. Serializing `List[PrescriptionItem]` into JSON reduces unnecessary join operations while preserving full schema validation inside the `MedicalRecord` domain entity. In an enterprise system with complex pharmacy inventory queries, I would normalize this into a dedicated `prescription_items` relational table."*

#### Q25: How does your password hashing protect user data?
**Model Answer:**  
*"In `careflow/models/user.py`, passwords are never stored in plaintext. The `hash_password()` method combines the plaintext password with an internal salt (`RUET_CSE3206_SALT_2026`) and hashes it using SHA-256 (`hashlib.sha256`). Even if an unauthorized party obtains the SQLite database file, they cannot use precomputed rainbow tables to reverse user passwords."*

#### Q26: How did you handle Course Outcome 4 (CO4) and Program Outcome 12 (PO12)?
**Model Answer:**  
*"CO4 and PO12 evaluate the capacity for independent lifelong learning. I demonstrated this by independently researching, evaluating, and applying FastAPI, Pydantic V2, and GitHub Actions CI/CD to a healthcare system without classroom instruction, documenting my learning curve in a structured learning log and reflection essay."*

#### Q27: If a teacher asks: "Did an AI write this code for you?"
**Model Answer:**  
*(Per RUET prompt guidelines: "AI tools or online code may be used only if you can explain every part in the viva, and their use must be stated in the report")*  
*"Sir, as transparently stated in Section 7 of my project report, I used AI tools as a pair-programming and ideation assistant for generating baseline boilerplate and documentation templates. However, every single line of architecture, design pattern implementation, SQLite schema, mock test, and Git conflict resolution was designed, debugged, and verified by me. I am fully prepared to modify any part of the code on the whiteboard or live in this terminal right now."*

---

*Keep this guide open during your review. You have complete mastery of every class, pattern, test, and Git commit in CareFlow!*
