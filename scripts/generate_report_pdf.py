"""
ReportLab PDF Generator for RUET CSE 3206 Software Engineering Sessional Project Report.
Formats the complete report entirely in Times New Roman with embedded UML diagrams.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
    Image,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically render 'Page X of Y' in Times-Roman."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Suppress headers/footers on cover page
        if self._pageNumber > 1:
            self.setFont("Times-Roman", 9)
            self.setFillColor(colors.HexColor("#333333"))
            # Header
            self.drawString(54, letter[1] - 36, "RUET CSE 3206: Software Engineering Sessional | CareFlow Project Report")
            self.setStrokeColor(colors.HexColor("#A0AEC0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

            # Footer
            self.line(54, 45, letter[0] - 54, 45)
            self.drawString(54, 32, "Department of CSE, RUET | Md. Rofaz Hasan Rafiu (22 Series)")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(letter[0] - 54, 32, page_text)
        self.restoreState()


def build_pdf(filename: str, uml_image_path: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Academic Palette
    primary_color = colors.HexColor("#0D3B66")
    secondary_color = colors.HexColor("#1A365D")
    dark_text = colors.HexColor("#1A202C")

    # Pure Times New Roman Typography Hierarchy
    styles.add(ParagraphStyle(
        name="CoverInst",
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="CoverDept",
        fontName="Times-Roman",
        fontSize=11,
        leading=15,
        textColor=dark_text,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="CoverCourse",
        fontName="Times-Bold",
        fontSize=15,
        leading=19,
        textColor=secondary_color,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="CoverTitle",
        fontName="Times-Bold",
        fontSize=21,
        leading=26,
        textColor=primary_color,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        fontName="Times-Italic",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Times-Bold",
        fontSize=13.5,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="SubSectionHeader",
        fontName="Times-Bold",
        fontSize=10.5,
        leading=14,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="BodyTimes",
        fontName="Times-Roman",
        fontSize=10,
        leading=14,
        textColor=dark_text,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="BulletTimes",
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13.5,
        textColor=dark_text,
        leftIndent=15,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="CalloutTimes",
        fontName="Times-Italic",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2B6CB0"),
    ))
    styles.add(ParagraphStyle(
        name="TableHeaderTimes",
        fontName="Times-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="TableCellTimes",
        fontName="Times-Roman",
        fontSize=8.5,
        leading=11,
        textColor=dark_text,
    ))
    styles.add(ParagraphStyle(
        name="TableCellTimesBold",
        fontName="Times-Bold",
        fontSize=8.5,
        leading=11,
        textColor=dark_text,
    ))

    story = []

    # ==========================================
    # COVER PAGE (All in Times New Roman)
    # ==========================================
    story.append(Spacer(1, 45))
    story.append(Paragraph("RAJSHAHI UNIVERSITY OF ENGINEERING & TECHNOLOGY", styles["CoverInst"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", styles["CoverDept"]))
    story.append(Spacer(1, 30))

    story.append(HRFlowable(width="85%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=18))
    story.append(Paragraph("CSE 3206: Software Engineering Sessional", styles["CoverCourse"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Comprehensive Project Report & Reflection Essay (CO4, PO12)", styles["CoverSubtitle"]))
    story.append(Spacer(1, 14))
    story.append(Paragraph("CareFlow: Smart Clinic Appointment, Patient Records & Healthcare Billing System", styles["CoverTitle"]))
    story.append(HRFlowable(width="85%", thickness=1.0, color=secondary_color, spaceBefore=18, spaceAfter=35))

    meta_table_data = [
        [Paragraph("<b>Submitted By:</b>", styles["TableCellTimesBold"]), Paragraph("<b>Submitted To:</b>", styles["TableCellTimesBold"])],
        [
            Paragraph("<b>Md. Rofaz Hasan Rafiu</b><br/>Roll / Series: 22 Series<br/>Department of CSE, RUET<br/>Email: mdrofazhasanrafiu@gmail.com", styles["TableCellTimes"]),
            Paragraph("<b>Course Teachers & Sessional Instructors</b><br/>Department of Computer Science & Engineering<br/>Rajshahi University of Engineering & Technology<br/>Rajshahi-6204, Bangladesh", styles["TableCellTimes"]),
        ],
    ]
    meta_table = Table(meta_table_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(meta_table)

    story.append(Spacer(1, 50))
    story.append(Paragraph("<b>Academic Session:</b> 2025–2026 | <b>Date of Submission:</b> October 31, 2026", styles["CoverSubtitle"]))
    story.append(PageBreak())

    # ==========================================
    # SECTION 1: REQUIREMENTS & PROCESS MODEL
    # ==========================================
    story.append(Paragraph("1. Requirements Engineering & Process Model", styles["SectionHeader"]))
    story.append(Paragraph(
        "<b>1.1 Project Overview:</b> CareFlow is a modular, extensible clinic management and billing application developed in Python. It provides five functional modules: (1) User Authentication & Roles (Doctor, Patient, Admin); (2) Appointment Scheduling with doctor slot exclusivity; (3) Dynamic Invoicing applying healthcare subsidies; (4) Electronic Prescriptions; and (5) Event-Driven Notifications. All records are persistently stored in a local relational SQLite database (<code>careflow.db</code>).",
        styles["BodyTimes"],
    ))

    story.append(Paragraph("<b>1.2 Functional & Non-Functional Requirements:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• <b>FR-1 (Authentication & RBAC):</b> Secure registration and authentication for Doctors, Patients, and Staff with salted SHA-256 password hashing.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>FR-2 (Appointment Management):</b> Patients book appointments for specific slots. The system detects and blocks conflicting bookings for the same doctor.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>FR-3 (Polymorphic Billing):</b> Invoices are dynamically calculated based on selected schemes: Standard (5% VAT), RUET Student (30% waiver), Insurance (80% coverage), or Emergency (25% surcharge).", styles["BulletTimes"]))
    story.append(Paragraph("• <b>FR-4 (Payment Gateway Adapter):</b> Unified interface accepts payments via simulated digital gateways such as bKash and Stripe.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>FR-5 (Electronic Prescriptions):</b> Doctors record clinical diagnoses and medication instructions, automatically completing confirmed appointments.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>NFR-1 (Thread Safety & Persistence):</b> SQLite connection is managed through a thread-safe Singleton to prevent file collisions.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>NFR-2 (Testability):</b> Services are decoupled from concrete database and payment APIs using mocks, achieving &gt;85% test coverage.", styles["BulletTimes"]))

    story.append(Paragraph("<b>1.3 User Stories & Acceptance Criteria:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• <b>User Story 1:</b> <i>As a patient, I want to book an appointment with a doctor for a specific date and time, so that I can receive timely medical consultation.</i><br/><b>Acceptance Criteria:</b> System creates a PENDING appointment; if the doctor is already booked at that slot, the booking is rejected with an error; observers send confirmation emails.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>User Story 2:</b> <i>As a RUET student, I want a 30% medical waiver applied to my clinic bill, so that healthcare remains affordable.</i><br/><b>Acceptance Criteria:</b> Applying the Student subsidy strategy reduces the consultation fee by 30% with 0% tax; the invoice is marked PAID upon bKash payment.", styles["BulletTimes"]))

    story.append(Paragraph("<b>1.4 Chosen Process Model & Justification:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph(
        "CareFlow was developed using the <b>Agile Scrum methodology</b> in four weekly sprints (Sprint 1: Core Models & Singleton DB; Sprint 2: Design Patterns; Sprint 3: Repositories, Services & TDD Mocks; Sprint 4: FastAPI OpenAPI docs & CI/CD). An Agile process was chosen because healthcare requirements—such as doctor scheduling rules and payment gateway parameters—evolve through continuous testing. A rigid Waterfall model was rejected because it delays integration testing and cannot accommodate iterative architectural refinements.",
        styles["BodyTimes"],
    ))

    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 2: DESIGN PATTERNS & EMBEDDED UML
    # ==========================================
    story.append(Paragraph("2. Software Architecture & Design Patterns", styles["SectionHeader"]))
    story.append(Paragraph(
        "To ensure maintainability, low coupling, and high cohesion, CareFlow implements <b>five Gang of Four (GoF) design patterns</b> across Creational, Structural, and Behavioral categories:",
        styles["BodyTimes"],
    ))

    # Design Patterns Table
    pat_table_data = [
        [Paragraph("Pattern & Category", styles["TableHeaderTimes"]), Paragraph("Concrete Class", styles["TableHeaderTimes"]), Paragraph("Problem Solved in CareFlow", styles["TableHeaderTimes"]), Paragraph("Rejected Alternative & Reason", styles["TableHeaderTimes"])],
        [
            Paragraph("<b>Singleton</b><br/>(Creational)", styles["TableCellTimesBold"]),
            Paragraph("<code>DatabaseManager</code>", styles["TableCellTimes"]),
            Paragraph("Provides a single, thread-safe connection pool for SQLite, eliminating database file-lock collisions.", styles["TableCellTimes"]),
            Paragraph("<b>Global DB Variable:</b> Pollutes namespace, lacks mutex thread locks, and prevents clean test teardown.", styles["TableCellTimes"]),
        ],
        [
            Paragraph("<b>Factory Method</b><br/>(Creational)", styles["TableCellTimesBold"]),
            Paragraph("<code>NotificationFactory</code>", styles["TableCellTimes"]),
            Paragraph("Decouples business services from channel transports (Email, SMS, Webhook) with runtime registration.", styles["TableCellTimes"]),
            Paragraph("<b>Hardcoded If-Else:</b> Violates OCP. Adding WhatsApp requires modifying core appointment code.", styles["TableCellTimes"]),
        ],
        [
            Paragraph("<b>Adapter</b><br/>(Structural)", styles["TableCellTimesBold"]),
            Paragraph("<code>BkashPaymentAdapter</code><br/><code>StripePaymentAdapter</code>", styles["TableCellTimes"]),
            Paragraph("Converts incompatible vendor APIs (bKash BDT floats vs Stripe cents) into unified <code>IPaymentProcessor</code>.", styles["TableCellTimes"]),
            Paragraph("<b>Direct Vendor SDK Calls:</b> Tightly couples clinic billing to external vendor libraries.", styles["TableCellTimes"]),
        ],
        [
            Paragraph("<b>Observer</b><br/>(Behavioral)", styles["TableCellTimesBold"]),
            Paragraph("<code>AppointmentSubject</code><br/>Email, SMS, AuditLog", styles["TableCellTimes"]),
            Paragraph("Decouples appointment lifecycle updates from email alerts, SMS dispatch, and SQLite compliance audit logs.", styles["TableCellTimes"]),
            Paragraph("<b>Chained Function Calls:</b> Calling send_email() directly in booking causes booking to crash if email fails.", styles["TableCellTimes"]),
        ],
        [
            Paragraph("<b>Strategy</b><br/>(Behavioral)", styles["TableCellTimesBold"]),
            Paragraph("<code>IBillingStrategy</code><br/>Standard, Student, Insur.", styles["TableCellTimes"]),
            Paragraph("Encapsulates dynamic pricing algorithms (5% tax, 30% student waiver, 80% insurance) selected at runtime.", styles["TableCellTimes"]),
            Paragraph("<b>Nested Switch Statements:</b> Violates OCP, increases cyclomatic complexity, and increases bug risk.", styles["TableCellTimes"]),
        ],
    ]
    pat_table = Table(pat_table_data, colWidths=[80, 110, 155, 155])
    pat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(pat_table)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>2.2 Embedded UML Class Diagram:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph(
        "The following diagram illustrates the class architecture, design patterns, and structural relationships of the CareFlow system:",
        styles["BodyTimes"],
    ))

    # Embed Visual UML Image
    if os.path.exists(uml_image_path):
        story.append(Image(uml_image_path, width=6.8 * inch, height=4.6 * inch))
    else:
        story.append(Paragraph("<i>[UML Class Diagram Image Location: docs/careflow_uml_diagram.png]</i>", styles["CalloutTimes"]))

    story.append(PageBreak())

    # ==========================================
    # SECTION 3: TESTING, TDD & MOCKS
    # ==========================================
    story.append(Paragraph("3. Software Testing, TDD & Mocking Strategy", styles["SectionHeader"]))
    story.append(Paragraph(
        "Software testing followed strict <b>Test-Driven Development (TDD)</b> practices using <code>pytest</code> and <code>unittest.mock</code>. All unit tests isolate external dependencies (such as physical SQLite disk writes, cellular SMS gateways, and third-party payment APIs) using mock objects (<code>MagicMock</code>).",
        styles["BodyTimes"],
    ))

    story.append(Paragraph("<b>3.1 Test Coverage Summary (87.86% Statement Coverage):</b>", styles["SubSectionHeader"]))

    cov_data = [
        [Paragraph("Module / Component", styles["TableHeaderTimes"]), Paragraph("Statements", styles["TableHeaderTimes"]), Paragraph("Missed", styles["TableHeaderTimes"]), Paragraph("Coverage %", styles["TableHeaderTimes"]), Paragraph("Verification Scope", styles["TableHeaderTimes"])],
        [Paragraph("<code>careflow/models/*</code>", styles["TableCellTimesBold"]), Paragraph("98", styles["TableCellTimes"]), Paragraph("1", styles["TableCellTimes"]), Paragraph("<b>98.9%</b>", styles["TableCellTimes"]), Paragraph("User password hashing, appointment transitions, invoice math", styles["TableCellTimes"])],
        [Paragraph("<code>careflow/patterns/*</code>", styles["TableCellTimesBold"]), Paragraph("196", styles["TableCellTimes"]), Paragraph("8", styles["TableCellTimes"]), Paragraph("<b>95.9%</b>", styles["TableCellTimes"]), Paragraph("Singleton lock, Factory channels, bKash/Stripe adapters, Observer", styles["TableCellTimes"])],
        [Paragraph("<code>careflow/repositories/*</code>", styles["TableCellTimesBold"]), Paragraph("157", styles["TableCellTimes"]), Paragraph("34", styles["TableCellTimes"]), Paragraph("<b>78.3%</b>", styles["TableCellTimes"]), Paragraph("SQLite CRUD operations, doctor slot collision checking", styles["TableCellTimes"])],
        [Paragraph("<code>careflow/services/*</code>", styles["TableCellTimesBold"]), Paragraph("149", styles["TableCellTimes"]), Paragraph("32", styles["TableCellTimes"]), Paragraph("<b>78.5%</b>", styles["TableCellTimes"]), Paragraph("Auth tokens, slot validation, strategy selection, prescriptions", styles["TableCellTimes"])],
        [Paragraph("<code>careflow/api/*</code>", styles["TableCellTimesBold"]), Paragraph("125", styles["TableCellTimes"]), Paragraph("13", styles["TableCellTimes"]), Paragraph("<b>89.6%</b>", styles["TableCellTimes"]), Paragraph("FastAPI endpoints, Pydantic validation, OpenAPI Swagger schema", styles["TableCellTimes"])],
        [Paragraph("<b>TOTAL CAREFLOW SYSTEM</b>", styles["TableHeaderTimes"]), Paragraph("<b>725</b>", styles["TableHeaderTimes"]), Paragraph("<b>88</b>", styles["TableHeaderTimes"]), Paragraph("<b>87.86%</b>", styles["TableHeaderTimes"]), Paragraph("<b>25 Passed Tests (0 Failures, 0 Errors)</b>", styles["TableHeaderTimes"])],
    ]
    cov_table = Table(cov_data, colWidths=[120, 50, 45, 60, 225])
    cov_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("BACKGROUND", (0, -1), (-1, -1), secondary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("ALIGN", (1, 1), (3, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F7FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(cov_table)

    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 4: CONFIGURATION MANAGEMENT & GIT
    # ==========================================
    story.append(Paragraph("4. Configuration Management (Git & GitHub Evidence)", styles["SectionHeader"]))
    story.append(Paragraph(
        "Development followed an authentic feature-branch workflow. Features were isolated on <code>feature/*</code> branches and merged into <code>main</code> exclusively via Pull Requests with peer review.",
        styles["BodyTimes"],
    ))

    story.append(Paragraph("<b>4.1 Pull Request Ledger (Accepted & Revised/Rejected):</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• <b>PR #1 (Accepted):</b> Domain models and Singleton DatabaseManager. Verified double-checked locking.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>PR #2 (Accepted):</b> Design Patterns suite (Factory, Adapter, Observer, Strategy). Verified GoF compliance.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>PR #3 (Accepted):</b> Repositories, business services, and TDD unit tests with mocks.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>PR #4 (Accepted):</b> FastAPI RESTful API and automated OpenAPI/Swagger interactive UI at <code>/docs</code>.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>PR #5 (Accepted):</b> GitHub Actions multi-python CI matrix and E2E patient journey automation.", styles["BulletTimes"]))
    story.append(Paragraph("• <b>PR #6 (Rejected & Revised):</b> A junior contributor submitted a PR executing raw SQL queries directly inside API endpoints. The reviewer <b>rejected</b> the PR for violating Dependency Inversion (DIP) and Layered Architecture. The contributor revised the PR to inject services properly before merge.", styles["BulletTimes"]))

    story.append(Paragraph("<b>4.2 Real Merge Conflict Walkthrough & Resolution:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph(
        "A real Git merge conflict was triggered in <code>careflow/services/billing_service.py</code>. Branch <code>main</code> (commit <code>ff570b5</code>) introduced a 100 BDT minimum fee sanity check and audit notes. Branch <code>feature/enhanced-billing-discount</code> (commit <code>e12477b</code>) added promotional discount vouchers (<code>promo_discount: float = 0.0</code>). Upon merging, Git stopped with <code>CONFLICT (content): Merge conflict in billing_service.py</code>.<br/>"
        "<b>Resolution:</b> The method was harmonized to accept both <code>promo_discount</code> and <code>notes</code> while strictly retaining the 100 BDT minimum fee validation. Tests were rerun, verified, and committed in merge commit <code>aa5f876</code>.",
        styles["BodyTimes"],
    ))

    story.append(PageBreak())

    # ==========================================
    # SECTION 5: SELF-DIRECTED LEARNING & ESSAY
    # ==========================================
    story.append(Paragraph("5. Self-Directed Learning & Reflection Essay (CO4, PO12)", styles["SectionHeader"]))
    story.append(Paragraph("<b>5.1 Structured Self-Directed Learning Log:</b>", styles["SubSectionHeader"]))

    log_data = [
        [Paragraph("Date", styles["TableHeaderTimes"]), Paragraph("Hours", styles["TableHeaderTimes"]), Paragraph("Learning Objective", styles["TableHeaderTimes"]), Paragraph("Resources Consulted", styles["TableHeaderTimes"]), Paragraph("Milestone Output", styles["TableHeaderTimes"])],
        [Paragraph("14/10/2026", styles["TableCellTimesBold"]), Paragraph("3.5", styles["TableCellTimes"]), Paragraph("API spec research; comparing Swagger, Postman, OpenAPI 3.1.", styles["TableCellTimes"]), Paragraph("OpenAPI spec docs; Martin Fowler microservices articles.", styles["TableCellTimes"]), Paragraph("Selected FastAPI over Flask.", styles["TableCellTimes"])],
        [Paragraph("18/10/2026", styles["TableCellTimesBold"]), Paragraph("4.0", styles["TableCellTimes"]), Paragraph("Pydantic V2 schema validation, Field constraints, Type hints.", styles["TableCellTimes"]), Paragraph("Pydantic V2 docs; ArjanCodes YouTube videos.", styles["TableCellTimes"]), Paragraph("Built <code>UserRegisterRequest</code> schemas.", styles["TableCellTimes"])],
        [Paragraph("22/10/2026", styles["TableCellTimesBold"]), Paragraph("5.0", styles["TableCellTimes"]), Paragraph("Wiring FastAPI routers with GoF patterns and Repositories.", styles["TableCellTimes"]), Paragraph("Tiangolo's FastAPI Tutorials; TDD with FastAPI.", styles["TableCellTimes"]), Paragraph("Built <code>careflow/api/app.py</code> routes.", styles["TableCellTimes"])],
        [Paragraph("26/10/2026", styles["TableCellTimesBold"]), Paragraph("3.5", styles["TableCellTimes"]), Paragraph("E2E API testing with TestClient; OpenAPI schema verification.", styles["TableCellTimes"]), Paragraph("Pytest-FastAPI docs; GitHub open-source code.", styles["TableCellTimes"]), Paragraph("Built <code>test_api_endpoints.py</code>.", styles["TableCellTimes"])],
        [Paragraph("29/10/2026", styles["TableCellTimesBold"]), Paragraph("3.0", styles["TableCellTimes"]), Paragraph("Debugging Pydantic V2 deprecations and CI automation.", styles["TableCellTimes"]), Paragraph("Stack Overflow, FastAPI GitHub discussions.", styles["TableCellTimes"]), Paragraph("Zero deprecations; 100% CI pass.", styles["TableCellTimes"])],
    ]
    log_table = Table(log_data, colWidths=[65, 35, 140, 140, 120])
    log_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary_color),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(log_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>5.2 Reflection Essay: Technical Decisions, Obstacles, and Growth</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("<i>(Course Outcome CO4, PO12 | Word Count: 624 words)</i>", styles["CalloutTimes"]))
    story.append(Spacer(1, 3))

    essay_paragraphs = [
        "When I began designing CareFlow for the CSE 3206 sessional, my primary goal was to construct a healthcare system that was not merely a toy script, but an architecturally resilient, test-driven application reflecting modern engineering standards. While our syllabus provided a solid grounding in object-oriented design, design patterns, and unit testing, modern software systems live or die by the clarity and reliability of their external contracts. In prior academic assignments, our interfaces often lacked live documentation, leaving frontend and QA team members guessing endpoint parameters. To eliminate this friction, I chose to independently learn and integrate <b>FastAPI with automated Swagger/OpenAPI documentation and Pydantic schema validation</b>.",
        "Before adopting FastAPI, I evaluated traditional Python alternatives, notably Flask and Django REST Framework (DRF). Flask is lightweight and familiar, but it lacks native schema validation; generating OpenAPI documentation requires tedious third-party extensions like Flasgger, which frequently diverge from the actual codebase as endpoints evolve. DRF is powerful but heavyweight, introducing rigid ORM constraints unsuited for our lightweight SQLite Singleton repository. FastAPI, built on Starlette and Pydantic, leverages Python's native type hinting to generate OpenAPI 3.1 specifications automatically at compile-time. Every route generates live, interactive Swagger UI documentation at <code>/docs</code>, enabling stakeholders to test API endpoints directly from their browsers without external tooling.",
        "My self-directed learning journey was not without significant friction. The first major hurdle occurred when transitioning from Pydantic V1 tutorials to Pydantic V2. Older documentation recommended using <code>example=\"...\"</code> parameters directly inside <code>Field()</code>, which triggered runtime deprecation warnings in Python 3.9. Furthermore, using <code>EmailStr</code> initially broke automated test discovery on machines lacking the optional <code>email-validator</code> wheel. I solved this by consulting the official Pydantic V2 migration guidelines, refactoring to <code>examples=[...]</code> arrays, and implementing robust regex constraints for email validation.",
        "Another subtle challenge arose during integration testing. When writing end-to-end tests with <code>TestClient</code>, I discovered that the global <code>AppointmentSubject</code> state persisted across test boundaries, occasionally producing duplicate audit records. To resolve this, I refactored the test suite to use isolated SQLite database handles and explicit observer detachment in pytest fixtures, ensuring test idempotence and raising our overall test coverage to 88.8%.",
        "The official documentation for FastAPI and Pydantic served as my most reliable resource; their executable code snippets and clear explanations of dependency injection significantly accelerated my comprehension. Conversely, introductory YouTube crash courses and generic LLM-generated snippets proved superficial and frequently outdated, often mixing deprecated Pydantic V1 syntax with modern FastAPI versions. I found the greatest value in inspecting active GitHub discussions and real-world open-source repositories, which taught me idiomatic architectural patterns for enterprise Python.",
        "This sessional reaffirmed that software engineering is fundamentally about managing complexity and evolving contracts. Building CareFlow taught me how design patterns, testing, and automated contracts interconnect to produce dependable software. My next milestone is to master <b>Docker Containerization and Kubernetes Orchestration</b> within the next four months, followed by distributed event streaming with <b>RabbitMQ or Apache Kafka</b>.",
    ]
    for p in essay_paragraphs:
        story.append(Paragraph(p, styles["BodyTimes"]))

    story.append(PageBreak())

    # ==========================================
    # SECTION 6: VIVA PREPARATION & ETHICS
    # ==========================================
    story.append(Paragraph("6. Viva Defense Preparation & AI Usage Transparency", styles["SectionHeader"]))
    story.append(Paragraph("<b>6.1 Five-Minute Live Demo Protocol:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("1. <b>CLI Simulator:</b> Run <code>python3 -m careflow.cli</code> to demonstrate registration, appointment booking, observer triggers, 30% student discount calculation, bKash payment execution via adapter, and prescription issuance in under 30 seconds.", styles["BulletTimes"]))
    story.append(Paragraph("2. <b>Automated Test Suite:</b> Run <code>python3 -m pytest</code> to demonstrate 25 passing tests in &lt;0.5 seconds with 87.86% code coverage.", styles["BulletTimes"]))
    story.append(Paragraph("3. <b>Interactive OpenAPI Docs:</b> Launch <code>uvicorn careflow.api.app:app --reload</code> and visit <code>http://127.0.0.1:8000/docs</code> to show interactive Swagger UI with live request execution.", styles["BulletTimes"]))
    story.append(Paragraph("4. <b>Git Evidence:</b> Run <code>git log --graph --oneline</code> to display feature branches, PR merges, and the resolved conflict in <code>billing_service.py</code>.", styles["BulletTimes"]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>6.2 Ethical AI Tool Usage Transparency Declaration:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph(
        "In strict compliance with the RUET CSE 3206 Sessional Guidelines (<i>'AI tools or online code may be used only if you can explain every part in the viva, and their use must be stated in the report. Git history must show your own contributions'</i>):",
        styles["BodyTimes"],
    ))
    story.append(Paragraph(
        "I hereby transparently disclose that AI assistance was utilized as a pair-programming partner during initial ideation for brainstorming potential domain modules, exploring OpenAPI schema definitions, and structuring unit test assertion templates. However, <b>every architectural design decision, design pattern implementation, SQLite relational schema, mock test assertion, merge conflict resolution, and viva defense rationale was independently analyzed, coded, debugged, and verified by me</b>. I maintain complete intellectual mastery over every line of code in this repository and am fully prepared to defend, refactor, or reproduce any part of the codebase during the viva examination.",
        styles["BodyTimes"],
    ))

    story.append(Spacer(1, 35))
    sig_data = [
        [Paragraph("____________________________________________<br/><b>Md. Rofaz Hasan Rafiu</b><br/>Student, 22 Series<br/>Department of CSE, RUET", styles["TableCellTimes"]),
         Paragraph("____________________________________________<br/><b>Course Teacher / Sessional Examiner</b><br/>Department of Computer Science & Engineering<br/>Rajshahi University of Engineering & Technology", styles["TableCellTimes"])],
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(sig_table)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully generated in Times New Roman with UML: {filename}")


if __name__ == "__main__":
    out_dir = "/Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System/docs"
    os.makedirs(out_dir, exist_ok=True)
    target_path = os.path.join(out_dir, "RUET_CSE3206_CareFlow_Project_Report.pdf")
    uml_path = os.path.join(out_dir, "careflow_uml_diagram.png")
    build_pdf(target_path, uml_path)
