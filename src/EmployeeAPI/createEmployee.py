from fastapi import FastAPI
from dataSource import employees
from models import Employee
from fastapi import APIRouter

router = APIRouter()

@router.post("/createEmployee")
def create_employee(employee: Employee):
    employees.append(employee.model_dump())
    return {"message": "Employee created successfully here", "employee": {"id": employee.id, "name": employee.name, "salary": employee.salary}  }





