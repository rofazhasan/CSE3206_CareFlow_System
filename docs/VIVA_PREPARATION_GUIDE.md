# CareFlow: Complete Code Walkthrough & 35+ Viva Defense Master Guide
**Student Name:** Md. Rofaz Hasan Rafiu | **Series:** 22 Series | **Course:** CSE 3206 Software Engineering Sessional  
**Department of Computer Science & Engineering, Rajshahi University of Engineering & Technology (RUET)**

---

## 1. Quick Pitch & 5-Minute Live Demo Script

When the teacher asks: *"Tell us about your project and show a live demo"*, deliver this calm, natural, and confident 60–90 second answer:

> **Student Voice:**  
> *"Good morning, Sir. For my CSE 3206 sessional project, I built **CareFlow**, a clinic appointment and billing system designed using the full Software Development Life Cycle under an **Agile Scrum** process.*
> 
> *The system has **5 core functional modules**: User Authentication (Doctor, Patient, Staff), Appointment Scheduling with doctor slot exclusivity, Electronic Prescriptions, Dynamic Invoicing with healthcare discounts, and Event-Driven Notifications—all backed by persistent **SQLite database storage**.*
> 
> *To satisfy the design pattern requirement, I implemented **5 GoF Design Patterns across 3 categories**:
> 1. **Singleton (Creational)**: Thread-safe `DatabaseManager` ensuring one shared SQLite connection.
> 2. **Factory Method (Creational)**: `NotificationFactory` creating Email, SMS, or Webhook dispatchers.
> 3. **Adapter (Structural)**: `BkashPaymentAdapter` adapting third-party payment APIs to our unified billing system.
> 4. **Observer (Behavioral)**: `AppointmentSubject` automatically notifying Email, SMS, and SQLite audit loggers on appointment changes.
> 5. **Strategy (Behavioral)**: `IBillingStrategy` dynamically computing Standard 5% VAT, RUET Student 30% subsidy, and Insurance discounts.
> 
> *For testing, I practiced **Test-Driven Development (TDD)** using `unittest.mock` to isolate the database and payment gateways, achieving **87.86% statement coverage across 25 automated tests**.*
> 
> *For **Self-Directed Learning (CO4)**, I learned **FastAPI and Pydantic V2** to automatically generate interactive **OpenAPI 3.1 / Swagger documentation** at `/docs`, and configured a **GitHub Actions CI/CD pipeline**.*
> 
> *Let me quickly run the CLI simulator and show you the tests."*

---

### 3 Commands for Live Demo:
1. **Run the 20-Second Complete System Simulation:**
   ```bash
   python3 -m careflow.cli
   ```
   *(Shows user registration, appointment booking, observer email/SMS, 30% student discount calculation, bKash payment adapter, and prescription creation.)*

2. **Run Automated Test Suite & Coverage:**
   ```bash
   python3 -m pytest
   ```
   *(Shows 25 passing tests and 87.86% statement coverage.)*

3. **Show Interactive Swagger API in Browser (Optional / If Asked):**
   ```bash
   uvicorn careflow.api.app:app --reload --port 8000
   ```
   *(Open `http://127.0.0.1:8000/docs` to show auto-generated interactive documentation.)*

---

## 2. Simple, Clear Explanation of Every Design Pattern

If the teacher points to any pattern, here is the exact, natural way to explain it:

### 1. Singleton Pattern (`careflow/patterns/singleton.py`)
- **How it works:**
  *"Sir, in Python, `__new__` controls object creation. Inside `__new__`, we check `if cls._instance is None:`. If it is None, we connect to SQLite and store the instance. On subsequent calls, it simply returns the already created instance. We also use a mutex lock (`threading.Lock()`) so multiple concurrent requests don't accidentally create two instances."*
- **Why we used it:**
  *"In SQLite, having multiple uncontrolled connections across threads causes database locks and memory leaks. The Singleton guarantees one synchronized connection handle."*
- **Rejected alternative:**
  *"A global variable like `db = connect()`. Rejected because global variables pollute the namespace and make it hard to reset the database between unit test runs."*

### 2. Factory Method Pattern (`careflow/patterns/factory.py`)
- **How it works:**
  *"Sir, the `NotificationFactory.create_channel('email')` returns an `EmailNotificationChannel`, while `'sms'` returns `SMSNotificationChannel`. The calling service just asks for a channel by name and calls `send()`, without caring how SMTP or SMS gateways are constructed."*
- **Why we used it:**
  *"It adheres to the Open-Closed Principle (OCP). If we want to add WhatsApp notifications in the future, we just create a `WhatsAppChannel` and register it with `register_channel()`—we don't modify existing appointment code."*
- **Rejected alternative:**
  *"Hardcoded `if channel == 'email': ... elif channel == 'sms': ...` inside the appointment service, which would violate OCP."*

### 3. Adapter Pattern (`careflow/patterns/adapter.py`)
- **How it works:**
  *"Sir, our clinic expects a clean interface: `process_payment(amount, reference_id, customer_info)`. But real-world payment SDKs have completely different methods. For example, `BkashGateway` has `execute_bKash_payment(msisdn, bdt_amount)`. Our `BkashPaymentAdapter` implements our interface, takes our parameters, formats the Bangladeshi phone number, and calls the bKash SDK behind the scenes."*
- **Why we used it:**
  *"It protects our clinic billing from third-party API changes. If bKash or Stripe changes their method names, we only update the adapter, not our clinic invoices."*
- **Rejected alternative:**
  *"Calling bKash or Stripe SDK methods directly inside `BillingService`. Rejected because it creates tight vendor lock-in and makes unit testing impossible without live merchant credentials."*

### 4. Observer Pattern (`careflow/patterns/observer.py`)
- **How it works:**
  *"Sir, `AppointmentSubject` holds a list of observers (`observers = []`). When an appointment is booked or confirmed, we call `subject.notify('CONFIRMED', appt, metadata)`. The subject loops through all attached observers: `EmailNotificationObserver` sends an email, `SMSNotificationObserver` sends an SMS, and `AuditLogObserver` saves an immutable audit log entry into SQLite."*
- **Why we used it:**
  *"It ensures loose coupling. The appointment booking logic doesn't need to know anything about email servers or SMS gateways. If the email observer throws an error, the core appointment booking still succeeds."*
- **Rejected alternative:**
  *"Calling `send_email()`, `send_sms()`, and `insert_audit()` sequentially inside `book_appointment()`. Rejected because it violates the Single Responsibility Principle (SRP) and creates high coupling."*

### 5. Strategy Pattern (`careflow/patterns/strategy.py`)
- **How it works:**
  *"Sir, `IBillingStrategy` defines a method `compute(base_amount)`. Each pricing policy is its own class: `StandardBillingStrategy` adds 5% VAT, `StudentDiscountStrategy` deducts a 30% RUET student subsidy, and `InsuranceCoverageStrategy` deducts 80% co-pay. The `BillingService` simply calls `strategy.compute(fee)` dynamically."*
- **Why we used it:**
  *"Healthcare billing schemes change frequently. By isolating each algorithm into a strategy class, we can add new discount schemes (like Senior Citizen discount) without touching the invoice class."*
- **Rejected alternative:**
  *"Writing a giant `if/elif/else` tree inside `Invoice.calculate_total()`. Rejected because it inflates cyclomatic complexity and increases bug risk."*

---

## 3. Top 35+ Categorized Viva Questions & Model Student Answers

### Category A: Software Engineering & Process Models
#### Q1: Which process model did you follow and why?
**Answer:** *"I chose Agile Scrum with 4 weekly sprints. Clinic software has evolving requirements—such as doctor slot availability rules and payment gateway parameters—that are uncovered through testing. Agile allowed me to deliver working software iteratively under the safety of our automated unit tests. Waterfall was rejected because it assumes static requirements and delays integration testing until the very end."*

#### Q2: What are your functional and non-functional requirements?
**Answer:** *"Functional: User registration with roles, appointment booking with doctor conflict checking, dynamic billing with student/insurance discounts, payment execution via bKash/Stripe adapters, and prescription records. Non-functional: Thread-safe SQLite access via Singleton, fast deterministic unit tests (&lt;0.5s) using mocks, password security with salted SHA-256, and interactive API documentation via OpenAPI."*

#### Q3: How did you implement data persistence?
**Answer:** *"I used a local SQLite database (`careflow.db`) managed through dedicated Repository classes (`UserRepository`, `AppointmentRepository`, `BillingRepository`, `MedicalRecordRepository`). Tables are automatically initialized upon startup using `DatabaseManager.init_database()`."*

---

### Category B: Testing, TDD & Mocking
#### Q4: What is Test-Driven Development (TDD) and how did you use it?
**Answer:** *"TDD follows Red-Green-Refactor: write a failing test first, write the simplest code to make it pass, and then refactor. For example, I wrote `test_appointment_service_slot_collision` asserting that duplicate bookings raise a `ValueError` before writing the `is_doctor_slot_occupied` query in `AppointmentRepository`."*

#### Q5: Why did you use Mocks? How do they work?
**Answer:** *"Mocks isolate the class under test from external dependencies like real SQLite files or real banking networks. Using `unittest.mock.MagicMock`, I simulated repository returns and payment gateway results. This ensures our 25 unit tests run in less than 0.5 seconds without needing internet access or real bKash merchant accounts."*

#### Q6: What is your test coverage and how did you measure it?
**Answer:** *"I achieved **87.86% total statement coverage across 25 tests**, measured using `pytest-cov` with a strict `--cov-fail-under=85` rule in `pyproject.toml`."*

---

### Category C: Configuration Management & Git
#### Q7: Explain your Git branching strategy.
**Answer:** *"I used a feature-branch workflow: `main` contains production code; features were built on dedicated branches (`feature/design-patterns-suite`, `feature/fastapi-openapi-documentation`, etc.); and all changes were merged into `main` via Pull Requests using `--no-ff` to preserve clear merge commits."*

#### Q8: Walk me through your merge conflict. How did you resolve it?
**Answer:** *"The conflict occurred in `careflow/services/billing_service.py` in the `generate_invoice()` method. Branch `main` introduced a 100 BDT minimum fee sanity check and audit notes, while branch `feature/enhanced-billing-discount` introduced promotional vouchers (`promo_discount`). When merging, Git stopped with a conflict. I resolved it by keeping both features: accepting `promo_discount` alongside `notes` while preserving the 100 BDT validation check. I verified it with `pytest` and committed it in merge commit `aa5f876`."*

#### Q9: Can you mention a Pull Request that was rejected or revised?
**Answer:** *"Yes, PR #6 was submitted with raw SQLite queries directly inside the API router. The reviewer rejected it because bypassing `AppointmentService` broke our layered architecture, skipped doctor conflict validation, and prevented observer notifications from firing. It was revised to properly inject `AppointmentService` before merging."*

---

### Category D: Self-Directed Learning (CO4, PO12)
#### Q10: What did you choose for your Self-Directed Learning beyond the syllabus?
**Answer:** *"I chose **FastAPI with Interactive OpenAPI (Swagger) Documentation and Pydantic V2**. In the sessional, we learned standard testing, but modern industry backends require automated API contracts. FastAPI uses Python type hints to auto-generate an interactive Swagger UI at `/docs`, allowing frontend developers to test endpoints directly in the browser."*

#### Q11: How does FastAPI compare with Flask?
**Answer:** *"Flask is lightweight, but it lacks built-in data validation and requires extra third-party libraries like Flasgger to generate documentation, which easily gets out-of-sync. FastAPI unifies validation, serialization, and interactive OpenAPI documentation automatically at runtime."*

#### Q12: What was the hardest challenge you faced while learning this tool?
**Answer:** *"Migrating between Pydantic V1 and V2 syntax. Older tutorials used `Field(..., example='...')`, which caused deprecation warnings in Pydantic 2.13. Also, Pydantic's `EmailStr` required an extra external package. I solved this by reading official Pydantic V2 migration documentation and using standard string regex validation."*

#### Q13: What is your plan for the next skill to learn?
**Answer:** *"My next goal is **Docker Containerization and Kubernetes Orchestration** over the next 4 months to package CareFlow into scalable containers, followed by **RabbitMQ or Apache Kafka** to make our Observer pattern work across distributed servers."*

---

### Category E: Tough / Defensive Questions
#### Q14: "Why not just use simple if-else statements instead of design patterns?"
**Answer:** *"If-else is easy for a tiny script with 2 options, but it violates the Open-Closed Principle and inflates cyclomatic complexity. In a clinic with evolving government taxes, student subsidies, and insurance co-pays, putting if-else in the invoice class means every new discount policy risks breaking existing billing logic. The Strategy pattern isolates each calculation cleanly."*

#### Q15: "What happens if two patients book the same doctor at the same slot simultaneously?"
**Answer:** *"The `is_doctor_slot_occupied` query in `AppointmentRepository` checks for active appointments at that time slot and blocks the duplicate with a `ValueError`. At the database level, `DatabaseManager` synchronizes thread access, preventing race conditions."*

#### Q16: "Did an AI write this code for you?"
**Answer:** *(Transparent and honest per RUET prompt guidelines)*  
*"Sir, as disclosed in Section 6 of my report, I used AI as a pair-programming assistant for initial brainstorming and boilerplate templates. However, every design pattern, database query, mock test, and Git conflict resolution was understood, verified, and debugged by me. I am 100% prepared to write or modify any part of this code right now on the board or in terminal."*

---

*Keep this guide open during your preparation. You have complete mastery of every class, pattern, test, and Git commit in CareFlow!*
