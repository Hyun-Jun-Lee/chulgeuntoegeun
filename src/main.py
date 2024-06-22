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
    QTimeEdit,
)
from datetime import date, datetime
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

        self.time_label_start = QLabel("출근 시간: ", self)
        self.time_label_end = QLabel("퇴근 시간: ", self)

        time_label_layout = QVBoxLayout()  # 레이블 수직 배치
        time_label_layout.addWidget(self.time_label_start)
        time_label_layout.addWidget(self.time_label_end)

        # Calendar 위젯 추가
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked[QDate].connect(self.show_selected_date_work_time)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.date_label)
        top_layout.addWidget(self.reset_button)

        # 시간 수정 위젯 추가
        self.start_time_edit = QTimeEdit(self)
        self.end_time_edit = QTimeEdit(self)
        self.save_button = QPushButton("저장", self)
        self.save_button.clicked.connect(self.save_work_time)
        self.save_button.setEnabled(False)  # 초기에는 저장 버튼 비활성화

        time_edit_layout = QHBoxLayout()
        time_edit_layout.addWidget(QLabel("출근 시간:", self))
        time_edit_layout.addWidget(self.start_time_edit)
        time_edit_layout.addWidget(QLabel("퇴근 시간:", self))
        time_edit_layout.addWidget(self.end_time_edit)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.end_button)
        layout.addLayout(time_edit_layout)
        layout.addWidget(self.save_button)
        layout.addLayout(time_label_layout)
        layout.addWidget(self.calendar)

        self.setLayout(layout)

    def start_work(self):
        with get_db() as db:
            workday = WorkDay(
                date=date.today(), start_time=QTime.currentTime().toPyTime()
            )
            db.add(workday)
            db.commit()
            db.refresh(workday)
            start_time = workday.start_time.strftime("%H:%M")
            self.workday_id = workday.id

        self.start_button.setEnabled(False)
        self.end_button.setEnabled(True)
        self.time_label_start.setText(f"출근 시간: { start_time if start_time else ''}")

    def end_work(self):
        with get_db() as db:
            workday = db.query(WorkDay).get(self.workday_id)
            workday.end_time = QTime.currentTime().toPyTime()
            end_time = workday.end_time.strftime("%H:%M")
            db.commit()
            db.refresh(workday)

        self.end_button.setEnabled(False)
        self.time_label_end.setText(f"퇴근 시간: {end_time if end_time else ''}")

    def reset_work(self):
        self.start_button.setEnabled(True)
        self.end_button.setEnabled(False)
        self.workday_id = None
        self.time_label_start.setText("출근 시간: ")
        self.time_label_end.setText("퇴근 시간: ")

        selected_date_str = self.calendar.selectedDate().toPyDate().strftime("%Y-%m-%d")
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        with get_db() as db:
            workday = (
                db.query(WorkDay).filter(WorkDay.date.like(f"{selected_date}%")).first()
            )
            db.delete(workday)
            db.commit()

    def show_selected_date_work_time(self, date):
        """
        선택한 날짜의 출 퇴근 시간
        """
        with get_db() as db:
            date_str = date.toPyDate().strftime("%Y-%m-%d")
            workday = (
                db.query(WorkDay).filter(WorkDay.date.like(f"{date_str}%")).first()
            )

            if workday:
                self.start_time_edit.setEnabled(True)
                self.end_time_edit.setEnabled(True)
                self.start_time_edit.setTime(
                    QTime(
                        workday.start_time.hour,
                        workday.start_time.minute,
                    )
                )  # QTime 생성자에 시, 분, 초 전달
                self.end_time_edit.setTime(
                    QTime(
                        workday.end_time.hour,
                        workday.end_time.minute,
                    )
                    if workday.end_time
                    else QTime()
                )
                self.save_button.setEnabled(True)
                start_time = workday.start_time
                end_time = workday.end_time
                self.time_label_start.setText(
                    f"출근 시간: {start_time.strftime('%H:%M') if start_time else ''}"
                )
                self.time_label_end.setText(
                    f"퇴근 시간: {end_time.strftime('%H:%M') if end_time else ''}"
                )
            else:
                self.start_time_edit.setEnabled(True)
                self.end_time_edit.setEnabled(True)
                self.save_button.setEnabled(True)
                self.time_label_start.setText(f"출근 시간: ")
                self.time_label_end.setText(f"퇴근 시간: ")

                # self.new_workday = WorkDay(date=date.today())

    def save_work_time(self):
        """
        시간 수정 반영
        """
        selected_date_str = self.calendar.selectedDate().toPyDate().strftime("%Y-%m-%d")
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d")
        with get_db() as db:
            workday = (
                db.query(WorkDay).filter(WorkDay.date.like(f"{selected_date}%")).first()
            )

            if workday is None:
                workday = WorkDay(
                    date=selected_date,
                    start_time=self.start_time_edit.time().toPyTime(),
                    end_time=self.end_time_edit.time().toPyTime(),
                )
                db.add(workday)
            else:

                workday.start_time = self.start_time_edit.time().toPyTime()
                workday.end_time = self.end_time_edit.time().toPyTime()

            db.commit()
            start_time = workday.start_time
            end_time = workday.end_time

            self.time_label_start.setText(
                f"출근 시간: {start_time.strftime('%H:%M') if start_time else ''}"
            )
            self.time_label_end.setText(
                f"퇴근 시간: {end_time.strftime('%H:%M') if end_time else ''}"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = OnDuty()
    ex.show()
    sys.exit(app.exec_())
