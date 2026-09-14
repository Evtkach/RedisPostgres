import asyncio
import random
from faker import Faker
from database import async_session, engine, Base
from models import Product

fake = Faker(['ru_RU']) # Генерирует названия на русском языке

async def seed_data():
    async with async_session() as session:
        print("Начинаем заполнение базы данных...")

        # Создаем 100 случайных товаров
        for _ in range(100):
            # Генерируем случайное название из 2 слов и случайную цену
            random_product = Product(
                name=fake.catch_phrase(),
                price=round(random.uniform(500, 150000), 2)
            )
            session.add(random_product)

        await session.commit()
        print("Успешно добавлено 100 тестовых товаров!")

if __name__ == "__main__":
    asyncio.run(seed_data())
