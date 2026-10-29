employee=[{"name": "Johnnny","id":111, "salary": 50000}, {"name": "Janeysa", "id":112,"salary": 60000}, {"name": "Bobbobb", "id":113, "salary": 55000}]
for emp in employee:
    if len(emp["name"])>6 and (emp["salary"]>54000):
        print(f"Employee Name: {emp['name']}")
        print(f"Employee ID: {emp['id']}")
        print(f"Employee Salary: {emp['salary']}")
    else:
        print(f"Employee Name: {emp['name']} does not meet the criteria.")