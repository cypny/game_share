from typing import TypeVar, Generic, Type, Any

from sqlalchemy import select, update, delete, inspect, func
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.infrastructure.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий для CRUD-операций.
    """
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_primary_key_name(self) -> str:
        """Получить имя первичного ключа модели."""
        return inspect(self.model).primary_key[0].name

    async def get_by_id(self, model_id: Any, options = None) -> ModelType | None:
        """Получить запись по ID."""
        if options is None:
            options = []
        pk_name = self._get_primary_key_name()
        return await self.session.scalar(
            select(self.model).options(*options).where(getattr(self.model, pk_name) == model_id)
        )

    async def get_all(self, options = None, skip=0, take=None) -> list[ModelType]:
        """Получить все записи."""
        if not options:
            options = []

        query = select(self.model).options(*options)
        query = query.offset(skip)
        if take is not None:
            query = query.limit(take)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **data) -> ModelType:
        """Создать новую запись."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, model_id: Any, **data) -> ModelType | None:
        """Обновить запись по ID."""
        pk_name = self._get_primary_key_name()
        stmt = (
            update(self.model)
            .where(getattr(self.model, pk_name) == model_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, model_id: Any) -> bool:
        """Удалить запись по ID."""
        pk_name = self._get_primary_key_name()
        stmt = delete(self.model).where(getattr(self.model, pk_name) == model_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_field(self, field_name: str, value: Any, options = None) -> ModelType | None:
        """метод для поиска по любому полю."""
        options = options or []
        field = getattr(self.model, field_name)
        stmt = (select(self.model)
                .options(*options)
                .where(field == value))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_field(self, field_name: str, value: Any) -> list[ModelType]:
        """метод для поиска всех записей по полю."""
        field = getattr(self.model, field_name)
        stmt = select(self.model).where(field == value)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_all(self) -> int:
        """Считает все строки в таблице."""
        stmt = select(func.count()).select_from(self.model)
        return await self.session.scalar(stmt)

