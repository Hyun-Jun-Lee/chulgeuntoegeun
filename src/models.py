from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, DateTime, Time, func
from datetime import datetime, time


Base = declarative_base()


class WorkDay(Base):

    __tablename__ = "workday"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=True)
    end_time: Mapped[time] = mapped_column(Time, nullable=True)
    memo: Mapped[str] = mapped_column(String(255), nullable=True)
