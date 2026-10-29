invoices=[
        {"invoiceid": 1, "vendor": "Vendor A", "amount": 100.0, "status": "Pending", "approval": "Approved"},
        {"invoiceid": 2, "vendor": "Vendor B", "amount": 200.0, "status": "Approved", "approval": "Approved"},
        {"invoiceid": 3, "vendor": "Vendor A", "amount": 3000.0, "status": "Pending", "approval": "Pending"},
        

]

for invoice in invoices:
    if invoice["status"]=="Pending":
        print(f"Invoice ID: {invoice['invoiceid']}, Vendor: {invoice['vendor']}, Amount: {invoice['amount']}, Status: {invoice['status']}, Approval: {invoice['approval']}")    


sorter_invoices=sorted(invoices,key=lambda x:x["amount"],reverse=True)  
print("\nInvoices sorted by amount in descending order:")
for invoice in sorter_invoices:
    print(f"Invoice ID: {invoice['invoiceid']}, Vendor: {invoice['vendor']}, Amount: {invoice['amount']}, Status: {invoice['status']}, Approval: {invoice['approval']}")



vendor_totals={}    
for invoice in invoices:
    print(f"Invoice: {invoice}")
    vendor = invoice["vendor"]
    amount = invoice["amount"]
    vendor_totals[vendor] = vendor_totals.get(vendor, 0) + amount
    print(f"Vendor: {vendor}, Total Amount: {vendor_totals[vendor]}")
print("\nTotal amount of invoices for each vendor:")
for vendor, total in vendor_totals.items():
    print(f"Vendor: {vendor}, Total Amount: {total}")



    
groupBy_vendor={}
for invoice in invoices:
    vendor=invoice["vendor"]
    if vendor not in groupBy_vendor:
        groupBy_vendor[vendor]=[]
    groupBy_vendor[vendor].append(invoice)
print("\nInvoices grouped by vendor:")
for vendor, invoices in groupBy_vendor.items():
    print(f"Vendor: {vendor}")
    for invoice in invoices:
        print(f"  Invoice ID: {invoice['invoiceid']}, Amount: {invoice['amount']}, Status: {invoice['status']}, Approval: {invoice['approval']}")



