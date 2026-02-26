import asyncio
import logging
from AsyncCrawler.AsyncCrawler import AsyncCrawler

# Настроим логирование, чтобы видеть попытки повторов в консоли
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

async def main():
    # Создаем краулер. Ставим макс. 5 страниц, чтобы он не ушел в бесконечный цикл
    crawler = AsyncCrawler(max_concurrent=2, requests_per_second=2.0)
    
    test_urls = [
        "https://httpbin.org/status/404", # Тест PermanentError
        "https://httpbin.org/status/503", # Тест TransientError (повторы)
        "https://httpbin.org/delay/20",   # Тест Timeout (повторы)
    ]
    
    print("🚀 Начинаем стресс-тест системы повторов...")
    try:
        await crawler.crawl(test_urls, max_pages=3)
    finally:
        # Важно закрыть сессию aiohttp
        await crawler.close()

if __name__ == "__main__":
    # ВОТ ЭТОЙ СТРОЧКИ НЕ ХВАТАЛО:
    asyncio.run(main())