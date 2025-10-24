import sqlite3, os, Password_Hasher, re
from datetime import date, timedelta

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def create_tables():
    """
    Initialise the database, create the tables and add the statuses to the table.
    """
    
    connectionHandler = sqlite3.connect('Database.db')
    cursor = connectionHandler.cursor()

    cursor.execute("CREATE TABLE Business(business_id INTEGER PRIMARY KEY, name TEXT, address TEXT)")
    cursor.execute("CREATE TABLE Business_Settings(setting_id INTEGER PRIMARY KEY, business_id INTEGER, key TEXT, value INTEGER)")
    cursor.execute("CREATE TABLE Employees(employee_id INTEGER PRIMARY KEY, business_id INTEGER, first_name TEXT, last_name TEXT, email TEXT, phone_number TEXT, position_id INTEGER, hourly_rate FLOAT, hire_date DATE, photo BLOB, minimum_hours INTEGER, maximum_hours INTEGER, password_hashed TEXT)")
    cursor.execute("CREATE TABLE Positions(position_id INTEGER PRIMARY KEY, business_id INTEGER, position_name TEXT, description TEXT)")
    cursor.execute("CREATE TABLE Shifts(shift_id INTEGER PRIMARY KEY, business_id INTEGER, start_time TEXT, end_time TEXT, shift_date TEXT, employees _required INTEGER, role_required INTEGER)")
    cursor.execute("CREATE TABLE Employee_Shifts(employee_id INTEGER, shift_id INTEGER, status INTEGER, notes TEXT, PRIMARY KEY (employee_id, shift_id))")
    cursor.execute("CREATE TABLE Statuses(status_id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("CREATE TABLE Time_Off(timeoff_id INTEGER PRIMARY KEY, employee_id INTEGER, start_date TEXT, end_date Text, start_time TEXT, end_time Text, status_id INTEGER, notes TEXT)")    
    
    stati = ['Pending', 'Approved', 'Rejected', 'Published']
    for status in stati:
        cursor.execute(f"INSERT INTO Statuses(name) VALUES ('{status}')")

    connectionHandler.commit()
    connectionHandler.close()


def connect_to_database():
    """
    Connect to the database so that it can be accessed and ammended.
    """

    if not os.path.isfile("Database.db"):
        create_tables()  
        connectionHandler = sqlite3.connect('Database.db')
        cursor = connectionHandler.cursor()

    else:
        connectionHandler = sqlite3.connect('Database.db')
        cursor = connectionHandler.cursor()

    return cursor, connectionHandler


def add_business(business_name, business_address):
    """
    Add a businesses information to the database.
    """

    cursor, connectionHandler = connect_to_database()
    cursor.execute(f"INSERT INTO Business(name, address) VALUES ('{business_name}','{business_address}')")

    connectionHandler.commit()
    connectionHandler.close()


def add_employee(business_id, first_name, last_name, email, phone_number, position_id, hourly_rate, photo, minimum_hours, maximum_hours, password):  
    """
    Adds a new employees information to the database.
    """

    cursor, connectionHandler = connect_to_database()

    hire_date = date.today()
    password_hashed = Password_Hasher.hash_password(password)
    if photo == None:
        pass
        #photo = image_to_blob('UserImage.jpg')
    cursor.execute(f"INSERT INTO Employees(business_id, first_name, last_name, email, phone_number, position_id, hourly_rate, hire_date, photo, minimum_hours, maximum_hours, password_hashed) VALUES ('{business_id}', '{first_name}', '{last_name}', '{email}', '{phone_number}', '{position_id}', '{hourly_rate}', '{hire_date}', ?, '{minimum_hours}', '{maximum_hours}', '{password_hashed}')", ([photo]))
    
    connectionHandler.commit()
    connectionHandler.close()


def add_position(business_id, position_name, position_description):
    """
    Add a job position to the business and return its id.
    """

    cursor, connectionHandler = connect_to_database()

    cursor.execute(f"INSERT INTO Positions(business_id, position_name, description) VALUES ('{business_id}','{position_name}','{position_description}')")
    position_id = cursor.execute("SELECT MAX (position_id) FROM Positions").fetchone()

    connectionHandler.commit()
    connectionHandler.close()

    return position_id[0]


def add_shift(business_id, position, num_employees, shift_date, start_time, end_time):
    """
    Add a shift to the business
    """

    cursor, connectionHandler = connect_to_database()

    cursor.execute(f"INSERT INTO Shifts(business_id, start_time, end_time, shift_date, employees, role_required) VALUES ('{business_id}','{start_time}','{end_time}','{shift_date}','{num_employees}','{position}')")

    connectionHandler.commit()
    connectionHandler.close()


def update_employee(first_name, last_name, email, phone_number, hourly_rate, minimum_hours, maximum_hours, file_path, id):
    """
    Update an employee's profile with newly entered information.
    """

    fields = ['first_name', 'last_name', 'email', 'phone_number', 'hourly_rate', 'minimum_hours', 'maximum_hours']
    updated_details = [first_name, last_name, email, phone_number, hourly_rate, minimum_hours, maximum_hours]
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    phone_pattern = r"^\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$"

    try:
        cursor, connection = connect_to_database()

        id = str(id)
        current_details = cursor.execute(
            f"SELECT first_name, last_name, email, phone_number, hourly_rate, minimum_hours, maximum_hours, photo FROM employees WHERE employee_id = {id}").fetchone()

        if not current_details:
            return False

        new_details = [new if new != '' else current for new, current in zip(updated_details, current_details[:-1])]
        
        new_details = [None if val == 'None' else val for val in new_details]

        for i, field in enumerate(['hourly_rate', 'minimum_hours', 'maximum_hours'], 4):
            if new_details[i] is not None:
                try:
                    value = float(new_details[i])
                    if (i == 4 and value <= 0) or (i in [5, 6] and value < 0):
                        return False
                    new_details[i] = value
                except ValueError:
                    return False

        try:
            new_photo = image_to_blob(file_path) if file_path else current_details[-1]
        except Exception:
            new_photo = current_details[-1]
        
        if (new_details[5] is None or new_details[6] is None or (new_details[5] is not None and new_details[6] is not None and new_details[5] < new_details[6])) and (new_details[3] is None or bool(re.match(phone_pattern, new_details[3]))) and (new_details[2] is None or bool(re.match(email_pattern, new_details[2]))):
            update_query = f"""
                UPDATE employees
                SET {', '.join(f"{field} = ?" for field in fields)}, photo = ?
                WHERE employee_id = ?
            """
            cursor.execute(update_query, (*new_details, new_photo, id))
        
            connection.commit()
            connection.close()
        else:
            connection.commit()
            connection.close()
            return False

    except sqlite3.Error:
        return False


def update_password(password, employee_id):
    """
    Update the password to an employees account
    """
    cursor, connectionHandler = connect_to_database()

    password_hashed = Password_Hasher.hash_password(str(password))
    
    cursor.execute(f"UPDATE Employees SET password_hashed = '{password_hashed}' WHERE employee_id = '{int(employee_id)}'")

    connectionHandler.commit()
    connectionHandler.close()


def update_time_off_status(status_id, time_id):
    """
    Update the status of a time off request.
    """

    cursor, connectionHandler = connect_to_database()

    cursor.execute(f"UPDATE Time_Off SET status_id = {status_id} WHERE timeoff_id = {time_id}").fetchone()

    connectionHandler.commit()
    connectionHandler.close()


def add_time_off(employee_id, start_date, end_date, start_time, end_time, status_id, notes):
    """
    Add an employees time off request to the database.
    """

    cursor, connectionHandler = connect_to_database()

    cursor.execute(f"INSERT INTO Time_Off(employee_id, start_date, end_date, start_time, end_time, status_id, notes) VALUES ('{employee_id}', '{start_date}', '{end_date}', '{start_time}', '{end_time}', '{status_id}', '{notes}')")

    connectionHandler.commit()
    connectionHandler.close()


def assign_shift(employee_id, shift_id, shift_status):
    """
    Add an employee to a shift.
    """

    cursor, connectionHandler = connect_to_database()

    cursor.execute(f"INSERT INTO Employee_Shifts(employee_id, shift_id, status) VALUES ('{employee_id}', '{shift_id}', '{shift_status}')")

    connectionHandler.commit()
    connectionHandler.close()


def employee_login(first_name, last_name, password):
    """
    Check the details of an employee against those entered to verify a login.
    """

    cursor, connectionHandler = connect_to_database()

    try:
        id, employees_password =cursor.execute(f"""SELECT employee_id, password_hashed FROM Employees WHERE first_name = '{first_name}' AND last_name = '{last_name}'""").fetchone()
    
        if Password_Hasher.verify_password(str(password),employees_password):
            return id, True
        
        return None, False
    
    except sqlite3.Error:
        return None, False


def find_new_business():
    """
    Return the ID of the latest created business.
    """

    cursor, connectionHandler = connect_to_database()

    business_id = cursor.execute("SELECT MAX (business_id) FROM Business").fetchone()

    return business_id[0]


def find_new_employee():
    """
    Return the ID of the latest created employee.
    """

    cursor, connectionHandler = connect_to_database()

    business_id = cursor.execute("SELECT MAX (employee_id) FROM Employees").fetchone()

    return business_id[0]


def find_status_name(id):
    """
    Find the title of a status from its ID.
    """

    cursor, connectionHandler = connect_to_database()

    status = cursor.execute(f"SELECT name FROM Statuses WHERE status_id = '{id}'").fetchone()

    return status


def find_employee(id):
    """
    Return the information of an employee found by their ID
    """

    cursor, connectionHandler = connect_to_database()

    details = cursor.execute(f"SELECT * FROM Employees WHERE employee_id = '{id}'").fetchmany()[0]

    return details


def find_num_of_employees_working(id):
    """
    Return the number of employees working on a shift
    """

    cursor, connectionHandler = connect_to_database()

    details = cursor.execute(f"SELECT * FROM Employee_Shifts WHERE shift_id = '{id}'").fetchall()

    return len(details)


def find_employee_id(first_name, last_name):
    """
    Return the ID of an employee found by their name
    """

    cursor, connectionHandler = connect_to_database()

    id = cursor.execute(f"SELECT employee_id FROM Employees WHERE first_name = '{str(first_name)}' and last_name = '{str(last_name)}'").fetchone()

    return id


def find_business(id):
    """
    Return the information of a business found by it's ID
    """

    cursor, connectionHandler = connect_to_database()

    details = cursor.execute(f"SELECT name FROM Business WHERE business_id = '{id}'").fetchone()

    return details[0]


def find_position(id):
    """
    Return the name of a position found by its ID
    """

    cursor, connectionHandler = connect_to_database()

    details = cursor.execute(f"SELECT position_name FROM Positions WHERE position_id = '{id}'").fetchone()

    return details[0]


def find_if_employee_available(employee_id, shift_id):
    """
    Find if an employee found by their ID is available to work a shift find by its ID.
    """

    cursor, connectionHandler = connect_to_database()
    shift_date, start_time, end_time = cursor.execute(f"SELECT shift_date, start_time, end_time FROM Shifts WHERE shift_id = '{shift_id}'").fetchall()[0]

    try:
        day, month, year = str(shift_date).split("-")
        weekday = date(int(year),int(month),int(day)).isoweekday()
        day_of_week = DAYS_OF_WEEK[weekday-1]

    except ValueError:
        day_of_week = shift_date

    working_shift_ids = cursor.execute(f"SELECT shift_id FROM Shifts WHERE shift_date = '{shift_date}' or shift_date = '{day_of_week}'").fetchall()
    for id in range(len(working_shift_ids)):
        shifts = cursor.execute(f"SELECT * FROM Employee_Shifts WHERE employee_id = '{employee_id}' and shift_id = '{str(working_shift_ids[id][0])}'").fetchall()
        if shifts != []:
            connectionHandler.commit()
            connectionHandler.close()
            return False
        else:
            pass

    connectionHandler.commit()
    connectionHandler.close()

    return True


def find_position_id(name, business_id):
    """
    Return the ID of a position given it's name and its business_id
    """

    cursor, connectionHandler = connect_to_database()

    details = cursor.execute(f"SELECT position_id FROM Positions WHERE position_name = '{name}' and business_id = '{business_id}'").fetchone()

    return details[0]


def get_assigned_shifts(business_id, day):
    """
    Find all shifts that have been assigned on a given day.
    """

    cursor, connectionHandler = connect_to_database()
    all_shifts = []
    assigned_shifts = []
    shift_ids = cursor.execute(f"SELECT shift_id FROM Shifts WHERE business_id = '{int(business_id)}' and shift_date = '{str(day)}'").fetchall()

    for i in range (len(shift_ids)):
        all_shifts.append(shift_ids[i][0])

    if all_shifts != []:
        for j in range(len(all_shifts)):
            employee_id = cursor.execute(f"SELECT employee_id FROM Employee_Shifts WHERE shift_id = '{all_shifts[j]}' ").fetchall()
            if employee_id != []:
                for i in range(len(employee_id)):
                    assigned_shifts.append([employee_id[i][0], all_shifts[j]])

    connectionHandler.commit()
    connectionHandler.close()

    return assigned_shifts


def get_positions(business_id):
    """
    Return a list containing all the position names within a business.
    """

    cursor, connectionHandler = connect_to_database()
    details = []

    positions = cursor.execute(f"SELECT position_name FROM Positions WHERE business_id = {(str(business_id))}").fetchall()

    connectionHandler.commit()
    connectionHandler.close()

    for i in range (len(positions)):
        details.append(positions[i][0])

    return details


def get_employees(business_id):
    """
    Get the names of an employees in a business.
    """

    employees = []

    cursor, connectionHandler = connect_to_database()
    
    employees_raw = cursor.execute(f"SELECT first_name, last_name FROM Employees WHERE business_id = '{business_id}'").fetchall()

    connectionHandler.commit()
    connectionHandler.close()

    for name in employees_raw:
        employees.append(name[0] + " " + name[1])

    return employees


def get_shifts(business_id, date):
    """
    Get the information about shifts in a business on  given day.
    """

    cursor, connectionHandler = connect_to_database()

    shifts = cursor.execute(f"SELECT * FROM Shifts WHERE business_id = '{business_id}' and shift_date = '{date}'").fetchall()

    connectionHandler.commit()
    connectionHandler.close()

    return shifts


def get_shift_times(shift_id):
    """
    Get the start and end times, and the date of a shift given its id.
    """

    cursor, connectionHandler = connect_to_database()

    times = cursor.execute(f"SELECT start_time, end_time, shift_date FROM Shifts WHERE shift_id = '{shift_id}'").fetchall()[0]

    connectionHandler.commit()
    connectionHandler.close()

    return times


def get_shift_status(employee_id, shift_id):
    """
    Get the status of a shift given its ID and the ID of the employee working it.
    """

    cursor, connectionHandler = connect_to_database()

    status = cursor.execute(f"SELECT status FROM Employee_Shifts WHERE shift_id = '{shift_id}' and employee_id = '{employee_id}'").fetchone()[0]

    connectionHandler.commit()
    connectionHandler.close()

    return status


def get_shift_info(shift_id):
    """
    Get all information about a shift with a given ID.
    """

    cursor, connectionHandler = connect_to_database()

    info = cursor.execute(f"SELECT * FROM Shifts WHERE shift_id = '{shift_id}'").fetchall()[0]

    connectionHandler.commit()
    connectionHandler.close()

    return info


def get_time_off_info(business_id, date_from):
    """
    Gets the time off requests for a business given a date and a business id.
    """

    cursor, connectionHandler = connect_to_database()
    all_entries = []
    time_off = []
    final = []
    cyear,cmonth,cday = str(date_from).split("-")

    employee_ids = cursor.execute(f"SELECT employee_id FROM Employees WHERE business_id = '{business_id}'").fetchall()

    for id in employee_ids:
        time_off = []
        
        details = cursor.execute(f"SELECT * FROM Time_Off WHERE employee_id = '{id[0]}'").fetchall()
        if details == []:
            final.append([])

        else:
            all_entries = []
            for i in range(len(details)):
                all_entries.append(details[i])
            for entry in all_entries:
                day,month,year = str(entry[2]).split("-")
                if date(int(year),int(month),int(day)) >= date(int(cyear),int(cmonth),int(cday)):
                    time_off.append(entry)
            final.append(time_off)

    connectionHandler.commit()
    connectionHandler.close()

    return final


def get_employee_on_shift(shift_id):
    """
    Get the deatils of an employees on a shift given the shifts ID.
    """

    cursor, connectionHandler = connect_to_database()

    employee_details = cursor.execute(f"""SELECT * FROM Employees, Employee_Shifts WHERE Employees.employee_id = Employee_Shifts.employee_id AND Employee_Shifts.shift_id = ?""", ([shift_id])).fetchall()[0]

    firstname, lastname, position_id = employee_details[2], employee_details[3], employee_details[6]

    connectionHandler.commit()
    connectionHandler.close()

    return firstname, lastname, position_id


def get_available_employees(business_id, position_id, shift_date, start_time, end_time):
    """
    Get a list of employees that are available in a time range.
    """

    if shift_date in DAYS_OF_WEEK:
        day_of_week = DAYS_OF_WEEK.index(shift_date)
        monday_this_week = date.today() - timedelta(days=(day_of_week - 1))
        shift_date = (monday_this_week + timedelta(day_of_week)).strftime("%d-%m-20%y")
    
    day, month, year = map(int, shift_date.split("-"))
    cursor, connectionHandler = connect_to_database()
    
    employees_of_position = set(row[0] for row in cursor.execute(f"SELECT employee_id FROM Employees WHERE business_id = '{business_id}' AND position_id = '{position_id}'").fetchall())
    
    employees_unavailable = cursor.execute("SELECT employee_id, start_time, end_time, start_date, end_date, status_id FROM Time_Off").fetchall()
    
    for emp_id, s_time, e_time, s_date, e_date, status in employees_unavailable:
        if status == 2:
            s_day, s_month, s_year = map(int, s_date.split("-"))
            e_day, e_month, e_year = map(int, e_date.split("-"))
            
            if date(s_year, s_month, s_day) <= date(year, month, day) <= date(e_year, e_month, e_day):
                employees_of_position.discard(emp_id)

            elif (float(s_time) <= float(start_time) <= float(e_time)) or (float(s_time) >= float(start_time) and float(s_time) <= float(end_time)) or (float(e_time) >= float(start_time) and float(e_time) <= float(end_time)):
                employees_of_position.discard(emp_id)
    
    connectionHandler.commit()
    connectionHandler.close()
    
    return list(employees_of_position)


def remove_employee_from_shift(employee_id, shift_id):
    """
    Removes an employee from a shift.
    """

    cursor, connectionHandler =connect_to_database()

    cursor.execute(f"DELETE FROM Employee_Shifts WHERE shift_id = '{shift_id}' and employee_id = '{employee_id}'")

    connectionHandler.commit()
    connectionHandler.close()


def delete_shift(shift_id):
    """
    Deletes a shift from the database.
    """

    cursor, connectionHandler =connect_to_database()

    cursor.execute(f"DELETE FROM Shifts WHERE shift_id = '{shift_id}'")
    cursor.execute(f"DELETE FROM Employee_Shifts WHERE shift_id = '{shift_id}'")

    connectionHandler.commit()
    connectionHandler.close()


def delete_employee(id):
    """
    Deletes an employee from the database
    """

    cursor, connectionHandler =connect_to_database()

    cursor.execute(f"DELETE FROM Employees WHERE employee_id = '{id}'")

    connectionHandler.commit()
    connectionHandler.close()


def publish_shift(shift_id, employee_id):
    """
    Switch a shift from pending to published
    """

    cursor, connectionHandler = connect_to_database()

    cursor.execute(f"UPDATE Employee_Shifts SET status = 4 WHERE shift_id = '{shift_id}' and employee_id = '{employee_id}' ").fetchone()

    connectionHandler.commit()
    connectionHandler.close()


def image_to_blob(filename):
    """
    Convert a file located by its filepath into BLOB datatype (Binary Large Object)
    """

    with open(filename, 'rb') as file:
        blobData = file.read()

    return blobData