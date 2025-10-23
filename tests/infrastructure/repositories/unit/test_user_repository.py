import pytest
from game_share_bot.infrastructure.repositories.user import UserRepository


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_try_create_success(self, test_session):
        repo = UserRepository(test_session)
        user = await repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="test_user"
        )
        assert user is not None
        assert user.tg_id == 123
        assert user.phone == "+1234567890"
        assert user.name == "test_user"

        saved_user = await repo.get_by_tg_id(123)
        assert saved_user.id == user.id

    @pytest.mark.asyncio
    async def test_try_create_duplicate_phone(self, test_session):
        repo = UserRepository(test_session)
        user1 = await repo.try_create(
            tg_id=111,
            phone="+1234567890",
            name="user1"
        )
        assert user1 is not None

        user2 = await repo.try_create(
            tg_id=222,
            phone="+1234567890",
            name="user2"
        )
        assert user2 is None

    @pytest.mark.asyncio
    async def test_try_create_duplicate_tg_id(self, test_session):
        repo = UserRepository(test_session)
        user1 = await repo.try_create(
            tg_id=123,
            phone="+1111111111",
            name="user1"
        )
        assert user1 is not None

        user2 = await repo.try_create(
            tg_id=123,
            phone="+2222222222",
            name="user2"
        )
        assert user2 is None

    @pytest.mark.asyncio
    async def test_get_by_phone_exists(self, test_session):
        repo = UserRepository(test_session)
        test_user = await repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="test_user"
        )

        found_user = await repo.get_by_phone("+1234567890")
        assert found_user is not None
        assert found_user.tg_id == 123
        assert found_user.phone == "+1234567890"

    @pytest.mark.asyncio
    async def test_get_by_phone_not_exists(self, test_session):
        repo = UserRepository(test_session)
        found_user = await repo.get_by_phone("+9999999999")
        assert found_user is None

    @pytest.mark.asyncio
    async def test_make_admin_success(self, test_session):
        repo = UserRepository(test_session)
        user = await repo.try_create(
            tg_id=123,
            phone="+1234567890",
            name="test_user"
        )

        result = await repo.make_admin(123)
        assert result is True

        updated_user = await repo.get_by_tg_id(123)
        assert updated_user.role == "admin"

    @pytest.mark.asyncio
    async def test_make_admin_user_not_found(self, test_session):
        repo = UserRepository(test_session)
        result = await repo.make_admin(999)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_users(self, test_session):
        repo = UserRepository(test_session)
        await repo.try_create(tg_id=1, phone="+1111111111", name="user1")
        await repo.try_create(tg_id=2, phone="+2222222222", name="user2")
        await repo.try_create(tg_id=3, phone="+3333333333", name="user3")

        users = await repo.get_all()
        assert len(users) == 3

    @pytest.mark.asyncio
    async def test_get_all_admins(self, test_session):
        repo = UserRepository(test_session)
        await repo.try_create(tg_id=1, phone="+1111111111", name="user1")
        await repo.try_create(tg_id=2, phone="+2222222222", name="admin_user")

        await repo.make_admin(2)

        admins = await repo.get_all_admins()
        assert len(admins) == 1
        assert admins[0].tg_id == 2
        assert admins[0].role == "admin"