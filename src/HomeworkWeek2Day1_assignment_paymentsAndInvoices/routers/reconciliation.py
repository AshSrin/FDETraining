from fastapi import APIRouter, HTTPException
import services.reconcilation as reconcilation_service

router = APIRouter()

@router.post("/reconcile")
def reconcile():
    try:
        reconciled_payments = reconcilation_service.run_reconciliation()
        return {"message": "Reconciliation successful", "reconciled_payments": reconciled_payments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")