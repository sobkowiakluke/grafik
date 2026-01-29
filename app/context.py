# app/context.py
from app.db.connection import Database
from app.services.employee_service import EmployeeService
from app.services.schedule_day_service import ScheduleDayService
from app.services.schedule_service import ScheduleService

# 1. Singleton do bazy
db = Database()  # tu używamy już gotowego singletona lub parametrów z config

# 2. Serwisy
employee_service = EmployeeService(db)
day_service = ScheduleDayService(db)
schedule_service = ScheduleService(db, day_service)
