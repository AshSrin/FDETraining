from fastapi import FastAPI
from dataSource import employees
from fastapi import APIRouter


router = APIRouter()

@router.get("/employees")
def get_employees():
    return employees

@router.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return {"error": "Employee not found"}
