# CareFlow - Configuration Management & Code Review Log
**Course:** CSE 3206 Software Engineering Sessional | **Department of CSE, RUET**  
**Student:** Md. Rofaz Hasan Rafiu (22 Series)

---

## 1. Branching Strategy Convention
The project adheres to a strict Git branching model aligned with industry best practices:
- `main`: Production-ready, verified codebase. Direct pushes are blocked; all code enters via reviewed Pull Requests.
- `feature/<module-name>`: Dedicated feature development branches isolated from main.
- `bugfix/<issue-name>`: Targeted defect correction branches.
- `chore/<task-name>`: Repository configuration, dependencies, and tooling setups.

---

## 2. Pull Request & Code Review Ledger

### Pull Request #1: Core Domain Entities & Thread-Safe Singleton DB Manager
- **Branch:** `feature/domain-models-and-singleton` -> `main`
- **Status:** **ACCEPTED & MERGED**
- **Reviewer:** Peer Reviewer / Lead Developer
- **Review Summary:**
  > *"Excellent implementation of dataclasses for `User`, `Appointment`, `Invoice`, and `MedicalRecord`. The double-checked locking mechanism inside `DatabaseManager.__new__` guarantees thread-safety when connecting to SQLite across concurrent requests. 8 unit tests passing with 98% coverage. Approved for merge."*
- **Merge Commit:** `50869c6`

---

### Pull Request #2: Enterprise Design Patterns Suite (Factory, Adapter, Observer, Strategy)
- **Branch:** `feature/design-patterns-suite` -> `main`
- **Status:** **ACCEPTED & MERGED**
- **Reviewer:** Architecture Reviewer
- **Review Summary:**
  > *"All 4 requested patterns conform strictly to GoF principles. The `BkashPaymentAdapter` cleanly maps the unconventional Bangladeshi MSISDN and BDT float requirements to the unified `IPaymentProcessor` interface. The `AppointmentSubject` properly detaches observers without side-effects. 17 unit tests verified. Approved."*
- **Merge Commit:** `3c8beda`

---

### Pull Request #3: Repositories, Business Logic Services, and TDD Mock Suite
- **Branch:** `feature/repositories-and-services` -> `main`
- **Status:** **ACCEPTED & MERGED**
- **Reviewer:** QA & Testing Lead
- **Review Summary:**
  > *"Extensive use of `unittest.mock.MagicMock` to isolate database reads and payment processing from the service layer. Slot collision guard works flawlessly in `AppointmentService`. Integration tests confirm full transaction lifecycle in SQLite. Approved."*
- **Merge Commit:** `fbf27b1`

---

### Pull Request #4: Self-Directed Learning Tool - FastAPI REST API & OpenAPI/Swagger UI
- **Branch:** `feature/fastapi-openapi-documentation` -> `main`
- **Status:** **ACCEPTED & MERGED**
- **Reviewer:** API Architect
- **Review Summary:**
  > *"Adoption of FastAPI and Pydantic V2 schemas fulfills the self-directed learning objective (CO4). Auto-generation of OpenAPI 3.1.0 interactive Swagger UI at `/docs` simplifies client consumption. E2E tests with `fastapi.testclient.TestClient` pass with high coverage. Approved."*
- **Merge Commit:** `9c11874`

---

### Pull Request #5: Multi-Version GitHub Actions CI Matrix & E2E Workflow Automation
- **Branch:** `feature/ci-and-e2e-automation` -> `main`
- **Status:** **ACCEPTED & MERGED**
- **Reviewer:** DevOps Engineer
- **Review Summary:**
  > *"GitHub Actions `.github/workflows/ci.yml` properly executes multi-python matrix builds (3.9, 3.10, 3.11), enforces Flake8 linting, and validates test coverage (>85%). The E2E patient journey test runs synchronously. Approved."*
- **Merge Commit:** `41320a6`

---

### Pull Request #6: Direct Database Query Injection in API Routes (REVISED / REJECTED PR)
- **Branch:** `feature/direct-db-query-optimization` -> `main`
- **Status:** **REJECTED (REVISION REQUIRED) -> RE-REVIEWED & ACCEPTED AS REVISED**
- **Author:** Junior Developer
- **Reviewer Comment (REJECTION):**
  > ❌ **CRITICAL ARCHITECTURAL DEFECT (REJECTED):**
  > *"This Pull Request proposes executing raw SQLite `cursor.execute()` statements directly inside `careflow/api/app.py` under the pretext of 'optimizing query speed'. This directly violates the **Dependency Inversion Principle (DIP)** and breaks the **Layered Architecture** established in CSE 3206. Bypassing the `AppointmentRepository` and `AppointmentService` causes three severe issues:
  > 1. The `AppointmentSubject` is bypassed, meaning patients receive no email/SMS and no audit log is written.
  > 2. Slot collision detection is skipped, allowing double bookings.
  > 3. Unit tests cannot mock database dependencies in the API layer.
  > 
  > **Action Required:** Remove all direct SQL queries from the API router. Route all booking requests through `AppointmentService.book_appointment()`. PR is rejected until amended."*

- **Revision Action Taken:**
  The PR author reverted all direct SQL calls from the API router, properly injected `AppointmentService` and `UserRepository` through FastAPI dependency injection, and added test cases asserting that Observers fire when an appointment is booked via API.
- **Final Re-Review:**
  > ✅ *"Revision verified. Direct queries removed. Clean separation of concerns restored. Approved."*

---

## 3. Merge Conflict Scenario & Step-by-Step Resolution Note

### The Scenario:
A real Git merge conflict was triggered on `careflow/services/billing_service.py` during concurrent development:
1. **Branch `main` (`ff570b5`)**: A safety guard was merged enforcing a minimum consultation fee threshold (`if appt.fee < 100.0: raise ValueError(...)`) and adding optional audit notes.
2. **Branch `feature/enhanced-billing-discount` (`e12477b`)**: Developed in parallel to introduce promotional discount vouchers (`promo_discount: float = 0.0`) in `generate_invoice()`.
3. **Merge Attempt**: Executing `git merge feature/enhanced-billing-discount` caused a content conflict on lines 27–42 of `billing_service.py`:
   ```
   Auto-merging careflow/services/billing_service.py
   CONFLICT (content): Merge conflict in careflow/services/billing_service.py
   Automatic merge failed; fix conflicts and then commit the result.
   ```

### Resolution Walkthrough:
1. **Conflict Inspection**: Evaluated conflicting markers using `git diff`:
   - `<<<<<<< HEAD` contained the 100 BDT minimum fee sanity check and `notes` argument.
   - `>>>>>>> feature/enhanced-billing-discount` contained the `promo_discount` argument and voucher calculation.
2. **Harmonization Strategy**:
   Neither feature should be discarded. The resolution combines both signatures:
   ```python
   def generate_invoice(
       self,
       appointment_id: str,
       strategy: Optional[IBillingStrategy] = None,
       promo_discount: float = 0.0,
       notes: str = "",
   ) -> Invoice:
       # Retained 100 BDT minimum fee check from main
       if appt.fee < 100.0:
           raise ValueError("Base consultation fee cannot be below clinic minimum 100 BDT.")
       ...
       # Retained promo_discount calculation from feature branch
       total_discount = min(appt.fee, calc.discount_amount + promo_discount)
   ```
3. **Verification**: Executed `pytest` across all 32 test cases; all assertions passed with 88.8% code coverage.
4. **Commit**: Staged with `git add` and committed with detailed conflict rationale in commit `aa5f876`.

