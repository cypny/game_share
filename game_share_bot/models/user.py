from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


# TODO
# note(boboboba): Степа писал модели, могут пригодиться, см коммит 6e7ade90361dba68fba33fd4ffc150343875e1c1
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50))