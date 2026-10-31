"""
Generates a publication-quality UML Class Diagram image for the CareFlow System
using Matplotlib, suitable for embedding into the official PDF report.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def draw_class_box(ax, x, y, width, height, title, stereo=None, attributes=None, methods=None, bg_color="#EBF8FF", border_color="#3182CE"):
    # Main outer rectangle
    rect = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        edgecolor=border_color,
        facecolor=bg_color,
        linewidth=1.2,
        zorder=2,
    )
    ax.add_patch(rect)

    # Header text
    header_y = y + height - 0.22
    if stereo:
        ax.text(x + width / 2.0, header_y, f"<<{stereo}>>", ha="center", va="center", fontsize=7.5, fontstyle="italic", color="#4A5568", zorder=3, fontfamily="serif")
        header_y -= 0.18
    ax.text(x + width / 2.0, header_y, title, ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1A202C", zorder=3, fontfamily="serif")

    # Divider below header
    div1_y = y + height - 0.45
    ax.plot([x, x + width], [div1_y, div1_y], color=border_color, linewidth=0.8, zorder=3)

    # Attributes
    curr_y = div1_y - 0.16
    if attributes:
        for attr in attributes:
            ax.text(x + 0.1, curr_y, attr, ha="left", va="center", fontsize=6.8, color="#2D3748", zorder=3, fontfamily="monospace")
            curr_y -= 0.16

    # Divider below attributes
    div2_y = y + 0.65
    if methods:
        ax.plot([x, x + width], [div2_y, div2_y], color=border_color, linewidth=0.8, zorder=3)
        curr_m_y = div2_y - 0.16
        for m in methods:
            ax.text(x + 0.1, curr_m_y, m, ha="left", va="center", fontsize=6.8, color="#2D3748", zorder=3, fontfamily="monospace")
            curr_m_y -= 0.16


def draw_arrow(ax, x1, y1, x2, y2, label=None, style="->", color="#4A5568", is_dashed=False):
    ls = "--" if is_dashed else "-"
    ax.annotate(
        "",
        xy=(x2, y2), xycoords="data",
        xytext=(x1, y1), textcoords="data",
        arrowprops=dict(arrowstyle=style, color=color, lw=1.2, ls=ls),
        zorder=1,
    )
    if label:
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0 + 0.1
        ax.text(mid_x, mid_y, label, ha="center", va="center", fontsize=7, color="#2C5282", fontweight="bold", fontfamily="serif")


def generate_uml_diagram(output_path: str):
    fig, ax = plt.subplots(figsize=(11, 8.2), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.2)
    ax.axis("off")

    # Title Banner
    ax.text(5.5, 7.95, "CareFlow System: Object-Oriented Architecture & UML Class Diagram", ha="center", va="center", fontsize=12, fontweight="bold", color="#0D3B66", fontfamily="serif")
    ax.text(5.5, 7.7, "RUET CSE 3206 | Sessional Techniques & GoF Patterns Across 3 Categories", ha="center", va="center", fontsize=8.5, color="#4A5568", fontfamily="serif")

    # ==========================================
    # Top Row: Creational Patterns & Repositories
    # ==========================================
    # Singleton: DatabaseManager
    draw_class_box(
        ax, x=0.5, y=5.4, width=2.8, height=1.9,
        title="DatabaseManager",
        stereo="Singleton (Creational)",
        attributes=["-_instance: DatabaseManager", "-db_name: str", "-connection: Connection"],
        methods=["+get_connection(): Connection", "+init_database(): void", "+reset_instance(): void"],
        bg_color="#EBF8FF", border_color="#3182CE",
    )

    # Factory Method: NotificationFactory & Channels
    draw_class_box(
        ax, x=4.1, y=5.5, width=2.8, height=1.8,
        title="NotificationFactory",
        stereo="Factory Method",
        attributes=["-_channels: dict"],
        methods=["+create_channel(type): Channel", "+register_channel(name, cls)"],
        bg_color="#FEFCBF", border_color="#D69E2E",
    )

    draw_class_box(
        ax, x=7.6, y=5.5, width=2.9, height=1.8,
        title="INotificationChannel",
        stereo="Interface",
        attributes=["# Abstract Channel"],
        methods=["+send(to, subj, msg): dict", "[EmailNotificationChannel]", "[SMSNotificationChannel]"],
        bg_color="#FEFCBF", border_color="#D69E2E",
    )
    draw_arrow(ax, 6.9, 6.4, 7.6, 6.4, label="creates", color="#D69E2E")

    # ==========================================
    # Middle Row: Services & Structural Pattern
    # ==========================================
    # AppointmentService
    draw_class_box(
        ax, x=0.5, y=2.8, width=2.9, height=2.2,
        title="AppointmentService",
        stereo="Service Orchestrator",
        attributes=["-appt_repo: AppointmentRepository", "-user_repo: UserRepository", "-subject: AppointmentSubject"],
        methods=["+book_appointment(...): Appt", "+confirm_appointment(id): Appt", "+cancel_appointment(id): Appt"],
        bg_color="#E6FFFA", border_color="#319795",
    )

    # Observer Pattern: Subject & Observers
    draw_class_box(
        ax, x=4.1, y=2.8, width=2.8, height=2.2,
        title="AppointmentSubject",
        stereo="Observer (Behavioral)",
        attributes=["-_observers: List[Observer]"],
        methods=["+attach(observer): void", "+detach(observer): void", "+notify(event, appt, meta): void"],
        bg_color="#FAF5FF", border_color="#805AD5",
    )
    draw_arrow(ax, 3.4, 3.9, 4.1, 3.9, label="triggers", color="#319795")

    draw_class_box(
        ax, x=7.6, y=2.8, width=2.9, height=2.2,
        title="IAppointmentObserver",
        stereo="Observer Interface",
        attributes=["+update(event, appt, meta)"],
        methods=["• EmailNotificationObserver", "• SMSNotificationObserver", "• AuditLogObserver (SQLite)"],
        bg_color="#FAF5FF", border_color="#805AD5",
    )
    draw_arrow(ax, 6.9, 3.9, 7.6, 3.9, label="notifies", color="#805AD5")

    # ==========================================
    # Bottom Row: Strategy & Adapter Patterns
    # ==========================================
    # Strategy Pattern: Billing
    draw_class_box(
        ax, x=0.5, y=0.3, width=3.0, height=2.1,
        title="IBillingStrategy",
        stereo="Strategy (Behavioral)",
        attributes=["# Dynamic Pricing Schemes"],
        methods=["• StandardBilling (5% tax)", "• StudentDiscount (30% off)", "• InsuranceCoverage (80% off)", "• EmergencyCare (25% surch.)"],
        bg_color="#FEEBC8", border_color="#DD6B20",
    )

    # BillingService
    draw_class_box(
        ax, x=4.1, y=0.3, width=2.8, height=2.1,
        title="BillingService",
        stereo="Service Layer",
        attributes=["-billing_repo: BillingRepo", "-payment_processor: IPayProcessor"],
        methods=["+generate_invoice(appt, strat): Inv", "+process_invoice_payment(...)"],
        bg_color="#E6FFFA", border_color="#319795",
    )
    draw_arrow(ax, 4.1, 1.35, 3.5, 1.35, label="applies", color="#DD6B20")

    # Adapter Pattern: Payment Processor
    draw_class_box(
        ax, x=7.6, y=0.3, width=2.9, height=2.1,
        title="BkashPaymentAdapter",
        stereo="Adapter (Structural)",
        attributes=["-gateway: BkashGateway", "-app_token: str"],
        methods=["+process_payment(amt, ref, cust)", "Adapts BkashGateway.execute_bKash()", "to IPaymentProcessor interface"],
        bg_color="#FED7D7", border_color="#E53E3E",
    )
    draw_arrow(ax, 6.9, 1.35, 7.6, 1.35, label="delegates", color="#E53E3E")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"UML Diagram successfully generated at: {output_path}")


if __name__ == "__main__":
    out_file = "/Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System/docs/careflow_uml_diagram.png"
    generate_uml_diagram(out_file)
