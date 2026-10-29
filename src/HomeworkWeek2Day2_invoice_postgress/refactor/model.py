from pydantic import BaseModel


class Invoice(BaseModel):
    invoice_id: str
    vendor: str
    amount: float | None
    status: str
    approval: str


