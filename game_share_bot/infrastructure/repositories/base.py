from typing import TypeVar, Generic, Type, Any, List, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from game_share_bot.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий для CRUD-операций.
    """
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, model_id: Any) -> Optional[ModelType]:
        """Получить запись по ID."""
        return await self.session.get(self.model, model_id)

    async def get_all(self) -> List[ModelType]:
        """Получить все записи."""
        result = await self.session.execute(select(self.model))

        # note(boboboba): можно скастить через cast чтобы не ругался пайчарм, но пох
        return result.scalars().all() # type: ignore

    async def create(self, **data) -> ModelType:
        """Создать новую запись."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, model_id: Any, **data) -> Optional[ModelType]:
        """Обновить запись по ID."""
        stmt = (
            update(self.model)
            .where(self.model.id == model_id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, model_id: Any) -> bool:
        """Удалить запись по ID."""
        stmt = delete(self.model).where(self.model.id == model_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0