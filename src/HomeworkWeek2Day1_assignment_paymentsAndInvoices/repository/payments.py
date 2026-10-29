import json
DATA_FILE="src/HomeworkWeek2Day1_assignment_paymentsAndInvoices/data.json"

def read_payments():
    with open(DATA_FILE, 'r') as file:
      return json.load(file)["payments"]    

#get payments by invoice_id    
       
def get_payments_by_invoice_id(invoice_id):
    payments = read_payments()
    result = []
    for payment in payments:
        if payment["invoice_id"] == invoice_id:
            result.append(payment)
    return result

#write to payments json file
def write_all_payments(payments: list) -> None:
    with open(DATA_FILE, 'w') as file:
        json.dump({"payments": payments}, file, indent=4)   

#Add payment to the JSON file
def add_payment(payment: dict) -> None:
    payments = read_payments()
    payments.append(payment)
    write_all_payments(payments)

#update payment by invoice_id in json file
def update_payment(invoice_id: str, updated_payment: dict) -> None:
    payments = read_payments()
    for i, payment in enumerate(payments):
        if payment["invoice_id"] == invoice_id:
            payments[i] = updated_payment
            write_all_payments(payments)
            return 
    raise ValueError(f"Payment with invoice_id {invoice_id} not found.")


# delete payment by invoice_id in json file
def delete_payment(invoice_id: str, paid: float) -> bool:
    payments = read_payments()
    for i, payment in enumerate(payments):
        if payment["invoice_id"] == invoice_id and payment["paid"] == paid:
            del payments[i]
            write_all_payments(payments)
            return
    raise ValueError(f"Payment with invoice_id {invoice_id} and paid amount {paid} not found.") 
    
