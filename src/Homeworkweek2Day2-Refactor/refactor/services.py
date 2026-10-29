import repository
from model import Invoice


def create_invoice(invoice: Invoice) -> Invoice:
    repository.add_invoice(invoice.dict())
    return invoice


def get_invoices(invoice_id: str) -> Invoice:
    invoice = repository.find_invoice_by_id(invoice_id)
    if invoice is None:
        raise ValueError(f"Invoice with ID {invoice_id} not found")
    return Invoice(**invoice)


def delete_invoice(invoice_id: str) -> None:
    success = repository.delete_invoice(invoice_id)
    if not success:
        raise ValueError(f"Invoice with ID {invoice_id} not found")


def update_invoice(invoice_id: str, updated_invoice: Invoice) -> Invoice:
    success = repository.update_invoice(invoice_id, updated_invoice.dict())
    if not success:
        raise ValueError(f"Invoice with ID {invoice_id} not found")
    return updated_invoice

  

