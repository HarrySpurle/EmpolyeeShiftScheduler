from datetime import date, timedelta
import Database_Controller

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class Employee:
    """
    Stores information about an employee.
    """

    def __init__(self, id):
        """
        Assigns attributes to data given.
        """

        information = Database_Controller.find_employee(id)
        self.minimum_hours = float(information[10]) if information[10] != None else 0
        self.maximum_hours = float(information[11]) if information[11] != None else float('inf')
        self.rate = float(information[7]) if information[7] != None else float('inf')
        self.current_hours = 0
        self.scheduled_days = set()  # Track days the employee is scheduled

    def increase_hours(self, shift_id):
        """
        Increases the current hours attribute by the length of a shift.
        """

        start_time, end_time, date = Database_Controller.get_shift_times(shift_id)
        start_hour, start_min = map(int, str(start_time).split("."))
        end_hour, end_min = map(int, str(end_time).split("."))

        delta_time = ((end_hour * 60 + end_min) - (start_hour * 60 + start_min)) / 60
        self.current_hours += delta_time

    def is_available_for_day(self, date):
        """
        Check if the employee is already scheduled for the day.
        """
        return date not in self.scheduled_days

    def mark_scheduled_for_day(self, date):
        """
        Mark the employee as scheduled for a particular day.
        """
        self.scheduled_days.add(date)


def create_employees(user_id):
    """
    Creates a dictionary of instances of employee class.
    """

    employee_ids = [
        Database_Controller.find_employee_id(*person.split(" "))[0]
        for person in Database_Controller.get_employees(user_id)
    ]
    return {f"employee_id_{id}": Employee(id) for id in employee_ids}


def get_shifts_in_week(user_id):
    """
    Returns a list of the shifts in a given week.
    """

    business_id = Database_Controller.find_employee(user_id)[1]
    monday_this_week = date.today() - timedelta(days=date.today().isoweekday() - 1)
    week_dates = [(monday_this_week + timedelta(days=i)).strftime('%d-%m-%Y') for i in range(7)]
    
    return [
        Database_Controller.get_shifts(business_id, day) + Database_Controller.get_shifts(business_id, week_date)
        for day, week_date in zip(DAYS_OF_WEEK, week_dates)
    ]


def clear_shifts(user_id, shifts):
    """
    Removes all shifts in the week from the database.
    """

    employee_ids = [
        Database_Controller.find_employee_id(*person.split(" "))[0]
        for person in Database_Controller.get_employees(user_id)
    ]
    
    for day in shifts:
        for shift_id, *_ in day:
            for emp_id in employee_ids:
                try:
                    Database_Controller.remove_employee_from_shift(emp_id, shift_id)
                except:
                    pass  


def find_available_employees(shifts):
    """
    Finds the employees who are available to work each shift in the week.
    """

    available = []
    
    for day in shifts:
        used_employees = []
        for shift in day:
            shift_id, business_id, start_time, end_time, cal_date, _, position_required = shift[:7]
            available_employees = [
                emp for emp in Database_Controller.get_available_employees(business_id, position_required, cal_date, start_time, end_time)
                if Database_Controller.find_if_employee_available(emp, shift_id)
            ]
            used_employees.append(emp for emp in available_employees)
            available.append((shift_id, available_employees))
    
    return available


def find_optimal_employees(available_employees, employees):
    """
    Ranks the employees to create an optimal assignment of workers.
    """

    employees_working = []

    for shift_id, employee_ids in available_employees:
        shift_info = Database_Controller.get_shift_info(shift_id)
        num_required = int(shift_info[-2])
        employees_working_shift = []
        shift_date = shift_info[4]

        for employee in employee_ids:
            emp_obj = employees[f"employee_id_{employee}"]
            if emp_obj.current_hours < emp_obj.maximum_hours and emp_obj.current_hours <= emp_obj.minimum_hours and emp_obj.is_available_for_day(shift_date):
                employees_working_shift.append(employee)
                emp_obj.increase_hours(shift_id)
                emp_obj.mark_scheduled_for_day(shift_date)
                if len(employees_working_shift) >= num_required:
                    break

        if len(employees_working_shift) < num_required:
            eligible_employees = [
                (emp, employees[f"employee_id_{emp}"].rate)
                for emp in employee_ids
                if emp not in employees_working_shift and employees[f"employee_id_{emp}"].current_hours < employees[f"employee_id_{emp}"].maximum_hours and employees[f"employee_id_{emp}"].is_available_for_day(shift_date)
            ]
            eligible_employees.sort(key=lambda x: x[1])

            for emp, _ in eligible_employees:
                employees_working_shift.append(emp)
                employees[f"employee_id_{emp}"].increase_hours(shift_id)
                employees[f"employee_id_{emp}"].mark_scheduled_for_day(shift_date)
                if len(employees_working_shift) >= num_required:
                    break

        employees_working.append((shift_id, employees_working_shift))

    return employees_working


def assign_shifts(assignments):
    """
    Adds the employees and shifts to the database.
    """

    for shift_id, employee_list in assignments:
        for employee in employee_list:
            Database_Controller.assign_shift(employee, shift_id, 1)


def create_new_schedule(user_id):
    """
    Generates a new, optimal, schedule.
    """

    employees = create_employees(user_id)
    shifts = get_shifts_in_week(user_id)
    clear_shifts(user_id, shifts)
    available_employees = find_available_employees(shifts)
    optimal_employees = find_optimal_employees(available_employees, employees)
    assign_shifts(optimal_employees)


def clear_schedule(user_id):
    """
    Clears the current schedule from the database.
    """
    
    shifts = get_shifts_in_week(user_id)
    clear_shifts(user_id, shifts)
