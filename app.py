import csv
import os
import sqlite3
import sys
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtCore import QPointF, Qt, QDate
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPixmap,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

DB_NAME = "wedding_manager.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        relation TEXT,
        rsvp_status TEXT DEFAULT 'Pending',
        meal_preference TEXT,
        seating TEXT,
        attended INTEGER DEFAULT 0
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        date TEXT,
        venue TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_guests (
        event_id INTEGER,
        guest_id INTEGER,
        PRIMARY KEY (event_id, guest_id),
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE CASCADE
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        event_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rituals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ritual_name TEXT NOT NULL,
        muhurat_time TEXT,
        pundit_notes TEXT,
        event_id INTEGER,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
    )""")

    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('groom_name', 'Aarav')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('bride_name', 'Ananya')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('wedding_date', ?)", (datetime.now().strftime("%Y-%m-%d"),))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('rsvp_deadline', ?)", (datetime.now().strftime("%Y-%m-%d"),))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('budget_per_guest', '0')")

    conn.commit()
    conn.close()


ROYAL_INDIAN_QSS = """
QMainWindow {
    background-color: transparent;
}

QWidget#CentralContainer {
    background: transparent;
}

/* Tab Bar Styling */
QTabWidget::pane {
    border: 2px solid rgba(255, 215, 0, 0.65);
    border-radius: 18px;
    background-color: rgba(18, 2, 6, 0.78);
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(60, 6, 16, 0.85), stop:1 rgba(25, 2, 7, 0.85));
    color: #F3E5AB;
    font-weight: bold;
    font-size: 13px;
    padding: 12px 22px;
    margin-right: 6px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border: 1px solid rgba(212, 175, 55, 0.45);
    border-bottom: none;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:0.5 #FF9900, stop:1 #D4AF37);
    color: #120103;
    font-weight: 900;
    border-color: #FFE57F;
}

QTabBar::tab:hover:!selected {
    background: rgba(139, 0, 0, 0.9);
    color: #FFFFFF;
}

/* Glassmorphism Cards */
QFrame#Card {
    background-color: rgba(26, 3, 8, 0.82);
    border: 1.5px solid rgba(255, 215, 0, 0.45);
    border-radius: 16px;
}

QFrame#MetricCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(50, 6, 14, 0.88), stop:1 rgba(20, 2, 6, 0.88));
    border: 1.5px solid rgba(255, 215, 0, 0.6);
    border-left: 6px solid #FF9900;
    border-radius: 14px;
}

QLabel#MetricValue {
    color: #FFD700;
    font-size: 28px;
    font-weight: 900;
}

QLabel#MetricLabel {
    color: #F3E5AB;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
}

QLineEdit, QComboBox, QTimeEdit, QDateEdit {
    background-color: rgba(10, 1, 3, 0.88);
    border: 1px solid rgba(212, 175, 55, 0.5);
    border-radius: 8px;
    padding: 9px 12px;
    font-size: 13px;
    color: #FFFDF7;
}

QLineEdit:focus, QComboBox:focus, QTimeEdit:focus, QDateEdit:focus {
    border: 2px solid #FFD700;
    background-color: rgba(22, 2, 6, 0.95);
}

QComboBox QAbstractItemView {
    background-color: #2D0308;
    color: #FFFDF7;
    selection-background-color: #FF9900;
    selection-color: #120103;
    border: 1px solid #FFD700;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFE066, stop:1 #D4AF37);
    color: #120103;
    font-weight: bold;
    font-size: 12px;
    border-radius: 8px;
    padding: 10px 16px;
    border: 1px solid #FFD700;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFD700, stop:1 #FF9900);
    color: #000000;
}

QPushButton#SecondaryBtn {
    background-color: rgba(139, 0, 0, 0.85);
    color: #FFFDF7;
    border: 1px solid rgba(255, 215, 0, 0.6);
}

QPushButton#SecondaryBtn:hover {
    background-color: #A52A2A;
}

QPushButton#DangerBtn {
    background-color: rgba(120, 20, 30, 0.88);
    color: #F8D7DA;
    border: 1px solid #F5C6CB;
}

QPushButton#DangerBtn:hover {
    background-color: #A91D22;
}

/* Tables */
QTableWidget {
    background-color: rgba(10, 1, 3, 0.85);
    border: 1px solid rgba(212, 175, 55, 0.4);
    border-radius: 8px;
    gridline-color: #4A0810;
    color: #FFFDF7;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #8B0000;
    color: #FFD700;
}

QHeaderView::section {
    background-color: #2D0308;
    color: #FFD700;
    font-weight: bold;
    font-size: 12px;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #FFD700;
}

QCheckBox {
    color: #F3E5AB;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #FFD700;
    background-color: rgba(10, 1, 3, 0.9);
}

QCheckBox::indicator:checked {
    background-color: #FF9900;
    border-color: #FFD700;
}
"""


class MetricCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("MetricCard")
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 14, 18, 14)

        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("MetricValue")

        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("MetricLabel")

        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_title)
        self.setLayout(layout)

    def set_value(self, val):
        self.lbl_value.setText(val)


class BackgroundOverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_image_path = "wedding_bg.jpg"
        self.bg_pixmap = None
        if os.path.exists(self.bg_image_path):
            self.bg_pixmap = QPixmap(self.bg_image_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        if self.bg_pixmap and not self.bg_pixmap.isNull():
            scaled = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (w - scaled.width()) // 2
            y = (h - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            fallback = QLinearGradient(0, 0, w, h)
            fallback.setColorAt(0.0, QColor("#1C0104"))
            fallback.setColorAt(0.5, QColor("#3D040D"))
            fallback.setColorAt(1.0, QColor("#120002"))
            painter.fillRect(0, 0, w, h, fallback)

        painter.fillRect(0, 0, w, h, QColor(12, 1, 4, 180))

        center = QPointF(w / 2, h / 2)
        rad_grad = QRadialGradient(center, max(w, h) * 0.6)
        rad_grad.setColorAt(0.0, QColor(255, 180, 0, 45))
        rad_grad.setColorAt(0.7, QColor(18, 2, 5, 140))
        rad_grad.setColorAt(1.0, QColor(8, 0, 2, 230))
        painter.setBrush(QBrush(rad_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, w, h)


class WeddingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shubh Vivah — Executive Royal Mandap Suite")
        self.resize(1380, 900)
        self.setStyleSheet(ROYAL_INDIAN_QSS)

        self.bg_overlay = BackgroundOverlayWidget(self)
        self.setCentralWidget(self.bg_overlay)

        self.selected_guest_id = None

        main_layout = QVBoxLayout(self.bg_overlay)
        main_layout.setContentsMargins(28, 18, 28, 22)

        # Header Section
        header_layout = QHBoxLayout()

        self.header_title = QLabel("🪔 Aarav ❤️ Ananya")
        self.header_title.setFont(QFont("Georgia", 24, QFont.Weight.Bold))
        self.header_title.setStyleSheet("color: #FFD700;")

        sub_header = QLabel("｜ Royal Vivah Manager 🪷")
        sub_header.setFont(QFont("Georgia", 14))
        sub_header.setStyleSheet("color: #F3E5AB; margin-top: 6px;")

        badge = QLabel("GRAND EDITION")
        badge.setStyleSheet("""
            background-color: rgba(139, 0, 0, 0.88);
            color: #FFD700;
            font-size: 10px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid #FFD700;
            margin-left: 12px;
        """)

        header_layout.addWidget(self.header_title)
        header_layout.addWidget(sub_header)
        header_layout.addWidget(badge)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Tabs Setup
        self.tabs = QTabWidget()
        self.tab_dashboard = QWidget()
        self.tab_guests = QWidget()
        self.tab_events = QWidget()
        self.tab_rituals = QWidget()
        self.tab_expenses = QWidget()
        self.tab_reports = QWidget()

        self.tabs.addTab(self.tab_dashboard, "Overview")
        self.tabs.addTab(self.tab_guests, "Guest Directory")
        self.tabs.addTab(self.tab_events, "Functions & Itinerary")
        self.tabs.addTab(self.tab_rituals, "Muhurat & Rituals")
        self.tabs.addTab(self.tab_expenses, "Budget Ledger")
        self.tabs.addTab(self.tab_reports, "Analytics & Insights")

        main_layout.addWidget(self.tabs)

        self.setup_dashboard()
        self.setup_guests()
        self.setup_events()
        self.setup_rituals()
        self.setup_expenses()
        self.setup_reports()

        self.load_settings()
        self.tabs.currentChanged.connect(self.on_tab_changed)

    def get_db(self):
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def load_settings(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        settings = dict(cursor.fetchall())
        conn.close()

        groom = settings.get("groom_name", "Aarav")
        bride = settings.get("bride_name", "Ananya")
        wedding_date_str = settings.get("wedding_date", datetime.now().strftime("%Y-%m-%d"))
        rsvp_deadline_str = settings.get("rsvp_deadline", datetime.now().strftime("%Y-%m-%d"))
        budget_per_guest_str = settings.get("budget_per_guest", "0")

        self.inp_groom.setText(groom)
        self.inp_bride.setText(bride)
        self.header_title.setText(f"🪔 {groom} ❤️ {bride}")

        self.dt_wedding.setDate(QDate.fromString(wedding_date_str, "yyyy-MM-dd"))
        self.dt_rsvp_deadline.setDate(QDate.fromString(rsvp_deadline_str, "yyyy-MM-dd"))
        self.inp_budget_per_guest.setText(budget_per_guest_str)

    def save_settings(self):
        groom = self.inp_groom.text().strip() or "Aarav"
        bride = self.inp_bride.text().strip() or "Ananya"
        w_date = self.dt_wedding.date().toString("yyyy-MM-dd")
        r_date = self.dt_rsvp_deadline.date().toString("yyyy-MM-dd")

        if self.dt_rsvp_deadline.date() > self.dt_wedding.date():
            QMessageBox.warning(
                self,
                "Invalid Dates",
                "The RSVP deadline cannot be after the wedding date.",
            )
            return

        try:
            budget_per_guest = float(self.inp_budget_per_guest.text().strip() or "0")
            if budget_per_guest < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Budget per guest must be a valid non-negative number.")
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('groom_name', ?)", (groom,))
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('bride_name', ?)", (bride,))
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('wedding_date', ?)", (w_date,))
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('rsvp_deadline', ?)", (r_date,))
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('budget_per_guest', ?)", (str(budget_per_guest),))
        conn.commit()
        conn.close()

        self.header_title.setText(f"🪔 {groom} ❤️ {bride}")
        QMessageBox.information(self, "Updated", "Wedding Settings and Dates saved successfully.")

    def reset_settings(self):
        self.inp_groom.setText("Aarav")
        self.inp_bride.setText("Ananya")
        self.dt_wedding.setDate(QDate.currentDate())
        self.dt_rsvp_deadline.setDate(QDate.currentDate())
        self.inp_budget_per_guest.setText("0")
        self.save_settings()

    def is_rsvp_locked(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='rsvp_deadline'")
        row = cursor.fetchone()
        conn.close()

        if row and row[0]:
            deadline = datetime.strptime(row[0], "%Y-%m-%d").date()
            if datetime.now().date() > deadline:
                return True
        return False

    def get_attending_guest_count(self):
        """Guests currently confirmed as attending the wedding."""
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM guests WHERE rsvp_status = 'Confirmed'")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_budget_per_guest(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='budget_per_guest'")
        row = cursor.fetchone()
        conn.close()
        try:
            return float(row[0]) if row and row[0] else 0.0
        except ValueError:
            return 0.0

    def get_budget_limit(self):
        """Total budget cap = budget per guest x number of guests currently attending."""
        return self.get_budget_per_guest() * self.get_attending_guest_count()

    def on_tab_changed(self, index):
        self.sync_all_data()
        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.load_guests()
        elif index == 2:
            self.load_events()
            self.load_assigned()
        elif index == 3:
            self.load_rituals()
        elif index == 4:
            self.load_expenses()
        elif index == 5:
            self.render_charts()

    def sync_all_data(self):
        self.populate_event_dropdowns()
        self.populate_expense_event_dropdown()
        self.populate_ritual_event_dropdown()

    def reset_all_data(self):
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to clear all wedding data?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            conn = self.get_db()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM event_guests;")
            cursor.execute("DELETE FROM rituals;")
            cursor.execute("DELETE FROM expenses;")
            cursor.execute("DELETE FROM events;")
            cursor.execute("DELETE FROM guests;")

            try:
                cursor.execute("DELETE FROM sqlite_sequence;")
            except sqlite3.OperationalError:
                pass

            conn.commit()
            conn.close()

            self.clear_guest_form()
            self.sync_all_data()
            self.refresh_dashboard()
            self.load_guests()
            self.load_events()
            self.load_rituals()
            self.load_expenses()
            self.load_assigned()
            self.render_charts()

            QMessageBox.information(self, "Reset Complete", "All wedding records wiped clean.")

    # --- DASHBOARD ---
    def setup_dashboard(self):
        layout = QVBoxLayout()

        couple_card = QFrame()
        couple_card.setObjectName("Card")
        couple_layout = QVBoxLayout()
        couple_layout.setContentsMargins(20, 16, 20, 16)

        c_title = QLabel("👑 Wedding Personalization & Key Dates")
        c_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFD700;")
        couple_layout.addWidget(c_title)

        c_inputs = QHBoxLayout()
        self.inp_groom = QLineEdit()
        self.inp_groom.setPlaceholderText("Groom Name")

        self.inp_bride = QLineEdit()
        self.inp_bride.setPlaceholderText("Bride Name")

        # Added Wedding Date and RSVP Deadline pickers
        lbl_wdate = QLabel("Wedding Date:")
        lbl_wdate.setStyleSheet("color: #F3E5AB; font-weight: bold;")
        self.dt_wedding = QDateEdit()
        self.dt_wedding.setCalendarPopup(True)
        self.dt_wedding.setDisplayFormat("yyyy-MM-dd")
        self.dt_wedding.setMinimumDate(QDate.currentDate())

        lbl_rsvp = QLabel("RSVP Deadline:")
        lbl_rsvp.setStyleSheet("color: #F3E5AB; font-weight: bold;")
        self.dt_rsvp_deadline = QDateEdit()
        self.dt_rsvp_deadline.setCalendarPopup(True)
        self.dt_rsvp_deadline.setDisplayFormat("yyyy-MM-dd")

        lbl_budget = QLabel("Budget / Guest (₹):")
        lbl_budget.setStyleSheet("color: #F3E5AB; font-weight: bold;")
        self.inp_budget_per_guest = QLineEdit()
        self.inp_budget_per_guest.setPlaceholderText("e.g. 1500")
        self.inp_budget_per_guest.setFixedWidth(100)

        btn_save_couple = QPushButton("Save Settings")
        btn_save_couple.clicked.connect(self.save_settings)

        btn_reset_couple = QPushButton("Reset Settings")
        btn_reset_couple.setObjectName("SecondaryBtn")
        btn_reset_couple.clicked.connect(self.reset_settings)

        c_inputs.addWidget(self.inp_groom)
        c_inputs.addWidget(self.inp_bride)
        c_inputs.addWidget(lbl_wdate)
        c_inputs.addWidget(self.dt_wedding)
        c_inputs.addWidget(lbl_rsvp)
        c_inputs.addWidget(self.dt_rsvp_deadline)
        c_inputs.addWidget(lbl_budget)
        c_inputs.addWidget(self.inp_budget_per_guest)
        c_inputs.addWidget(btn_save_couple)
        c_inputs.addWidget(btn_reset_couple)

        couple_layout.addLayout(c_inputs)
        couple_card.setLayout(couple_layout)

        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("🌺 Event Statistics Dashboard")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFD700;")
        card_layout.addWidget(title)
        card_layout.addSpacing(10)

        cards_hbox = QHBoxLayout()
        self.c1 = MetricCard("Total Invited Guests", "0")
        self.c2 = MetricCard("Confirmed RSVPs", "0")
        self.c3 = MetricCard("Scheduled Rituals", "0")
        self.c4 = MetricCard("Total Expense", "₹0.00")
        self.c5 = MetricCard("Budget Limit", "₹0.00")
        self.c6 = MetricCard("Budget Remaining", "₹0.00")

        cards_hbox.addWidget(self.c1)
        cards_hbox.addWidget(self.c2)
        cards_hbox.addWidget(self.c3)
        cards_hbox.addWidget(self.c4)
        cards_hbox.addWidget(self.c5)
        cards_hbox.addWidget(self.c6)

        card_layout.addLayout(cards_hbox)
        card_layout.addSpacing(15)

        btn_box = QHBoxLayout()
        btn_reset = QPushButton("Reset All System Data")
        btn_reset.setObjectName("DangerBtn")
        btn_reset.clicked.connect(self.reset_all_data)

        btn_refresh = QPushButton("Refresh Counters")
        btn_refresh.clicked.connect(self.refresh_dashboard)

        btn_box.addStretch()
        btn_box.addWidget(btn_reset)
        btn_box.addWidget(btn_refresh)

        card_layout.addLayout(btn_box)
        card.setLayout(card_layout)

        layout.addWidget(couple_card)
        layout.addWidget(card)
        layout.addStretch()
        self.tab_dashboard.setLayout(layout)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM guests")
        tot = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM guests WHERE rsvp_status = 'Confirmed'")
        conf = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM rituals")
        rit = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(amount) FROM expenses")
        exp = cursor.fetchone()[0] or 0.0
        conn.close()

        budget_limit = self.get_budget_limit()
        remaining = budget_limit - exp

        self.c1.set_value(f"{tot:,}")
        self.c2.set_value(f"{conf:,}")
        self.c3.set_value(f"{rit:,}")
        self.c4.set_value(f"₹{exp:,.2f}")
        self.c5.set_value(f"₹{budget_limit:,.2f}")
        self.c6.set_value(f"₹{remaining:,.2f}")

    # --- GUEST DIRECTORY ---
    def setup_guests(self):
        layout = QHBoxLayout()

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_card.setFixedWidth(340)
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Add / Modify Guest")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFD700;")
        form_layout.addWidget(title)
        form_layout.addSpacing(10)

        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Full Name *")
        self.inp_contact = QLineEdit()
        self.inp_contact.setPlaceholderText("Phone / Email")
        self.inp_relation = QLineEdit()
        self.inp_relation.setPlaceholderText("Side (e.g. Ladkewale / Ladkiwale)")

        self.cmb_rsvp = QComboBox()
        self.cmb_rsvp.addItems(["Pending", "Confirmed", "Declined"])

        self.inp_meal = QLineEdit()
        self.inp_meal.setPlaceholderText("Diet (Jain, Pure Veg, Non-Veg)")
        self.inp_seating = QLineEdit()
        self.inp_seating.setPlaceholderText("Table / Zone Assignment")

        self.chk_attended = QCheckBox("Attendance Confirmed")

        btn_add = QPushButton("Add Guest")
        btn_add.clicked.connect(self.add_guest)

        btn_update = QPushButton("Update Selected")
        btn_update.setObjectName("SecondaryBtn")
        btn_update.clicked.connect(self.update_guest)

        btn_delete = QPushButton("Delete Guest")
        btn_delete.setObjectName("DangerBtn")
        btn_delete.clicked.connect(self.delete_guest)

        form_layout.addWidget(self.inp_name)
        form_layout.addWidget(self.inp_contact)
        form_layout.addWidget(self.inp_relation)
        form_layout.addWidget(self.cmb_rsvp)
        form_layout.addWidget(self.inp_meal)
        form_layout.addWidget(self.inp_seating)
        form_layout.addWidget(self.chk_attended)
        form_layout.addSpacing(10)
        form_layout.addWidget(btn_add)
        form_layout.addWidget(btn_update)
        form_layout.addWidget(btn_delete)
        form_layout.addStretch()
        form_card.setLayout(form_layout)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 20, 20, 20)

        top_bar = QHBoxLayout()
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Search guests by name or side...")
        self.inp_search.textChanged.connect(self.load_guests)

        btn_export = QPushButton("Export List (.csv)")
        btn_export.setObjectName("SecondaryBtn")
        btn_export.clicked.connect(self.export_guests_csv)

        top_bar.addWidget(self.inp_search)
        top_bar.addWidget(btn_export)
        table_layout.addLayout(top_bar)

        self.table_guests = QTableWidget()
        self.table_guests.setColumnCount(8)
        self.table_guests.setHorizontalHeaderLabels(
            ["ID", "Name", "Contact", "Side", "RSVP", "Diet", "Seating", "Present"]
        )
        self.table_guests.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_guests.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_guests.itemSelectionChanged.connect(self.on_select_guest)

        table_layout.addWidget(self.table_guests)
        table_card.setLayout(table_layout)

        layout.addWidget(form_card)
        layout.addWidget(table_card)
        self.tab_guests.setLayout(layout)
        self.load_guests()

    def add_guest(self):
        name = self.inp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Guest name is required.")
            return

        selected_rsvp = self.cmb_rsvp.currentText()
        if self.is_rsvp_locked() and (selected_rsvp != "Pending" or self.chk_attended.isChecked()):
            QMessageBox.warning(
                self,
                "RSVP Closed",
                "The RSVP/attendance deadline has passed! RSVP status and attendance can no longer be set.",
            )
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO guests (name, contact, relation, rsvp_status, meal_preference, seating, attended)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                name,
                self.inp_contact.text().strip(),
                self.inp_relation.text().strip(),
                selected_rsvp,
                self.inp_meal.text().strip(),
                self.inp_seating.text().strip(),
                1 if self.chk_attended.isChecked() else 0,
            ),
        )
        conn.commit()
        conn.close()
        self.clear_guest_form()
        self.load_guests()
        self.sync_all_data()

    def load_guests(self):
        self.table_guests.blockSignals(True)
        self.table_guests.setRowCount(0)
        query = f"%{self.inp_search.text().strip()}%"
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM guests WHERE name LIKE ? OR relation LIKE ?",
            (query, query),
        )
        rows = cursor.fetchall()
        conn.close()

        for r_idx, row in enumerate(rows):
            self.table_guests.insertRow(r_idx)
            for c_idx in range(7):
                self.table_guests.setItem(r_idx, c_idx, QTableWidgetItem(str(row[c_idx])))
            self.table_guests.setItem(r_idx, 7, QTableWidgetItem("Yes" if row[7] else "No"))
        self.table_guests.blockSignals(False)

    def on_select_guest(self):
        selected_rows = self.table_guests.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()

        id_item = self.table_guests.item(row, 0)
        if not id_item:
            return

        self.selected_guest_id = id_item.text()
        self.inp_name.setText(self.table_guests.item(row, 1).text())
        self.inp_contact.setText(self.table_guests.item(row, 2).text())
        self.inp_relation.setText(self.table_guests.item(row, 3).text())
        self.cmb_rsvp.setCurrentText(self.table_guests.item(row, 4).text())
        self.inp_meal.setText(self.table_guests.item(row, 5).text())
        self.inp_seating.setText(self.table_guests.item(row, 6).text())
        self.chk_attended.setChecked(self.table_guests.item(row, 7).text() == "Yes")

    def update_guest(self):
        if not self.selected_guest_id:
            QMessageBox.information(
                self, "Selection Required", "Select a guest record to update."
            )
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT rsvp_status, attended FROM guests WHERE id=?", (self.selected_guest_id,))
        old_rsvp, old_attended = cursor.fetchone()

        selected_rsvp = self.cmb_rsvp.currentText()
        new_attended = 1 if self.chk_attended.isChecked() else 0

        if self.is_rsvp_locked() and (old_rsvp != selected_rsvp or old_attended != new_attended):
            conn.close()
            QMessageBox.warning(
                self,
                "RSVP Closed",
                "The RSVP/attendance deadline has passed! Guests can no longer change their RSVP status or attendance.",
            )
            return

        cursor.execute(
            """UPDATE guests SET name=?, contact=?, relation=?, rsvp_status=?, meal_preference=?, seating=?, attended=?
               WHERE id=?""",
            (
                self.inp_name.text().strip(),
                self.inp_contact.text().strip(),
                self.inp_relation.text().strip(),
                selected_rsvp,
                self.inp_meal.text().strip(),
                self.inp_seating.text().strip(),
                new_attended,
                self.selected_guest_id,
            ),
        )
        conn.commit()
        conn.close()
        self.clear_guest_form()
        self.load_guests()
        self.sync_all_data()

    def delete_guest(self):
        if not self.selected_guest_id:
            QMessageBox.information(
                self, "Selection Required", "Select a guest record to delete."
            )
            return
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM guests WHERE id=?", (self.selected_guest_id,))
        conn.commit()
        conn.close()
        self.clear_guest_form()
        self.load_guests()
        self.sync_all_data()

    def clear_guest_form(self):
        self.selected_guest_id = None
        self.inp_name.clear()
        self.inp_contact.clear()
        self.inp_relation.clear()
        self.inp_meal.clear()
        self.inp_seating.clear()
        self.chk_attended.setChecked(False)

    def export_guests_csv(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guests")
        rows = cursor.fetchall()
        conn.close()
        with open("guests_export.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["ID", "Name", "Contact", "Relation", "RSVP", "Meal", "Seating", "Attended"]
            )
            writer.writerows(rows)
        QMessageBox.information(self, "Exported", "Saved guest list to 'guests_export.csv'.")

    # --- EVENT SCHEDULE ---
    def setup_events(self):
        layout = QHBoxLayout()

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_card.setFixedWidth(340)
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)

        form_layout.addWidget(QLabel("<b>Add Ceremony / Function</b>"))
        self.inp_ev_name = QLineEdit()
        self.inp_ev_name.setPlaceholderText("Function (Haldi, Sangeet, Phere)")
        self.inp_ev_date = QLineEdit()
        self.inp_ev_date.setPlaceholderText("Date (YYYY-MM-DD)")
        self.inp_ev_venue = QLineEdit()
        self.inp_ev_venue.setPlaceholderText("Venue / Hall")

        btn_ev = QPushButton("Create Function")
        btn_ev.clicked.connect(self.add_event)

        form_layout.addWidget(self.inp_ev_name)
        form_layout.addWidget(self.inp_ev_date)
        form_layout.addWidget(self.inp_ev_venue)
        form_layout.addWidget(btn_ev)
        form_layout.addSpacing(15)

        form_layout.addWidget(QLabel("<b>Assign Guest to Function</b>"))
        self.cmb_assign_ev = QComboBox()
        self.cmb_assign_gt = QComboBox()
        btn_assign = QPushButton("Assign Guest")
        btn_assign.setObjectName("SecondaryBtn")
        btn_assign.clicked.connect(self.assign_guest)

        form_layout.addWidget(self.cmb_assign_ev)
        form_layout.addWidget(self.cmb_assign_gt)
        form_layout.addWidget(btn_assign)

        form_layout.addStretch()
        form_card.setLayout(form_layout)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 20, 20, 20)

        table_layout.addWidget(QLabel("<b>Scheduled Ceremonies</b>"))
        self.table_events = QTableWidget()
        self.table_events.setColumnCount(4)
        self.table_events.setHorizontalHeaderLabels(["ID", "Function", "Date", "Venue"])
        self.table_events.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.table_events)

        table_layout.addWidget(QLabel("<b>Function Invites Roster</b>"))
        self.table_assigned = QTableWidget()
        self.table_assigned.setColumnCount(3)
        self.table_assigned.setHorizontalHeaderLabels(["Function", "Guest Name", "Side"])
        self.table_assigned.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.table_assigned)

        table_card.setLayout(table_layout)
        layout.addWidget(form_card)
        layout.addWidget(table_card)
        self.tab_events.setLayout(layout)

        self.load_events()
        self.populate_event_dropdowns()
        self.load_assigned()

    def add_event(self):
        name = self.inp_ev_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Function name is required.")
            return
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (event_name, date, venue) VALUES (?, ?, ?)",
            (
                name,
                self.inp_ev_date.text().strip(),
                self.inp_ev_venue.text().strip(),
            ),
        )
        conn.commit()
        conn.close()
        self.inp_ev_name.clear()
        self.inp_ev_date.clear()
        self.inp_ev_venue.clear()
        self.load_events()
        self.sync_all_data()

    def load_events(self):
        self.table_events.setRowCount(0)
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events")
        for r_idx, row in enumerate(cursor.fetchall()):
            self.table_events.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table_events.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        conn.close()

    def populate_event_dropdowns(self):
        self.cmb_assign_ev.clear()
        self.cmb_assign_gt.clear()
        conn = self.get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, event_name FROM events")
        self.ev_map = {f"{r[1]} (ID:{r[0]})": r[0] for r in cursor.fetchall()}
        self.cmb_assign_ev.addItems(list(self.ev_map.keys()))

        cursor.execute("SELECT id, name FROM guests")
        self.gt_map = {f"{r[1]} (ID:{r[0]})": r[0] for r in cursor.fetchall()}
        self.cmb_assign_gt.addItems(list(self.gt_map.keys()))
        conn.close()

    def assign_guest(self):
        ev_key = self.cmb_assign_ev.currentText()
        gt_key = self.cmb_assign_gt.currentText()
        if ev_key not in self.ev_map or gt_key not in self.gt_map:
            QMessageBox.warning(self, "Selection Error", "Select a valid Function and Guest.")
            return
        conn = self.get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO event_guests (event_id, guest_id) VALUES (?, ?)",
                (self.ev_map[ev_key], self.gt_map[gt_key]),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.information(self, "Notice", "Guest already added to this ceremony.")
        conn.close()
        self.load_assigned()

    def load_assigned(self):
        self.table_assigned.setRowCount(0)
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT events.event_name, guests.name, guests.relation 
                          FROM event_guests 
                          JOIN events ON event_guests.event_id = events.id 
                          JOIN guests ON event_guests.guest_id = guests.id""")
        for r_idx, row in enumerate(cursor.fetchall()):
            self.table_assigned.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table_assigned.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        conn.close()

    # --- MUHURAT & RITUALS PLANNER ---
    def setup_rituals(self):
        layout = QHBoxLayout()

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_card.setFixedWidth(340)
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)

        form_layout.addWidget(QLabel("<b>Log Vedic Ritual / Shubh Muhurat</b>"))

        self.cmb_rit_ev = QComboBox()
        self.inp_rit_name = QLineEdit()
        self.inp_rit_name.setPlaceholderText("Ritual (Ganesh Puja, Hasta Melap)")

        self.time_rit_muhurat = QTimeEdit()
        self.time_rit_muhurat.setDisplayFormat("hh:mm AP")

        self.inp_rit_notes = QLineEdit()
        self.inp_rit_notes.setPlaceholderText("Pundit Instructions / Samagri Notes")

        btn_rit = QPushButton("Add Ritual Schedule")
        btn_rit.clicked.connect(self.add_ritual)

        form_layout.addWidget(self.cmb_rit_ev)
        form_layout.addWidget(self.inp_rit_name)
        form_layout.addWidget(QLabel("Auspicious Time (Muhurat):"))
        form_layout.addWidget(self.time_rit_muhurat)
        form_layout.addWidget(self.inp_rit_notes)
        form_layout.addSpacing(10)
        form_layout.addWidget(btn_rit)
        form_layout.addStretch()
        form_card.setLayout(form_layout)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 20, 20, 20)

        table_layout.addWidget(QLabel("<b>Auspicious Muhurat & Ceremony Sequence</b>"))
        self.table_rituals = QTableWidget()
        self.table_rituals.setColumnCount(4)
        self.table_rituals.setHorizontalHeaderLabels(
            ["Function", "Ritual / Vidhi", "Muhurat Time", "Pundit Notes"]
        )
        self.table_rituals.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table_layout.addWidget(self.table_rituals)
        table_card.setLayout(table_layout)

        layout.addWidget(form_card)
        layout.addWidget(table_card)
        self.tab_rituals.setLayout(layout)

        self.load_rituals()
        self.populate_ritual_event_dropdown()

    def populate_ritual_event_dropdown(self):
        self.cmb_rit_ev.clear()
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, event_name FROM events")
        self.rit_ev_map = {f"{r[1]} (ID:{r[0]})": r[0] for r in cursor.fetchall()}
        self.cmb_rit_ev.addItems(list(self.rit_ev_map.keys()))
        conn.close()

    def add_ritual(self):
        rit_name = self.inp_rit_name.text().strip()
        if not rit_name:
            QMessageBox.warning(self, "Input Error", "Ritual name is required.")
            return

        ev_str = self.cmb_rit_ev.currentText()
        if ev_str not in self.rit_ev_map:
            QMessageBox.warning(self, "Selection Error", "Select a valid parent function.")
            return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rituals (ritual_name, muhurat_time, pundit_notes, event_id) VALUES (?, ?, ?, ?)",
            (
                rit_name,
                self.time_rit_muhurat.time().toString("hh:mm AP"),
                self.inp_rit_notes.text().strip(),
                self.rit_ev_map[ev_str],
            ),
        )
        conn.commit()
        conn.close()

        self.inp_rit_name.clear()
        self.inp_rit_notes.clear()
        self.load_rituals()
        self.refresh_dashboard()

    def load_rituals(self):
        self.table_rituals.setRowCount(0)
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT events.event_name, rituals.ritual_name, rituals.muhurat_time, rituals.pundit_notes
                          FROM rituals JOIN events ON rituals.event_id = events.id""")
        for r_idx, row in enumerate(cursor.fetchall()):
            self.table_rituals.insertRow(r_idx)
            for c_idx, val in enumerate(row):
                self.table_rituals.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))
        conn.close()

    # --- EXPENSE TRACKER ---
    def setup_expenses(self):
        layout = QHBoxLayout()

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_card.setFixedWidth(340)
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(20, 20, 20, 20)

        form_layout.addWidget(QLabel("<b>Log New Expense</b>"))
        self.cmb_exp_cat = QComboBox()
        self.cmb_exp_cat.addItems([
            "Mandap & Venue",
            "Catering & Sweets",
            "Decorations & Lights",
            "Photography & Video",
            "Attire & Makeup",
            "Jewelry & Gifts",
            "Music & Dhol",
            "Transportation",
        ])

        self.inp_exp_amt = QLineEdit()
        self.inp_exp_amt.setPlaceholderText("Amount (₹) *")

        self.cmb_exp_ev = QComboBox()

        btn_exp = QPushButton("Add Expense")
        btn_exp.clicked.connect(self.add_expense)

        self.lbl_budget_info = QLabel("")
        self.lbl_budget_info.setWordWrap(True)
        self.lbl_budget_info.setStyleSheet("color: #F3E5AB; font-size: 11px;")

        form_layout.addWidget(self.cmb_exp_cat)
        form_layout.addWidget(self.inp_exp_amt)
        form_layout.addWidget(self.cmb_exp_ev)
        form_layout.addSpacing(10)
        form_layout.addWidget(btn_exp)
        form_layout.addSpacing(12)
        form_layout.addWidget(self.lbl_budget_info)
        form_layout.addStretch()
        form_card.setLayout(form_layout)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 20, 20, 20)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        btn_exp_csv = QPushButton("Export Ledger (.csv)")
        btn_exp_csv.setObjectName("SecondaryBtn")
        btn_exp_csv.clicked.connect(self.export_expenses_csv)
        top_bar.addWidget(btn_exp_csv)
        table_layout.addLayout(top_bar)

        self.table_expenses = QTableWidget()
        self.table_expenses.setColumnCount(4)
        self.table_expenses.setHorizontalHeaderLabels(
            ["ID", "Category", "Amount", "Assigned Function"]
        )
        self.table_expenses.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table_layout.addWidget(self.table_expenses)
        table_card.setLayout(table_layout)

        layout.addWidget(form_card)
        layout.addWidget(table_card)
        self.tab_expenses.setLayout(layout)

        self.load_expenses()
        self.populate_expense_event_dropdown()

    def populate_expense_event_dropdown(self):
        self.cmb_exp_ev.clear()
        self.cmb_exp_ev.addItem("General Budget")
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, event_name FROM events")
        self.exp_ev_map = {f"{r[1]} (ID:{r[0]})": r[0] for r in cursor.fetchall()}
        self.cmb_exp_ev.addItems(list(self.exp_ev_map.keys()))
        conn.close()

    def add_expense(self):
        try:
            amt = float(self.inp_exp_amt.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Enter a valid numerical amount.")
            return

        ev_str = self.cmb_exp_ev.currentText()
        ev_id = self.exp_ev_map.get(ev_str) if ev_str in self.exp_ev_map else None

        budget_limit = self.get_budget_limit()
        if budget_limit > 0:
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM expenses")
            current_total = cursor.fetchone()[0] or 0.0
            conn.close()

            projected_total = current_total + amt
            if projected_total > budget_limit:
                attending = self.get_attending_guest_count()
                over_by = projected_total - budget_limit
                reply = QMessageBox.warning(
                    self,
                    "Budget Limit Exceeded",
                    (
                        f"This expense would exceed the wedding budget.\n\n"
                        f"Guests attending: {attending}\n"
                        f"Budget limit: ₹{budget_limit:,.2f}\n"
                        f"Total after this expense: ₹{projected_total:,.2f}\n"
                        f"Over budget by: ₹{over_by:,.2f}\n\n"
                        f"Add it anyway?"
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (category, amount, event_id) VALUES (?, ?, ?)",
            (self.cmb_exp_cat.currentText(), amt, ev_id),
        )
        conn.commit()
        conn.close()
        self.inp_exp_amt.clear()
        self.load_expenses()
        self.refresh_dashboard()

    def load_expenses(self):
        self.table_expenses.setRowCount(0)
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT expenses.id, expenses.category, expenses.amount, events.event_name 
                          FROM expenses LEFT JOIN events ON expenses.event_id = events.id""")
        for r_idx, row in enumerate(cursor.fetchall()):
            self.table_expenses.insertRow(r_idx)
            self.table_expenses.setItem(r_idx, 0, QTableWidgetItem(str(row[0])))
            self.table_expenses.setItem(r_idx, 1, QTableWidgetItem(str(row[1])))
            self.table_expenses.setItem(r_idx, 2, QTableWidgetItem(f"₹{row[2]:,.2f}"))
            self.table_expenses.setItem(
                r_idx,
                3,
                QTableWidgetItem(str(row[3]) if row[3] else "General"),
            )
        conn.close()
        self.update_budget_info_label()

    def update_budget_info_label(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses")
        spent = cursor.fetchone()[0] or 0.0
        conn.close()

        attending = self.get_attending_guest_count()
        per_guest = self.get_budget_per_guest()
        limit = per_guest * attending
        remaining = limit - spent

        if per_guest <= 0:
            self.lbl_budget_info.setText(
                "Set a per-guest budget in Overview to enable budget limit tracking."
            )
        else:
            self.lbl_budget_info.setText(
                f"Attending: {attending} × ₹{per_guest:,.2f}/guest = ₹{limit:,.2f} budget\n"
                f"Spent: ₹{spent:,.2f}  |  Remaining: ₹{remaining:,.2f}"
            )

    def export_expenses_csv(self):
        conn = self.get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT expenses.id, expenses.category, expenses.amount, events.event_name 
                          FROM expenses LEFT JOIN events ON expenses.event_id = events.id""")
        rows = cursor.fetchall()
        conn.close()
        with open("expenses_export.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Category", "Amount", "Function"])
            writer.writerows(rows)
        QMessageBox.information(
            self, "Exported", "Saved expense ledger to 'expenses_export.csv'."
        )

    # --- ANALYTICS ---
    def setup_reports(self):
        layout = QVBoxLayout()
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 20)

        btn_draw = QPushButton("Update Charts")
        btn_draw.clicked.connect(self.render_charts)
        card_layout.addWidget(btn_draw, alignment=Qt.AlignmentFlag.AlignRight)

        plt.style.use("dark_background")
        self.fig, self.axes = plt.subplots(1, 3, figsize=(12, 4))
        self.fig.patch.set_facecolor("#2D0308")

        self.canvas = FigureCanvas(self.fig)
        card_layout.addWidget(self.canvas)

        card.setLayout(card_layout)
        layout.addWidget(card)
        self.tab_reports.setLayout(layout)
        self.render_charts()

    def render_charts(self):
        for ax in self.axes:
            ax.clear()
            ax.set_facecolor("#120103")

        conn = self.get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        cat_data = cursor.fetchall()

        cursor.execute("""SELECT COALESCE(events.event_name, 'General'), SUM(expenses.amount) 
                          FROM expenses LEFT JOIN events ON expenses.event_id = events.id 
                          GROUP BY events.event_name""")
        evt_data = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM guests WHERE rsvp_status = 'Confirmed'")
        conf_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM guests WHERE attended = 1")
        att_count = cursor.fetchone()[0]
        conn.close()

        palette = [
            "#FFD700",
            "#FF9900",
            "#FF5722",
            "#D4AF37",
            "#E11D48",
            "#C5A059",
        ]

        if cat_data:
            wedges, texts, autotexts = self.axes[0].pie(
                [r[1] for r in cat_data],
                labels=[r[0] for r in cat_data],
                autopct="%1.1f%%",
                colors=palette[: len(cat_data)],
                textprops=dict(color="#FFFDF7"),
            )
            for autotext in autotexts:
                autotext.set_color("#120103")
                autotext.set_weight("bold")
            self.axes[0].set_title(
                "Expense Allocation",
                fontsize=11,
                fontweight="bold",
                color="#FFD700",
            )
        else:
            self.axes[0].text(
                0.5,
                0.5,
                "No Expense Records",
                ha="center",
                va="center",
                color="#F3E5AB",
            )

        if evt_data:
            self.axes[1].bar(
                [r[0] for r in evt_data],
                [r[1] for r in evt_data],
                color="#FF9900",
                width=0.5,
            )
            self.axes[1].set_title(
                "Expense per Function",
                fontsize=11,
                fontweight="bold",
                color="#FFD700",
            )
            self.axes[1].tick_params(axis="x", rotation=25, colors="#FFFDF7")
            self.axes[1].tick_params(axis="y", colors="#FFFDF7")
        else:
            self.axes[1].text(
                0.5,
                0.5,
                "No Function Costs",
                ha="center",
                va="center",
                color="#F3E5AB",
            )

        self.axes[2].bar(
            ["Confirmed", "Attended"],
            [conf_count, att_count],
            color=["#FFD700", "#D4AF37"],
            width=0.4,
        )
        self.axes[2].set_title(
            "Guest Turnout", fontsize=11, fontweight="bold", color="#FFD700"
        )
        self.axes[2].tick_params(axis="both", colors="#FFFDF7")

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = WeddingApp()
    window.show()
    sys.exit(app.exec())