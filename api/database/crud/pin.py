from collections.abc import Sequence

from sqlalchemy import ColumnElement, and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.crud.base import CRUDBase
from api.database.models.pin import PinModel
from api.routers.schemas.pin import PinBase, PinCreate, PinUpdate


def equivalent_pin_model(pin: PinBase) -> ColumnElement[bool]:
    return and_(
        PinModel.server_id == pin.server_id,
        PinModel.channel_id == pin.channel_id,
        PinModel.message_id == pin.message_id,
    )


class PinCRUD(CRUDBase[PinModel, PinCreate, PinUpdate]):
    async def get_all(self, db: AsyncSession, *, limit: int, offset: int) -> Sequence[PinModel]:
        items = await db.execute(select(self.model).limit(limit).offset(offset))

        return items.scalars().all()

    async def get_by_section_ids(self, db: AsyncSession, *, pin: PinCreate) -> PinModel | None:
        items = await db.execute(select(self.model).where(equivalent_pin_model(pin)))

        return items.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: PinCreate) -> PinModel:
        return await self.create_(db, obj_in=obj_in)

    async def delete(self, db: AsyncSession, *, pin: PinBase) -> int:
        return await self.delete_(db, func=lambda: equivalent_pin_model(pin))


pin_dao = PinCRUD(PinModel)
