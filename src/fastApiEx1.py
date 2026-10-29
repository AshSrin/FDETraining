from fastApiEx1 import FastAPI
app=FastAPI()
invoices=[  ]
@app.get("/invoices")
def invoices():
    return invoices