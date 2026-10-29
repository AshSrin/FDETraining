from fastapi import FastAPI 
from getEmployee import router as employee_router
from createEmployee import router as create_employee_router


app = FastAPI()
app.include_router(employee_router)
app.include_router(create_employee_router)

