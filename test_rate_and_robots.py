import sys
import os

# Добавляем путь к подпапке AsyncCrawler в список путей поиска Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(current_dir, "AsyncCrawler")
sys.path.append(project_dir)

# Теперь импортируем сам краулер (VS Code может подчеркнуть красным, но работать будет)
from AsyncCrawler import AsyncCrawler
import asyncio

from AsyncCrawler.AsyncCrawler import AsyncCrawler


async def main():
    # Настраиваем вежливого робота: 0.5 запроса в сек (1 запрос в 2 сек)
    crawler = AsyncCrawler(requests_per_second=0.5)
    
    # Скармливаем ему список, включая потенциально запрещенный URL
    urls = ["https://www.google.com/search"] 
    
    print("🤖 Тест вежливости и robots.txt...")
    await crawler.crawl(urls, max_pages=3)
    
    await crawler.close()

if __name__ == "__main__":
    asyncio.run(main())