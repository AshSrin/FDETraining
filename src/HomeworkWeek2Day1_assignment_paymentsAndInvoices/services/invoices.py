import repository.invoices as repo
from models.invoices import Invoice

# Read all invoices from the JSON file with return type as list of Invoice objects
def get_all_invoices()->list[Invoice]:
    invoices_data = repo.load_invoices()
    return [Invoice(**invoice) for invoice in invoices_data]


# Write all invoices to the JSON file and return type as list of Invoice objects
def write_all_invoices(invoices: list[Invoice]) -> list[Invoice]:
    invoices_data = [invoice.__dict__ for invoice in invoices]
    repo.write_all_invoices(invoices_data)
    return invoices

# Add invoice to the JSON file and return type as Invoice object
def add_invoice(invoice: Invoice) -> Invoice:
    repo.add_invoice(invoice.__dict__)
    return invoice  

# get invoice by invoice_id and return type as Invoice object
def get_invoice_by_id(invoice_id: str) -> Invoice | None:
    invoice_data = repo.get_invoice_by_id(invoice_id)
    if invoice_data:
        return Invoice(**invoice_data)
    return None

#Update invoice by invoice_id in json file 
def update_invoice(invoice_id: str, updated_invoice: Invoice) -> bool:
    # if invoice id exists, update the invoice and return updated invoices
   existing= get_invoice_by_id(invoice_id)
   if not existing:
       return None
   updated_data = updated_invoice.__dict__
   updated_data['invoice_id'] = invoice_id
   repo.update_invoice(invoice_id, updated_data)
   return Invoice(**updated_data)

# delete invoice by invoice_id in json file and return 
def delete_invoice(invoice_id: str) -> bool:
    exist = repo.get_invoice_by_id(invoice_id)
    if exist:
        repo.delete_invoice(invoice_id)
        return True
    return False


#normalise the vendor name in  invoice data to remove empty spaces and convert to lowercase and return normalized invoice object 
def normalize_invoice(invoice: Invoice) -> Invoice:
    invoice.vendor_name = invoice.vendor_name.strip().lower()
    return invoice

# Exact duplicates. Build an exact_dupes dict that maps each duplicated key to a list of its indexes. 
# Keep the first row of each group and remove the rest.
#return a dictionary of exact duplicates
def find_exact_duplicates(invoices: list[Invoice]) -> dict:
    exact_dupes = {}
    for i, invoice in enumerate(invoices):
        key = (invoice.invoice_id, invoice.vendor_name, invoice.amount, invoice.status, invoice.approval)
        if key in exact_dupes:
            exact_dupes[key].append(i)
        else:
            exact_dupes[key] = [i]
        
    return exact_dupes


#Remove duplicates from the invoices list based on the exact_dupes dictionary and return the updated invoices list
def remove_exact_duplicates(invoices: list[Invoice]) -> list[Invoice]:
    exact_dupes = find_exact_duplicates(invoices)
    indexes_to_remove = [indexes[1:] for indexes in exact_dupes.values() if len(indexes) > 1]
    indexes_to_remove = [index for sublist in indexes_to_remove for index in sublist]
    updated_invoices = [invoice for i, invoice in enumerate(invoices) if i not in indexes_to_remove]
    return updated_invoices

# Report any row where amount is None, with its index, and exclude it in to another list of invoices with non-null amounts and return the list of invoices with non-null amounts
def findnullinvoices(invoices: list[Invoice]) -> list[Invoice]:
    null_invoices = []
    for i, invoice in enumerate(invoices):
        if invoice.amount is None:
            null_invoices.append((i, invoice))
    return null_invoices

# remove the null amount invoices from the list of invoices
def removenullinvoices(invoices: list[Invoice]) -> list[Invoice]:
    return [invoice for invoice in invoices if invoice.amount is not None]



#find  Suspected duplicates. Find rows that match on vendor, amount and date but have different IDs. Print them as pairs, (INV-107 ~ INV-101), and don't remove them.   
def find_suspected_duplicates(invoices: list[Invoice]) -> list[tuple[Invoice, Invoice]]:
    suspected_dupes = []
    for i, invoice1 in enumerate(invoices):
        for j, invoice2 in enumerate(invoices):
            if i < j and invoice1.vendor_name == invoice2.vendor_name and invoice1.amount == invoice2.amount and invoice1.date == invoice2.date and invoice1.invoice_id != invoice2.invoice_id:
                suspected_dupes.append((invoice1, invoice2))
    return suspected_dupes

#Credit notes. 
# #Match each negative invoice to its positive partner. 
# Mark both as "CANCELLED" and exclude them from totals. Print the index pair, for example
#  3 <-> 6. Handle a credit note with no partner.
#return  invoices list with credit notes processed
def process_credit_notes_and_refunds(invoices: list[Invoice], payments: list[Payment]) -> None:
    for i, invoice in enumerate(invoices):
        if invoice.amount < 0:
            partner_found = False
            for j, partner_invoice in enumerate(invoices):
                if (partner_invoice.amount == -invoice.amount and
                    partner_invoice.vendor_name == invoice.vendor_name and
                    partner_invoice.date == invoice.date and
                    partner_invoice.invoice_id != invoice.invoice_id):
                    invoices[i].status = "CANCELLED"
                    invoices[j].status = "CANCELLED"
                    print(f"Credit note {invoice.invoice_id} matched with {partner_invoice.invoice_id}")
                    partner_found = True
                    break
            if not partner_found:
                print(f"Credit note {invoice.invoice_id} has no matching positive invoice.")
    return invoices