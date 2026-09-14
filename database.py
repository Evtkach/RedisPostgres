from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Замените на ваши данные пользователя, пароля и имени БД
DATABASE_URL = "postgresql+asyncpg://myuser:password@localhost:5432/mydatabase"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Зависимость для получения сессии БД в эндпоинтах
async def get_db():
    async with async_session() as session:
        yield session
