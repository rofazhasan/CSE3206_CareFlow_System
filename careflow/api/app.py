"""
CareFlow RESTful API & Interactive OpenAPI / Swagger Documentation.
Self-Directed Learning Module (CO4, PO12) - FastAPI
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

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
from careflow.models.medical_record import PrescriptionItem

app = FastAPI(
    title="CareFlow Clinic Management API",
    description="RUET CSE 3206 Software Engineering Sessional API with Interactive Swagger UI at /docs",
    version="1.0.0",
)

db = DatabaseManager()
user_repo = UserRepository(db)
appt_repo = AppointmentRepository(db)
bill_repo = BillingRepository(db)
rec_repo = MedicalRecordRepository(db)

subject = AppointmentSubject()
email_obs = EmailNotificationObserver()
sms_obs = SMSNotificationObserver()
audit_obs = AuditLogObserver(db)
subject.attach(email_obs)
subject.attach(sms_obs)
subject.attach(audit_obs)

auth_service = AuthService(user_repo)
appt_service = AppointmentService(appt_repo, user_repo, subject)
billing_service = BillingService(bill_repo, appt_repo, BkashPaymentAdapter())
record_service = MedicalRecordService(rec_repo, appt_repo)


class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str
    phone: str = ""


class UserLoginRequest(BaseModel):
    email: str
    password: str


class AppointmentBookRequest(BaseModel):
    patient_id: str
    doctor_id: str
    scheduled_time: str
    reason: str
    fee: float = 1000.0


class InvoiceGenerateRequest(BaseModel):
    appointment_id: str
    scheme: str = "STANDARD"
    promo_discount: float = 0.0


class InvoicePaymentRequest(BaseModel):
    invoice_id: str
    gateway: str = "BKASH"
    phone: Optional[str] = "01711223344"
    email: Optional[str] = "patient@clinic.org"


class PrescriptionItemSchema(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    duration_days: int


class MedicalRecordRequest(BaseModel):
    appointment_id: str
    diagnosis: str
    notes: str = ""
    prescriptions: List[PrescriptionItemSchema] = []


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "CareFlow API",
        "database": "SQLite (Singleton Pool)",
    }


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(request: UserRegisterRequest):
    try:
        user = auth_service.register_user(
            name=request.name,
            email=request.email,
            password=request.password,
            role=request.role,
            phone=request.phone,
        )
        return {"message": "User registered", "user": user.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login", tags=["Auth"])
def login(request: UserLoginRequest):
    try:
        return auth_service.authenticate(request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


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
        return {"message": "Appointment booked", "appointment": appt.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/appointments/{appointment_id}/confirm", tags=["Appointments"])
def confirm_appointment(appointment_id: str):
    try:
        appt = appt_service.confirm_appointment(appointment_id)
        return {"message": "Appointment confirmed", "appointment": appt.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/billing/generate", status_code=status.HTTP_201_CREATED, tags=["Billing"])
def generate_invoice(request: InvoiceGenerateRequest):
    try:
        schemes = {
            "STANDARD": StandardBillingStrategy(),
            "STUDENT": StudentDiscountStrategy(),
            "INSURANCE": InsuranceCoverageStrategy(),
            "EMERGENCY": EmergencyCareStrategy(),
        }
        strategy = schemes.get(request.scheme.upper(), StandardBillingStrategy())
        invoice = billing_service.generate_invoice(
            appointment_id=request.appointment_id,
            strategy=strategy,
            promo_discount=request.promo_discount,
        )
        return {"message": "Invoice generated", "invoice": invoice.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/billing/pay", tags=["Billing"])
def pay_invoice(request: InvoicePaymentRequest):
    try:
        processor = StripePaymentAdapter() if request.gateway.upper() == "STRIPE" else BkashPaymentAdapter()
        result = billing_service.process_invoice_payment(
            invoice_id=request.invoice_id,
            customer_info={"phone": request.phone, "email": request.email},
            custom_processor=processor,
        )
        if not result.success:
            raise HTTPException(status_code=402, detail=result.error_message)
        return {
            "message": "Payment successful",
            "transaction_id": result.transaction_id,
            "amount_paid": result.amount_paid,
            "currency": result.currency,
            "gateway": result.gateway_name,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/records/prescribe", status_code=status.HTTP_201_CREATED, tags=["Prescriptions"])
def add_prescription(request: MedicalRecordRequest):
    try:
        prescriptions = [
            PrescriptionItem(p.medicine_name, p.dosage, p.frequency, p.duration_days)
            for p in request.prescriptions
        ]
        record = record_service.create_record(
            appointment_id=request.appointment_id,
            diagnosis=request.diagnosis,
            notes=request.notes,
            prescriptions=prescriptions,
        )
        return {"message": "Prescription added", "record": record.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
