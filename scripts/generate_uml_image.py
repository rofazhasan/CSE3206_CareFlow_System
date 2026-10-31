"""
Comprehensive Professional UML Class Diagram Generator for CareFlow System.
Renders an extensive, publication-grade UML diagram with detailed class compartments,
stereotypes, visibility modifiers, types, and standard UML association arrows.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def draw_uml_class(ax, x, y, width, height, title, stereo=None, attributes=None, methods=None,
                   bg_color="#FFFFFF", border_color="#2B6CB0", header_color="#EDF2F7"):
    """
    Renders standard 3-compartment UML class box:
    1. Header (Stereotype + Class Name)
    2. Attributes compartment
    3. Methods / Operations compartment
    """
    # Outer rectangle with subtle drop shadow
    shadow = patches.FancyBboxPatch(
        (x + 0.04, y - 0.04), width, height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        edgecolor="none", facecolor="#CBD5E0", alpha=0.35, zorder=1
    )
    ax.add_patch(shadow)

    main_box = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        edgecolor=border_color, facecolor=bg_color,
        linewidth=1.2, zorder=2
    )
    ax.add_patch(main_box)

    # Header compartment background
    header_h = 0.45 if stereo else 0.32
    header_box = patches.FancyBboxPatch(
        (x, y + height - header_h), width, header_h,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        edgecolor="none", facecolor=header_color, zorder=3
    )
    ax.add_patch(header_box)

    # Header text
    if stereo:
        ax.text(x + width / 2.0, y + height - 0.14, f"«{stereo}»",
                ha="center", va="center", fontsize=7, fontstyle="italic",
                color="#4A5568", zorder=4, fontfamily="serif")
        ax.text(x + width / 2.0, y + height - 0.32, title,
                ha="center", va="center", fontsize=8.2, fontweight="bold",
                color="#1A202C", zorder=4, fontfamily="serif")
    else:
        ax.text(x + width / 2.0, y + height - 0.20, title,
                ha="center", va="center", fontsize=8.2, fontweight="bold",
                color="#1A202C", zorder=4, fontfamily="serif")

    # Divider line under header
    ax.plot([x, x + width], [y + height - header_h, y + height - header_h],
            color=border_color, linewidth=0.9, zorder=4)

    # Attributes Compartment
    attr_start_y = y + height - header_h - 0.12
    curr_y = attr_start_y
    if attributes:
        for attr in attributes:
            ax.text(x + 0.08, curr_y, attr,
                    ha="left", va="center", fontsize=6.3,
                    color="#2D3748", zorder=4, fontfamily="monospace")
            curr_y -= 0.13

    # Divider line under attributes
    num_methods = len(methods) if methods else 0
    attr_box_bottom = y + 0.12 + (num_methods * 0.13)
    if methods:
        ax.plot([x, x + width], [attr_box_bottom, attr_box_bottom],
                color=border_color, linewidth=0.7, zorder=4)
        m_curr_y = attr_box_bottom - 0.10
        for m in methods:
            ax.text(x + 0.08, m_curr_y, m,
                    ha="left", va="center", fontsize=6.3,
                    color="#1A202C", zorder=4, fontfamily="monospace")
            m_curr_y -= 0.13


def draw_arrow(ax, x1, y1, x2, y2, label=None, style="->", color="#4A5568", is_dashed=False):
    ls = "--" if is_dashed else "-"
    ax.annotate(
        "",
        xy=(x2, y2), xycoords="data",
        xytext=(x1, y1), textcoords="data",
        arrowprops=dict(
            arrowstyle=style,
            color=color,
            lw=1.1,
            ls=ls,
            shrinkA=0, shrinkB=0,
        ),
        zorder=2,
    )
    if label:
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        ax.text(mid_x, mid_y, label, ha="center", va="bottom",
                fontsize=6.8, color="#2C5282", fontweight="bold",
                fontfamily="serif",
                bbox=dict(boxstyle="square,pad=0.1", fc="#FFFFFF", ec="none", alpha=0.8),
                zorder=5)


def generate_comprehensive_uml(output_path: str):
    # Large high-res canvas (14 x 10.5 inches)
    fig, ax = plt.subplots(figsize=(14, 10.2), dpi=300)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10.2)
    ax.axis("off")

    # Outer decorative academic border
    outer_border = patches.Rectangle(
        (0.15, 0.15), 13.7, 9.9,
        fill=False, edgecolor="#CBD5E0", linewidth=1.5, zorder=1
    )
    ax.add_patch(outer_border)

    # Title & Subtitle Banner
    ax.text(7.0, 9.82, "CareFlow System: Comprehensive UML Class & Architecture Diagram",
            ha="center", va="center", fontsize=13, fontweight="bold", color="#0D3B66", fontfamily="serif")
    ax.text(7.0, 9.58, "CSE 3206: Software Engineering Sessional | Rajshahi University of Engineering & Technology (RUET)",
            ha="center", va="center", fontsize=8.5, color="#4A5568", fontfamily="serif")
    ax.text(7.0, 9.38, "Gang of Four Design Patterns: Singleton, Factory Method, Adapter, Observer, Strategy | Layered MVC/Repository Architecture",
            ha="center", va="center", fontsize=7.5, fontstyle="italic", color="#2B6CB0", fontfamily="serif")

    # =========================================================================
    # COLUMN 1: DOMAIN ENTITIES & VALUE OBJECTS (x: 0.4 to 3.4)
    # =========================================================================
    ax.text(1.9, 9.05, "DOMAIN ENTITIES (PERSISTED IN SQLITE)", ha="center", va="center",
            fontsize=8, fontweight="bold", color="#2C5282", fontfamily="serif")

    # User Entity
    draw_uml_class(
        ax, x=0.4, y=6.95, width=3.0, height=1.95,
        title="User", stereo="Entity",
        attributes=[
            "+user_id: string",
            "+name: string",
            "+email: string [UNIQUE]",
            "+role: string (DOCTOR|PATIENT)",
            "+password_hash: string",
            "+phone: string",
            "+created_at: string",
        ],
        methods=[
            "+hash_password(pwd): string",
            "+verify_password(pwd): bool",
            "+to_dict(): dict",
        ],
        border_color="#3182CE", header_color="#EBF8FF"
    )

    # Appointment Entity
    draw_uml_class(
        ax, x=0.4, y=4.45, width=3.0, height=2.25,
        title="Appointment", stereo="Entity / Aggregate Root",
        attributes=[
            "+appointment_id: string",
            "+patient_id: string [FK]",
            "+doctor_id: string [FK]",
            "+scheduled_time: string",
            "+reason: string",
            "+fee: float",
            "+status: string (PENDING|CONFIRMED|COMPLETED)",
            "+created_at: string",
        ],
        methods=[
            "+confirm(): void",
            "+complete(): void",
            "+cancel(): void",
            "+to_dict(): dict",
        ],
        border_color="#3182CE", header_color="#EBF8FF"
    )

    # Invoice Entity
    draw_uml_class(
        ax, x=0.4, y=2.25, width=3.0, height=2.00,
        title="Invoice", stereo="Entity",
        attributes=[
            "+invoice_id: string",
            "+appointment_id: string [FK]",
            "+patient_id: string",
            "+base_amount: float",
            "+discount_amount: float",
            "+tax_amount: float",
            "+status: string (UNPAID|PAID)",
            "+payment_reference: string",
        ],
        methods=[
            "+total_payable: float [get]",
            "+mark_as_paid(ref): void",
            "+to_dict(): dict",
        ],
        border_color="#3182CE", header_color="#EBF8FF"
    )

    # MedicalRecord & PrescriptionItem
    draw_uml_class(
        ax, x=0.4, y=0.35, width=3.0, height=1.75,
        title="MedicalRecord", stereo="Entity",
        attributes=[
            "+record_id: string",
            "+appointment_id: string [FK]",
            "+diagnosis: string",
            "+notes: string",
            "+prescriptions: List[Item]",
        ],
        methods=[
            "+add_prescription(item): void",
            "+to_dict(): dict",
        ],
        border_color="#3182CE", header_color="#EBF8FF"
    )

    # Relationship between Entities
    draw_arrow(ax, 1.9, 6.95, 1.9, 6.70, label="1..* has", color="#3182CE")
    draw_arrow(ax, 1.9, 4.45, 1.9, 4.25, label="1 generates", color="#3182CE")
    draw_arrow(ax, 1.9, 2.25, 1.9, 2.10, label="1 consults", color="#3182CE")

    # =========================================================================
    # COLUMN 2: REPOSITORIES & DATABASE SINGLETON (x: 3.8 to 6.8)
    # =========================================================================
    ax.text(5.3, 9.05, "DATA ACCESS LAYER (REPOSITORY PATTERN)", ha="center", va="center",
            fontsize=8, fontweight="bold", color="#276749", fontfamily="serif")

    # DatabaseManager (Singleton)
    draw_uml_class(
        ax, x=3.8, y=7.15, width=3.0, height=1.75,
        title="DatabaseManager", stereo="Singleton (Creational)",
        attributes=[
            "-_instance: DatabaseManager",
            "-_lock: threading.Lock",
            "+db_name: string",
            "+connection: sqlite3.Connection",
        ],
        methods=[
            "+__new__(cls, db_name): Inst",
            "+get_connection(): Connection",
            "+init_database(): void",
            "+reset_instance(): void",
        ],
        border_color="#2B6CB0", header_color="#BEE3F8", bg_color="#F7FAFC"
    )

    # AppointmentRepository
    draw_uml_class(
        ax, x=3.8, y=4.75, width=3.0, height=1.95,
        title="AppointmentRepository", stereo="Repository",
        attributes=[
            "-db: DatabaseManager",
        ],
        methods=[
            "+create(appt): Appointment",
            "+get_by_id(id): Appointment",
            "+is_doctor_slot_occupied(...): bool",
            "+update_status(id, status): bool",
            "+list_by_patient(pat_id): List",
            "+list_by_doctor(doc_id): List",
        ],
        border_color="#38A169", header_color="#C6F6D5"
    )

    # BillingRepository & MedicalRecordRepository
    draw_uml_class(
        ax, x=3.8, y=2.50, width=3.0, height=1.85,
        title="BillingRepository", stereo="Repository",
        attributes=[
            "-db: DatabaseManager",
        ],
        methods=[
            "+create_invoice(inv): Invoice",
            "+get_by_id(id): Invoice",
            "+get_by_appointment_id(id): Inv",
            "+update_payment(id, st, ref): bool",
            "+list_by_patient(pat_id): List",
        ],
        border_color="#38A169", header_color="#C6F6D5"
    )

    # UserRepository & MedicalRecordRepository
    draw_uml_class(
        ax, x=3.8, y=0.35, width=3.0, height=1.75,
        title="UserRepository & MedicalRepo", stereo="Repository Layer",
        attributes=[
            "+UserRepository.create(user): User",
            "+UserRepository.get_by_email(): User",
            "+UserRepository.list_by_role(): List",
            "+MedicalRepo.create(record): Record",
        ],
        methods=[
            "+get_by_appointment_id(): Record",
            "+list_by_patient(pat_id): List",
        ],
        border_color="#38A169", header_color="#C6F6D5"
    )

    # Dependency of Repositories on DatabaseManager
    draw_arrow(ax, 5.3, 6.70, 5.3, 7.15, label="queries via", color="#2B6CB0", is_dashed=True)
    draw_arrow(ax, 5.3, 4.35, 5.3, 4.75, color="#2B6CB0", is_dashed=True)
    draw_arrow(ax, 3.4, 5.50, 3.8, 5.50, label="persists", color="#38A169")

    # =========================================================================
    # COLUMN 3: SERVICE LAYER ORCHESTRATION (x: 7.2 to 10.2)
    # =========================================================================
    ax.text(8.7, 9.05, "BUSINESS SERVICE LAYER & CONTROLLERS", ha="center", va="center",
            fontsize=8, fontweight="bold", color="#744210", fontfamily="serif")

    # AppointmentService
    draw_uml_class(
        ax, x=7.2, y=6.95, width=3.0, height=1.95,
        title="AppointmentService", stereo="Business Service",
        attributes=[
            "-appt_repo: AppointmentRepository",
            "-user_repo: UserRepository",
            "-subject: AppointmentSubject",
        ],
        methods=[
            "+book_appointment(...): Appointment",
            "+confirm_appointment(id): Appointment",
            "+cancel_appointment(id, reason): Appt",
        ],
        border_color="#D69E2E", header_color="#FEFCBF"
    )

    # BillingService
    draw_uml_class(
        ax, x=7.2, y=4.45, width=3.0, height=2.10,
        title="BillingService", stereo="Business Service",
        attributes=[
            "-billing_repo: BillingRepository",
            "-appt_repo: AppointmentRepository",
            "-payment_processor: IPaymentProcessor",
        ],
        methods=[
            "+generate_invoice(appt_id, strategy,",
            "                  promo_disc, notes): Inv",
            "+process_invoice_payment(...): Result",
            "+get_invoice(id): Invoice",
        ],
        border_color="#D69E2E", header_color="#FEFCBF"
    )

    # AuthService & MedicalRecordService
    draw_uml_class(
        ax, x=7.2, y=2.45, width=3.0, height=1.65,
        title="AuthService & MedicalService", stereo="Business Service",
        attributes=[
            "+AuthService.register_user(...): User",
            "+AuthService.authenticate(...): token",
            "+MedicalService.create_record(...)",
        ],
        methods=[
            "+get_patient_history(pat_id): List",
        ],
        border_color="#D69E2E", header_color="#FEFCBF"
    )

    # FastAPI Controller & CLI Simulator
    draw_uml_class(
        ax, x=7.2, y=0.35, width=3.0, height=1.75,
        title="FastAPI & CLI Controller", stereo="Client / Presentation Layer",
        attributes=[
            "+GET  /health",
            "+POST /api/auth/register, /login",
            "+POST /api/appointments/book",
            "+POST /api/billing/generate, /pay",
            "+POST /api/records/prescribe",
        ],
        methods=[
            "+Swagger UI (/docs) | CLI Simulator",
        ],
        border_color="#4A5568", header_color="#EDF2F7", bg_color="#F7FAFC"
    )

    # Service to Repo arrows
    draw_arrow(ax, 7.2, 7.80, 6.8, 5.70, label="delegates", color="#D69E2E")
    draw_arrow(ax, 7.2, 5.50, 6.8, 3.40, color="#D69E2E")
    draw_arrow(ax, 8.7, 2.10, 8.7, 2.45, label="calls", color="#4A5568")

    # =========================================================================
    # COLUMN 4: GANG OF FOUR DESIGN PATTERNS (x: 10.6 to 13.6)
    # =========================================================================
    ax.text(12.1, 9.05, "ENTERPRISE DESIGN PATTERNS (GoF)", ha="center", va="center",
            fontsize=8, fontweight="bold", color="#702459", fontfamily="serif")

    # Pattern 1: Factory Method (Notifications)
    draw_uml_class(
        ax, x=10.6, y=7.30, width=3.0, height=1.65,
        title="NotificationFactory", stereo="Factory Method (Creational)",
        attributes=[
            "-_channels: dict",
        ],
        methods=[
            "+create_channel(type): INotification",
            "+register_channel(name, cls): void",
            "Creates: Email | SMS | Webhook",
        ],
        border_color="#9B2C2C", header_color="#FED7D7"
    )

    # Pattern 2: Observer (Appointment Events)
    draw_uml_class(
        ax, x=10.6, y=4.95, width=3.0, height=2.00,
        title="AppointmentSubject", stereo="Observer (Behavioral)",
        attributes=[
            "-_observers: List[IAppointmentObserver]",
        ],
        methods=[
            "+attach(observer): void",
            "+detach(observer): void",
            "+notify(event, appt, meta): void",
            "Observers: EmailNotificationObserver,",
            "           SMSNotificationObserver,",
            "           AuditLogObserver (SQLite)",
        ],
        border_color="#805AD5", header_color="#E9D8FD"
    )

    # Pattern 3: Adapter (Payment Gateways)
    draw_uml_class(
        ax, x=10.6, y=2.65, width=3.0, height=2.00,
        title="Bkash & Stripe Adapters", stereo="Adapter (Structural)",
        attributes=[
            "-gateway: BkashGateway / StripeGateway",
            "+process_payment(amt, ref, cust): Result",
        ],
        methods=[
            "Adapts:",
            "• BkashGateway.execute_bKash_payment()",
            "• StripeGateway.charge_customer_cents()",
            "To target: IPaymentProcessor",
        ],
        border_color="#C53030", header_color="#FED7D7"
    )

    # Pattern 4: Strategy (Billing Schemes)
    draw_uml_class(
        ax, x=10.6, y=0.35, width=3.0, height=2.00,
        title="Billing Strategy Hierarchy", stereo="Strategy (Behavioral)",
        attributes=[
            "+compute(base_amount): Result",
        ],
        methods=[
            "Concrete Strategies:",
            "• StandardBillingStrategy (5% tax)",
            "• StudentDiscountStrategy (30% waiver)",
            "• InsuranceCoverageStrategy (80% co-pay)",
            "• EmergencyCareStrategy (25% surcharge)",
        ],
        border_color="#DD6B20", header_color="#FEEBC8"
    )

    # Service to Pattern arrows
    draw_arrow(ax, 10.2, 7.80, 10.6, 6.00, label="notifies", color="#805AD5")
    draw_arrow(ax, 10.2, 5.50, 10.6, 3.65, label="adapts", color="#C53030")
    draw_arrow(ax, 10.2, 4.80, 10.6, 1.35, label="computes", color="#DD6B20")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Comprehensive UML Diagram generated successfully at: {output_path}")


if __name__ == "__main__":
    out_file = "/Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System/docs/careflow_uml_diagram.png"
    generate_comprehensive_uml(out_file)
