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

## 4. সহজ বাংলায় সম্পূর্ণ প্রজেক্টের কাজের ফ্লো, আর্কিটেকচার ও ভাইভা প্রস্তুতি (Bangla Master Walkthrough)

ভাইভা বোর্ডে স্যারদের সামনে সহজ ভাষায় আত্মবিশ্বাসের সাথে উপস্থাপন করার জন্য এই অংশে **CareFlow** অ্যাপটি আসলে কী করে, এর শুরু থেকে শেষ পর্যন্ত কাজের ধাপগুলো কী, এবং কোডের ভেতরের জটিল বিষয়গুলো (Design Patterns, TDD, Git, FastAPI) সহজ বাংলায় সুন্দরভাবে বুঝিয়ে দেওয়া হলো।

---

### ৪.১ CareFlow অ্যাপটি আসলে কী এবং কী করে?

**CareFlow** হলো একটি **স্মার্ট ক্লিনিক ম্যানেজমেন্ট এবং হেলথকেয়ার বিলিং সিস্টেম (Smart Clinic Appointment & Healthcare Billing System)**।

বাস্তব জীবনে একটি ডায়াগনস্টিক সেন্টার বা ক্লিনিকে যেসব কাজ হয়, সেগুলোকে সফটওয়্যার আর্কিটেকচার অনুযায়ী অটোমেট করা হয়েছে:
1. **ডাক্তার ও স্টাফদের শিডিউল ম্যানেজমেন্ট:** ডাক্তাররা কখন চেম্বারে বসবেন এবং প্রতি স্লটে রোগী দেখতে পারবেন তা ঠিক করা।
2. **রোগীদের অ্যাপয়েন্টমেন্ট বুকিং:** একই সময়ে দুইজন রোগী যেন একজন ডাক্তারকে বুক না করতে পারে (ডবল বুকিং বা স্লট সংঘর্ষ রোধ)।
3. **স্বয়ংক্রিয় নোটিফিকেশন:** অ্যাপয়েন্টমেন্ট কনফার্ম হলে রোগীকে ইমেইল ও এসএমএস পাঠানো এবং সিস্টেমে অডিট লগ রাখা।
4. **ডায়নামিক বিলিং ও ওয়েভার:** সাধারণ রোগীদের ৫% ভ্যাট যোগ করা, কিন্তু **RUET-এর শিক্ষার্থীদের জন্য ৩০% ছাড় (Student Subsidy)** এবং ইন্স্যুরেন্স থাকলে ৮০% ছাড়ের স্বয়ংক্রিয় হিসাব।
5. **মাল্টি-গেটওয়ে পেমেন্ট:** রোগী চাইলে bKash বা আন্তর্জাতিক কার্ড (Stripe)-এ পেমেন্ট করতে পারবে।
6. **ডিজিটাল প্রেসক্রিপশন:** ডাক্তার রোগী দেখার পর ডিজিটালি প্রেসক্রিপশন লিখবেন এবং তা রোগীর হিস্টরিতে পার্মানেন্টলি সেভ থাকবে।
7. **স্বয়ংক্রিয় এপিআই ও সোয়েগার ডক্স:** ব্রাউজারে `http://127.0.0.1:8000/docs`-এ গেলে যে কেউ ক্লিক করে লাইভ এপিআই টেস্ট করতে পারবে।

---

### ৪.২ অ্যাপটির সম্পূর্ণ কাজের ফ্লো (End-to-End Workflow)

টার্মিনালে `python3 -m careflow.cli` রান করলে ব্যাকগ্রাউন্ডে পুরো সিস্টেমটি ধাপে ধাপে ৬টি কাজ সম্পন্ন করে:

```
[ধাপ ১: ডাটাবেজ চালু (Singleton)]
               │
               ▼
[ধাপ ২: ডক্টর শিডিউল সেট]
               │
               ▼
[ধাপ ৩: রোগী প্রোফাইল তৈরি]
               │
               ▼
[ধাপ ৪: অ্যাপয়েন্টমেন্ট বুকিং (স্লট চেক + Observer SMS/Email)]
               │
               ▼
[ধাপ ৫: ইনভয়েস ও পেমেন্ট (Strategy ৩০% ছাড় + bKash Adapter)]
               │
               ▼
[ধাপ ৬: প্রেসক্রিপশন ও হিস্ট্রি সেভ]
```

#### ধাপ ১: ডাটাবেজ ইনিশিয়ালাইজেশন (Singleton DatabaseManager)
- অ্যাপ চালু হওয়ামাত্র `DatabaseManager` একটি লোকাল SQLite ডাটাবেজ (`careflow.db`) চালু করে।
- **কী হচ্ছে:** এখানে **Singleton Pattern** কাজ করছে। পুরো অ্যাপ্লিকেশনে যত রিকোয়েস্টই আসুক না কেন, ডাটাবেজের কানেকশন থাকবে মাত্র **একটিই**। ফলে মেমোরি নষ্ট হয় না এবং ডেটাবেজে কোনো ফাইল-লক ইস্যু তৈরি হয় না।

#### ধাপ ২: ডাক্তার ও ক্লিনিক স্টাফ রেজিস্ট্রেশন
- সিস্টেমে একজন ডাক্তার (যেমন: *Dr. Ayesha Rahman, কার্ডিওলজিস্ট*) রেজিস্টার করা হয়।
- ডাক্তারের ফি (যেমন: ১,০০০ টাকা) এবং তার চেম্বারের সময় (সকাল ১০:০০টা থেকে ১১:০০টা) নির্ধারণ করা হয়।

#### ধাপ ৩: রোগীর প্রোফাইল তৈরি
- রোগী (যেমন: *Tanvir Ahmed*, স্টুডেন্ট) সিস্টেমে রেজিস্ট্রেশন করে।
- রোগীর প্রোফাইলে তার রোল ঠিক করা হয় (তিনি কি জেনারেল রোগী, নাকি স্টুডেন্ট, নাকি ইন্স্যুরেন্স হোল্ডার)।

#### ধাপ ৪: অ্যাপয়েন্টমেন্ট বুকিং ও এক্সক্লুসিভিটি চেক
- রোগী ডাক্তারের সকাল ১০:০০টার স্লটটি বুক করতে চান।
- **স্লট চেক (Conflict Check):** সিস্টেম আগে ডাটাবেজে গিয়ে চেক করে এই তারিখে এবং এই সময়ে অন্য কেউ ডক্টরকে বুক করে রেখেছে কি না (`is_doctor_slot_occupied`)।
  - যদি স্লটটি ইতিমধ্যে বুক থাকে $\rightarrow$ সিস্টেম সাথে সাথে এরর দিবে (`ValueError: Doctor slot already booked`)।
  - যদি স্লট খালি থাকে $\rightarrow$ অ্যাপয়েন্টমেন্ট স্ট্যাটাস `CONFIRMED` হবে।
- **স্বয়ংক্রিয় নোটিফিকেশন (Observer Pattern):** অ্যাপয়েন্টমেন্ট কনফার্ম হওয়ামাত্রই পেছনের **Observer** স্বয়ংক্রিয়ভাবে ৩টি কাজ একসাথে করে ফেলে:
  1. `EmailNotificationObserver`: রোগীর ইমেইলে কনফার্মেশন পাঠায়।
  2. `SMSNotificationObserver`: রোগীর ফোনে এসএমএস অ্যালার্ট পাঠায়।
  3. `AuditLogObserver`: ডাটাবেজের `audit_logs` টেবিলে টাইমস্ট্যাম্পসহ পার্মানেন্ট রেকর্ড লিখে রাখে।

#### ধাপ ৫: ডায়নামিক ইনভয়েস ও পেমেন্ট প্রসেসিং
- ডাক্তারের ভিজিট ফি ছিল ১,০০০ টাকা।
- **ফি হিসাব (Strategy Pattern):** রোগীর ক্যাটাগরি অনুযায়ী ডায়নামিক অ্যালগরিদম চলে:
  - রোগী যেহেতু একজন শিক্ষার্থী, সিস্টেম সিলেক্ট করে `StudentDiscountStrategy`।
  - ১০০০ টাকার ওপর **৩০% RUET স্টুডেন্ট ওয়েভার** কেটে বিল দাঁড়ায় **৭০০ টাকা**।
  - (যদি সাধারণ রোগী হতো, তবে ৫% ভ্যাট যোগ হয়ে বিল হতো ১০৫০ টাকা)।
- **পেমেন্ট প্রসেসিং (Adapter Pattern):**
  - রোগী বিকাশ (bKash) দিয়ে বিল পে করতে চান।
  - আমাদের সিস্টেমের মেথড হলো `process_payment(amount, reference_id, customer_info)`।
  - কিন্তু বিকাশের নিজস্ব SDK-র নিয়ম ভিন্ন: `execute_bKash_payment(msisdn, bdt_amount)`।
  - আমাদের **BkashPaymentAdapter** মাঝখানে বসে এই রূপান্তরটি করে দেয় এবং বিকাশ থেকে সফল ট্রানজেকশন আইডি (`TRX-BKASH-XXXX`) নিয়ে ইনভয়েসকে `PAID` করে দেয়।

#### ধাপ ৬: ডিজিটাল প্রেসক্রিপশন ও রেকর্ড সংরক্ষণ
- কনসাল্টেশন শেষে ডাক্তার রোগীকে ওষুধ (Medications) ও পরামর্শ (Instructions) দেন।
- এই প্রেসক্রিপশনটি সিস্টেমে ডিজিটাল মেডিকেল রেকর্ড হিসেবে চিরতরে সেভ হয়ে যায়।

---

### ৪.৩ অ্যাপটিতে ব্যবহৃত ৫টি GoF ডিজাইন প্যাটার্ন (সহজ বাস্তব উদাহরণ)

| প্যাটার্ন ও ক্যাটাগরি | অ্যাপের কোন ক্লাসে আছে? | বাস্তব উদাহরণ ও সহজ কাজের ব্যাখ্যা | এটি বাদ দিলে কী সমস্যা হতো? |
| :--- | :--- | :--- | :--- |
| **১. Singleton**<br/>*(Creational)* | `DatabaseManager`<br/>(`patterns/singleton.py`) | একটি ক্লিনিকের ক্যাশ ড্রয়ার যেমন একটাই থাকে, তেমনি পুরো অ্যাপে ডাটাবেজের কানেকশন থাকবে মাত্র একটি। থ্রেড-লক দিয়ে সুরক্ষিত। | বারবার কানেকশন খুললে SQLite ডাটাবেজ ক্র্যাশ করত এবং মেমোরি লিক হতো। |
| **২. Factory Method**<br/>*(Creational)* | `NotificationFactory`<br/>(`patterns/factory.py`) | আপনি শুধু বলবেন "email" অথবা "sms"; ফ্যাক্টরি নিজ দায়িত্বে সঠিক চ্যানেল ক্লাস তৈরি করে দিবে। আপনি জানেনও না SMTP পোর্ট কীভাবে কানেক্ট হয়েছে। | অ্যাপের কোডে বড় বড় `if/else` লিখতে হতো এবং নতুন চ্যানেল (যেমন: WhatsApp) যোগ করতে গেলে মূল কোড ভাঙতে হতো। |
| **৩. Adapter**<br/>*(Structural)* | `BkashPaymentAdapter`<br/>`StripePaymentAdapter`<br/>(`patterns/adapter.py`) | বিদেশে গেলে যেমন বাংলাদেশি প্লাগ ঢোকাতে চার্জার কনভার্টার লাগে, তেমনি বিকাশের ভিন্ন মেথডকে আমাদের সিস্টেমের সাথে মেলানোর কনভার্টার হলো এই অ্যাডাপ্টার। | বিকাশ বা স্ট্রাইপ তাদের API চেঞ্জ করলে পুরো ক্লিনিকের বিলিং কোড নষ্ট হয়ে যেত। |
| **৪. Observer**<br/>*(Behavioral)* | `AppointmentSubject`<br/>(`patterns/observer.py`) | ইউটিউব চ্যানেলে নতুন ভিডিও আসলে যেমন সব সাবস্ক্রাইবারের কাছে বেল নোটিফিকেশন যায়, তেমনি অ্যাপয়েন্টমেন্ট কনফার্ম হলে ইমেইল, এসএমএস আর অডিট লগে খবর চলে যায়। | বুকিং ফাংশনের ভেতরেই ইমেইল আর এসএমএস কোড লিখতে হতো। ইমেইল সার্ভার ডাউন থাকলে পুরো বুকিং ফেইল করত। |
| **৫. Strategy**<br/>*(Behavioral)* | `IBillingStrategy`<br/>`StudentDiscountStrategy`<br/>(`patterns/strategy.py`) | বিভিন্ন যাত্রীর জন্য বাসের টিকিটের নিয়ম যেমন আলাদা (হাফ পাস, ফুল ভাড়া), তেমনি স্টুডেন্টদের ৩০% ছাড় আর জেনারেলদের ৫% ভ্যাট হিসাব করার জন্য আলাদা ক্লাস। | ইনভয়েস ক্লাসে বিশাল `if-elif-else` জটলা হতো, যা OCP নীতি লঙ্ঘন করে। |

---

### ৪.৪ টেস্টিং এবং মকিং (TDD & Mocks) কেন ব্যবহার করেছি?

ভাইভায় স্যাররা যদি জিজ্ঞেস করেন: **"তুমি মকিং কেন করলা? আসল ডাটাবেজ দিয়ে টেস্ট করলা না কেন?"**

- **সহজ উত্তর:**
  > *"স্যার, ইউনিট টেস্টের নিয়ম হলো—যে ক্লাসটিকে টেস্ট করছি, শুধু সেটির লজিক টেস্ট করা।
  > যদি টেস্টের সময় সত্যি সত্যি হার্ডডিস্কের ডেটাবেজে লেখালেখি করি, বা বিকাশের লাইভ সার্ভারে কল দিই, বা সত্যি সত্যি রোগীর ফোনে এসএমএস পাঠাই—তবে:
  > ১. টেস্ট অনেক স্লো হয়ে যাবে।
  > ২. ইন্টারনেটের স্পিড কম থাকলে টেস্ট ফেইল করবে।
  > ৩. সত্যি সত্যি বিকাশে টাকা কাটতে চাইবে।
  > তাই `unittest.mock.MagicMock` ব্যবহার করে আমরা ডেটাবেজ আর বিকাশ গেটওয়েকে নকল (Mock) বানিয়েছি। ফলে আমাদের সবকটি **২৫টি টেস্ট মাত্র ০.৫ সেকেন্ডে সম্পূর্ণ অফলাইনে পাস করে এবং ৮৭.৮৬% স্টেটমেন্ট কভারেজ দেয়**।"*

---

### ৪.৫ সিলেবাসের বাইরে সেলফ-ডিরেক্টেড লার্নিং (FastAPI ও Swagger UI)

আমাদের ল্যাবের নিয়মিত সিলেবাসে ছিল ডিজাইন প্যাটার্ন ও টেস্টিং। কিন্তু বাস্তব সফটওয়্যার ইন্ডাস্ট্রিতে ফ্রন্টএন্ড বা মোবাইল ডেভেলপারদের সাথে কাজ করার জন্য ব্যাকএন্ডের এপিআই ডকুমেন্টেশন দরকার হয়।

- **আমরা কী শিখেছি:** **FastAPI** ফ্রেমওয়ার্ক এবং **Pydantic V2**।
- **এটি কী করে:**
  - পাইথনের টাইপ হিন্টস (`type hints`) দেখে FastAPI নিজে থেকেই ব্রাউজারে একটি ইন্টারেক্টিভ পেজ তৈরি করে (`http://127.0.0.1:8000/docs`)।
  - পোস্টম্যান বা কোনো এক্সটার্নাল টুল ছাড়াই যে কেউ ব্রাউজার থেকেই `POST /api/v1/appointments/book` বাটনে ক্লিক করে সরাসরি টেস্ট করতে পারে।
  - ডেটা ভুল দিলে (যেমন ইমেইল ফরমেট ভুল হলে) Pydantic নিজে থেকেই সুন্দর এরর মেসেজ রিটার্ন করে।

---

### ৪.৬ ভাইভা বোর্ডে যেভাবে বাংলায় গুছিয়ে কথা বলবেন (Model Viva Pitch)

যদি স্যার বলেন: **"তোমার প্রজেক্টটা সংক্ষেপে বাংলায় বলো তো—কী বানিয়েছো এবং কেন বানিয়েছো?"**

আপনি এই ফরম্যাটে শান্তভাবে বলবেন:

> *"স্যার, আমি একটি ক্লিনিক অ্যাপয়েন্টমেন্ট ও হেলথকেয়ার বিলিং সিস্টেম বানিয়েছি—যার নাম **CareFlow**।
> সফটওয়্যারটিতে ৫টি কোর মডিউল আছে: ইউজার অথেন্টিকেশন, ডক্টর স্লট এক্সক্লুসিভিটিসহ অ্যাপয়েন্টমেন্ট বুকিং, ডায়নামিক স্টুডেন্ট ছাড়সহ বিলিং, বিকাশ পেমেন্ট এবং প্রেসক্রিপশন সিস্টেম।
> 
> সফটওয়্যার ইঞ্জিনিয়ারিংয়ের নিয়ম অনুযায়ী আমি ৫টি GoF ডিজাইন প্যাটার্ন ব্যবহার করেছি:
> - ডাটাবেজের সিঙ্গেল থ্রেড-সেফ কানেকশনের জন্য **Singleton**,
> - নোটিফিকেশন চ্যানেল তৈরির জন্য **Factory Method**,
> - বিকাশ পেমেন্টকে আমাদের সিস্টেমের সাথে যুক্ত করার জন্য **Adapter**,
> - অ্যাপয়েন্টমেন্ট বুক হলে স্বয়ংক্রিয়ভাবে এসএমএস ও অডিট লগ পাঠানোর জন্য **Observer**, এবং
> - স্টুডেন্টদের ৩০% ছাড় দেওয়ার ডায়নামিক হিসাবের জন্য **Strategy প্যাটার্ন**।
> 
> পুরো সিস্টেমটি টেস্ট-ড্রিভেন ডেভেলপমেন্ট (TDD) মেনে মকিংয়ের মাধ্যমে টেস্ট করা হয়েছে, যার টেস্ট কভারেজ **৮৭.৮৬%**। আর সিলেবাসের বাইরে গিয়ে সেলফ-ডিরেক্টেড লার্নিং হিসেবে আমি **FastAPI** শিখেছি, যাতে করে অ্যাপটি নিজে নিজেই ব্রাউজারে লাইভ সোয়েগার ইন্টারফেস তৈরি করতে পারে।"*

---

*Keep this guide open during your preparation. You have complete mastery of every class, pattern, test, and Git commit in CareFlow!*  
*For a complete end-to-end workflow explanation and natural speaking script in Bangla, refer to: [`CAREFLOW_WORKFLOW_AND_VIVA_BANGLA.md`](./CAREFLOW_WORKFLOW_AND_VIVA_BANGLA.md).*
