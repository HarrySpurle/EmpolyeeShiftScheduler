from PySide6.QtCore import Qt, QTime, QDate
from PySide6.QtWidgets import (QPushButton, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QMainWindow, QSpacerItem, QSizePolicy, QLineEdit, QStackedWidget, QMessageBox, QFileDialog, QComboBox, QTextEdit, QFrame, QTableWidget, QHeaderView, QScrollArea, QDateEdit, QTimeEdit, QStyledItemDelegate, QAbstractItemView, QTableWidgetItem)
from PySide6.QtGui import QFont, QPixmap, QImage, QPainter, QPainterPath, QIcon, QTextOption, QColor
from datetime import date, timedelta
import sys, Database_Controller, Schedule_employees, Password_Hasher, re

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

class Popup(QMainWindow):
    """
    Standard format for an information popup
    """

    def __init__(self):
        super().__init__()
        self.popup = QMessageBox()
        self.popup.setStandardButtons(QMessageBox.StandardButton.Ok)


class Insufficient_details(Popup):
    """
    Popup to indicate a lack of information in input boxes
    """

    def __init__(self):
        super().__init__()
        self.popup.setIcon(QMessageBox.Icon.Information)
        self.popup.setWindowTitle('Insufficient Details')
        self.popup.setText('Please make sure these details are correct!')
        self.popup.exec()


class Incorrect_details(Popup):
    """
    Popup to indicate incorrect information in input boxes
    """

    def __init__(self):
        super().__init__()
        self.popup.setIcon(QMessageBox.Icon.Warning)
        self.popup.setWindowTitle('Incorrect Details')
        self.popup.setText('It looks like the details you provided are incorrect!')
        self.popup.exec()


class No_details(Popup):
    """
    Popup to indicate no or a lack of information in input boxes
    """

    def __init__(self):
        super().__init__()
        self.popup.setIcon(QMessageBox.Icon.Warning)
        self.popup.setWindowTitle('Insufficient Details')
        self.popup.setText('Please fill out all fields!')
        self.popup.exec()


class Stack(QMainWindow):
    """
    A system to store all the pages of the program
    """

    def __init__(self):
        """
        Setup and add all pages to the system
        """

        super().__init__()
        
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.view = QVBoxLayout(self.central_widget)

        self.stack = QStackedWidget(self)
        self.view.addWidget(self.stack)

        self.current_user = None
        self.editing_user = None
        self.current_shift = None
        self.current_request = None

        self.history = []

        self.pages = {
            "Start Page": Start_Page(self),
            "Login": Employee_Login_Page(self),
            "Create Business": Create_Business(self),
            "Create Managing Account": Create_Managing_Account(self),
            "Edit Employee Details": Edit_Employee_Details(self),
            "Create Employee": Create_Employee(self),
            "Create Position": Create_Position(self),
            "Managers Main Page": Manager_MainPage(self),
            "Employees Main Page": Employee_MainPage(self),
            "Create One Time Shift": Create_OneTime_Shift(self),
            "Create Recurring Shift": Create_Recurring_Shift(self),
            "Manage Shifts": Manage_Shifts(self),
            "Empty Shift Details": View_Empty_Shift_Details(self),
            "Assigned Shift Details": View_Assigned_Shift_Details(self),
            "Assign Shift To Employee": Assign_Shift(self),
            "Request Time Off": Request_Time_Off(self),
            "Manage Employees": Manage_Employees(self),
            "Timeoff Request Details": View_Timeoff_Request_Details(self),
            "Initialise Employee Details": Initialise_Employee_Details(self),
            "Manager Login": Manager_Login_Page(self),
            "Reset Password": Reset_Password(self)
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.setWindowTitle("Employee Shift Scheduler")
        self.stack.setCurrentWidget(self.pages["Start Page"])


    def load_page(self, page_key):
        """
        Load a page from the system when called
        """

        page = self.pages[page_key]

        if self.stack.currentWidget() is not page:
            self.history.append(self.stack.currentWidget())
        self.stack.setCurrentWidget(page)

        self.titles = {
            "Start": "Employee Shift Scheduler",
            "Login": "Login",
            "Create Business": "Create a Business",
            "Create Managing Account": "Create a Managing Account",
            "Edit Employee Details": "Edit Employee Details",
            "Create Employee": "Add Employee Profile",
            "Create Position": "Create Business Position",
            "Managers Main Page": "Employee Shift Scheduler",
            "Employees Main Page": "Employee Shift Scheduler",
            "Create One Time Shift": "Create a Shift",
            "Create Recurring Shift": "Create a Shift",
            "Manage Shifts": "Manage Shifts",
            "Empty Shift Details": "Shift Details",
            "Assigned Shift Details": "Shift Details",
            "Assign Shift To Employee": "Assign Employee to Shift",
            "Request Time Off": "Request Time Off",
            "Manage Employees": "Manage Employees",
            "Timeoff Request Details": "Time-Off Request",
            "Initialise Employee Details": "Edit Employee Details"
        }

        self.setWindowTitle(self.titles.get(page_key, "Employee Shift Scheduler"))

        if hasattr(page, 'refresh'):
            page.refresh()


    def go_back(self):
        """
        Return to the page that was last open
        """

        if self.history:
            previous_page = self.history.pop()
            self.stack.setCurrentWidget(previous_page)

        page_key = [key for key, value in self.pages.items() if value == previous_page][0]

        self.setWindowTitle(self.titles.get(page_key, "Employee Shift Scheduler"))


class Page(QMainWindow):
    """
    Standard format for a page
    """

    BUTTON_WIDTH = 250
    FORM_WIDTH = 300
    BACK_BUTTON_WIDTH = 100
    TITLE_FONT = QFont('Cascadia Mono', 26)
    LABEL_FONT = QFont('Cascadia Mono', 18)
    BUTTON_FONT = QFont('Cascadia Mono', 15)
    FORM_STYLE = """QLineEdit {padding: 15px; border-radius: 20px; background-color: #5b5b5b; color: white;}"""
    BUTTON_STYLE = """QPushButton {padding: 15px; border-radius: 20px; background-color: #5b5b5b; color: white;} QPushButton:hover {background-color: #757575;} QPushButton:pressed {background-color: #333333;}"""
    CHOOSE_PHOTO_STYLE = """QPushButton {padding: 10px; border-radius: 20px; background-color: #5b5b5b; color: white;} QPushButton:hover {background-color: #757575;} QPushButton:pressed {background-color: #333333;}"""
    DROPDOWN_STYLE = """QComboBox {padding: 10px; border-radius: 20px; background-color: #5b5b5b; color: white;}"""
    TIMETABLE_GRID_STYLE = """QHeaderView::section {background-color: #5b5b5b; color: White; border: 2px solid #333333; padding: 5px; border-radius: 5px; text-align: center;} QTableWidget { margin-top: 100px; margin-left: 30px; border-radius: 10px;} QTableWidget::item {border: 2px solid #2d2d2d;}   """
    WRAPAROUND_STYLE = """QTextEdit {padding: 15px; border-radius: 20px; background-color: #5b5b5b; color: white;}"""
    CALENDAR_DROPDOWN_STYLE = """QDateEdit { border: 1px solid #333333; background-color: #5b5b5b; color: white; padding: 15px; border-radius: 20px; width: 250px; font: Cascadia Mono;} QCalendarWidget QAbstractItemView::item {background-color: #5b5b5b; border: 1px solid #333333;} QCalendarWidget QAbstractItemView::item:selected {background-color: #333333;} QCalendarWidget QAbstractItemView::item:highlighted {background-color: #5b5b5b;} QCalendarWidget QHeaderView::section {background-color: #5b5b5b; color: white; padding: 4px;}"""
    TIME_SELECTOR_STYLE = """QTimeEdit {padding: 15px; border-radius: 20px; background-color: #5b5b5b; color: white; width: 100;}"""
    

    def __init__(self):
        """
        Setup the layout and add a back button
        """

        super().__init__()
        self.page = QWidget()
        self.view = QVBoxLayout(self.page)
        self.setCentralWidget(self.page)
        
        
        self.back_button = self.create_button("Back", self.BACK_BUTTON_WIDTH, self.BUTTON_FONT, self.go_back)
        self.view.addWidget(self.back_button)


    def create_button(self, text, width, font, callback, padding_value = None, height = 55 ):
        """
        Simplfy the button creation process
        """

        button = QPushButton(text)
        button.setStyleSheet(self.BUTTON_STYLE)
        button.setFont(font)
        button.setFixedWidth(width)
        button.setFixedHeight(height)
        button.clicked.connect(callback)
        
        return button
    

    def create_input_field(self, label, placeholder=None, is_password=False, multi_line=False):
        """
        Simplfy the input field creation process
        """
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        if multi_line:
            input_field = QTextEdit()
            input_field.setWordWrapMode(QTextOption.WordWrap)  
            input_field.setStyleSheet(self.WRAPAROUND_STYLE)
            input_field.setPlaceholderText(placeholder)  
            input_field.setMinimumHeight(150)  

        else:
            input_field = QLineEdit()
            input_field.setStyleSheet(self.FORM_STYLE)
            input_field.setMinimumWidth(self.FORM_WIDTH)
            input_field.setPlaceholderText(placeholder)

            if is_password:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)

        label_widget = QLabel(label)
        label_widget.setFont(self.LABEL_FONT)

        layout.addWidget(label_widget, alignment=Qt.AlignCenter)
        layout.addWidget(input_field)

        container.input_field = input_field 

        return container
    

    def remove_back_button(self):
        """ 
        Remove the back button from a layout
        """

        self.view.removeWidget(self.back_button)
        self.back_button.deleteLater()


    def add_vspacer(self, height=20, expanding=False):
        """
        Add a vertical spacer to a layout
        """

        spacer = QSpacerItem(20, height, QSizePolicy.Minimum, QSizePolicy.Expanding if expanding else QSizePolicy.Minimum)
        self.view.addSpacerItem(spacer)


    def add_hspacer(self, width=20, expanding=False):
        """
        Add a horizontal spacer to a layout
        """

        spacer = QSpacerItem(width, 20, QSizePolicy.Minimum, QSizePolicy.Expanding if expanding else QSizePolicy.Minimum)
        self.view.addSpacerItem(spacer)


    def add_widget(self, widget, alignment=Qt.AlignCenter):
        """
        Add a widget to a layout
        """

        self.view.addWidget(widget, alignment=alignment)


    def refresh(self):
        """
        Placeholder for refresh method
        """

        pass 


    def go_back(self):
        """
        Return to previous page
        """

        self.parent_stack.go_back()


class Start_Page(Page):
    """
    The homepage that opens when the program starts
    """

    def __init__(self, parent_stack):
        """
        Create and load the buttons and titles onto the page
        """

        super().__init__()
        self.parent_stack = parent_stack
        self.remove_back_button()

        buttons = [
            ("Employee Login", self.login),
            ("Create a Business", self.create_business),
            ("Exit", self.exit)
            ]

        title = QLabel("Employee Shift Scheduler")
        title.setFont(self.TITLE_FONT)
        
        self.add_vspacer(100)
        self.add_widget(title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(200)

        for text, callback in buttons:
            button = self.create_button(text, self.BUTTON_WIDTH, self.BUTTON_FONT, callback)
            self.add_widget(button)
            self.add_vspacer(30)

        self.add_vspacer(70, expanding=True)


    def login(self):
        """
        Load the login page
        """

        self.parent_stack.load_page("Login")


    def create_business(self):
        """
        Load the page to create a new business
        """

        self.parent_stack.load_page("Create Business")


    def exit(self):
        """
        Exit the program
        """

        QApplication.quit()


class Create_Business(Page):
    """
    The page allowing users to create a business
    """

    def __init__(self, parent_stack):
        """
        Create input fields and load them to the page
        """

        super().__init__()
        self.parent_stack = parent_stack

        create_business_title = QLabel("Create a Business", self)
        create_business_title.setFont(self.TITLE_FONT)

        self.widgets = [
            (self.create_input_field("Business Name:")), 
            (self.create_input_field("Business Address:")),
            (self.create_button("Next page", self.BUTTON_WIDTH, self.BUTTON_FONT, self.next_page))
        ]

        self.add_vspacer(30)
        self.add_widget(create_business_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(150)

        for widget in self.widgets:
            self.add_widget(widget)
            self.add_vspacer(30)

        self.add_vspacer(140)


    def next_page(self):
        """
        Create the business and load the create account page
        """

        name = self.widgets[0].input_field.text()
        address = self.widgets[1].input_field.text()

        nospace = r"^(?!\s*$).+"

        if re.match(nospace, name) and re.match(nospace, address):
            Database_Controller.add_business(name,address)
            self.parent_stack.load_page("Create Managing Account")

        else:
            No_details()
            self.widgets[0].input_field.clear()
            self.widgets[1].input_field.clear()


class Create_Managing_Account(Page):
    """
    Allows a user to create a managing account when making a business
    """

    def __init__(self, parent_stack):
        """
        Setup placeholders for the input fields to be updated on refresh
        """

        super().__init__()
        self.parent_stack = parent_stack

        create_manager_title = QLabel("Create a Managing Account", self)
        create_manager_title.setFont(self.TITLE_FONT)

        create_business_button = self.create_button("Create Business", self.BUTTON_WIDTH, self.BUTTON_FONT, self.create_manager)

        self.input_fields = [
            (self.create_input_field("First Name:", "John")),
            (self.create_input_field("Last Name:", "Smith")),
            (self.create_input_field("Set Manager's Password:","••••••••••••" , is_password=True)),
        ]

        self.add_vspacer(30)
        self.add_widget(create_manager_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(60)

        for input in self.input_fields:
            self.add_widget(input)
            self.add_vspacer(30)
        
        self.add_vspacer(30)
        self.add_widget(create_business_button)
        self.add_vspacer(160)


    def create_manager(self):
        """
        Add the information to the database and load the edit details page
        """

        first_name = self.input_fields[0].input_field.text()
        last_name = self.input_fields[1].input_field.text()
        password = self.input_fields[2].input_field.text()

        business_id = Database_Controller.find_new_business()

        position_id = Database_Controller.add_position(business_id, 'Manager', None)

        if password != "" and last_name != "" and first_name != "":
            if " " in first_name or " " in last_name:
                Insufficient_details()
            else:
                Database_Controller.add_employee(business_id, first_name, last_name, None, None, position_id, None, None, None, None, password)
                id = Database_Controller.find_new_employee()
                self.input_fields[0].input_field.clear()
                self.input_fields[1].input_field.clear()
                self.input_fields[2].input_field.clear()

                self.parent_stack.current_user = id
                self.parent_stack.editing_user = id
                self.parent_stack.load_page("Initialise Employee Details")

        else:
            No_details()


class Employee_Login_Page(Page):
    """
    The page that allows employees to log in to their accounts
    """

    def __init__(self, parent_stack):
        """
        Create and load the titles and input buttons onto the page
        """

        super().__init__()
        self.parent_stack = parent_stack

        self.inputs = [
            (self.create_input_field("Name:", "Firstname Lastname")),
            (self.create_input_field("Password:", "••••••••••••",  is_password=True))
        ]

        login_title = QLabel("Login to Employee Profile", self)
        login_title.setFont(self.TITLE_FONT)

        login_button = self.create_button("Login", self.BUTTON_WIDTH, self.BUTTON_FONT, self.login)

        self.add_vspacer(30)
        self.add_widget(login_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(150)

        for input in self.inputs:
            self.add_widget(input)
            self.add_vspacer(30)

        self.add_widget(login_button)
        self.add_vspacer(160, expanding=True)


    def login(self):
        """
        Confirm the employees details and allow them to log in
        """

        try:
            first_name, last_name = self.inputs[0].input_field.text().split(' ')
            password = self.inputs[1].input_field.text()
            id, Correct_Details = Database_Controller.employee_login(first_name, last_name, password)
            if Correct_Details:
                self.inputs[0].input_field.clear()
                self.inputs[1].input_field.clear()
                self.parent_stack.current_user = id
                position_id = Database_Controller.find_employee(id)[6]
                position_title = Database_Controller.find_position(position_id)
                if position_title == "Manager":
                    self.parent_stack.load_page("Manager Login")
                else:
                    self.parent_stack.load_page("Employees Main Page")
            else:
                Incorrect_details()
        except:
            Insufficient_details()
            pass


class Manager_Login_Page(Page):

    def __init__(self, parent_stack):
        """
        Create and load the buttons and titles onto the page
        """

        super().__init__()
        self.parent_stack = parent_stack
        self.remove_back_button()

        buttons = [
            ("Employee Dashboard", self.employee_login),
            ("Manager Dashboard", self.manager_login),
            ]

        title = QLabel("Select Dashboard to View")
        title.setFont(self.TITLE_FONT)
        
        self.add_vspacer(100)
        self.add_widget(title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(200)

        for text, callback in buttons:
            button = self.create_button(text, self.BUTTON_WIDTH, self.BUTTON_FONT, callback)
            self.add_widget(button)
            self.add_vspacer(30)

        self.add_vspacer(70, expanding=True)


    def employee_login(self):
        """
        Loads the mainpage for an employee
        """

        self.parent_stack.load_page("Employees Main Page")


    def manager_login(self):
        """
        Loads the mainpage for a manager
        """

        self.parent_stack.load_page("Managers Main Page")


class Edit_Employee_Details(Page):
    """
    Allows a manager to edit the details of an employee
    """

    def __init__(self, parent_stack):
        """
        Load basic information before an employees id is entered
        """

        super().__init__()
        self.parent_stack = parent_stack

        self.details = [0, 0, "", "", "", "", "", 0, 0, 0, 0, ""]

        self.employee_photo = QLabel()
        self.name_title = QLabel()
        self.job_title = QLabel()
        self.business_title = QLabel()
        employee_badge = QHBoxLayout()
        photo_layout = QVBoxLayout()
        info_layout = QVBoxLayout()

        if self.employee_photo.pixmap():
            pixmap = self.make_circle(self.employee_photo.pixmap())
            self.employee_photo.setPixmap(pixmap)

        self.employee_photo.setAlignment(Qt.AlignTop)
        photo_layout.addWidget(self.employee_photo, alignment=Qt.AlignTop | Qt.AlignCenter)
        employee_badge.addLayout(photo_layout)

        titles = [self.name_title, self.job_title, self.business_title]

        for title in titles:
            title.setFont(self.TITLE_FONT)
            info_layout.addWidget(title, alignment=Qt.AlignTop | Qt.AlignCenter)

        employee_badge.addLayout(photo_layout)
        employee_badge.addSpacing(-1000)
        employee_badge.addLayout(info_layout)
        employee_badge.addSpacing(40)

        self.view.addLayout(employee_badge)
        self.view.addSpacing(10)

        left_input_column = QVBoxLayout()
        right_input_column = QVBoxLayout()
        input_layout = QHBoxLayout()

        self.first_name_input = self.create_input_field("First Name:", self.details[2])
        self.last_name_input = self.create_input_field("Last Name:", self.details[3])
        self.email_input = self.create_input_field("Email:", str(self.details[4]))
        self.phone_number_input = self.create_input_field("Phone Number:", str(self.details[5]))
        self.hourly_rate_input = self.create_input_field("Hourly Rate:", str(self.details[7]))
        self.minimum_hours_input = self.create_input_field("Minimum Hours:", str(self.details[10]))
        self.maximum_hours_input = self.create_input_field("Maximum Hours:", str(self.details[11]))
        self.choose_photo_button = self.create_button("Employee Photo", self.FORM_WIDTH, self.BUTTON_FONT, self.select_photo)
        self.submit_button = self.create_button("Submit", self.FORM_WIDTH, self.BUTTON_FONT, self.submit)
        self.delete_button = self.create_button("Delete Employee", self.FORM_WIDTH, self.BUTTON_FONT, self.delete_employee)
        self.reset_password_button = self.create_button("Reset Password", self.FORM_WIDTH, self.BUTTON_FONT, self.reset_password)

        self.choose_photo_button.setStyleSheet(self.CHOOSE_PHOTO_STYLE)
        self.choose_photo_button.setFont(QFont('Cascadia Mono', 18))
        
        right_column_widgets = [self.hourly_rate_input, self.minimum_hours_input, self.maximum_hours_input]
        left_column_widgets = [self.first_name_input, self.last_name_input, self.email_input, self.phone_number_input]

        for widget in left_column_widgets:
            left_input_column.addWidget(widget)

        for widget in right_column_widgets:
            right_input_column.addWidget(widget)

        right_input_column.addSpacing(35)
        right_input_column.addWidget(self.choose_photo_button, alignment=Qt.AlignTop)

        input_layout.addLayout(left_input_column)
        input_layout.addSpacing(-400) 
        input_layout.addLayout(right_input_column)
        input_layout.addSpacing(400) 

        self.view.addLayout(input_layout)
        self.view.addWidget(self.submit_button, alignment= Qt.AlignCenter)
        self.view.addWidget(self.delete_button, alignment= Qt.AlignCenter)
        self.view.addWidget(self.reset_password_button, alignment= Qt.AlignCenter)


    def refresh(self):
        """
        Refreshes the page with the employees information
        """
        
        self.details = Database_Controller.find_employee(self.parent_stack.editing_user)
        position = Database_Controller.find_position(self.details[6])
        business = Database_Controller.find_business(self.details[1])

        self.business_title.setText(f"{business}")
        self.job_title.setText(f"{position}")
        self.name_title.setText(f"{self.details[2]} {self.details[3]}")

        if self.details[-4]:
            pixmap = QPixmap()
            if pixmap.loadFromData(self.details[-4]):
                circular_pixmap = self.make_circle(pixmap)
                self.employee_photo.setPixmap(circular_pixmap)
            else:
                self.employee_photo.clear()
        else:
            self.employee_photo.clear()

        self.first_name_input.input_field.setPlaceholderText(self.details[2])
        self.last_name_input.input_field.setPlaceholderText(self.details[3])
        self.email_input.input_field.setPlaceholderText(str(self.details[4]))
        self.phone_number_input.input_field.setPlaceholderText(str(self.details[5]))
        self.hourly_rate_input.input_field.setPlaceholderText(str(self.details[7]))
        self.minimum_hours_input.input_field.setPlaceholderText(str(self.details[10]))
        self.maximum_hours_input.input_field.setPlaceholderText(str(self.details[11]))


    def create_input_field(self, label, data, is_password=False):
        """
        Override the original method to show the data instead of the label
        """

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        input_field = QLineEdit()
        input_field.setPlaceholderText(data)
        input_field.setStyleSheet(self.FORM_STYLE)
        input_field.setFixedWidth(self.FORM_WIDTH)
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)

        label_widget = QLabel(label)
        label_widget.setFont(self.LABEL_FONT)

        layout.addWidget(label_widget, alignment=Qt.AlignCenter)
        layout.addWidget(input_field, alignment=Qt.AlignCenter)

        container.input_field = input_field

        return container


    def select_photo(self):
        """
        Allows a user to pick a file from their device
        """

        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Choose Employee Photo", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if self.file_path:
            pixmap = QPixmap(self.file_path)
            if not pixmap.isNull():
                self.circular_pixmap = self.make_circle(pixmap)
                self.employee_photo.setPixmap(self.circular_pixmap)


    def make_circle(self, pixmap, size=140):
        """
        Make the photo inputted by the user into a circle
        """

        image = pixmap.toImage().scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation)

        circular_image = QImage(size, size, QImage.Format.Format_ARGB32)
        circular_image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(circular_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        painter.drawPixmap(0, 0, QPixmap.fromImage(image))
        painter.end()

        return QPixmap.fromImage(circular_image)
    

    def delete_employee(self):
        """
        Removes an employee from the database
        """

        shifts = Schedule_employees.get_shifts_in_week(self.parent_stack.current_user)
        Schedule_employees.clear_shifts(self.parent_stack.current_user, shifts)
        Database_Controller.delete_employee(self.parent_stack.editing_user)
        self.parent_stack.load_page("Managers Main Page")

    
    def reset_password(self):
        """
        Gives an employee the standard password for the program
        """

        Database_Controller.update_password('1234', self.parent_stack.editing_user)
        self.parent_stack.load_page("Managers Main Page")


    def submit(self):
        """
        Update the database with the newly entered information
        """       

        try:
            self.file_path = self.file_path

        except:
            self.file_path = None

        done = Database_Controller.update_employee(self.first_name_input.input_field.text(), self.last_name_input.input_field.text(), self.email_input.input_field.text(), self.phone_number_input.input_field.text(), self.hourly_rate_input.input_field.text(), self.minimum_hours_input.input_field.text(), self.maximum_hours_input.input_field.text(), self.file_path, self.parent_stack.editing_user)
        if done == False:
            Insufficient_details()
        else:
            
            self.refresh()
            self.first_name_input.input_field.setPlaceholderText(self.details[2])
            self.last_name_input.input_field.setPlaceholderText(self.details[3])
            self.email_input.input_field.setPlaceholderText(str(self.details[4]))
            self.phone_number_input.input_field.setPlaceholderText(str(self.details[5]))
            self.hourly_rate_input.input_field.setPlaceholderText(str(self.details[7]))
            self.minimum_hours_input.input_field.setPlaceholderText(str(self.details[10]))
            self.maximum_hours_input.input_field.setPlaceholderText(str(self.details[11]))

            self.first_name_input.input_field.clear()
            self.last_name_input.input_field.clear()
            self.email_input.input_field.clear()
            self.phone_number_input.input_field.clear()
            self.hourly_rate_input.input_field.clear()
            self.minimum_hours_input.input_field.clear()
            self.maximum_hours_input.input_field.clear()
            self.parent_stack.load_page("Managers Main Page")


class Initialise_Employee_Details(Page):
    """
    Allows a manager to edit the details of an employee
    """

    def __init__(self, parent_stack):
        """
        Load basic information before an employees id is entered
        """

        super().__init__()
        self.parent_stack = parent_stack

        self.details = [0, 0, "", "", "", "", "", 0, 0, 0, 0, ""]

        self.employee_photo = QLabel()
        self.name_title = QLabel()
        self.job_title = QLabel()
        self.business_title = QLabel()
        employee_badge = QHBoxLayout()
        photo_layout = QVBoxLayout()
        info_layout = QVBoxLayout()

        if self.employee_photo.pixmap():
            pixmap = self.make_circle(self.employee_photo.pixmap())
            self.employee_photo.setPixmap(pixmap)

        self.employee_photo.setAlignment(Qt.AlignTop)
        photo_layout.addWidget(self.employee_photo, alignment=Qt.AlignTop | Qt.AlignCenter)
        employee_badge.addLayout(photo_layout)

        titles = [self.name_title, self.job_title, self.business_title]

        for title in titles:
            title.setFont(self.TITLE_FONT)
            info_layout.addWidget(title, alignment=Qt.AlignTop | Qt.AlignCenter)

        employee_badge.addLayout(photo_layout)
        employee_badge.addSpacing(-1000)
        employee_badge.addLayout(info_layout)
        employee_badge.addSpacing(40)

        self.view.addLayout(employee_badge)
        self.view.addSpacing(60)

        left_input_column = QVBoxLayout()
        right_input_column = QVBoxLayout()
        input_layout = QHBoxLayout()

        self.first_name_input = self.create_input_field("First Name:", self.details[2])
        self.last_name_input = self.create_input_field("Last Name:", self.details[3])
        self.email_input = self.create_input_field("Email:", str(self.details[4]))
        self.phone_number_input = self.create_input_field("Phone Number:", str(self.details[5]))
        self.hourly_rate_input = self.create_input_field("Hourly Rate:", str(self.details[7]))
        self.minimum_hours_input = self.create_input_field("Minimum Hours:", str(self.details[10]))
        self.maximum_hours_input = self.create_input_field("Maximum Hours:", str(self.details[11]))
        self.choose_photo_button = self.create_button("Employee Photo", self.FORM_WIDTH, self.BUTTON_FONT, self.select_photo)
        self.submit_button = self.create_button("Submit", self.FORM_WIDTH, self.BUTTON_FONT, self.submit)

        self.choose_photo_button.setStyleSheet(self.CHOOSE_PHOTO_STYLE)
        self.choose_photo_button.setFont(QFont('Cascadia Mono', 18))
        
        right_column_widgets = [self.hourly_rate_input, self.minimum_hours_input, self.maximum_hours_input]
        left_column_widgets = [self.first_name_input, self.last_name_input, self.email_input, self.phone_number_input]

        for widget in left_column_widgets:
            left_input_column.addWidget(widget)

        for widget in right_column_widgets:
            right_input_column.addWidget(widget)

        right_input_column.addSpacing(35)
        right_input_column.addWidget(self.choose_photo_button, alignment=Qt.AlignTop)

        input_layout.addLayout(left_input_column)
        input_layout.addSpacing(-400) 
        input_layout.addLayout(right_input_column)
        input_layout.addSpacing(400) 

        self.view.addLayout(input_layout)
        self.view.addWidget(self.submit_button, alignment= Qt.AlignCenter)


    def refresh(self):
        """
        Refreshes the page with the employees information
        """
        
        self.details = Database_Controller.find_employee(self.parent_stack.editing_user)
        position = Database_Controller.find_position(self.details[6])
        business = Database_Controller.find_business(self.details[1])

        self.business_title.setText(f"{business}")
        self.job_title.setText(f"{position}")
        self.name_title.setText(f"{self.details[2]} {self.details[3]}")

        if self.details[-4]:
            pixmap = QPixmap()
            if pixmap.loadFromData(self.details[-4]):
                circular_pixmap = self.make_circle(pixmap)
                self.employee_photo.setPixmap(circular_pixmap)
            else:
                self.employee_photo.clear()
        else:
            self.employee_photo.clear()

        self.first_name_input.input_field.setPlaceholderText(self.details[2])
        self.last_name_input.input_field.setPlaceholderText(self.details[3])
        self.email_input.input_field.setPlaceholderText(str(self.details[4]))
        self.phone_number_input.input_field.setPlaceholderText(str(self.details[5]))
        self.hourly_rate_input.input_field.setPlaceholderText(str(self.details[7]))
        self.minimum_hours_input.input_field.setPlaceholderText(str(self.details[10]))
        self.maximum_hours_input.input_field.setPlaceholderText(str(self.details[11]))


    def create_input_field(self, label, data, is_password=False):
        """
        Override the original method to show the data instead of the label
        """

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        input_field = QLineEdit()
        input_field.setPlaceholderText(data)
        input_field.setStyleSheet(self.FORM_STYLE)
        input_field.setFixedWidth(self.FORM_WIDTH)
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)

        label_widget = QLabel(label)
        label_widget.setFont(self.LABEL_FONT)

        layout.addWidget(label_widget, alignment=Qt.AlignCenter)
        layout.addWidget(input_field, alignment=Qt.AlignCenter)

        container.input_field = input_field

        return container


    def select_photo(self):
        """
        Allows a user to pick a file from their device
        """

        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Choose Employee Photo", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if self.file_path:
            pixmap = QPixmap(self.file_path)
            if not pixmap.isNull():
                self.circular_pixmap = self.make_circle(pixmap)
                self.employee_photo.setPixmap(self.circular_pixmap)


    def make_circle(self, pixmap, size=140):
        """
        Make the photo inputted by the user into a circle
        """

        image = pixmap.toImage().scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation)

        circular_image = QImage(size, size, QImage.Format.Format_ARGB32)
        circular_image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(circular_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        painter.drawPixmap(0, 0, QPixmap.fromImage(image))
        painter.end()

        return QPixmap.fromImage(circular_image)


    def submit(self):
        """
        Update the database with the newly entered information
        """       

        try:
            self.file_path = self.file_path

        except:
            self.file_path = None

        done = Database_Controller.update_employee(self.first_name_input.input_field.text(), self.last_name_input.input_field.text(), self.email_input.input_field.text(), self.phone_number_input.input_field.text(), self.hourly_rate_input.input_field.text(), self.minimum_hours_input.input_field.text(), self.maximum_hours_input.input_field.text(), self.file_path, self.parent_stack.editing_user)
        if done == False:
            Insufficient_details()
        else:
            
            self.refresh()
            self.first_name_input.input_field.setPlaceholderText(self.details[2])
            self.last_name_input.input_field.setPlaceholderText(self.details[3])
            self.email_input.input_field.setPlaceholderText(str(self.details[4]))
            self.phone_number_input.input_field.setPlaceholderText(str(self.details[5]))
            self.hourly_rate_input.input_field.setPlaceholderText(str(self.details[7]))
            self.minimum_hours_input.input_field.setPlaceholderText(str(self.details[10]))
            self.maximum_hours_input.input_field.setPlaceholderText(str(self.details[11]))

            self.first_name_input.input_field.clear()
            self.last_name_input.input_field.clear()
            self.email_input.input_field.clear()
            self.phone_number_input.input_field.clear()
            self.hourly_rate_input.input_field.clear()
            self.minimum_hours_input.input_field.clear()
            self.maximum_hours_input.input_field.clear()
            self.parent_stack.load_page("Managers Main Page")


class Manager_MainPage(Page):
    """
    The managers main page of the program
    """

    def __init__(self, parent_stack):
        """
        Run the methods that setup the header and the tables
        """

        super().__init__()
        self.parent_stack = parent_stack
        self.remove_back_button()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.add_schedule_grid()
        self.add_header()


    def add_header(self):
        """
        Change the backgroud of the header and add the utility buttons
        """

        header = QFrame(self)
        header.setFixedHeight(70)
        header.setFixedWidth(1525)
        header.setStyleSheet("background-color: #1c1c1c;")  

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)  
        header_layout.setSpacing(20) 

        log_out_button = self.create_button("Log Out", 100, QFont('Cascadia Mono', 12), self.logout, height = 50)
        manage_employees_button = self.create_button("Manage Employees", 200, QFont('Cascadia Mono', 12), self.manage_employees, height = 50)
        manage_shifts_button = self.create_button("Manage Shifts", 160, QFont('Cascadia Mono', 12), self.manage_shifts, height = 50)
        generate_schedule_button = self.create_button("Generate Schedule", 200, QFont('Cascadia Mono', 12), self.generate_schedule, height = 50)
        clear_schedule_button = self.create_button("Clear Schedule", 200, QFont('Cascadia Mono', 12), self.clear_schedule, height = 50)
        publish_schedule_button = self.create_button("Publish Schedule", 200, QFont('Cascadia Mono', 12), self.publish_schedule, height = 50)
        
        left_buttons = [manage_shifts_button, manage_employees_button]
        for button in left_buttons:
            header_layout.addSpacing(10)
            header_layout.addWidget(button)
        
        right_buttons = [publish_schedule_button, generate_schedule_button,clear_schedule_button,log_out_button]
        header_layout.addSpacing(2400)
        for button in right_buttons:
            header_layout.addWidget(button)
            header_layout.addSpacing(10)


    def add_schedule_grid(self):
        """
        Setup the table to display the shift information
        """     

        if self.parent_stack.current_user == None:
            self.schedule_table = QTableWidget(self)
            scroll_area = QScrollArea(self)
            people_names = ['placeholder']
            self.target_cells = {(1,1)}
            self.shift_grid = [[1], [2]]
            
        else: 
            people_names = []
            self.shift_grid = []

            business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            names = Database_Controller.get_employees(business_id)
            people_names = [str(names[i]) for i in range(len(names))]
    
            day_of_week = date.today().isoweekday()
            monday_this_week = date.today() - timedelta(days=(day_of_week - 1))
            week_dates = [(monday_this_week + timedelta(days=i)).strftime("%d-%m-20%y") for i in range(7)]

            for name in names:
                firstname,lastname = str(name).split(" ")
                self.shift_grid.append([Database_Controller.find_employee_id(firstname, lastname)[0], [()]*7])

            one_time_shifts = []

            for day in week_dates:
                shifts = Database_Controller.get_assigned_shifts(int(business_id), str(day))
                for index, shift in enumerate(shifts):
                    days,month,year = day.split("-")
                    weekday = date(int(year),int(month),int(days)).isoweekday()
                    list_for_shift = list(shifts[index])
                    list_for_shift.append(weekday-1)
                    one_time_shifts.append(list_for_shift)
            

            recurring_shifts = []

            for index, name in enumerate(DAYS_OF_WEEK):
                shifts = Database_Controller.get_assigned_shifts(int(business_id), str(name))

                for ind in range(len(shifts)):

                    days,month,year = week_dates[index].split("-")
                    weekday = date(int(year),int(month),int(days)).isoweekday()
                    list_for_shift = list(shifts[ind])
                    list_for_shift.append(weekday-1)
                    recurring_shifts.append(list_for_shift)

            self.shifts = one_time_shifts + recurring_shifts

            for day in range(7):
                for index, employee in enumerate(self.shift_grid):
                    for shift in self.shifts:
                        if employee[0] == shift[0]:
                            self.shift_grid[index][1][shift[2]] = shift[1]

            self.target_cells = set()
            for shift in range(len(self.shifts)):
                employee_details = Database_Controller.find_employee(self.shifts[shift][0])
                employee_name = f"{employee_details[2]} {employee_details[3]}"
                self.target_cells.add((people_names.index(employee_name), self.shifts[shift][2]))

        try:
            header_font = QFont("Cascadia Mono", 12, QFont.Bold)

            self.schedule_table.setRowCount(len(people_names))
            self.schedule_table.setVerticalHeaderLabels(people_names)
            self.schedule_table.verticalHeader().setFont(header_font)
            self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

            for row in range(self.schedule_table.rowCount()):
                self.schedule_table.setRowHeight(row, 100)

            self.schedule_table.setColumnCount(7)
            self.schedule_table.setHorizontalHeaderLabels(DAYS_OF_WEEK)
            self.schedule_table.horizontalHeader().setFont(header_font)
            self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            self.schedule_table.setStyleSheet(self.TIMETABLE_GRID_STYLE)

            shift_data = Add_Assigned_Shift_Data_Manager(self.target_cells, self.shift_grid)
            self.schedule_table.setItemDelegate(shift_data)
        
            self.schedule_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.schedule_table.setSelectionBehavior(QAbstractItemView.SelectItems)

            for row in range(self.schedule_table.rowCount()):
                for col in range(self.schedule_table.columnCount()):
                    item = self.schedule_table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem()
                        self.schedule_table.setItem(row, col, item)
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            self.schedule_table.verticalHeader().sectionClicked.connect(self.on_name_clicked)

            scroll_area.setWidget(self.schedule_table)
            scroll_area.setWidgetResizable(True)

            scroll_area.setMinimumSize(1500, 750)

            self.schedule_table.cellClicked.disconnect()
            self.schedule_table.cellClicked.connect(self.shift_clicked)

        except:
            pass


    def shift_clicked(self, row, column):
        """
        Opens shift details when a shift is clicked
        """

        if (row, column) in self.target_cells:
            self.parent_stack.current_shift = self.shift_grid[row][1][column]
            self.parent_stack.load_page("Assigned Shift Details")
        self.refresh()


    def on_name_clicked(self, row_index):
        """
        Handle clicking on a name in the vertical header
        """

        first_name, last_name = self.schedule_table.verticalHeaderItem(row_index).text().split(" ")
        id = Database_Controller.find_employee_id(first_name, last_name)

        self.parent_stack.editing_user = id[0]
        self.parent_stack.load_page("Edit Employee Details")

    def generate_schedule(self):
        Schedule_employees.create_new_schedule(self.parent_stack.current_user)
        self.refresh()

    def clear_schedule(self):
        Schedule_employees.clear_schedule(self.parent_stack.current_user)
        self.refresh()

    def publish_schedule(self):
        for shift in self.shifts:
            shift_id = shift[1]
            employee_id = shift[0]
            Database_Controller.publish_shift(shift_id, employee_id)
        self.refresh()


    def refresh(self):
        """
        Refresh the grid when the page is loaded
        """

        self.add_schedule_grid()
        return super().refresh()
    

    def manage_shifts(self):
        """
        Load the page which allows a user to create a shift
        """

        self.parent_stack.load_page("Manage Shifts")


    def manage_employees(self):
        """
        Load the page that allows managers to manage the employees
        """

        self.parent_stack.load_page("Manage Employees")


    def logout(self):
        """
        Log the user out and return to the start page
        """

        self.parent_stack.current_user = None
        self.parent_stack.load_page("Start Page")


class Employee_MainPage(Page):
    """
    The Employees main page of the program
    """

    def __init__(self, parent_stack):
        """
        Run the methods that setup the header and the tables
        """

        super().__init__()
        self.parent_stack = parent_stack
        self.remove_back_button()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.add_schedule_grid()
        self.add_header()


    def add_header(self):
        """
        Change the backgroud of the header and add the utility buttons
        """

        header = QFrame(self)
        header.setFixedHeight(70)
        header.setFixedWidth(1525)
        header.setStyleSheet("background-color: #1c1c1c;")  

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)  
        header_layout.setSpacing(20) 

        request_time_off_button = self.create_button("Request Time Off", 200, QFont('Cascadia Mono', 12), self.time_off, height = 50)
        reset_password_button = self.create_button("Reset Password", 200, QFont('Cascadia Mono', 12), self.reset_password, height = 50)
        log_out_button = self.create_button("Log Out", 100, QFont('Cascadia Mono', 12), self.logout, height = 50)
        
        header_layout.addSpacing(25)
        header_layout.addWidget(request_time_off_button)
        header_layout.addSpacing(2650)
        header_layout.addWidget(reset_password_button)
        header_layout.addSpacing(25)
        header_layout.addWidget(log_out_button)
        header_layout.addSpacing(25)


    def time_off(self):
        """
        Load the page to request time off
        """

        self.parent_stack.load_page("Request Time Off")


    def reset_password(self):
        """
        Loads the page for an employee to reset their password
        """

        self.parent_stack.load_page("Reset Password")


    def add_schedule_grid(self):
        """
        Setup the table to display the shift information
        """     

        if self.parent_stack.current_user == None:
            self.schedule_table = QTableWidget(self)
            scroll_area = QScrollArea(self)
            people_names = ['placeholder']
            self.target_cells = {(1,1)}
            self.shift_grid = [[1], [2]]
            
        else: 
            people_names = []
            self.shift_grid = []

            business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            names = Database_Controller.get_employees(business_id)
            people_names = [str(names[i]) for i in range(len(names))]

            day_of_week = date.today().isoweekday()
            monday_this_week = date.today() - timedelta(days=(day_of_week - 1))
            week_dates = [(monday_this_week + timedelta(days=i)).strftime("%d-%m-20%y") for i in range(7)]

            for name in names:
                firstname,lastname = str(name).split(" ")
                self.shift_grid.append([Database_Controller.find_employee_id(firstname, lastname)[0], [()]*7])

            one_time_shifts = []

            for day in week_dates:
                shifts = Database_Controller.get_assigned_shifts(int(business_id), str(day))

                for index, shift in enumerate(shifts):

                    days,month,year = day.split("-")
                    weekday = date(int(year),int(month),int(days)).isoweekday()
                    list_for_shift = list(shifts[index])
                    list_for_shift.append(weekday-1)
                    one_time_shifts.append(list_for_shift)

            recurring_shifts = []

            for index, name in enumerate(DAYS_OF_WEEK):
                shifts = Database_Controller.get_assigned_shifts(int(business_id), str(name))

                for ind in range(len(shifts)):

                    days,month,year = week_dates[index].split("-")
                    weekday = date(int(year),int(month),int(days)).isoweekday()
                    list_for_shift = list(shifts[ind])
                    list_for_shift.append(weekday-1)
                    recurring_shifts.append(list_for_shift)

            self.shifts = one_time_shifts + recurring_shifts

            for day in range(7):
                for index, employee in enumerate(self.shift_grid):
                    for shift in self.shifts:
                        if employee[0] == shift[0]:
                            self.shift_grid[index][1][shift[2]] = shift[1]

            self.target_cells = set()

            for shift in range(len(self.shifts)):
                employee_details = Database_Controller.find_employee(self.shifts[shift][0])
                employee_name = f"{employee_details[2]} {employee_details[3]}"
                self.target_cells.add((people_names.index(employee_name), self.shifts[shift][2]))

        try:
            header_font = QFont("Cascadia Mono", 12, QFont.Bold)

            self.schedule_table.setRowCount(len(people_names))
            self.schedule_table.setVerticalHeaderLabels(people_names)
            self.schedule_table.verticalHeader().setFont(header_font)
            self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

            for row in range(self.schedule_table.rowCount()):
                self.schedule_table.setRowHeight(row, 100)

            self.schedule_table.setColumnCount(7)
            self.schedule_table.setHorizontalHeaderLabels(DAYS_OF_WEEK)
            self.schedule_table.horizontalHeader().setFont(header_font)
            self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            self.schedule_table.setStyleSheet(self.TIMETABLE_GRID_STYLE)

            shift_data = Add_Assigned_Shift_Data_Employee(self.target_cells, self.shift_grid)
            self.schedule_table.setItemDelegate(shift_data)
        
            self.schedule_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.schedule_table.setSelectionBehavior(QAbstractItemView.SelectItems)

            for row in range(self.schedule_table.rowCount()):
                for col in range(self.schedule_table.columnCount()):
                    item = self.schedule_table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem()
                        self.schedule_table.setItem(row, col, item)
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            scroll_area.setWidget(self.schedule_table)
            scroll_area.setWidgetResizable(True)

            scroll_area.setMinimumSize(1500, 750)

        except UnboundLocalError:
            pass
        

    def refresh(self):
        """
        Refresh the grid when the page is loaded
        """

        self.add_schedule_grid()
        return super().refresh()
    

    def logout(self):
        """
        Log the user out and return to the start page
        """

        self.parent_stack.current_user = None
        self.parent_stack.load_page("Start Page")


class Reset_Password(Page):
    """
    Page that allows the user to reset their password
    """

    def __init__(self, parent_stack):
        """
        Load the three input fields for this page
        """

        super().__init__()
        self.parent_stack = parent_stack

        self.inputs = [
            (self.create_input_field("Current Password:", is_password=True)),
            (self.create_input_field("New Password:", is_password=True)),
            (self.create_input_field("Confirm New Password:", is_password=True))
        ]

        reset_password_title = QLabel("Reset Password", self)
        reset_password_title.setFont(self.TITLE_FONT)

        submit_button = self.create_button("Submit", self.BUTTON_WIDTH, self.BUTTON_FONT, self.submit)

        self.add_vspacer(30)
        self.add_widget(reset_password_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(110)

        for input in self.inputs:
            self.add_widget(input)
            self.add_vspacer(30)

        self.add_vspacer(70, expanding=True)
        self.add_widget(submit_button)
        self.add_vspacer(100, expanding=True)


    def submit(self):
        """
        Check the details and add the new employee to the database
        """

        try:
            if not self.parent_stack.current_user:
                raise ValueError("No user logged in.")
            
            if self.inputs[0].input_field.text() != "" and self.inputs[1].input_field.text() != "" and self.inputs[2].input_field.text() != "":
                entered_current_password = self.inputs[0].input_field.text()
                new_password = self.inputs[1].input_field.text()
                confirm_new_password = self.inputs[2].input_field.text()
                self.inputs[0].input_field.clear()
                self.inputs[1].input_field.clear()
                self.inputs[2].input_field.clear()
                current_password = Database_Controller.find_employee(self.parent_stack.current_user)[-1]
                is_matching = Password_Hasher.verify_password(entered_current_password, current_password)
                if is_matching and str(new_password) == str(confirm_new_password):
                    Database_Controller.update_password(str(new_password), self.parent_stack.current_user)
                    self.parent_stack.load_page("Employees Main Page")
                else:
                    Insufficient_details()
        except:
            Insufficient_details()


class Request_Time_Off(Page):
    """
    Page that allows users to request time off
    """

    def __init__(self, parent_stack):
        """
        Setup the buttons and input fields needed
        """

        super().__init__()
        self.parent_stack = parent_stack

        create_shift_title = QLabel("Request Time Off", self)
        create_shift_title.setFont(self.TITLE_FONT)

        start_date_title = QLabel("Select Start Date:", self)
        start_date_title.setFont(self.LABEL_FONT)

        end_date_title = QLabel("Select End Date:", self)
        end_date_title.setFont(self.LABEL_FONT)

        self.start_date = self.calendar()
        self.end_date = self.calendar()
        
        self.notes = self.create_input_field("Add A Note:", "Please provide reasons as to why you would like time off", multi_line=True)

        widgets = [create_shift_title, start_date_title, self.start_date, end_date_title, self.end_date, self.notes]
        self.add_widget(create_shift_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(30)
        for widget in widgets:
            self.add_widget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.start_end_time()
        self.add_widget(self.create_button("Submit", self.BUTTON_WIDTH, self.BUTTON_FONT, self.submit))
        self.add_vspacer(60)


    def start_end_time(self):
        """
        Add the start and end time selectors to the bottom of the page.
        """

        time_selector_layout = QHBoxLayout()
        time_title_layout = QHBoxLayout()

        start = QLabel('Start Time:')
        start.setFont(self.LABEL_FONT)

        end = QLabel('End Time:')
        end.setFont(self.LABEL_FONT)

        self.start_time_selector = QTimeEdit(self)
        self.start_time_selector.setTime(QTime.currentTime())
        self.start_time_selector.setDisplayFormat("HH:mm")
        self.start_time_selector.setStyleSheet(self.TIME_SELECTOR_STYLE)

        self.end_time_selector = QTimeEdit(self)
        self.end_time_selector.setTime(QTime.currentTime())
        self.end_time_selector.setDisplayFormat("HH:mm")
        self.end_time_selector.setStyleSheet(self.TIME_SELECTOR_STYLE)

        time_selector_layout.addWidget(self.start_time_selector)
        time_selector_layout.addSpacing(50)
        time_selector_layout.addWidget(self.end_time_selector)

        time_title_layout.addWidget(start)
        time_title_layout.addSpacing(50)
        time_title_layout.addWidget(end)

        self.add_widget(QWidget(self, layout=time_title_layout), alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.add_widget(QWidget(self, layout=time_selector_layout), alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)


    def calendar(self):
        """
        Add a calendar popup for date selection.
        """

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet(self.CALENDAR_DROPDOWN_STYLE)

        return self.date_edit


    def submit(self):
        """
        Gather all the information entered by the user and validate the input.
        """

        try:
            start_date = self.start_date.date().toString('dd-MM-yyyy')
            end_date = self.end_date.date().toString('dd-MM-yyyy')
            start_time = self.start_time_selector.time().toString('HH.mm')
            end_time = self.end_time_selector.time().toString('HH.mm')
            startday, startmonth, startyear = start_date.split("-")
            endday, endmonth, endyear = end_date.split("-")
            notes = self.notes.input_field.toPlainText()
            self.notes.input_field.clear()

            status_id = 1
            employee_id = self.parent_stack.current_user

            if date(int(startyear), int(startmonth), int(startday)) < date(int(endyear), int(endmonth), int(endday)):
                Database_Controller.add_time_off(employee_id, start_date, end_date, start_time, end_time, status_id, notes)
                self.parent_stack.load_page("Employees Main Page")
            elif date(int(startyear), int(startmonth), int(startday)) == date(int(endyear), int(endmonth), int(endday)) and float(start_time) < float(end_time):
                Database_Controller.add_time_off(employee_id, start_date, end_date, start_time, end_time, status_id, notes)
                self.parent_stack.load_page("Employees Main Page")
            else:
                Insufficient_details()

        except ValueError:
            Insufficient_details()


class View_Assigned_Shift_Details(Page):
    """
    Allows a user to view the details for a shift
    """

    def __init__(self, parent_stack):
        """
        Setup the widgets for the shift details page
        """

        super().__init__()
        self.parent_stack = parent_stack

        shift_details_title = QLabel("Shift Details", self)
        shift_details_title.setFont(self.TITLE_FONT)

        self.date =  QLabel("Placeholder", self)
        self.date.setFont(self.LABEL_FONT)

        self.time = QLabel("Placeholder", self)
        self.time.setFont(self.LABEL_FONT)

        self.employee = QLabel("Placeholder", self)
        self.employee.setFont(self.LABEL_FONT)

        done_button = self.create_button("Done", 240, QFont('Cascadia Mono', 12), self.done_clicked )
        remove_button = self.create_button("Remove From Shift", 240, QFont('Cascadia Mono', 12), self.remove_clicked )

        self.add_vspacer(30)
        self.add_widget(shift_details_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(70)

        widgets = [ self.date, self.time, self.employee]
        for widget in widgets:
            self.add_widget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.add_vspacer(35)

        self.add_vspacer(50)
        self.add_widget(done_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(20)
        self.add_widget(remove_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(185)


    def done_clicked(self):
        """
        Handle the done button being clicked
        """

        self.parent_stack.load_page("Managers Main Page")


    def remove_clicked(self):
        """
        Removes an employee from working a shift 
        """

        shift_id = self.parent_stack.current_shift
        firstname, lastname, position_id =  Database_Controller.get_employee_on_shift(self.parent_stack.current_shift)
        id = Database_Controller.find_employee_id(firstname, lastname)
        Database_Controller.remove_employee_from_shift(int(id[0]), int(shift_id))
        self.parent_stack.load_page("Managers Main Page")


    def refresh(self):
        """
        Refreshes the page with the employees information
        """

        times = Database_Controller.get_shift_times(self.parent_stack.current_shift)
        start_time = times[0]
        end_time = times[1]
        cal_date = times[2]
        firstname, lastname, position_id =  Database_Controller.get_employee_on_shift(self.parent_stack.current_shift)

        position = Database_Controller.find_position(position_id)

        if not '-' in cal_date:
            self.date.setText(f"Every {cal_date}")
        else:
            day,month,year = cal_date.split("-")
            day_of_week = date(int(year),int(month),int(day)).isoweekday() -1
            if int(day) == 1 or int(day) == 21 or int(day) == 31:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}st of {MONTHS[int(month)-1]} {year}")
            elif int(day) == 2 or int(day) == 22:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}nd of {MONTHS[int(month)-1]} {year}")
            elif int(day) == 3 or int(day) == 23:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}rd of {MONTHS[int(month)-1]} {year}")
            else:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}th of {MONTHS[int(month)-1]} {year}")
            
        self.time.setText(f"{start_time} - {end_time}")
        self.employee.setText(f"Assigned to the {position} {firstname} {lastname}")
        

class Create_Employee(Page):
    """
    Allows the manager to add an employee account to the system
    """

    def __init__(self, parent_stack):
        """
        Create and load the input fields for the firstname and lastname
        """
        
        super().__init__()
        self.parent_stack = parent_stack

        self.inputs = [
            (self.create_input_field("First Name:", "John")),
            (self.create_input_field("Last Name:", "Smith"))
        ]

        self.business_id = None
        self.selected_position = None
        self.position_dropdown = QComboBox()
        self.position_dropdown.setStyleSheet(self.DROPDOWN_STYLE)
        self.position_dropdown.setFixedWidth(self.FORM_WIDTH)
        self.position_dropdown.setFont(QFont('Ariel', 12))
        self.position_dropdown.currentIndexChanged.connect(self.selection_changed)

        position_label = QLabel('Position:')
        position_label.setFont(self.LABEL_FONT)

        add_employee_title = QLabel("Add an Employee Account", self)
        add_employee_title.setFont(self.TITLE_FONT)

        submit_button = self.create_button("Submit", self.BUTTON_WIDTH, self.BUTTON_FONT, self.submit)

        self.add_vspacer(30)
        self.add_widget(add_employee_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(110)

        for input in self.inputs:
            self.add_widget(input)
            self.add_vspacer(30)

        self.add_widget(position_label)
        self.add_widget(self.position_dropdown)
        self.add_vspacer(70, expanding=True)
        self.add_widget(submit_button)
        self.add_vspacer(100, expanding=True)

        self.load_positions()


    def refresh(self):
        """
        Refresh by loading the positions dropdown again
        """

        self.load_positions()
        return super().refresh()


    def load_positions(self):
        """
        Load the positions in the business from the database into the dropdown
        """

        if self.parent_stack.current_user:
            self.business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            positions = Database_Controller.get_positions(self.business_id)
            self.position_dropdown.clear()
            self.position_dropdown.addItems(positions)
            return True

        else:
            self.position_dropdown.clear()
            self.position_dropdown.addItem("No user logged in")
            return False


    def selection_changed(self, index):
        """
        Update the attribite to the contents of the dropdown option selected
        """

        self.selected_position = self.position_dropdown.itemText(index)


    def submit(self):
        """
        Check the details and add the new employee to the database
        """

        try:
            if not self.parent_stack.current_user:
                raise ValueError("No user logged in.")
            if not self.business_id:
                raise ValueError("Business ID not found.")

            first_name = self.inputs[0].input_field.text()
            last_name = self.inputs[1].input_field.text()
            self.inputs[0].input_field.clear()
            self.inputs[1].input_field.clear()
            if not self.selected_position:
                raise ValueError("No position selected.")
            
            if " " in first_name or " " in last_name or first_name == "" or last_name == "":
                Insufficient_details()

            else:
                position_id = Database_Controller.find_position_id(self.selected_position, self.business_id)
                Database_Controller.add_employee(self.business_id, first_name, last_name, None, None, position_id, None, None, None, None, '1234')
                self.parent_stack.editing_user = Database_Controller.find_new_employee()
                self.parent_stack.load_page("Initialise Employee Details")

        except:
            Insufficient_details()


class Create_Position(Page):
    """
    Adds a job position to the business
    """

    def __init__(self, parent_stack):
        """
        Setup the input fields to allow for adding positions
        """

        super().__init__()
        self.parent_stack = parent_stack

        self.inputs = [
            (self.create_input_field("Position Title:", "Barista")),
            (self.create_input_field("Description:", "In the Barista role, you will greet customers cheerfully, courteously and professionally, take orders, prepare specialty food & beverage items and fulfill orders. Your main goal is providing an exemplary customer experience to all store patrons.", multi_line=True))
        ]
    
        self.inputs[1].setMinimumWidth(500)

        add_employee_title = QLabel("Create Positon", self)
        add_employee_title.setFont(self.TITLE_FONT)

        sumbit_button = self.create_button("Submit", self.BUTTON_WIDTH, self.BUTTON_FONT, self.submit)

        self.add_vspacer(30)
        self.add_widget(add_employee_title, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.add_vspacer(70)

        for input in self.inputs:
            self.add_widget(input)
            self.add_vspacer(30)

        self.add_vspacer(30,expanding=True)
        self.add_widget(sumbit_button)
        self.add_vspacer(120, expanding=True)


    def submit(self):
        """
        Add new information about positions to the database
        """

        try:
            title = self.inputs[0].input_field.text()
            description = self.inputs[1].input_field.toPlainText()
            if title != "":
                business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
                Database_Controller.add_position(business_id, title, description)
                self.inputs[0].input_field.clear()
                self.inputs[1].input_field.clear()
                self.parent_stack.load_page("Managers Main Page")
            else:
                Insufficient_details()

        except:
            Insufficient_details()
            return


class Manage_Shifts(Page):
    """
    The page to view and manage shifts
    """

    def __init__(self, parent_stack):
        """
        Run the methods that setup the header and the tables
        """

        super().__init__()
        self.parent_stack = parent_stack
        self.remove_back_button()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.target_cells = set()
        self.add_shift_grid()
        self.add_header()


    def add_header(self):
        """
        Change the background of the header and add the utility buttons
        """

        header = QFrame(self)
        header.setFixedHeight(70)
        header.setFixedWidth(1525)
        header.setStyleSheet("background-color: #1c1c1c;")  

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)  
        header_layout.setSpacing(20) 

        back_button = self.create_button("Back", self.BACK_BUTTON_WIDTH, self.BUTTON_FONT, self.go_back)
        shift_buttons = [
            self.create_button("Create One Time Shift", 240, QFont('Cascadia Mono', 12), self.create_one_time_shift, height=50),
            self.create_button("Create Recurring Shift", 240, QFont('Cascadia Mono', 12), self.create_recurring_shift, height=50),
            self.create_button("Delete All Shifts", 220, QFont('Cascadia Mono', 12), self.delete_all_shifts, height=50)
        ]
        
        header_layout.addWidget(back_button)
        header_layout.addSpacing(2400)

        for button in shift_buttons:
            header_layout.addWidget(button)
            header_layout.addSpacing(25)


    def add_shift_grid(self):
        """
        Setup the table to display the shift information
        """

        if self.parent_stack.current_user is None:
            self.shifts_table = QTableWidget(self)
            self.shift_scroll_area = QScrollArea(self)
            left_side = ['placeholder']
        else:
            one_time_shifts = []
            recurring_shifts = []
            most_shifts = 0

            business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]

            day_of_week = date.today().isoweekday()
            monday_this_week = date.today() - timedelta(days=(day_of_week - 1))
            week_dates = [monday_this_week + timedelta(days=i) for i in range(7)]

            for day in DAYS_OF_WEEK:
                recurring_shifts.append(Database_Controller.get_shifts(business_id, day))

            for day in week_dates:
                date_of_day = day.strftime('%d-%m-20%y')
                one_time_shifts.append(Database_Controller.get_shifts(business_id, date_of_day))
            
            self.shifts = [a + b for a, b in zip(recurring_shifts, one_time_shifts)]

            for i in range(0, 7):
                if len(self.shifts[i]) > most_shifts:
                    most_shifts = len(self.shifts[i])

            left_side = [str(i) for i in range(1, most_shifts + 1)]

        
        try:
            self.shifts_table.setRowCount(most_shifts)
            self.shifts_table.setVerticalHeaderLabels(left_side)
            self.shifts_table.verticalHeader().setFont(QFont("Cascadia Mono", 12, QFont.Bold))
            self.shifts_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

            for row in range(self.shifts_table.rowCount()):
                self.shifts_table.setRowHeight(row, 100)
    
            self.shifts_table.setColumnCount(7)
            self.shifts_table.setHorizontalHeaderLabels(DAYS_OF_WEEK)
            self.shifts_table.horizontalHeader().setFont(QFont("Cascadia Mono", 12, QFont.Bold))
            self.shifts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            self.shifts_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.shifts_table.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.shifts_table.setStyleSheet(self.TIMETABLE_GRID_STYLE)
            
            self.target_cells = set()
            for day_num, day in enumerate(self.shifts):
                for shift_num, shift in enumerate(day):
                    self.target_cells.add((shift_num, day_num))

            shift_data = Add_Empty_Shift_Data(self.target_cells, self.shifts)
            self.shifts_table.setItemDelegate(shift_data)

            self.shift_scroll_area.setWidget(self.shifts_table)
            self.shift_scroll_area.setWidgetResizable(True)
            self.shift_scroll_area.setMinimumSize(1500, 750)

            self.shifts_table.cellClicked.disconnect()
            self.shifts_table.cellClicked.connect(self.shift_clicked)

        except:
            pass


    def shift_clicked(self, row, column):
        """
        Opens shift details when a shift is clicked
        """

        if (row, column) in self.target_cells:
            self.parent_stack.current_shift = self.shifts[column][row]
            self.parent_stack.load_page("Empty Shift Details")
        self.refresh()


    def refresh(self):
        """
        Refresh the grid to ensure the data remains correct
        """

        self.target_cells.clear()
        self.shifts_table.clearContents()

        self.add_shift_grid()

        self.shifts_table.blockSignals(False)


    def create_one_time_shift(self):
        """
        Load the page which allows a user to create a one time shift
        """

        self.parent_stack.load_page("Create One Time Shift")


    def create_recurring_shift(self):
        """
        Load the page which allows a user to create a recurring shift
        """

        self.parent_stack.load_page("Create Recurring Shift")


    def delete_all_shifts(self):
        """
        Clears the database of all shifts created in a week
        """

        for day in self.shifts:
            for shift in day:
                shift_id = shift[0]
                Database_Controller.delete_shift(shift_id)
        self.refresh()


    def go_back(self):
        """
        Return to the main page
        """

        self.parent_stack.load_page("Managers Main Page")


class Manage_Employees(Page):
    """
    Page that allows managers to manage the employees    
    """

    def __init__(self, parent_stack):
        """
        Run the methods that setup the header and the tables
        """

        super().__init__()
        self.parent_stack = parent_stack
        self.remove_back_button()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.target_cells = set()
        self.add_shift_grid()
        self.add_header()


    def add_header(self):
        """
        Change the background of the header and add the utility buttons
        """

        header = QFrame(self)
        header.setFixedHeight(70)
        header.setFixedWidth(1525)
        header.setStyleSheet("background-color: #1c1c1c;")  

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)  
        header_layout.setSpacing(20) 

        time_off_title = QLabel("Time-Off Requests:", self)
        time_off_title.setFont(self.LABEL_FONT)

        add_employee_button = self.create_button("Add Employee", 200, QFont('Cascadia Mono', 12), self.add_employee, height = 50)
        add_position_button = self.create_button("Add Position", 140, QFont('Cascadia Mono', 12), self.add_position, height = 50)
        back_button = self.create_button("Back", self.BACK_BUTTON_WIDTH, self.BUTTON_FONT, self.go_back)

        left_buttons = [add_employee_button, add_position_button]
        header_layout.addWidget(back_button)
        header_layout.addSpacing(20)
        header_layout.addWidget(time_off_title)
        header_layout.addSpacing(2400)

        for button in left_buttons:
            header_layout.addSpacing(25)
            header_layout.addWidget(button)


    def add_shift_grid(self):
        """
        Setup the table to display the shift information
        """

        if self.parent_stack.current_user is None:
            self.time_off_table = QTableWidget(self)
            self.time_off_scroll_area = QScrollArea(self)
            self.time_off_entries = [(1,1),(1,1)]
            people_names = ['placeholder']
            top = []
        else:
            people_names = []

            business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            names = Database_Controller.get_employees(business_id)
            people_names = [str(names[i]) for i in range(len(names))]

            most_requests = 0

            business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]

            day_of_week = date.today().isoweekday()
            monday_this_week = date.today() - timedelta(days=(day_of_week - 1))

            self.time_off_entries = Database_Controller.get_time_off_info(business_id, str(monday_this_week))

            top = [str(i) for i in range(1, most_requests + 1)]
    
        try:
            self.time_off_table.setRowCount(len(people_names))
            self.time_off_table.setVerticalHeaderLabels(people_names)
            self.time_off_table.verticalHeader().setFont(QFont("Cascadia Mono", 12, QFont.Bold))
            self.time_off_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

            for row in range(self.time_off_table.rowCount()):
                self.time_off_table.setRowHeight(row, 100)

            max_entries = 0
            for employee_id, employee in enumerate(self.time_off_entries):
                for index,entry in enumerate(employee):
                    if index+1 > max_entries:
                        max_entries = index+1
                
            self.time_off_table.setColumnCount(max_entries)
            self.time_off_table.setHorizontalHeaderLabels(top)
            self.time_off_table.horizontalHeader().setFont(QFont("Cascadia Mono", 12, QFont.Bold))
            self.time_off_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

            for column in range(self.time_off_table.columnCount()):
                self.time_off_table.setColumnWidth(column,150)
            
            self.time_off_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.time_off_table.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.time_off_table.setStyleSheet(self.TIMETABLE_GRID_STYLE)
            
            self.target_cells = set()
            for employee_id, employee in enumerate(self.time_off_entries):
                for index,entry in enumerate(employee):
                    self.target_cells.add((employee_id, index))

            time_requests_data = Add_Time_Off_Data(self.target_cells, self.time_off_entries)
            self.time_off_table.setItemDelegate(time_requests_data)

            for row in range(self.time_off_table.rowCount()):
                for col in range(self.time_off_table.columnCount()):
                    item = self.time_off_table.item(row, col)
                    if item is None:
                        item = QTableWidgetItem()
                        self.time_off_table.setItem(row, col, item)
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            self.time_off_scroll_area.setWidget(self.time_off_table)
            self.time_off_scroll_area.setWidgetResizable(True)
            self.time_off_scroll_area.setMinimumSize(1500, 750)

            self.time_off_table.cellClicked.disconnect()
            self.time_off_table.cellClicked.connect(self.request_clicked)

        except TypeError:
            pass


    def request_clicked(self, row, column):
        """
        Opens shift details when a shift is clicked
        """

        if (row, column) in self.target_cells:
            self.parent_stack.current_request = self.time_off_entries[row][column]
            self.parent_stack.load_page("Timeoff Request Details")
        self.refresh()


    def refresh(self):
        """
        Refresh the grid to ensure the data remains correct
        """

        self.target_cells.clear()
        self.time_off_table.clearContents()

        self.add_shift_grid()

        self.time_off_table.blockSignals(False)


    def go_back(self):
        """
        Return to the main page
        """

        self.parent_stack.load_page("Managers Main Page")


    def add_employee(self):
        """
        Load the page to add an employee to the database
        """
        
        self.parent_stack.load_page("Create Employee")


    def add_position(self):
        """
        Load the page to add a position to the business
        """

        self.parent_stack.load_page("Create Position")

        
class Create_OneTime_Shift(Page):
    """
    Allows a user to create a one-time shift for the business
    """

    def __init__(self, parent_stack):
        """
        Setup the buttons and input fields needed
        """

        super().__init__()
        self.parent_stack = parent_stack

        create_shift_title = QLabel("Create a Shift", self)
        create_shift_title.setFont(self.TITLE_FONT)

        select_date_title = QLabel("Select Date:", self)
        select_date_title.setFont(self.LABEL_FONT)

        position_label = QLabel('Position Needed:')
        position_label.setFont(self.LABEL_FONT)

        self.position_dropdown = QComboBox()
        self.position_dropdown.setStyleSheet(self.DROPDOWN_STYLE)
        self.position_dropdown.setFixedWidth(self.FORM_WIDTH)
        self.position_dropdown.setFont(QFont('Ariel', 12))
        self.position_dropdown.currentIndexChanged.connect(self.selection_changed)

        self.number_of_employees = self.create_input_field("Number of Employees:", "i.e. 4")

        widgets = [position_label, self.position_dropdown, self.number_of_employees, select_date_title]

        self.add_widget(create_shift_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        for widget in widgets:
            self.add_widget(widget)

        self.calendar()
        self.start_end_time()
        self.add_widget(self.create_button("Submit", self.BUTTON_WIDTH, self.BUTTON_FONT, self.submit))
        self.add_vspacer(60)


    def start_end_time(self):
        """
        Add the start and end time selectors to the bottom of the page.
        """

        time_selector_layout = QHBoxLayout()
        time_title_layout = QHBoxLayout()

        start = QLabel('Start Time:')
        start.setFont(self.LABEL_FONT)

        end = QLabel('End Time:')
        end.setFont(self.LABEL_FONT)

        self.start_time_selector = QTimeEdit(self)
        self.start_time_selector.setTime(QTime.currentTime())
        self.start_time_selector.setDisplayFormat("HH:mm")
        self.start_time_selector.setStyleSheet(self.TIME_SELECTOR_STYLE)

        self.end_time_selector = QTimeEdit(self)
        self.end_time_selector.setTime(QTime.currentTime())
        self.end_time_selector.setDisplayFormat("HH:mm")
        self.end_time_selector.setStyleSheet(self.TIME_SELECTOR_STYLE)

        time_selector_layout.addWidget(self.start_time_selector)
        time_selector_layout.addSpacing(50)
        time_selector_layout.addWidget(self.end_time_selector)

        time_title_layout.addWidget(start)
        time_title_layout.addSpacing(50)
        time_title_layout.addWidget(end)

        self.add_widget(QWidget(self, layout=time_title_layout), alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.add_widget(QWidget(self, layout=time_selector_layout), alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)


    def calendar(self):
        """
        Add a calendar popup for date selection.
        """

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet(self.CALENDAR_DROPDOWN_STYLE)

        self.add_widget(self.date_edit, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)


    def load_positions(self):
        """
        Load the positions in the business from the database into the dropdown.
        """

        if self.parent_stack.current_user:
            self.business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            positions = Database_Controller.get_positions(self.business_id)
            self.position_dropdown.clear()
            self.position_dropdown.addItems(positions)
            return True


    def selection_changed(self, index):
        """
        Update the attribute to the contents of the dropdown option selected.
        """

        self.selected_position = self.position_dropdown.itemText(index)


    def submit(self):
        """
        Gather all the information entered by the user and validate the input.
        """

        try:
            selected_position = self.position_dropdown.currentText()
            num_employees = self.number_of_employees.input_field.text()

            if not num_employees.isdigit():
                raise ValueError("Number of employees must be a valid integer.")

            num_employees = int(num_employees)

            shift_date = self.date_edit.date().toString('dd-MM-yyyy')
            start_time = self.start_time_selector.time().toString('HH.mm')
            end_time = self.end_time_selector.time().toString('HH.mm')
            if float(start_time) < float(end_time):
                business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
                position = Database_Controller.find_position_id(selected_position, business_id)

                Database_Controller.add_shift(business_id, position, num_employees, shift_date, start_time, end_time)
                self.number_of_employees.input_field.clear()

                self.parent_stack.load_page("Manage Shifts")
            else:
                Insufficient_details()

        except ValueError:
            Insufficient_details()


    def refresh(self):
        """
        Refresh the page by loading the positions dropdown.
        """

        self.load_positions()
        return super().refresh()


class Create_Recurring_Shift(Page):
    """
    Allows a user to create a recurring shift for the business
    """

    def __init__(self, parent_stack):
        """
        Setup the input fields for the setup recurring shift page
        """

        super().__init__()
        self.parent_stack = parent_stack

        create_shift_title = QLabel("Create a Shift", self)
        create_shift_title.setFont(self.TITLE_FONT)

        select_day_title = QLabel("Select Day of Week:", self)
        select_day_title.setFont(self.LABEL_FONT)

        self.day_dropdown = QComboBox()
        self.day_dropdown.setStyleSheet(self.DROPDOWN_STYLE)
        self.day_dropdown.setFixedWidth(self.FORM_WIDTH)
        self.day_dropdown.setFont(QFont('Ariel', 12))
        self.day_dropdown.addItems(DAYS_OF_WEEK)
        self.day_dropdown.currentIndexChanged.connect(self.day_selection_changed)

        position_label = QLabel('Position Needed:')
        position_label.setFont(self.LABEL_FONT)

        self.position_dropdown = QComboBox()
        self.position_dropdown.setStyleSheet(self.DROPDOWN_STYLE)
        self.position_dropdown.setFixedWidth(self.FORM_WIDTH)
        self.position_dropdown.setFont(QFont('Ariel', 12))
        self.position_dropdown.currentIndexChanged.connect(self.position_selection_changed)

        self.number_of_employees = self.create_input_field("Number of Employees:", "i.e. 4")

        widgets = [position_label, self.position_dropdown, self.number_of_employees, select_day_title, self.day_dropdown]

        self.add_widget(create_shift_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        for widget in widgets:
            self.add_widget(widget)

        self.start_end_time()
        self.add_widget(self.create_button("Submit", self.BUTTON_WIDTH, self.BUTTON_FONT, self.submit))
        self.add_vspacer(60)


    def start_end_time(self):
        """
        Add the start and end time selectors to the bottom of the page.
        """

        time_selector_layout = QHBoxLayout()
        time_title_layout = QHBoxLayout()

        start = QLabel('Start Time:')
        start.setFont(self.LABEL_FONT)

        end = QLabel('End Time:')
        end.setFont(self.LABEL_FONT)

        self.start_time_selector = QTimeEdit(self)
        self.start_time_selector.setTime(QTime.currentTime())
        self.start_time_selector.setDisplayFormat("HH:mm")
        self.start_time_selector.setStyleSheet(self.TIME_SELECTOR_STYLE)

        self.end_time_selector = QTimeEdit(self)
        self.end_time_selector.setTime(QTime.currentTime())
        self.end_time_selector.setDisplayFormat("HH:mm")
        self.end_time_selector.setStyleSheet(self.TIME_SELECTOR_STYLE)

        time_selector_layout.addWidget(self.start_time_selector)
        time_selector_layout.addSpacing(50)
        time_selector_layout.addWidget(self.end_time_selector)

        time_title_layout.addWidget(start)
        time_title_layout.addSpacing(50)
        time_title_layout.addWidget(end)

        self.add_widget(QWidget(self, layout=time_title_layout), alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.add_widget(QWidget(self, layout=time_selector_layout), alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)


    def calendar(self):
        """
        Add a calendar popup for date selection.
        """

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet(self.CALENDAR_DROPDOWN_STYLE)

        self.add_widget(self.date_edit, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)


    def load_positions(self):
        """
        Load the positions in the business from the database into the dropdown.
        """

        if self.parent_stack.current_user:
            self.business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            positions = Database_Controller.get_positions(self.business_id)
            self.position_dropdown.clear()
            self.position_dropdown.addItems(positions)
            return True


    def position_selection_changed(self, index):
        """
        Update the attribute to the contents of the dropdown option selected.
        """

        self.selected_position = self.position_dropdown.itemText(index)


    def day_selection_changed(self, index):
        """
        Update the attribute to the contents of the dropdown option selected.
        """

        self.selected_day = self.day_dropdown.itemText(index)


    def submit(self):
        """
        Gather all the information entered by the user and validate the input.
        """

        try:
            selected_position = self.position_dropdown.currentText()
            selected_day = self.day_dropdown.currentText()
            num_employees = self.number_of_employees.input_field.text()

            if not num_employees.isdigit():
                raise ValueError("Number of employees must be a valid integer.")

            num_employees = int(num_employees)

            start_time = self.start_time_selector.time().toString('HH.mm')
            end_time = self.end_time_selector.time().toString('HH.mm')
            if float(start_time) < float(end_time):
                business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
                position = Database_Controller.find_position_id(selected_position, business_id)
                Database_Controller.add_shift(business_id, position, num_employees, selected_day, start_time, end_time)
                self.number_of_employees.input_field.clear()

                self.parent_stack.load_page("Manage Shifts")
            else:
                Insufficient_details()
        except ValueError:
            Insufficient_details()


    def refresh(self):
        """
        Refresh the page by loading the positions dropdown.
        """

        self.load_positions()
        return super().refresh()


class View_Timeoff_Request_Details(Page):
    """
    Allows managers to view the details of a time off request
    """

    def __init__(self, parent_stack):
        """
        Sets up all of the text needed for the information
        """

        super().__init__()
        self.parent_stack = parent_stack

        self.employee = QLabel("Placeholder", self)
        self.employee.setFont(self.LABEL_FONT)

        shift_details_title = QLabel("Time-Off Request", self)
        shift_details_title.setFont(self.TITLE_FONT)

        self.startdate_time =  QLabel("Placeholder", self)
        self.startdate_time.setFont(self.LABEL_FONT)

        self.enddate_time = QLabel("Placeholder", self)
        self.enddate_time.setFont(self.LABEL_FONT)

        self.status = QLabel("Placeholder", self)
        self.status.setFont(self.LABEL_FONT)

        done_button = self.create_button("Accept", 240, QFont('Cascadia Mono', 12), self.accept_clicked)
        assign_shift = self.create_button("Reject", 240, QFont('Cascadia Mono', 12), self.reject_clicked)

        self.add_vspacer(30)
        self.add_widget(shift_details_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(70)

        widgets = [self.employee, self.startdate_time, self.enddate_time, self.status]
        for widget in widgets:
            self.add_widget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.add_vspacer(35)

        self.add_vspacer(50)
        self.add_widget(done_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(35)
        self.add_widget(assign_shift, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(150)


    def accept_clicked(self):
        """
        Handle the accept button being clicked
        """

        Database_Controller.update_time_off_status(2, self.parent_stack.current_request[0])
        self.parent_stack.load_page("Managers Main Page")


    def reject_clicked(self):
        """
        Handle the reject button being clicked
        """

        Database_Controller.update_time_off_status(3, self.parent_stack.current_request[0])
        self.parent_stack.load_page("Managers Main Page")


    def assign_shift_clicked(self):
        """
        Handle the assign shift button being clicked
        """

        self.parent_stack.load_page("Assign Shift To Employee")


    def refresh(self):
        """
        Refreshes the page with the employees information
        """

        start_time = self.parent_stack.current_request[4]
        start_date = self.parent_stack.current_request[2]
        end_time = self.parent_stack.current_request[5]
        end_date = self.parent_stack.current_request[3]
        employee = self.parent_stack.current_request[1]
        firstname, lastname = Database_Controller.find_employee(employee)[2],Database_Controller.find_employee(employee)[3]
        current_status_id = self.parent_stack.current_request[6]
        status = Database_Controller.find_status_name(current_status_id)
        notes = self.parent_stack.current_request[7]

        position_id = Database_Controller.find_employee(employee)[6]
        position = Database_Controller.find_position(position_id)

        startday,startmonth,startyear = str(start_date).split("-")
        endday,endmonth,endyear = str(end_date).split("-")

        startday_of_week = date(int(startyear),int(startmonth),int(startday)).isoweekday() -1
        if int(startday) == 1 or int(startday) == 21 or int(startday) == 31:
            startdate = f"The {startday}st of {MONTHS[int(startmonth)-1]} {startyear}"
        elif int(startday) == 2 or int(startday) == 22:
            startdate = f"The {startday}nd of {MONTHS[int(startmonth)-1]} {startyear}"
        elif int(startday) == 3 or int(startday) == 23:
            startdate = f"The {startday}rd of {MONTHS[int(startmonth)-1]} {startyear}"
        else:
            startdate = f"The {startday}th of {MONTHS[int(startmonth)-1]} {startyear}"

        if int(endday) == 1 or int(endday) == 21 or int(endday) == 31:
            enddate = f"The {endday}st of {MONTHS[int(endmonth)-1]} {endyear}"
        elif int(endday) == 2 or int(endday) == 22:
            enddate = f"The {endday}nd of {MONTHS[int(endmonth)-1]} {endyear}"
        elif int(endday) == 3 or int(endday) == 23:
            enddate = f"The {endday}rd of {MONTHS[int(endmonth)-1]} {endyear}"
        else:
            enddate = f"The {endday}th of {MONTHS[int(endmonth)-1]} {endyear}"
            
        self.startdate_time.setText(f"From: {startdate} at {start_time}")
        self.enddate_time.setText(f"To: {enddate} at {end_time}")
        self.employee.setText(f"{firstname} {lastname} has requested time off:")
        self.status.setText(f"Current status: {status[0]}")


class View_Empty_Shift_Details(Page):
    """
    Allows a user to view the details for a shift
    """

    def __init__(self, parent_stack):
        """
        Setup the widgets for the shift details page
        """

        super().__init__()
        self.parent_stack = parent_stack

        shift_details_title = QLabel("Shift Details", self)
        shift_details_title.setFont(self.TITLE_FONT)

        self.date =  QLabel("Placeholder", self)
        self.date.setFont(self.LABEL_FONT)

        self.time = QLabel("Placeholder", self)
        self.time.setFont(self.LABEL_FONT)

        self.employee = QLabel("Placeholder", self)
        self.employee.setFont(self.LABEL_FONT)

        done_button = self.create_button("Done", 240, QFont('Cascadia Mono', 12), self.done_clicked )
        assign_shift = self.create_button("Assign Employee to Shift", 270, QFont('Cascadia Mono', 12), self.assign_shift_clicked)
        delete_shift = self.create_button("Delete Shift", 270, QFont('Cascadia Mono', 12), self.delete_shift_clicked)

        self.add_vspacer(30)
        self.add_widget(shift_details_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(70)

        widgets = [ self.date, self.time, self.employee]
        for widget in widgets:
            self.add_widget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.add_vspacer(35)

        self.add_vspacer(50)
        self.add_widget(done_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(35)
        self.add_widget(assign_shift, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(35)
        self.add_widget(delete_shift, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(150)


    def done_clicked(self):
        """
        Handle the done button being clicked
        """

        self.parent_stack.load_page("Managers Main Page")


    def delete_shift_clicked(self):
        """
        Handle the event of a user pressing to delete a shift
        """
        
        shift_id = self.parent_stack.current_shift[0]
        Database_Controller.delete_shift(shift_id)
        self.parent_stack.load_page("Manage Shifts")


    def assign_shift_clicked(self):
        """
        Handle the assign shift button being clicked
        """

        self.parent_stack.load_page("Assign Shift To Employee")


    def refresh(self):
        """
        Refreshes the page with the employees information
        """

        start_time = self.parent_stack.current_shift[2]
        end_time = self.parent_stack.current_shift[3]
        cal_date = self.parent_stack.current_shift[4]
        employees = self.parent_stack.current_shift[5]

        position_id = self.parent_stack.current_shift[6]
        position = Database_Controller.find_position(position_id)

        if not '-' in cal_date:
            self.date.setText(f"Every {cal_date}")
        else:
            day,month,year = cal_date.split("-")
            day_of_week = date(int(year),int(month),int(day)).isoweekday() -1
            if int(day) == 1 or int(day) == 21 or int(day) == 31:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}st of {MONTHS[int(month)-1]} {year}")
            elif int(day) == 2 or int(day) == 22:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}nd of {MONTHS[int(month)-1]} {year}")
            elif int(day) == 3 or int(day) == 23:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}rd of {MONTHS[int(month)-1]} {year}")
            else:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}th of {MONTHS[int(month)-1]} {year}")
            
        self.time.setText(f"{start_time} - {end_time}")
        
        if employees == 1:
            self.employee.setText(f"{employees} {position} needed")
        else:
            self.employee.setText(f"{employees} {position}s needed")


class Assign_Shift(Page):
    """
    Allows a user to view the details for a shift
    """

    def __init__(self, parent_stack):
        super().__init__()
        self.parent_stack = parent_stack

        shift_details_title = QLabel("Shift Details", self)
        shift_details_title.setFont(self.TITLE_FONT)

        self.date =  QLabel("Placeholder", self)
        self.date.setFont(self.LABEL_FONT)

        self.time = QLabel("Placeholder", self)
        self.time.setFont(self.LABEL_FONT)

        self.employee = QLabel("Placeholder", self)
        self.employee.setFont(self.LABEL_FONT)

        select_employee_title = QLabel("Select Employee:", self)
        select_employee_title.setFont(self.LABEL_FONT)

        self.employee_dropdown = QComboBox()
        self.employee_dropdown.setStyleSheet(self.DROPDOWN_STYLE)
        self.employee_dropdown.setFixedWidth(self.FORM_WIDTH)
        self.employee_dropdown.setFont(QFont('Ariel', 12))
        self.employee_dropdown.currentIndexChanged.connect(self.position_selection_changed)

        submit_button = self.create_button("Submit", 240, QFont('Cascadia Mono', 12), self.submit_clicked )

        self.add_vspacer(30)
        self.add_widget(shift_details_title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(70)

        widgets = [self.date, self.time, self.employee, select_employee_title,self.employee_dropdown]
        for widget in widgets:
            self.add_widget(widget, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.add_vspacer(35)

        self.add_widget(submit_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.add_vspacer(185)


    def submit_clicked(self):
        """
        Handle the submit button being clicked
        """

        first, last = self.selected_employee.split(" ")
        employee_id = Database_Controller.find_employee_id(first, last)[0]
        shift_id = self.parent_stack.current_shift[0]

        Database_Controller.assign_shift(employee_id, shift_id, 1)
        self.parent_stack.load_page("Managers Main Page")


    def position_selection_changed(self, index):
        """
        Update the attribute to the contents of the dropdown option selected.
        """

        self.selected_employee = self.employee_dropdown.itemText(index)


    def load_employees(self):
        """
        Load the available employees for a shift
        """

        if self.parent_stack.current_user:
            shift_id = self.parent_stack.current_shift[0]
            start_time = self.parent_stack.current_shift[2]
            end_time = self.parent_stack.current_shift[3]
            cal_date = self.parent_stack.current_shift[4]
            position_id = self.parent_stack.current_shift[6]
            business_id = Database_Controller.find_employee(self.parent_stack.current_user)[1]
            names = []

            employee_ids = Database_Controller.get_available_employees(business_id, position_id, cal_date, start_time, end_time)
            for id in employee_ids:
                on_shift = Database_Controller.find_if_employee_available(id, self.parent_stack.current_shift[0] )
                if on_shift == True:
                    employee = Database_Controller.find_employee(id)
                    names.append(f"{employee[2]} {employee[3]}")
                else:
                    pass

            self.employee_dropdown.clear()
            self.employee_dropdown.addItems(names)
            return True


    def refresh(self):
        """
        Refreshes the page with the employees information
        """

        self.load_employees()
        start_time = self.parent_stack.current_shift[2]
        end_time = self.parent_stack.current_shift[3]
        cal_date = self.parent_stack.current_shift[4]
        employees = self.parent_stack.current_shift[5]

        position_id = self.parent_stack.current_shift[6]
        position = Database_Controller.find_position(position_id)

        if not '-' in cal_date:
            self.date.setText(f"Every {cal_date}")
        else:
            day,month,year = cal_date.split("-")
            day_of_week = date(int(year),int(month),int(day)).isoweekday() -1
            if int(day) == 1 or int(day) == 21 or int(day) == 31:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}st of {MONTHS[int(month)-1]} {year}")
            elif int(day) == 2 or int(day) == 22:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}nd of {MONTHS[int(month)-1]} {year}")
            elif int(day) == 3 or int(day) == 23:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}rd of {MONTHS[int(month)-1]} {year}")
            else:
                self.date.setText(f"{DAYS_OF_WEEK[day_of_week]} the {day}th of {MONTHS[int(month)-1]} {year}")
            
        self.time.setText(f"{start_time} - {end_time}")
        
        if employees == 1:
            self.employee.setText(f"{employees} {position} needed")
        else:
            self.employee.setText(f"{employees} {position}s needed")


class Add_Empty_Shift_Data(QStyledItemDelegate):
    """
    Fill out the shifts grid with all shift data
    """

    def __init__(self, target_cells, shifts, parent=None):
        """
        Setup target cells and shift data
        """

        super().__init__(parent)

        self.target_cells = target_cells
        self.shifts = shifts


    def paint(self, painter, option, index):
        """
        Fill cells with correct information
        """

        row, column = index.row(), index.column()
        if (row, column) in self.target_cells:

            shift = self.shifts[column][row]
            start_time = shift[2]
            end_time = shift[3]
            employees_needed = shift[5]
            position = Database_Controller.find_position(shift[6])
            employees_on = Database_Controller.find_num_of_employees_working(shift[0])
            if int(employees_needed) <= int(employees_on):
                painter.fillRect(option.rect, QColor("#222222"))
                painter.setPen(Qt.white)
                painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))

                if employees_needed == 1:
                    painter.drawText(option.rect, Qt.AlignCenter, f"{start_time} - {end_time} \n {employees_needed} {position}")

                else:
                    painter.drawText(option.rect, Qt.AlignCenter, f"{start_time} - {end_time} \n {employees_needed} {position}s")
            else:
                painter.fillRect(option.rect, QColor("#333333"))
                painter.setPen(Qt.white)
                painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))

                if employees_needed == 1:
                    painter.drawText(option.rect, Qt.AlignCenter, f"{start_time} - {end_time} \n {employees_needed} {position}")

                else:
                    painter.drawText(option.rect, Qt.AlignCenter, f"{start_time} - {end_time} \n {employees_needed} {position}s")

        else:
            super().paint(painter, option, index)


class Add_Assigned_Shift_Data_Manager(QStyledItemDelegate):
    """
    Fill out the employee-shifts grid with all shift times
    """

    def __init__(self, target_cells, shifts, parent=None):
        """
        Setup target cells and shift data
        """

        super().__init__(parent)
        self.target_cells = target_cells
        self.shifts = shifts  


    def paint(self, painter, option, index):
        """
        Fill cells with correct information
        """

        row, column = index.row(), index.column()
        if (row, column) in self.target_cells:
            shift_id = self.shifts[row][-1][column]
            time = Database_Controller.get_shift_times(shift_id)
            status = Database_Controller.get_shift_status(self.shifts[row][0], shift_id)

            painter.fillRect(option.rect, QColor("#333333"))
            painter.setPen(Qt.white)
            painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))
            if status == 1:
                painter.drawText(option.rect, Qt.AlignCenter, f"Pending Publish: \n{time[0]} - {time[1]}")
            elif status == 4:
                painter.drawText(option.rect, Qt.AlignCenter, f"{time[0]} - {time[1]}")

        else:
            super().paint(painter, option, index)


class Add_Assigned_Shift_Data_Employee(QStyledItemDelegate):
    """
    Fill out the employee-shifts grid with all shift times
    """

    def __init__(self, target_cells, shifts, parent=None):
        """
        Setup target cells and shift data
        """

        super().__init__(parent)
        self.target_cells = target_cells
        self.shifts = shifts  


    def paint(self, painter, option, index):
        """
        Fill cells with correct information
        """

        row, column = index.row(), index.column()
        if (row, column) in self.target_cells:
            
            shift_id = self.shifts[row][-1][column]
            time = Database_Controller.get_shift_times(shift_id)
            status = Database_Controller.get_shift_status(self.shifts[row][0], shift_id)
            if status == 4:
                painter.fillRect(option.rect, QColor("#333333"))
                painter.setPen(Qt.white)
                painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))
                painter.drawText(option.rect, Qt.AlignCenter, f"{time[0]} - {time[1]}")
            else:
                pass

        else:
            super().paint(painter, option, index)


class Add_Time_Off_Data(QStyledItemDelegate):
    """
    Fill out the time-off requests grid with all shift times
    """

    def __init__(self, target_cells, time_off, parent=None):
        """
        Setup target cells and request data
        """

        super().__init__(parent)
        self.target_cells = target_cells
        self.timeoff = time_off 

        
    def paint(self, painter, option, index):
        """
        Fill cells with correct information
        """

        row, column = index.row(), index.column()
        if (row, column) in self.target_cells:
            shift_data = self.timeoff[row][column]
            start_date, end_date = shift_data[2], shift_data[3]
            start_time, end_time = shift_data[4], shift_data[5]
            if shift_data[-2] == 1:      
                painter.fillRect(option.rect, QColor("#333333"))
                painter.setPen(Qt.white)
                painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))
                painter.drawText(option.rect, Qt.AlignCenter, f"Pending: \n{start_date}\n-\n{end_date}")
            elif shift_data[-2] == 2:            
                painter.fillRect(option.rect, QColor("#1E831F"))
                painter.setPen(Qt.black)
                painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))
                painter.drawText(option.rect, Qt.AlignCenter, f"Approved: \n{start_date}\n-\n{end_date}")
            elif shift_data[-2] == 3:            
                painter.fillRect(option.rect, QColor("#831E1E"))
                painter.setPen(Qt.white)
                painter.setFont(QFont("Cascadia Mono", 12, QFont.Bold))
                painter.drawText(option.rect, Qt.AlignCenter, f"Rejected: \n{start_date}\n-\n{end_date}")
        else:
            super().paint(painter, option, index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = Stack()
    program.showMaximized()
    sys.exit(app.exec())