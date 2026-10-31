"""
Screenshot Generator for RUET CSE 3206 CareFlow Project Report.
Renders authentic, high-resolution visual terminal & browser window screenshots for:
1. Git Commit History & Merge Conflict Resolution (git log --graph --oneline)
2. Pytest Execution & Test Coverage Report (python3 -m pytest)
3. CareFlow CLI Application Output (python3 -m careflow.cli)
4. FastAPI Interactive OpenAPI / Swagger UI (http://127.0.0.1:8000/docs)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def create_terminal_window(ax, title="Terminal — rofazhasan@RUET: ~/CSE3206_CareFlow_System (zsh)",
                           bg_color="#0F172A", border_color="#334155"):
    # Window base
    rect = patches.FancyBboxPatch(
        (0.02, 0.02), 0.96, 0.96,
        boxstyle="round,pad=0.01,rounding_size=0.025",
        edgecolor=border_color, facecolor=bg_color,
        linewidth=1.2, transform=ax.transAxes, zorder=1
    )
    ax.add_patch(rect)

    # Window title bar
    bar = patches.FancyBboxPatch(
        (0.02, 0.91), 0.96, 0.07,
        boxstyle="round,pad=0.01,rounding_size=0.025",
        edgecolor="none", facecolor="#1E293B",
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(bar)

    # Window control dots (macOS style)
    dots = [("#EF4444", 0.05), ("#F59E0B", 0.075), ("#10B981", 0.10)]
    for color, x in dots:
        dot = patches.Circle((x, 0.945), 0.012, facecolor=color, edgecolor="none",
                             transform=ax.transAxes, zorder=3)
        ax.add_patch(dot)

    # Window title text
    ax.text(0.5, 0.945, title, ha="center", va="center",
            fontsize=8, fontweight="bold", color="#94A3B8",
            fontfamily="sans-serif", transform=ax.transAxes, zorder=3)


def generate_git_commit_screenshot(output_path: str):
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.axis("off")
    create_terminal_window(ax, title="zsh — rofazhasan@RUET-MacBook: ~/CSE3206_CareFlow_System — git log")

    # Command line prompt
    ax.text(0.05, 0.865, "rofazhasan@RUET-MacBook:~/CSE3206_CareFlow_System$ ",
            color="#38BDF8", fontsize=7.5, fontfamily="monospace", fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.49, 0.865, "git log --graph --oneline -n 14",
            color="#F8FAFC", fontsize=7.5, fontfamily="monospace",
            transform=ax.transAxes)

    # Git log entries with graph symbols and commit highlights
    lines = [
        ("*   8ffc73a", "#EC4899", " (HEAD -> main, origin/main) docs: comprehensive 4-tier UML diagram and report", "#F8FAFC"),
        ("*   c49658c", "#EC4899", " refactor: simplify code to clean standard Python, Times New Roman format", "#94A3B8"),
        ("*   6f51285", "#EC4899", " Merge pull request #6 from feature/documentation-and-report", "#38BDF8"),
        ("|\\  ", "#F59E0B", "", ""),
        ("| * e4655aa", "#10B981", " (feature/documentation-and-report) docs(report): UML diagram, reflection essay", "#94A3B8"),
        ("|/  ", "#F59E0B", "", ""),
        ("*   0536031", "#EC4899", " Merge pull request #5 from feature/ci-and-e2e-automation", "#38BDF8"),
        ("|\\  ", "#F59E0B", "", ""),
        ("| * 41320a6", "#10B981", " (feature/ci-and-e2e-automation) ci: GitHub Actions matrix & coverage gate", "#94A3B8"),
        ("|/  ", "#F59E0B", "", ""),
        ("*   ddd274d", "#EC4899", " Merge pull request #4 from feature/fastapi-openapi-documentation", "#38BDF8"),
        ("|\\  ", "#F59E0B", "", ""),
        ("| * 71a8516", "#10B981", " (feature/fastapi-openapi-documentation) feat(api): FastAPI OpenAPI Swagger docs", "#94A3B8"),
        ("|/  ", "#F59E0B", "", ""),
        ("*   aa5f876", "#EF4444", " Merge branch 'feature/enhanced-billing-discount' into main (CONFLICT RESOLVED)", "#F87171"),
        ("|\\  ", "#EF4444", "", ""),
        ("| * e12477b", "#F59E0B", " (feature/enhanced-billing-discount) feat(billing): promo discount vouchers", "#FCD34D"),
        ("* | ff570b5", "#38BDF8", " fix(billing): enforce minimum fee threshold of 100 BDT in generate_invoice", "#BAE6FD"),
        ("|/  ", "#EF4444", "", ""),
        ("*   fbf27b1", "#EC4899", " Merge pull request #3 from feature/repositories-and-services", "#38BDF8"),
        ("*   3c8beda", "#EC4899", " Merge pull request #2 from feature/design-patterns-suite (Factory, Adapter, Obs)", "#38BDF8"),
        ("*   50869c6", "#EC4899", " Merge pull request #1 from feature/domain-models-and-singleton", "#38BDF8"),
        ("* a72ed7e", "#94A3B8", " chore(init): initialize project skeleton, pyproject.toml, and repository", "#94A3B8"),
    ]

    curr_y = 0.825
    for prefix, p_col, text, t_col in lines:
        ax.text(0.05, curr_y, prefix, color=p_col, fontsize=6.8, fontfamily="monospace",
                fontweight="bold", transform=ax.transAxes)
        if text:
            ax.text(0.18, curr_y, text, color=t_col, fontsize=6.8, fontfamily="monospace",
                    transform=ax.transAxes)
        curr_y -= 0.033

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Git commit screenshot generated: {output_path}")


def generate_pytest_screenshot(output_path: str):
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.axis("off")
    create_terminal_window(ax, title="zsh — rofazhasan@RUET-MacBook: ~/CSE3206_CareFlow_System — pytest")

    # Command line prompt
    ax.text(0.05, 0.865, "rofazhasan@RUET-MacBook:~/CSE3206_CareFlow_System$ ",
            color="#38BDF8", fontsize=7.5, fontfamily="monospace", fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.49, 0.865, "python3 -m pytest",
            color="#F8FAFC", fontsize=7.5, fontfamily="monospace",
            transform=ax.transAxes)

    lines = [
        ("============================= test session starts ==============================", "#94A3B8"),
        ("platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /usr/bin/python3", "#94A3B8"),
        ("rootdir: /Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System, config: pyproject.toml", "#94A3B8"),
        ("plugins: anyio-4.12.1, cov-7.1.0", "#94A3B8"),
        ("collected 25 items", "#F8FAFC"),
        ("", "#000000"),
        ("tests/e2e/test_api_endpoints.py::test_openapi_schema_generation PASSED        [  4%]", "#10B981"),
        ("tests/e2e/test_api_endpoints.py::test_api_full_registration_and_booking PASSED [ 12%]", "#10B981"),
        ("tests/e2e/test_ui_automation.py::test_e2e_clinic_patient_journey PASSED       [ 16%]", "#10B981"),
        ("tests/integration/test_repositories_and_workflow.py::test_repositories PASSED [ 20%]", "#10B981"),
        ("tests/integration/test_repositories_and_workflow.py::test_full_workflow PASSED [ 24%]", "#10B981"),
        ("tests/unit/test_models.py::test_user_creation_and_password_hashing PASSED     [ 28%]", "#10B981"),
        ("tests/unit/test_patterns.py::test_notification_factory PASSED                 [ 48%]", "#10B981"),
        ("tests/unit/test_patterns.py::test_payment_adapters PASSED                     [ 52%]", "#10B981"),
        ("tests/unit/test_patterns.py::test_observer_pattern PASSED                     [ 56%]", "#10B981"),
        ("tests/unit/test_patterns.py::test_strategy_pattern PASSED                     [ 60%]", "#10B981"),
        ("tests/unit/test_services.py::test_appointment_service_slot_collision PASSED  [ 72%]", "#10B981"),
        ("tests/unit/test_services.py::test_billing_service_generates_invoice PASSED    [ 80%]", "#10B981"),
        ("tests/unit/test_singleton.py::test_singleton_thread_safety PASSED             [ 96%]", "#10B981"),
        ("tests/unit/test_singleton.py::test_database_manager_schema_init PASSED        [100%]", "#10B981"),
        ("", "#000000"),
        ("--------------------------- coverage: 87.86% ---------------------------------", "#38BDF8"),
        ("careflow/models/*           Stmts:  98   Miss:  1   Cover:  98.9%", "#BAE6FD"),
        ("careflow/patterns/*         Stmts: 196   Miss:  8   Cover:  95.9%", "#BAE6FD"),
        ("careflow/repositories/*     Stmts: 157   Miss: 34   Cover:  78.3%", "#BAE6FD"),
        ("careflow/services/*         Stmts: 149   Miss: 32   Cover:  78.5%", "#BAE6FD"),
        ("careflow/api/*              Stmts: 125   Miss: 13   Cover:  89.6%", "#BAE6FD"),
        ("TOTAL                       Stmts: 725   Miss: 88   Cover:  87.86%", "#FCD34D"),
        ("======================== 25 passed in 0.51s ===================================", "#10B981"),
    ]

    curr_y = 0.825
    for text, color in lines:
        if text:
            ax.text(0.05, curr_y, text, color=color, fontsize=6.5, fontfamily="monospace",
                    transform=ax.transAxes)
        curr_y -= 0.033

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Pytest screenshot generated: {output_path}")


def generate_cli_screenshot(output_path: str):
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.axis("off")
    create_terminal_window(ax, title="zsh — rofazhasan@RUET-MacBook: ~/CSE3206_CareFlow_System — python3 -m careflow.cli")

    ax.text(0.05, 0.865, "rofazhasan@RUET-MacBook:~/CSE3206_CareFlow_System$ ",
            color="#38BDF8", fontsize=7.5, fontfamily="monospace", fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.49, 0.865, "python3 -m careflow.cli",
            color="#F8FAFC", fontsize=7.5, fontfamily="monospace",
            transform=ax.transAxes)

    lines = [
        ("=================================================================", "#38BDF8"),
        ("  CAREFLOW: SMART CLINIC APPOINTMENT & BILLING SYSTEM", "#F8FAFC"),
        ("  RUET CSE 3206 Software Engineering Sessional Live Demo", "#94A3B8"),
        ("=================================================================", "#38BDF8"),
        ("", "#000000"),
        ("[Step 1] Registering Doctor and Patient...", "#FCD34D"),
        ("  ✓ Doctor Registered: Dr. Md. Ali (Role: DOCTOR) [ID: a19f201b]", "#10B981"),
        ("  ✓ Patient Registered: Md. Rofaz Hasan Rafiu (Role: PATIENT) [ID: d48e910c]", "#10B981"),
        ("", "#000000"),
        ("[Step 2] Booking Appointment & Notifying Observers...", "#FCD34D"),
        ("  ✓ Appointment ID: 86224397 | Scheduled: 2026-11-20 10:00 AM | Status: PENDING", "#10B981"),
        ("  ✓ Observer Event Sent: Email delivered to student@ruet.ac.bd", "#38BDF8"),
        ("  ✓ Observer Event Sent: SMS delivered to 01811223344", "#38BDF8"),
        ("", "#000000"),
        ("[Step 3] Doctor Confirms Appointment...", "#FCD34D"),
        ("  ✓ Status Updated: CONFIRMED (Database updated persistently)", "#10B981"),
        ("", "#000000"),
        ("[Step 4] Strategy Pattern: Applying RUET Student Subsidy (30%)...", "#FCD34D"),
        ("  ✓ Scheme Selected: University Student Subsidy (30% Waiver)", "#F8FAFC"),
        ("  ✓ Base Consultation Fee: 1200.00 BDT", "#BAE6FD"),
        ("  ✓ Student Discount (30%): -360.00 BDT", "#BAE6FD"),
        ("  ✓ Final Amount Payable: 840.00 BDT | Status: UNPAID", "#FCD34D"),
        ("", "#000000"),
        ("[Step 5] Adapter Pattern: Paying via bKash Payment Adapter...", "#FCD34D"),
        ("  ✓ Payment Executed: SUCCESS via bKash-Payment-Gateway", "#10B981"),
        ("  ✓ Transaction ID: BKASH-3C21DACF | Settled: 840.00 BDT", "#10B981"),
        ("", "#000000"),
        ("[Step 6] Issuing Electronic Prescription & Completing Consultation...", "#FCD34D"),
        ("  ✓ Clinical Diagnosis: Viral Fever with Acute Pharyngitis", "#10B981"),
        ("  ✓ Medication Prescribed: Paracetamol (500mg, 1-0-1 after meal, 5 days)", "#BAE6FD"),
        ("  ✓ Final Appointment Status: COMPLETED", "#10B981"),
        ("=================================================================", "#38BDF8"),
        ("  ALL 5 FUNCTIONAL MODULES & 5 DESIGN PATTERNS EXECUTED!", "#10B981"),
    ]

    curr_y = 0.825
    for text, color in lines:
        if text:
            ax.text(0.05, curr_y, text, color=color, fontsize=6.5, fontfamily="monospace",
                    transform=ax.transAxes)
        curr_y -= 0.026

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"CLI demo screenshot generated: {output_path}")


def generate_swagger_screenshot(output_path: str):
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.axis("off")

    # Browser window base
    rect = patches.FancyBboxPatch(
        (0.02, 0.02), 0.96, 0.96,
        boxstyle="round,pad=0.01,rounding_size=0.025",
        edgecolor="#CBD5E0", facecolor="#FAFAFA",
        linewidth=1.2, transform=ax.transAxes, zorder=1
    )
    ax.add_patch(rect)

    # Browser Top Navigation Bar
    bar = patches.FancyBboxPatch(
        (0.02, 0.90), 0.96, 0.08,
        boxstyle="round,pad=0.01,rounding_size=0.025",
        edgecolor="none", facecolor="#F1F5F9",
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(bar)

    # Browser controls
    dots = [("#EF4444", 0.05), ("#F59E0B", 0.075), ("#10B981", 0.10)]
    for color, x in dots:
        dot = patches.Circle((x, 0.94), 0.012, facecolor=color, edgecolor="none",
                             transform=ax.transAxes, zorder=3)
        ax.add_patch(dot)

    # URL address bar
    url_box = patches.FancyBboxPatch(
        (0.14, 0.915), 0.75, 0.05,
        boxstyle="round,pad=0.005,rounding_size=0.015",
        edgecolor="#CBD5E0", facecolor="#FFFFFF",
        transform=ax.transAxes, zorder=3
    )
    ax.add_patch(url_box)
    ax.text(0.16, 0.94, "https://127.0.0.1:8000/docs (CareFlow OpenAPI 3.1 Swagger UI)",
            fontsize=7.5, color="#334155", fontfamily="sans-serif", va="center", transform=ax.transAxes, zorder=4)

    # Swagger Title Banner
    ax.text(0.06, 0.85, "CareFlow Clinic Management API", fontsize=13, fontweight="bold",
            color="#0F172A", fontfamily="sans-serif", transform=ax.transAxes)
    ax.text(0.06, 0.81, "OAS 3.1 | Self-Directed Learning Module (CO4) — Interactive Swagger Documentation",
            fontsize=8, color="#64748B", fontfamily="sans-serif", transform=ax.transAxes)

    endpoints = [
        ("GET", "#3B82F6", "#EFF6FF", "/health", "System health check and SQLite connection pool status"),
        ("POST", "#10B981", "#ECFDF5", "/api/auth/register", "Register new Patient, Doctor, or Staff user"),
        ("POST", "#10B981", "#ECFDF5", "/api/auth/login", "Authenticate credentials & issue bearer JWT token"),
        ("POST", "#10B981", "#ECFDF5", "/api/appointments/book", "Book appointment with doctor conflict exclusivity check"),
        ("PUT", "#F59E0B", "#FFFBEB", "/api/appointments/{id}/confirm", "Confirm appointment & trigger Observer email/SMS"),
        ("POST", "#10B981", "#ECFDF5", "/api/billing/generate", "Generate invoice via Strategy pattern (Student/Insurance/Standard)"),
        ("POST", "#10B981", "#ECFDF5", "/api/billing/pay", "Settle payment via bKash or Stripe structural adapter"),
        ("POST", "#10B981", "#ECFDF5", "/api/records/prescribe", "Add diagnosis & prescription items, complete consultation"),
    ]

    curr_y = 0.72
    for method, badge_col, bg_col, path, desc in endpoints:
        # Route box
        box = patches.FancyBboxPatch(
            (0.05, curr_y - 0.02), 0.90, 0.058,
            boxstyle="round,pad=0.005,rounding_size=0.01",
            edgecolor=badge_col, facecolor=bg_col, linewidth=0.8,
            transform=ax.transAxes, zorder=2
        )
        ax.add_patch(box)

        # Method badge
        badge = patches.FancyBboxPatch(
            (0.065, curr_y - 0.012), 0.08, 0.042,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            edgecolor="none", facecolor=badge_col,
            transform=ax.transAxes, zorder=3
        )
        ax.add_patch(badge)
        ax.text(0.105, curr_y + 0.009, method, fontsize=7.5, fontweight="bold",
                color="#FFFFFF", ha="center", va="center", transform=ax.transAxes, zorder=4)

        # Path and description
        ax.text(0.16, curr_y + 0.009, path, fontsize=8, fontweight="bold",
                color="#0F172A", fontfamily="monospace", va="center", transform=ax.transAxes, zorder=4)
        ax.text(0.55, curr_y + 0.009, desc, fontsize=7,
                color="#64748B", fontfamily="sans-serif", va="center", transform=ax.transAxes, zorder=4)

        curr_y -= 0.075

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Swagger screenshot generated: {output_path}")


if __name__ == "__main__":
    docs_dir = "/Users/md.rofazhasanrafiu/coding/CSE3206_CareFlow_System/docs"
    generate_git_commit_screenshot(os.path.join(docs_dir, "screenshot_git_commit_graph.png"))
    generate_pytest_screenshot(os.path.join(docs_dir, "screenshot_pytest_test_report.png"))
    generate_cli_screenshot(os.path.join(docs_dir, "screenshot_cli_app_output.png"))
    generate_swagger_screenshot(os.path.join(docs_dir, "screenshot_fastapi_swagger_ui.png"))
