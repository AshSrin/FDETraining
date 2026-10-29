# generte code with  api router
from fastapi import APIRouter, HTTPException
from models.payments import Payments
import services.payments as payment_service

router = APIRouter()

@router.post("/payments")
def create_payment(payment: Payments):
    try:
        created_payment = payment_service.create_payment(payment)
        return created_payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/payments")
def get_all_payments(): 
    try:
        payments = payment_service.get_all_payments()
        return payments
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    try:
        payment = payment_service.get_payment(payment_id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/payments/{payment_id}")
def update_payment(payment_id: str, updated_payment: Payments): 
    try:
        payment = payment_service.update_payment(payment_id, updated_payment)
        if payment is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: str, paid: float):
    try:
        success = payment_service.delete_payment(payment_id, paid)
        if not success:
            raise HTTPException(status_code=404, detail="Payment not found")
        return {"message": "Payment deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    