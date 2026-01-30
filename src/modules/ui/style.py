from PyQt6.QtGui import QFont


def apply_style(app) -> None:
    app.setFont(QFont("Fira Sans", 10))
    app.setStyleSheet(
        """
        QWidget { color: #1E293B; }
        QMainWindow { background: #F8FAFC; }
        QLabel#sectionTitle { font-size: 18px; font-weight: 600; }
        QLabel#pageTitle { font-size: 22px; font-weight: 700; }
        QLabel#kpiTitle { font-size: 13px; font-weight: 600; color: #64748B; }
        QLabel#kpiValue { font-size: 20px; font-weight: 700; }
        QLabel#kpiUnit { font-size: 12px; }
        QLabel#kpiFoot { font-size: 11px; }
        QFrame[class="card"] { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; }
        *[class="muted"] { color: #475569; }
        QTableWidget { background: #FFFFFF; border: 1px solid #E2E8F0; gridline-color: #E2E8F0; alternate-background-color: #F8FAFC; }
        QHeaderView::section { background: #F1F5F9; border: 1px solid #E2E8F0; padding: 6px; }
        QTableWidget::item:hover { background: #EFF6FF; }
        QTableWidget::item:selected { background: #BFDBFE; color: #0F172A; }

        QDateTimeEdit {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 6px 10px;
            min-height: 30px;
        }
        QDateTimeEdit:focus { border: 1px solid #3B82F6; }
        QDateTimeEdit::drop-down { width: 0px; border: 0px; }
        QDateTimeEdit::down-arrow { image: none; width: 0px; height: 0px; }
        QDateTimeEdit::up-button, QDateTimeEdit::down-button { width: 0px; height: 0px; border: 0px; }
        QDateTimeEdit::up-arrow, QDateTimeEdit::down-arrow { image: none; width: 0px; height: 0px; }

        QCalendarWidget QWidget { background: #FFFFFF; }
        QCalendarWidget QToolButton { color: #1E293B; background: transparent; border: none; margin: 4px; }
        QCalendarWidget QToolButton:hover { color: #1D4ED8; }
        QCalendarWidget QAbstractItemView { selection-background-color: #3B82F6; selection-color: #FFFFFF; outline: 0; }
        QCalendarWidget QAbstractItemView::item:hover { background: #E0EAFF; }
        """
    )
