

import json


with open('data/invoice.json') as f:
    invoices = json.load(f)
vendorTotal = {}

for invoice in invoices:
   
    vendor = invoice["vendor"]
    vendorTotal[vendor] = vendorTotal.get(vendor, 0) + invoice["amount"]
print(vendorTotal)


seen=set()
duplicates=[]
for invoice in invoices:
   
    if invoice["invoice_id"] in seen:
        duplicates.append(invoice)
   
    seen.add(invoice["invoice_id"])



for invoice in duplicates:
     print(invoice)
     