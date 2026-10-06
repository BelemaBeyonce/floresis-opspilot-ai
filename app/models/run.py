from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    citations: Mapped[str] = mapped_column(Text, nullable=False)