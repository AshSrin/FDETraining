
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from routers.invoices import router as invoices_router
# pyrefly: ignore [missing-import]
from routers.payments import router as payments_router
# pyrefly: ignore [missing-import]
from routers.reconciliation import router as reconciliation_router

# Create the FastAPI app
app = FastAPI()
app.include_router(invoices_router)
app.include_router(payments_router)
app.include_router(reconciliation_router)