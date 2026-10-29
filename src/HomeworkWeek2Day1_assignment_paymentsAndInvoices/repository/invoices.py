import json
DATA_FILE="src/HomeworkWeek2Day1_assignment_paymentsAndInvoices/data.json"


def load_invoices():
    with open(DATA_FILE, 'r') as file:
        return json.load(file)["invoices"]


# Write all invoices to the JSON file
def write_all_invoices(invoices: list) -> None:
    with open(DATA_FILE, 'w') as file:
        json.dump({"invoices": invoices}, file, indent=4)


#Add invoice to the JSON file
def add_invoice(invoice: dict) -> None:
    invoices = load_invoices()
    invoices.append(invoice)
    write_all_invoices(invoices)

#get invoice by invoice_id
def get_invoice_by_id(invoice_id: str) -> dict | None:
    invoices = load_invoices()
    for invoice in invoices:
        if invoice["invoice_id"] == invoice_id:
            return invoice
    return None

#update invoice by invoice_id in json file  
def update_invoice(invoice_id: str, updated_invoice: dict) -> bool:
    invoices = load_invoices()
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            invoices[i] = updated_invoice
            write_all_invoices(invoices)
            return True
    return False

# delete invoice by invoice_id in json file  
def delete_invoice(invoice_id: str) -> bool:
    invoices = load_invoices()
    for i, invoice in enumerate(invoices):
        if invoice["invoice_id"] == invoice_id:
            del invoices[i]
            write_all_invoices(invoices)
            return True
    return False

# Normalize the invoices by removing extra spaces and changing the status to upper case
def normalize_invoices(invoices: list[dict]) -> list[dict]:
    for invoice in invoices:
        if 'vendor' in invoice and invoice['vendor']:
            invoice['vendor'] = invoice['vendor'].strip().title()
        if 'status' in invoice and invoice['status']:
            invoice['status'] = invoice['status'].upper()
    return invoices


# Exact duplicates. Build an exact_dupes dict that maps each duplicated key to a list of its indexes. 
# Keep the first row of each group and remove the rest.
def find_exact_duplicates(invoices: list[dict]) -> dict:
    exact_dupes = {}
    for index, invoice in enumerate(invoices):
        # Sort items to ensure stable hashing
        items = tuple(sorted((k, v) for k, v in invoice.items() if isinstance(v, (str, int, float, bool, type(None)))))
        if items in exact_dupes:
            exact_dupes[items].append(index)
        else:
            exact_dupes[items] = [index]
    return exact_dupes


# remove the duplicates from the list of invoices
def remove_duplicates(invoices: list[dict], exact_dupes: dict) -> list[dict]:
    indices_to_remove = set()
    for indices in exact_dupes.values():
        indices_to_remove.update(indices[1:])
    return [inv for idx, inv in enumerate(invoices) if idx not in indices_to_remove]


# Report any row where amount is None, with its index, and exclude it from the later totals.
def find_amount_null(invoices: list[dict]) -> list:
    null_amount_invoices = []
    for index, invoice in enumerate(invoices):
        if invoice.get('amount') is None:
            null_amount_invoices.append((index, invoice))
    return null_amount_invoices


# remove the null amount invoices from the list of invoices
def remove_null_amount_invoices(invoices: list[dict]) -> list[dict]:
    return [invoice for invoice in invoices if invoice.get('amount') is not None]


# Suspected duplicates. Find rows that match on vendor, amount and date but have different IDs. 
# Print them as pairs, (INV-107 ~ INV-101), and don't remove them.
def find_suspected_duplicates(invoices: list[dict]) -> list:
    suspected_dupes = []
    for index, invoice in enumerate(invoices):
        for index2, invoice2 in enumerate(invoices):
            if (index < index2 and 
                invoice.get('vendor') == invoice2.get('vendor') and 
                invoice.get('amount') == invoice2.get('amount') and 
                invoice.get('date') == invoice2.get('date')):
                suspected_dupes.append((index, index2))
    return suspected_dupes
