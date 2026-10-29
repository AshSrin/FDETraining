import repository.payments as repo
from models.payments import Payment

# Read the payments from the JSON file
def get_all_payments() -> list[Payment]:
    payments_data = repo.read_payments()
    return [Payment(**payment) for payment in payments_data]

# Write all payments to the JSON file
def write_all_payments(payments: list[Payment]) -> None:
    payments_data = [payment.__dict__ for payment in payments]
    repo.write_all_payments(payments_data)  

# create a new payment and add it to the JSON file
def add_payment(payment: Payment) -> Payment:
    repo.add_payment(payment.__dict__)
    return payment  

# Update the payment in the JSON file, if id exists, update the payment and return updated payment
def update_payment(invoice_id: str, updated_payment: Payment) -> Payment | None:
    existing = repo.get_payments_by_invoice_id(invoice_id)   
    if not existing:
        return None
    updated_data = updated_payment.__dict__
    updated_data['invoice_id'] = invoice_id
    repo.update_payment(invoice_id, updated_data)
    return Payment(**updated_data)


# Delete the payment from the JSON file ,if id exists, delete the payment and return True, else return False
def delete_payment(invoice_id: str, paid: float) -> bool:
    try:
        repo.delete_payment(invoice_id, paid)
        return True
    except ValueError:
        return False

