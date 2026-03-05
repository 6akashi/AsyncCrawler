import asyncio
import os
from AsyncCrawler.AsyncCrawler import AsyncCrawler
from AsyncCrawler.CSVStorage import CSVStorage
from AsyncCrawler.JSONStorage import JSONStorage
from AsyncCrawler.SQLiteStorage import SQLiteStorage


async def test_json():
    print("\n--- Тест JSONStorage ---")
    filename = "test_results.json" # Исправил расширение
    if os.path.exists(filename): os.remove(filename)
    
    storage = JSONStorage(filename)
    crawler = AsyncCrawler(storage=storage)
    
    try:
        await crawler.crawl(["https://books.toscrape.com/"], max_pages=2)
    finally:
        await crawler.close() # Закрываем сессию!
    print(f"✅ Проверка: файл {filename} создан.")

async def test_sqlite():
    print("\n--- Тест SQLiteStorage ---")
    db_name = "test_crawler.db" # Исправил расширение
    if os.path.exists(db_name): os.remove(db_name)
    
    storage = SQLiteStorage(db_name)
    crawler = AsyncCrawler(storage=storage)
    
    try:
        await crawler.crawl(["https://quotes.toscrape.com/"], max_pages=2)
    finally:
        await storage.close()
        await crawler.close() # Закрываем сессию!
    print(f"✅ Проверка: база {db_name} создана.")

async def test_csv():
    print("\n--- Тест CSVStorage ---")
    filename = "test_results.csv"
    if os.path.exists(filename): os.remove(filename)
    
    storage = CSVStorage(filename)
    crawler = AsyncCrawler(storage=storage)
    
    try:
        await crawler.crawl(["https://books.toscrape.com/"], max_pages=3)
    finally:
        await crawler.close()
    print(f"✅ Проверка: файл {filename} создан и заполнен.")

if __name__ == "__main__":
    async def run_all():
        await test_json()
        await test_sqlite()
        await test_csv()
    
    asyncio.run(run_all())