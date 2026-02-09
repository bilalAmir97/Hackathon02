"""Create a test user in the database."""
import asyncio
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import engine
from src.domain.models import User


async def create_test_user():
    """Create a test user with a known UUID."""
    test_user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    test_email = "test@example.com"

    async with AsyncSession(engine) as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.id == test_user_id)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"✓ User already exists: {existing_user.email} ({existing_user.id})")
            return existing_user

        # Create new user
        user = User(
            id=test_user_id,
            email=test_email
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        print(f"✓ Created test user: {user.email} ({user.id})")
        return user


if __name__ == "__main__":
    asyncio.run(create_test_user())
