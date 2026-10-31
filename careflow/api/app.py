"""
CareFlow RESTful API & Interactive OpenAPI / Swagger Documentation.
Self-Directed Learning Tool (CO4, PO12) - FastAPI + OpenAPI Specification 3.1.0
"""

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from careflow.models.user import UserRole
from careflow.models.appointment import AppointmentStatus
from careflow.models.invoice import PaymentStatus
from careflow.models.medical_record import PrescriptionItem
from careflow.patterns.singleton import DatabaseManager
from careflow.patterns.strategy import (
    StandardBillingStrategy,
    StudentDiscountStrategy,
    InsuranceCoverageStrategy,
    EmergencyCareStrategy,
)
from careflow.patterns.adapter import BkashPaymentAdapter, StripePaymentAdapter
from careflow.patterns.observer import (
    AppointmentSubject,
    EmailNotificationObserver,
    SMSNotificationObserver,
    AuditLogObserver,
)
from careflow.repositories.user_repository import UserRepository
from careflow.repositories.appointment_repository import AppointmentRepository
from careflow.repositories.billing_repository import BillingRepository
from careflow.repositories.medical_record_repository import MedicalRecordRepository
from careflow.services.auth_service import AuthService
from careflow.services.appointment_service import AppointmentService
from careflow.services.billing_service import BillingService
from careflow.services.medical_record_service import MedicalRecordService

app = FastAPI(
    title="CareFlow Clinic Management API",
    description="""
    ## RUET CSE 3206 Software Engineering Sessional
    **Self-Directed Learning Module: Interactive OpenAPI (Swagger) Documentation & Pydantic Data Contracts**
    
    CareFlow provides automated, validated, and interactive healthcare endpoints covering:
    * **Identity & Role-Based Access Control**: Doctor and Patient registration.
    * **Appointment Lifecycle**: Slot validation, collision guard, and Observer notification triggers.
    * **Polymorphic Billing Engine**: Strategy-based discounts (RUET Student, Insurance, Emergency) & Adapter payment execution (bKash/Stripe).
    * **Clinical Consultation Records**: Prescriptions and diagnostic history.
    """,
    version="1.0.0",
    contact={
        "name": "Md. Rofaz Hasan Rafiu",
        "email": "mdrofazhasanrafiu@gmail.com",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# Shared singletons & services
db_manager = DatabaseManager()
user_repo = UserRepository(db_manager)
appt_repo = AppointmentRepository(db_manager)
bill_repo = BillingRepository(db_manager)
rec_repo = MedicalRecordRepository(db_manager)

# Global observer subject
global_subject = AppointmentSubject()
global_email_observer = EmailNotificationObserver()
global_sms_observer = SMSNotificationObserver()
global_audit_observer = AuditLogObserver(db_manager)
global_subject.attach(global_email_observer)
global_subject.attach(global_sms_observer)
global_subject.attach(global_audit_observer)

auth_service = AuthService(user_repo)
appt_service = AppointmentService(appt_repo, user_repo, global_subject)
billing_service = BillingService(bill_repo, appt_repo, BkashPaymentAdapter())
record_service = MedicalRecordService(rec_repo, appt_repo)


# ==========================================
# Pydantic Schemas (Data Contracts)
# ==========================================

class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, examples=["Dr. Anisur Rahman"])
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", examples=["anisur@ruet.ac.bd"])
    password: str = Field(..., min_length=6, examples=["DoctorKey2026"])
    role: UserRole = Field(..., examples=[UserRole.DOCTOR])
    phone: str = Field(default="", examples=["01711223344"])


class UserLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$", examples=["anisur@ruet.ac.bd"])
    password: str = Field(..., examples=["DoctorKey2026"])


class AppointmentBookRequest(BaseModel):
    patient_id: str = Field(..., examples=["p-001"])
    doctor_id: str = Field(..., examples=["d-001"])
    scheduled_time: str = Field(..., examples=["2026-11-20T10:00:00"])
    reason: str = Field(..., examples=["Cardiovascular screening"])
    fee: float = Field(default=1000.0, ge=100.0, examples=[1200.0])


class InvoiceGenerateRequest(BaseModel):
    appointment_id: str = Field(..., examples=["app-123"])
    scheme: str = Field(default="STANDARD", description="STANDARD | STUDENT | INSURANCE | EMERGENCY")
    promo_discount: float = Field(default=0.0, ge=0.0)


class InvoicePaymentRequest(BaseModel):
    invoice_id: str = Field(..., examples=["inv-456"])
    gateway: str = Field(default="BKASH", description="BKASH | STRIPE")
    phone: Optional[str] = Field(default="01711223344")
    email: Optional[str] = Field(default="patient@ruet.ac.bd")


class PrescriptionItemSchema(BaseModel):
    medicine_name: str = Field(..., examples=["Metformin"])
    dosage: str = Field(..., examples=["500mg"])
    frequency: str = Field(..., examples=["1-0-1 with meal"])
    duration_days: int = Field(..., ge=1, examples=[30])


class MedicalRecordRequest(BaseModel):
    appointment_id: str = Field(...)
    diagnosis: str = Field(..., min_length=3, examples=["Type 2 Diabetes Mellitus"])
    notes: str = Field(default="", examples=["Patient recommended 30 min daily walking."])
    prescriptions: List[PrescriptionItemSchema] = Field(default_factory=list)


# ==========================================
# API Endpoints
# ==========================================

@app.get("/health", tags=["Health & System"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "CareFlow Clinic Management API",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "SQLite (Singleton Pool)",
    }


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register(request: UserRegisterRequest):
    try:
        user = auth_service.register_user(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role,
            phone=request.phone,
        )
        return {"message": "User registered successfully", "user": user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/auth/login", tags=["Authentication"])
def login(request: UserLoginRequest):
    try:
        return auth_service.authenticate(request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.post("/api/appointments/book", status_code=status.HTTP_201_CREATED, tags=["Appointments"])
def book_appointment(request: AppointmentBookRequest):
    try:
        appt = appt_service.book_appointment(
            patient_id=request.patient_id,
            doctor_id=request.doctor_id,
            scheduled_time=request.scheduled_time,
            reason=request.reason,
            fee=request.fee,
        )
        return {"message": "Appointment booked successfully", "appointment": appt.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put("/api/appointments/{appointment_id}/confirm", tags=["Appointments"])
def confirm_appointment(appointment_id: str):
    try:
        appt = appt_service.confirm_appointment(appointment_id)
        return {"message": "Appointment confirmed", "appointment": appt.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@app.post("/api/billing/generate", status_code=status.HTTP_201_CREATED, tags=["Billing"])
def generate_invoice(request: InvoiceGenerateRequest):
    try:
        scheme_map = {
            "STANDARD": StandardBillingStrategy(),
            "STUDENT": StudentDiscountStrategy(),
            "INSURANCE": InsuranceCoverageStrategy(),
            "EMERGENCY": EmergencyCareStrategy(),
        }
        chosen_strategy = scheme_map.get(request.scheme.upper(), StandardBillingStrategy())
        invoice = billing_service.generate_invoice(
            appointment_id=request.appointment_id,
            strategy=chosen_strategy,
            promo_discount=request.promo_discount,
        )
        return {"message": "Invoice generated", "invoice": invoice.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/billing/pay", tags=["Billing"])
def pay_invoice(request: InvoicePaymentRequest):
    try:
        processor = (
            StripePaymentAdapter()
            if request.gateway.upper() == "STRIPE"
            else BkashPaymentAdapter()
        )
        result = billing_service.process_invoice_payment(
            invoice_id=request.invoice_id,
            customer_info={"phone": request.phone, "email": request.email},
            custom_processor=processor,
        )
        if not result.success:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=result.error_message)
        return {
            "message": "Payment processed successfully",
            "transaction_id": result.transaction_id,
            "amount_paid": result.amount_paid,
            "currency": result.currency,
            "gateway": result.gateway_name,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/records/prescribe", status_code=status.HTTP_201_CREATED, tags=["Medical Records"])
def create_medical_record(request: MedicalRecordRequest):
    try:
        prescriptions = [
            PrescriptionItem(
                medicine_name=p.medicine_name,
                dosage=p.dosage,
                frequency=p.frequency,
                duration_days=p.duration_days,
            )
            for p in request.prescriptions
        ]
        record = record_service.create_record(
            appointment_id=request.appointment_id,
            diagnosis=request.diagnosis,
            notes=request.notes,
            prescriptions=prescriptions,
        )
        return {"message": "Prescription recorded successfully", "record": record.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
