import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from PyQt5.QtCore import Qt, QTime, QDate
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QCalendarWidget,
    QHBoxLayout,
)
from datetime import date
from session import get_db
from models import WorkDay


class OnDuty(QWidget):
    def __init__(
        self, parent: QWidget | None = ..., flags: Qt.WindowFlags | Qt.WindowType = ...
    ) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("출퇴근 기록")
        self.setMinimumSize(400, 300)

        # 오늘 날짜 표시
        self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"), self)
        self.date_label.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("출근", self)
        self.start_button.clicked.connect(self.start_work)

        self.end_button = QPushButton("퇴근", self)
        self.end_button.clicked.connect(self.end_work)
        self.end_button.setEnabled(False)

        self.reset_button = QPushButton("Reset", self)
        self.reset_button.clicked.connect(self.reset_work)

        self.time_label = QLabel("출근 시간: ", self)
        self.time_label.setAlignment(Qt.AlignCenter)

        # Calendar 위젯 추가
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked[QDate].connect(self.show_selected_date_work_time)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.date_label)
        top_layout.addWidget(self.reset_button)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.end_button)
        layout.addWidget(self.time_label)
        layout.addWidget(self.calendar)

        self.setLayout(layout)

    def start_work(self):
        with get_db() as db:
            workday = WorkDay(
                date=date.today(), start_time=QTime.currentTime().toPyTime()
            )
            db.add(workday)
            self.start_time = workday.start_time
            db.commit()
            db.refresh(workday)
            self.workday_id = workday.id

        self.start_button.setEnabled(False)
        self.end_button.setEnabled(True)
        self.time_label.setText(f"출근 시간: {self.start_time.strftime('%H:%M:%S')}")

    def end_work(self):
        with get_db() as db:
            workday = db.query(WorkDay).get(self.workday_id)
            workday.end_time = QTime.currentTime().toPyTime()
            self.end_time = workday.end_time
            db.commit()
            db.refresh(workday)

        self.end_button.setEnabled(False)
        self.time_label.setText(
            f"출근 시간: {self.start_time.strftime('%H:%M:%S')}, "
            f"퇴근 시간: {self.end_time.strftime('%H:%M:%S')}"
        )

    def reset_work(self):
        self.start_button.setEnabled(True)
        self.end_button.setEnabled(False)
        self.workday_id = None
        self.time_label.setText("출근 시간: ")

    def show_selected_date_work_time(self, date):
        with get_db() as db:
            date_str = date.toPyDate().strftime("%Y-%m-%d")
            workday = (
                db.query(WorkDay).filter(WorkDay.date.like(f"{date_str}%")).first()
            )
            if workday:
                self.time_label.setText(
                    f"출근 시간: {workday.start_time.strftime('%H:%M:%S')}, "
                    f"퇴근 시간: {workday.end_time.strftime('%H:%M:%S') if workday.end_time else ''}"
                )
            else:
                self.time_label.setText(
                    f"{date.toPyDate()} 날짜의 출퇴근 기록이 없습니다."
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = OnDuty()
    ex.show()
    sys.exit(app.exec_())
