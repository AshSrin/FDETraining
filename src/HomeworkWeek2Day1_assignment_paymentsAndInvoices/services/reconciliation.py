from services.invoices import (get_all_invoices,
                              normalize_invoice,
                              findnullinvoices,
                              removenullinvoices,
                                find_exact_duplicates,   
                              remove_exact_duplicates,
                              process_credit_notes_and_refunds)
from services.payments import (get_all_payments,
                               normalize_payment,
                               findnullpayments,
                               removenullpayments,
                               find_exact_duplicates as find_exact_payment_duplicates,
                               remove_exact_duplicates as remove_exact_payment_duplicates)


def run_reconciliation():
    # Load invoices and payments
    invoices = get_all_invoices()
    payments = get_all_payments()

    # Normalize data
    normalized_invoices = [normalize_invoice(invoice) for invoice in invoices]
    

    # Find and remove null values
    null_invoices = findnullinvoices()
   
    
    removenullinvoices()


    # Find and remove exact duplicates
    exact_invoice_duplicates = find_exact_duplicates(normalized_invoices)
    exact_payment_duplicates = find_exact_payment_duplicates(normalized_payments)

    remove_exact_duplicates(normalized_invoices)
    remove_exact_payment_duplicates(normalized_payments)

    # Process credit notes and refunds
    process_credit_notes_and_refunds(normalized_invoices, normalized_payments)