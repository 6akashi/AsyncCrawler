import asyncio
import logging

from AsyncCrawler.AsyncCrawler import AsyncCrawler


async def main():
    crawler = AsyncCrawler(max_concurrent=3, max_depth=1)
    # Попробуем на простом сайте для тестов
    results = await crawler.crawl(["https://example.com"], max_pages=5)
    
    print(f"Итого собрано страниц: {len(results)}")
    await crawler.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())