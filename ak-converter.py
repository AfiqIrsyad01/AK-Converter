import sys
import math
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QLineEdit, QPushButton, QGridLayout, QGroupBox,
    QDateEdit, QSpinBox, QDoubleSpinBox, QColorDialog, QGraphicsDropShadowEffect,
    QSizePolicy, QScrollArea
)
from PyQt6.QtGui import QColor, QDoubleValidator
from PyQt6.QtCore import Qt, QDate
# Network for currency API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Requests library not available. Currency conversion will not work.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All-In-One Unit Converter")
        self.setGeometry(100, 100, 980, 720)

        # Modern dark theme stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1d1f27, stop:1 #14151b);
                color: #e6e6e6;
                font-family: Segoe UI, Roboto, "Helvetica Neue", Arial;
            }
            QTabWidget::pane {
                border: 0px;
                background: transparent;
                margin: 10px;
            }
            QTabBar::tab {
                background: #2a2d3a;
                color: #d8d8d8;
                padding: 10px 16px;
                margin-right: 6px;
                border-radius: 8px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: #3a3f54;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #34394b;
            }
            QGroupBox {
                background: #242734;
                border: 1px solid #3c4155;
                border-radius: 12px;
                margin-top: 20px;
                padding: 20px;
                padding-top: 28px;
                font-size: 16px;
                color: #9bd5ff;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 8px;
                margin-top: -12px;
                background: #242734;
            }
            QLabel {
                color: #e6e6e6;
                font-size: 14px;
            }
            QLabel#resultLabel {
                font-size: 18px;
                font-weight: bold;
                color: #7ce0d3;
                padding: 10px;
                background: rgba(124, 224, 211, 0.08);
                border: 1px solid rgba(124, 224, 211, 0.25);
                border-radius: 8px;
                margin-top: 10px;
            }
            QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit {
                background: #2a2d3a;
                color: #ffffff;
                border: 1px solid #414658;
                border-radius: 8px;
                padding: 8px 10px;
                min-height: 28px;
            }
            QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover {
                border: 1px solid #5a6075;
            }
            QComboBox QAbstractItemView {
                background: #2a2d3a;
                border: 1px solid #414658;
                selection-background-color: #3a3f54;
            }
            QPushButton {
                background: #5568fe;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #6a7bff;
            }
            QPushButton:pressed {
                background: #3f53ff;
            }
            QPushButton#secondary {
                background: #3a3f54;
            }
            QPushButton#secondary:hover {
                background: #464c67;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#scrollWidget {
                background: transparent;
            }
        """)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tabs
        self.add_category_tab("Physical Units", ["Length", "Mass", "Temperature", "Volume", "Area", "Speed", "Energy", "Power", "Pressure", "Angle", "Density"])
        self.add_category_tab("Digital Units", ["Storage", "Data Rate", "Time", "Decimal to Hex", "RGB to Hex"])
        self.add_category_tab("Health/Education", ["BMI", "CGPA", "Grade Converter", "Age Calculator", "Date Difference", "BMR/TDEE", "Tip Calculator", "Discount Calculator"])
        self.add_category_tab("Finance", ["Currency Converter"])
        self.add_category_tab("Miscellaneous", ["Frequency", "Force", "Torque", "Viscosity", "Fuel Efficiency", "Illuminance"])

        # Currency cache
        self.currency_rates_cache = {}  # { base: {"timestamp": datetime, "rates": {...}} }

    def add_category_tab(self, title, converters):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollWidget")
        scroll_layout = QVBoxLayout(scroll_widget)

        # Selector row
        selector_row = QHBoxLayout()
        selector_label = QLabel("Select Converter:")
        selector = QComboBox()
        selector.addItems(converters)
        selector.setMaximumWidth(300)
        selector_row.addWidget(selector)
        selector_row.addStretch()
        scroll_layout.addLayout(selector_row)

        # Per-tab content container
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        scroll_layout.addWidget(content_widget)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        tab_layout.addWidget(scroll_area)

        # Store in tab object
        tab.selector = selector
        tab.content_layout = content_layout

        # Hook
        selector.currentTextChanged.connect(lambda text, t=tab: self.update_converter(text, t))

        # Initial
        if converters:
            self.update_converter(converters[0], tab)

        self.tab_widget.addTab(tab, title)

    def clear_layout(self, layout):
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())

    def update_converter(self, converter_type, tab):
        self.clear_layout(tab.content_layout)

        group = QGroupBox(f"{converter_type} Converter")
        group_layout = QVBoxLayout(group)

        # Subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 8)
        group.setGraphicsEffect(shadow)

        # Build specific converter
        if converter_type == "Length":
            self.create_unit_converter(group_layout, self.get_length_units())
        elif converter_type == "Mass":
            self.create_unit_converter(group_layout, self.get_mass_units())
        elif converter_type == "Temperature":
            self.create_temperature_converter(group_layout)
        elif converter_type == "Volume":
            self.create_unit_converter(group_layout, self.get_volume_units())
        elif converter_type == "Area":
            self.create_unit_converter(group_layout, self.get_area_units())
        elif converter_type == "Speed":
            self.create_unit_converter(group_layout, self.get_speed_units())
        elif converter_type == "Energy":
            self.create_unit_converter(group_layout, self.get_energy_units())
        elif converter_type == "Power":
            self.create_unit_converter(group_layout, self.get_power_units())
        elif converter_type == "Pressure":
            self.create_unit_converter(group_layout, self.get_pressure_units())
        elif converter_type == "Angle":
            self.create_unit_converter(group_layout, self.get_angle_units())
        elif converter_type == "Density":
            self.create_unit_converter(group_layout, self.get_density_units())
        elif converter_type == "Storage":
            self.create_unit_converter(group_layout, self.get_storage_units())
        elif converter_type == "Data Rate":
            self.create_unit_converter(group_layout, self.get_data_rate_units())
        elif converter_type == "Time":
            self.create_unit_converter(group_layout, self.get_time_units())
        elif converter_type == "Decimal to Hex":
            self.create_dec_to_hex_converter(group_layout)
        elif converter_type == "RGB to Hex":
            self.create_rgb_to_hex_converter(group_layout)
        elif converter_type == "BMI":
            self.create_bmi_converter(group_layout)
        elif converter_type == "CGPA":
            self.create_cgpa_converter(group_layout)
        elif converter_type == "Grade Converter":
            self.create_grade_converter(group_layout)
        elif converter_type == "Age Calculator":
            self.create_age_calculator(group_layout)
        elif converter_type == "Date Difference":
            self.create_date_difference(group_layout)
        elif converter_type == "BMR/TDEE":
            self.create_bmr_tdee_converter(group_layout)
        elif converter_type == "Tip Calculator":
            self.create_tip_calculator(group_layout)
        elif converter_type == "Discount Calculator":
            self.create_discount_calculator(group_layout)
        elif converter_type == "Currency Converter":
            self.create_currency_converter(group_layout)
        elif converter_type == "Frequency":
            self.create_unit_converter(group_layout, self.get_frequency_units())
        elif converter_type == "Force":
            self.create_unit_converter(group_layout, self.get_force_units())
        elif converter_type == "Torque":
            self.create_unit_converter(group_layout, self.get_torque_units())
        elif converter_type == "Viscosity":
            self.create_unit_converter(group_layout, self.get_viscosity_units())
        elif converter_type == "Fuel Efficiency":
            self.create_fuel_efficiency_converter(group_layout)
        elif converter_type == "Illuminance":
            self.create_unit_converter(group_layout, self.get_illuminance_units())

        tab.content_layout.addWidget(group)

    def number_line_edit(self, placeholder="Enter a number", allow_negative=True):
        le = QLineEdit()
        le.setPlaceholderText(placeholder)
        bottom = -1e18 if allow_negative else 0.0
        le.setValidator(QDoubleValidator(bottom, 1e18, 12))
        return le

    # General unit converter using multiplicative factors to a base unit
    def create_unit_converter(self, layout, units):
        input_label = QLabel("Enter Value:")
        input_value = self.number_line_edit("Enter a number")
        from_unit = QComboBox()
        from_unit.addItems(list(units.keys()))
        to_unit = QComboBox()
        to_unit.addItems(list(units.keys()))
        btn_row = QHBoxLayout()
        convert_btn = QPushButton("Convert")
        swap_btn = QPushButton("Swap")
        swap_btn.setObjectName("secondary")
        btn_row.addWidget(convert_btn)
        btn_row.addWidget(swap_btn)
        output_label = QLabel("Result: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QGridLayout()
        form_layout.addWidget(input_label, 0, 0)
        form_layout.addWidget(input_value, 0, 1)
        form_layout.addWidget(QLabel("From:"), 1, 0)
        form_layout.addWidget(from_unit, 1, 1)
        form_layout.addWidget(QLabel("To:"), 2, 0)
        form_layout.addWidget(to_unit, 2, 1)
        form_layout.addLayout(btn_row, 3, 0, 1, 2)
        form_layout.addWidget(output_label, 4, 0, 1, 2)

        layout.addLayout(form_layout)

        def do_convert():
            text = input_value.text().strip()
            if not text:
                output_label.setText("Result: Enter a value")
                return
            try:
                value = float(text)
                from_factor = units[from_unit.currentText()]
                to_factor = units[to_unit.currentText()]
                result = value * from_factor / to_factor
                output_label.setText(f"Result: {result:.6f}")
            except Exception:
                output_label.setText("Result: Invalid input")

        def do_swap():
            i = from_unit.currentText()
            j = to_unit.currentText()
            from_unit.setCurrentText(j)
            to_unit.setCurrentText(i)
            do_convert()

        convert_btn.clicked.connect(do_convert)
        swap_btn.clicked.connect(do_swap)
        input_value.returnPressed.connect(do_convert)
        from_unit.currentIndexChanged.connect(do_convert)
        to_unit.currentIndexChanged.connect(do_convert)

    # Temperature special converter
    def create_temperature_converter(self, layout):
        input_label = QLabel("Enter Value:")
        input_value = self.number_line_edit("Enter temperature", allow_negative=True)
        from_unit = QComboBox()
        from_unit.addItems(["Celsius", "Fahrenheit", "Kelvin"])
        to_unit = QComboBox()
        to_unit.addItems(["Celsius", "Fahrenheit", "Kelvin"])
        btn_row = QHBoxLayout()
        convert_btn = QPushButton("Convert")
        swap_btn = QPushButton("Swap")
        swap_btn.setObjectName("secondary")
        btn_row.addWidget(convert_btn)
        btn_row.addWidget(swap_btn)
        output_label = QLabel("Result: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QGridLayout()
        form_layout.addWidget(input_label, 0, 0)
        form_layout.addWidget(input_value, 0, 1)
        form_layout.addWidget(QLabel("From:"), 1, 0)
        form_layout.addWidget(from_unit, 1, 1)
        form_layout.addWidget(QLabel("To:"), 2, 0)
        form_layout.addWidget(to_unit, 2, 1)
        form_layout.addLayout(btn_row, 3, 0, 1, 2)
        form_layout.addWidget(output_label, 4, 0, 1, 2)

        layout.addLayout(form_layout)

        def convert_temp(value, from_u, to_u):
            if from_u == to_u:
                return value
            if from_u == "Celsius":
                if to_u == "Fahrenheit": return value * 9/5 + 32
                if to_u == "Kelvin": return value + 273.15
            elif from_u == "Fahrenheit":
                if to_u == "Celsius": return (value - 32) * 5/9
                if to_u == "Kelvin": return (value - 32) * 5/9 + 273.15
            elif from_u == "Kelvin":
                if to_u == "Celsius": return value - 273.15
                if to_u == "Fahrenheit": return (value - 273.15) * 9/5 + 32
            return value

        def do_convert():
            text = input_value.text().strip()
            if not text:
                output_label.setText("Result: Enter a value")
                return
            try:
                value = float(text)
                result = convert_temp(value, from_unit.currentText(), to_unit.currentText())
                output_label.setText(f"Result: {result:.4f}")
            except Exception:
                output_label.setText("Result: Invalid input")

        def do_swap():
            i = from_unit.currentText()
            j = to_unit.currentText()
            from_unit.setCurrentText(j)
            to_unit.setCurrentText(i)
            do_convert()

        convert_btn.clicked.connect(do_convert)
        swap_btn.clicked.connect(do_swap)
        input_value.returnPressed.connect(do_convert)
        from_unit.currentIndexChanged.connect(do_convert)
        to_unit.currentIndexChanged.connect(do_convert)

    # Decimal to Hex
    def create_dec_to_hex_converter(self, layout):
        input_label = QLabel("Enter Decimal Value:")
        input_value = self.number_line_edit("e.g., 255 or -42", allow_negative=True)
        convert_btn = QPushButton("Convert to Hex")
        output_label = QLabel("Hex: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QVBoxLayout()
        form_layout.addWidget(input_label)
        form_layout.addWidget(input_value)
        form_layout.addWidget(convert_btn)
        form_layout.addWidget(output_label)

        layout.addLayout(form_layout)

        def do_convert():
            text = input_value.text().strip()
            if not text:
                output_label.setText("Hex: Enter a value")
                return
            try:
                value = int(float(text))
                result = hex(value)[2:].upper() if value >= 0 else "-" + hex(-value)[2:].upper()
                output_label.setText(f"Hex: {result}")
            except Exception:
                output_label.setText("Hex: Invalid input")

        convert_btn.clicked.connect(do_convert)
        input_value.returnPressed.connect(do_convert)

    # RGB to Hex
    def create_rgb_to_hex_converter(self, layout):
        color_btn = QPushButton("Pick RGB Color")
        output_label = QLabel("Hex: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QVBoxLayout()
        form_layout.addWidget(color_btn)
        form_layout.addWidget(output_label)
        layout.addLayout(form_layout)

        def pick_color():
            color = QColorDialog.getColor()
            if color.isValid():
                hex_color = color.name()[1:].upper()
                output_label.setText(f"Hex: {hex_color}")

        color_btn.clicked.connect(pick_color)

    # BMI with unit options and validation
    def create_bmi_converter(self, layout):
        weight_input = self.number_line_edit("Weight", allow_negative=False)
        weight_unit = QComboBox()
        weight_unit.addItems(["kg", "lb"])

        height_input = self.number_line_edit("Height", allow_negative=False)
        height_unit = QComboBox()
        height_unit.addItems(["m", "cm", "in"])

        convert_btn = QPushButton("Calculate BMI")
        output_label = QLabel("BMI: Waiting for input...")
        output_label.setObjectName("resultLabel")

        grid = QGridLayout()
        grid.addWidget(QLabel("Weight:"), 0, 0)
        hrow = QHBoxLayout()
        hrow.addWidget(weight_input)
        hrow.addWidget(weight_unit)
        w_widget = QWidget(); w_widget.setLayout(hrow)
        grid.addWidget(w_widget, 0, 1)

        grid.addWidget(QLabel("Height:"), 1, 0)
        h2 = QHBoxLayout()
        h2.addWidget(height_input)
        h2.addWidget(height_unit)
        h_widget = QWidget(); h_widget.setLayout(h2)
        grid.addWidget(h_widget, 1, 1)

        grid.addWidget(convert_btn, 2, 0, 1, 2)
        grid.addWidget(output_label, 3, 0, 1, 2)

        layout.addLayout(grid)

        def do_bmi():
            tw = weight_input.text().strip()
            th = height_input.text().strip()
            if not tw or not th:
                output_label.setText("BMI: Enter weight and height")
                return
            try:
                w = float(tw)
                h = float(th)
                # Convert weight to kg
                if weight_unit.currentText() == "lb":
                    w = w * 0.45359237
                # Convert height to meters
                hu = height_unit.currentText()
                if hu == "cm":
                    h = h / 100.0
                elif hu == "in":
                    h = h * 0.0254
                # Guard against zero
                if h <= 0 or w <= 0:
                    output_label.setText("BMI: Values must be > 0")
                    return
                bmi = w / (h * h)
                category = (
                    "Underweight" if bmi < 18.5 else
                    "Normal" if bmi < 25 else
                    "Overweight" if bmi < 30 else
                    "Obesity"
                )
                output_label.setText(f"BMI: {bmi:.2f} ({category})")
            except Exception:
                output_label.setText("BMI: Invalid input")

        convert_btn.clicked.connect(do_bmi)
        weight_input.returnPressed.connect(do_bmi)
        height_input.returnPressed.connect(do_bmi)

    # CGPA (simple average of grades)
    def create_cgpa_converter(self, layout):
        num_subjects_label = QLabel("Number of Subjects:")
        num_subjects = QSpinBox()
        num_subjects.setRange(1, 30)
        grades_layout = QVBoxLayout()
        convert_btn = QPushButton("Calculate CGPA")
        output_label = QLabel("CGPA: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(num_subjects_label)
        row.addWidget(num_subjects)
        form_layout.addLayout(row)
        form_layout.addLayout(grades_layout)
        form_layout.addWidget(convert_btn)
        form_layout.addWidget(output_label)
        layout.addLayout(form_layout)

        grades_inputs = []

        def update_grades():
            nonlocal grades_inputs
            # Clear old
            while grades_layout.count():
                item = grades_layout.takeAt(0)
                w = item.widget()
                if w: w.deleteLater()
            grades_inputs = []
            # Add new
            for i in range(num_subjects.value()):
                h_layout = QHBoxLayout()
                grade_input = self.number_line_edit(f"Grade {i+1} (0-4.0)", allow_negative=False)
                h_layout.addWidget(QLabel(f"Grade {i+1} (0-4.0):"))
                h_layout.addWidget(grade_input)
                container = QWidget(); container.setLayout(h_layout)
                grades_layout.addWidget(container)
                grades_inputs.append(grade_input)

        num_subjects.valueChanged.connect(update_grades)
        update_grades()

        def calculate():
            try:
                grades = []
                for g in grades_inputs:
                    if g.text().strip():
                        val = float(g.text())
                        if 0 <= val <= 4.0:
                            grades.append(val)
                        else:
                            output_label.setText("CGPA: Grades must be between 0 and 4.0")
                            return
                if grades:
                    cgpa = sum(grades) / len(grades)
                    output_label.setText(f"CGPA: {cgpa:.2f}")
                else:
                    output_label.setText("CGPA: Enter at least one grade")
            except Exception:
                output_label.setText("CGPA: Invalid input")

        convert_btn.clicked.connect(calculate)

    # Grade Converter (letter to GPA)
    def create_grade_converter(self, layout):
        grade_letter = QComboBox()
        grade_letter.addItems(["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"])
        convert_btn = QPushButton("Convert to GPA")
        output_label = QLabel("GPA: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Letter Grade:"))
        form_layout.addWidget(grade_letter)
        form_layout.addWidget(convert_btn)
        form_layout.addWidget(output_label)
        layout.addLayout(form_layout)

        grade_map = {
            "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
            "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0
        }

        def convert():
            g = grade_letter.currentText()
            output_label.setText(f"GPA: {grade_map[g]:.1f}")

        convert_btn.clicked.connect(convert)

    # Age Calculator
    def create_age_calculator(self, layout):
        birth_date = QDateEdit()
        birth_date.setCalendarPopup(True)
        birth_date.setDate(QDate.currentDate().addYears(-20))
        calculate_btn = QPushButton("Calculate Age")
        output_label = QLabel("Age: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Birth Date:"))
        form_layout.addWidget(birth_date)
        form_layout.addWidget(calculate_btn)
        form_layout.addWidget(output_label)
        layout.addLayout(form_layout)

        def calculate():
            birth = birth_date.date().toPyDate()
            today = datetime.today().date()
            age_years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            output_label.setText(f"Age: {age_years} years")

        calculate_btn.clicked.connect(calculate)

    # Date Difference
    def create_date_difference(self, layout):
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate().addDays(-1))
        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate())
        calculate_btn = QPushButton("Calculate Difference")
        output_label = QLabel("Difference: Waiting for input...")
        output_label.setObjectName("resultLabel")

        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Start Date:"), 0, 0)
        form_layout.addWidget(start_date, 0, 1)
        form_layout.addWidget(QLabel("End Date:"), 1, 0)
        form_layout.addWidget(end_date, 1, 1)
        form_layout.addWidget(calculate_btn, 2, 0, 1, 2)
        form_layout.addWidget(output_label, 3, 0, 1, 2)
        layout.addLayout(form_layout)

        def calculate():
            start = start_date.date().toPyDate()
            end = end_date.date().toPyDate()
            diff = (end - start).days
            output_label.setText(f"Difference: {diff} days")

        calculate_btn.clicked.connect(calculate)

    # BMR/TDEE (Mifflin-St Jeor)
    def create_bmr_tdee_converter(self, layout):
        weight = self.number_line_edit("kg", allow_negative=False)
        height = self.number_line_edit("cm", allow_negative=False)
        age = self.number_line_edit("Years", allow_negative=False)
        gender = QComboBox(); gender.addItems(["Male", "Female"])
        activity = QComboBox()
        activity.addItems(["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Super Active"])
        calculate_btn = QPushButton("Calculate BMR/TDEE")
        output_label = QLabel("Results: Waiting for input...")
        output_label.setObjectName("resultLabel")

        grid = QGridLayout()
        grid.addWidget(QLabel("Weight (kg):"), 0, 0); grid.addWidget(weight, 0, 1)
        grid.addWidget(QLabel("Height (cm):"), 1, 0); grid.addWidget(height, 1, 1)
        grid.addWidget(QLabel("Age:"), 2, 0); grid.addWidget(age, 2, 1)
        grid.addWidget(QLabel("Gender:"), 3, 0); grid.addWidget(gender, 3, 1)
        grid.addWidget(QLabel("Activity Level:"), 4, 0); grid.addWidget(activity, 4, 1)
        grid.addWidget(calculate_btn, 5, 0, 1, 2)
        grid.addWidget(output_label, 6, 0, 1, 2)
        layout.addLayout(grid)

        activity_factors = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Super Active": 1.9
        }

        def calculate():
            try:
                w = float(weight.text())
                h = float(height.text())
                a = int(float(age.text()))
                base = (10 * w) + (6.25 * h) - (5 * a) + (5 if gender.currentText() == "Male" else -161)
                tdee = base * activity_factors[activity.currentText()]
                output_label.setText(f"Results: BMR: {base:.0f} kcal/day, TDEE: {tdee:.0f} kcal/day")
            except Exception:
                output_label.setText("Results: Invalid input")

        calculate_btn.clicked.connect(calculate)

    # Tip Calculator
    def create_tip_calculator(self, layout):
        bill = self.number_line_edit("Bill amount", allow_negative=False)
        tip_percent = QDoubleSpinBox()
        tip_percent.setRange(0, 100)
        tip_percent.setValue(15.0)
        tip_percent.setSuffix("%")
        calculate_btn = QPushButton("Calculate Tip")
        output_label = QLabel("Tip: Waiting for input...")
        output_label.setObjectName("resultLabel")

        grid = QGridLayout()
        grid.addWidget(QLabel("Bill Amount:"), 0, 0); grid.addWidget(bill, 0, 1)
        grid.addWidget(QLabel("Tip Percentage:"), 1, 0); grid.addWidget(tip_percent, 1, 1)
        grid.addWidget(calculate_btn, 2, 0, 1, 2)
        grid.addWidget(output_label, 3, 0, 1, 2)
        layout.addLayout(grid)

        def calculate():
            try:
                b = float(bill.text())
                percent = tip_percent.value() / 100
                tip = b * percent
                total = b + tip
                output_label.setText(f"Tip: {tip:.2f}, Total: {total:.2f}")
            except Exception:
                output_label.setText("Tip: Invalid input")

        calculate_btn.clicked.connect(calculate)

    # Discount Calculator
    def create_discount_calculator(self, layout):
        price = self.number_line_edit("Original price", allow_negative=False)
        discount_percent = QDoubleSpinBox()
        discount_percent.setRange(0, 100)
        discount_percent.setValue(10.0)
        discount_percent.setSuffix("%")
        calculate_btn = QPushButton("Calculate Discount")
        output_label = QLabel("Discounted Price: Waiting for input...")
        output_label.setObjectName("resultLabel")

        grid = QGridLayout()
        grid.addWidget(QLabel("Original Price:"), 0, 0); grid.addWidget(price, 0, 1)
        grid.addWidget(QLabel("Discount Percentage:"), 1, 0); grid.addWidget(discount_percent, 1, 1)
        grid.addWidget(calculate_btn, 2, 0, 1, 2)
        grid.addWidget(output_label, 3, 0, 1, 2)
        layout.addLayout(grid)

        def calculate():
            try:
                p = float(price.text())
                percent = discount_percent.value() / 100
                discount = p * percent
                final = p - discount
                output_label.setText(f"Discount: {discount:.2f}, Final Price: {final:.2f}")
            except Exception:
                output_label.setText("Discounted Price: Invalid input")

        calculate_btn.clicked.connect(calculate)

    # Currency Converter (robust API, caching, swap, auto-convert)
    def create_currency_converter(self, layout):
        amount_input = self.number_line_edit("Amount", allow_negative=False)
        from_curr = QComboBox()
        to_curr = QComboBox()
        convert_btn = QPushButton("Convert")
        swap_btn = QPushButton("Swap")
        swap_btn.setObjectName("secondary")
        refresh_btn = QPushButton("Refresh Rates")
        refresh_btn.setObjectName("secondary")
        btn_row = QHBoxLayout()
        btn_row.addWidget(convert_btn)
        btn_row.addWidget(swap_btn)
        btn_row.addWidget(refresh_btn)
        output_label = QLabel("Result: Waiting for input...")
        output_label.setObjectName("resultLabel")
        attribution = QLabel('<a href="https://exchangerate.host" style="color: #9aa2c0;">Rates by exchangerate.host</a>')
        attribution.setOpenExternalLinks(True)

        # Broad set of common currencies + BTC/ETH
        currencies = [
            "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR",
            "NZD", "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "MXN", "BRL",
            "ZAR", "HKD", "SGD", "KRW", "THB", "TWD", "AED", "SAR", "TRY",
            "ILS", "RUB", "BTC", "ETH"
        ]
        from_curr.addItems(currencies)
        to_curr.addItems(currencies)
        from_curr.setCurrentText("USD")
        to_curr.setCurrentText("EUR")

        grid = QGridLayout()
        grid.addWidget(QLabel("Amount:"), 0, 0); grid.addWidget(amount_input, 0, 1)
        grid.addWidget(QLabel("From:"), 1, 0); grid.addWidget(from_curr, 1, 1)
        grid.addWidget(QLabel("To:"), 2, 0); grid.addWidget(to_curr, 2, 1)
        grid.addLayout(btn_row, 3, 0, 1, 2)
        grid.addWidget(output_label, 4, 0, 1, 2)
        grid.addWidget(attribution, 5, 0, 1, 2)
        layout.addLayout(grid)

        def fetch_rates(base, force_refresh=False):
            # Return cached if fresh (30 minutes)
            entry = self.currency_rates_cache.get(base)
            if entry and not force_refresh:
                ts = entry.get("timestamp")
                if ts and (datetime.now() - ts) < timedelta(minutes=30):
                    return entry["rates"]

            if not REQUESTS_AVAILABLE:
                return None

            try:
                # Free, no-key API that supports crypto: exchangerate.host
                url = f"https://api.exchangerate.host/latest?base={base}"
                resp = requests.get(url, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    rates = data.get("rates", {})
                    if rates:
                        self.currency_rates_cache[base] = {
                            "timestamp": datetime.now(),
                            "rates": rates
                        }
                        return rates
            except Exception as e:
                print(f"Error fetching currency rates: {e}")
            return None

        def do_convert(force=False):
            amt_text = amount_input.text().strip()
            if not amt_text:
                output_label.setText("Result: Enter an amount")
                return
            try:
                amount = float(amt_text)
                fc = from_curr.currentText()
                tc = to_curr.currentText()
                if fc == tc:
                    output_label.setText(f"Result: {amount:.6f} {tc}")
                    return
                rates = fetch_rates(fc, force_refresh=force)
                if rates and tc in rates:
                    rate = float(rates[tc])
                    result = amount * rate
                    output_label.setText(f"Result: {result:.6f} {tc}  (Rate: {rate:.6f})")
                else:
                    output_label.setText("Result: Could not fetch rates (try Refresh Rates)")
            except Exception:
                output_label.setText("Result: Invalid amount")

        def do_swap():
            i = from_curr.currentText()
            j = to_curr.currentText()
            from_curr.setCurrentText(j)
            to_curr.setCurrentText(i)
            do_convert()

        convert_btn.clicked.connect(lambda: do_convert(False))
        swap_btn.clicked.connect(do_swap)
        refresh_btn.clicked.connect(lambda: do_convert(True))
        amount_input.returnPressed.connect(lambda: do_convert(False))
        from_curr.currentIndexChanged.connect(lambda: do_convert(False))
        to_curr.currentIndexChanged.connect(lambda: do_convert(False))

    # Fuel efficiency MPG <-> L/100km
    def create_fuel_efficiency_converter(self, layout):
        input_value = self.number_line_edit("Enter value", allow_negative=False)
        from_unit = QComboBox(); from_unit.addItems(["MPG (US)", "L/100km"])
        to_unit = QComboBox(); to_unit.addItems(["MPG (US)", "L/100km"])
        convert_btn = QPushButton("Convert")
        output_label = QLabel("Result: Waiting for input...")
        output_label.setObjectName("resultLabel")

        grid = QGridLayout()
        grid.addWidget(QLabel("Enter Value:"), 0, 0); grid.addWidget(input_value, 0, 1)
        grid.addWidget(QLabel("From:"), 1, 0); grid.addWidget(from_unit, 1, 1)
        grid.addWidget(QLabel("To:"), 2, 0); grid.addWidget(to_unit, 2, 1)
        grid.addWidget(convert_btn, 3, 0, 1, 2)
        grid.addWidget(output_label, 4, 0, 1, 2)
        layout.addLayout(grid)

        def convert_fuel(v, fu, tu):
            if fu == tu:
                return v
            if fu == "MPG (US)" and tu == "L/100km":
                return 235.215 / v if v != 0 else float("inf")
            if fu == "L/100km" and tu == "MPG (US)":
                return 235.215 / v if v != 0 else float("inf")
            return v

        def do_convert():
            t = input_value.text().strip()
            if not t:
                output_label.setText("Result: Enter a value")
                return
            try:
                v = float(t)
                res = convert_fuel(v, from_unit.currentText(), to_unit.currentText())
                output_label.setText(f"Result: {res:.3f}")
            except Exception:
                output_label.setText("Result: Invalid input")

        convert_btn.clicked.connect(do_convert)
        input_value.returnPressed.connect(do_convert)
        from_unit.currentIndexChanged.connect(do_convert)
        to_unit.currentIndexChanged.connect(do_convert)

    # Units dictionaries (factors relative to base unit named in comment)
    def get_length_units(self):  # base: meter
        return {"Meter": 1, "Centimeter": 0.01, "Millimeter": 0.001, "Kilometer": 1000,
                "Inch": 0.0254, "Foot": 0.3048, "Yard": 0.9144, "Mile": 1609.344, "Nautical Mile": 1852}

    def get_mass_units(self):  # base: kilogram
        return {"Milligram": 1e-6, "Gram": 0.001, "Kilogram": 1, "Tonne": 1000,
                "Ounce": 0.028349523125, "Pound": 0.45359237}

    def get_volume_units(self):  # base: cubic meter
        return {"Cubic Meter": 1, "Liter": 0.001, "Milliliter": 1e-6,
                "Gallon (US)": 0.003785411784, "Quart (US)": 0.000946352946,
                "Pint (US)": 0.000473176473, "Cup (US)": 0.0002365882365}

    def get_area_units(self):  # base: square meter
        return {"Square Meter": 1, "Square Centimeter": 1e-4, "Square Kilometer": 1e6,
                "Square Inch": 0.00064516, "Square Foot": 0.09290304, "Acre": 4046.8564224, "Hectare": 10000}

    def get_speed_units(self):  # base: m/s
        return {"m/s": 1, "km/h": 1/3.6, "mph": 0.44704, "knot": 0.514444}

    def get_energy_units(self):  # base: joule
        return {"Joule": 1, "Kilojoule": 1000, "Calorie": 4.184, "Kilocalorie": 4184,
                "Watt-hour": 3600, "Kilowatt-hour": 3.6e6, "Electronvolt": 1.602176634e-19}

    def get_power_units(self):  # base: watt
        return {"Watt": 1, "Kilowatt": 1000, "Horsepower (metric)": 735.49875, "Horsepower (US)": 745.699872}

    def get_pressure_units(self):  # base: pascal
        return {"Pascal": 1, "Bar": 1e5, "Atmosphere": 101325, "PSI": 6894.757293168, "Torr": 133.322368}

    def get_angle_units(self):  # base: radian
        return {"Radian": 1, "Degree": math.pi/180, "Gradian": math.pi/200}

    def get_density_units(self):  # base: kg/m^3
        return {"kg/m³": 1, "g/cm³": 1000, "lb/ft³": 16.01846337}

    def get_storage_units(self):  # base: byte
        return {"Bit": 1/8, "Byte": 1, "Kilobyte (KB)": 1024, "Megabyte (MB)": 1024**2, "Gigabyte (GB)": 1024**3,
                "Terabyte (TB)": 1024**4}

    def get_data_rate_units(self):  # base: bps
        return {"bps": 1, "Kbps": 1_000, "Mbps": 1_000_000, "Gbps": 1_000_000_000,
                "KiB/s": 8*1024, "MiB/s": 8*1024**2, "GiB/s": 8*1024**3}

    def get_time_units(self):  # base: second
        return {"Second": 1, "Minute": 60, "Hour": 3600, "Day": 86400, "Week": 604800,
                "Year (365d)": 31536000}

    def get_frequency_units(self):  # base: hertz
        return {"Hertz": 1, "Kilohertz": 1_000, "Megahertz": 1_000_000, "Gigahertz": 1_000_000_000}

    def get_force_units(self):  # base: newton
        return {"Newton": 1, "Kilonewton": 1000, "Pound-force": 4.4482216152605, "Dyne": 1e-5}

    def get_torque_units(self):  # base: N·m
        return {"Newton-meter": 1, "Foot-pound": 1.3558179483314004, "Inch-pound": 0.1129848290276167}

    def get_viscosity_units(self):  # base: Pa·s
        return {"Pascal-second": 1, "Poise": 0.1, "Centipoise": 0.001}

    def get_illuminance_units(self):  # base: lux
        return {"Lux": 1, "Foot-candle": 10.76391041671}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
