import asyncio
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.config import get_settings
from src.backend.domain.user.entity import User, UserRole
from src.backend.infrastructure.db.sqlalchemy.user.repository import SqlAlchemyUserRepository
from src.backend.infrastructure.security.bcrypt.hasher import BcryptHasher

ADMIN_USERNAME = "sanjar"
ADMIN_EMAIL = "sanjaranvarov55563@gmail.com"
ADMIN_PASSWORD = "@Aa2020800077"


async def create_admin(username: str, email: str, password: str) -> None:
    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL)
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:
        hasher = BcryptHasher()
        hashed = hasher.hash(password)
        user = User.create(
            username=username,
            email=email,
            hashed_password=hashed,
            role=UserRole.admin,
        )
        repo = SqlAlchemyUserRepository(session=session)
        await repo.create(user)
        await session.commit()
        print(f"Admin '{username}' ({email}) created.")

    await engine.dispose()


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else ADMIN_USERNAME
    email = sys.argv[2] if len(sys.argv) > 2 else ADMIN_EMAIL
    password = sys.argv[3] if len(sys.argv) > 3 else ADMIN_PASSWORD
    asyncio.run(create_admin(username, email, password))
