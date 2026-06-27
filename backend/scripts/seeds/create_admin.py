import asyncio
import sys
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# backend/ directory — parent of src/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.backend.config import get_settings
from src.backend.domain.user.entity import User, UserRole
from src.backend.infrastructure.db.sqlalchemy.user.repository import SqlAlchemyUserRepository
from src.backend.infrastructure.security.bcrypt.hasher import BcryptHasher


async def create_admin(username: str, email: str, password: str) -> None:
    print(f"Creating admin user '{username}', ({password}) ({email})...")
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
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    print("Creating admin user...")
    asyncio.run(create_admin(sys.argv[1], sys.argv[2], sys.argv[3]))
