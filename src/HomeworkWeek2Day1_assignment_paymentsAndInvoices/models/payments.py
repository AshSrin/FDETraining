from pydantic import BaseModel

class Payment(BaseModel):
    invoice_id: str
    paid: float
