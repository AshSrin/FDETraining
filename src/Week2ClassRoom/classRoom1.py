invoices=[
    {
    "invoice_id": "INV001",
    "vendor": "Vendor A",
    "amount": 100.0,
    "status": "Pending",
    "approval": "Approved"
    },
    {
        "invoice_id": "INV002",
        "vendor": "Vendor B",
        "amount": 100.0,
        "status": "Pending",
        "approval": "Approved"
        },
    {
        "invoice_id": "INV002",
        "vendor": "Vendor B",
        "amount": 3000.0,
        "status": "Pending",
        "approval": "Pending"
    },
    {
            "invoice_id": "INV001",
            "vendor": "Vendor A",
            "amount": 3000.0,
            "status": "Pending",
            "approval": "Pending"
        },

]

invoiceTotals={}
for invoice in invoices:    
    print(f"Invoice: {invoice}")
    vendor = invoice["vendor"]      
    amount = invoice["amount"]
    invoiceTotals[vendor] = invoiceTotals.get(vendor, 0) + amount
for vendor in invoiceTotals:
    print(f"Vendor: {vendor}, Total Amount: {invoiceTotals[vendor]}")   


duplicate_invoices = []
seen_invoices = set()
for invoice in invoices:
    invoice_id = invoice["invoice_id"]
    if invoice_id in seen_invoices:
        duplicate_invoices.append(invoice)
    else:
        seen_invoices.add(invoice_id)   
for invoice in duplicate_invoices:
    print(f"Duplicate Invoice: {invoice}")