from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db, engine, Base
from redis_config import init_redis
from models import Product

from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

# Управление жизненным циклом приложения (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Действия при старте: создаем таблицы и инициализируем Redis
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_redis()
    yield
    # Действия при выключении (если необходимы)

app = FastAPI(lifespan=lifespan)

# Импортируем декоратор кэша
from fastapi_cache.decorator import cache

@app.get("/products")
@cache(expire=600) # Кэшируем ответ на 600 секунд
async def get_products(db: AsyncSession = Depends(get_db)):
    """
    При первом запросе данные возьмутся из PostgreSQL и запишутся в Redis.
    Следующие 60 секунд данные будут мгновенно отдаваться из Redis без обращения к БД.
    """
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products

@app.post("/products")
async def create_product(name: str, price: float, db: AsyncSession = Depends(get_db)):
    # При добавлении нового продукта кэш /products сбросится автоматически по истечении expire
    # В реальных проектах здесь также вызывают принудительный сброс кэша (FastAPICache.clear)
    new_product = Product(name=name, price=price)
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    await FastAPICache.clear(namespace="fastapi-cache")
    return new_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Удаляет товар из PostgreSQL по ID и мгновенно сбрасывает кэш в Redis.
    """
    # 1. Ищем товар в базе данных
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    # Если товар не найден, возвращаем ошибку 404
    if product is None:
        raise HTTPException(status_code=404, detail="Товар не найден")

    # 2. Удаляем товар из PostgreSQL
    await db.delete(product)
    await db.commit()

    # 3. Мгновенно сбрасываем кэш в Redis
    # Передаем тот же namespace, который указан в префиксе ("fastapi-cache")
    await FastAPICache.clear(namespace="fastapi-cache")

    # Возвращаем пустой ответ со статусом 204 No Content
    return None
