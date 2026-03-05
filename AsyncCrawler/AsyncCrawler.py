import asyncio
from datetime import datetime
import aiohttp
import time
import random
import logging
from typing import List, Optional
from urllib.parse import urlparse

from AsyncCrawler.DataStorage import DataStorage
from AsyncCrawler.Errors import *
from AsyncCrawler.RetryStrategy import RetryStrategy
from AsyncCrawler.CrawlerQueue import CrawlerQueue
from AsyncCrawler.HTMLParser import HTMLParser
from AsyncCrawler.RateLimiter import RateLimiter
from AsyncCrawler.RobotsManager import RobotsManager
from AsyncCrawler.JSONStorage import JSONStorage

# Твои модули


logger = logging.getLogger(__name__)

class AsyncCrawler:
    def __init__(self, 
                 max_concurrent: int = 5, 
                 requests_per_second: float = 1.0,
                 user_agent: str = "MyFriendlyBot/1.0",
                 max_depth: int = 2,
                 storage: DataStorage = None):
        self.storage: DataStorage = storage
        self.max_concurrent = max_concurrent
        self.max_depth = max_depth
        self.user_agent = user_agent
        
        # Инициализируем твои классы
        self.queue_manager = CrawlerQueue()
        self.rate_limiter = RateLimiter(requests_per_second=requests_per_second)
        self.robots_manager = RobotsManager(user_agent=user_agent)
        self.parser = HTMLParser()
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.results = []
        
        # Для мониторинга скорости
        self.start_time = None
        self.blocked_by_robots = 0

        self.retry_strategy = RetryStrategy(max_retries=3)
        self.stats = {
            "total_errors": 0,
            "retries_success": 0,
            "permanent_failures": [],
            "timeout_errors": 0  # <--- Убедись, что эта строка есть!
        }

    async def _init_session(self):
        if self.session is None or self.session.closed:
            headers = {"User-Agent": self.user_agent}
            timeout = aiohttp.ClientTimeout(total=15, connect=5)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    async def _fetch_page_logic(self, url:str) -> str:
        try:
            async with self.session.get(url) as response:
                status = response.status

                if status == 200:
                    return await response.text()
                if status in (429, 503, 504):
                    raise TransientError(f"Временная ошибка {status}")
                elif status in (404, 403, 401):
                    raise PermanentError(f"Постоянная ошибка {status}")
                elif status >= 500:
                    raise TransientError(f"Ошибка сервера {status}")
                else:
                    raise PermanentError(f"Неизвестный статус{status}")
        except asyncio.TimeoutError:
            self.stats["timeout_errors"] += 1
            raise TransientError("Таймаут запроса")
        except aiohttp.ClientError as e:
            raise NetworkError(f"Сетевой сбой: {e}")


    async def crawl(self, start_urls: List[str], max_pages: int = 10):
        await self._init_session()
        self.start_time = time.time()
        
        # Добавляем стартовые URL в твою очередь
        for url in start_urls:
            await self.queue_manager.add(url, depth=0)

        semaphore = asyncio.Semaphore(self.max_concurrent)
        if hasattr(self.storage, 'init_db'):
            await self.storage.init_db()
        async def worker():
            while self.queue_manager.processed_count < max_pages:
                if self.queue_manager.queue.empty():
                    await asyncio.sleep(0.1)
                    continue

                # Достаем данные из твоей CrawlerQueue
                url, depth = await self.queue_manager.queue.get()
                domain = urlparse(url).netloc

                # 1. Проверка Robots.txt
                if not await self.robots_manager.can_fetch(url, self.session):
                    logger.warning(f"Robots.txt запретил: {url}")
                    self.blocked_by_robots += 1
                    self.queue_manager.queue.task_done()
                    continue

                # 2. Ограничение скорости (Rate Limiting)
                await self.rate_limiter.acquire(domain)

                # 3. Выполнение запроса
                async with semaphore:
                    try:
                        # Вызываем логику через стратегию повторов
                        html = await self.retry_strategy.execute(self._fetch_page_logic, url)
                        
                        # Если дошли сюда — загрузка успешна (возможно, после повторов)
                        
                        if html:
                            await self._process_page(html, url, depth)
                            self.queue_manager.processed_count += 1
                        
                        print(f"[{self.queue_manager.processed_count}/{max_pages}] Успех: {url}")

                        # if depth < self.max_depth:
                        #     for link in data.get('links', []):
                        #         if urlparse(link).netloc == domain:
                        #             await self.queue_manager.add(link, depth + 1)
                                  
                    except PermanentError as e:
                        logger.error(f"Пропуск (Permanent): {url} - {e}")
                        self.stats["permanent_failures"].append(url)
                    except Exception as e:
                        logger.error(f"Провал после всех попыток: {url} - {e}")
                        self.stats["total_errors"] += 1
                
                self.queue_manager.queue.task_done()

        

        # Запускаем группу воркеров
        workers = [asyncio.create_task(worker()) for _ in range(self.max_concurrent)]
        
        # Ждем выполнения или достижения лимита страниц
        while self.queue_manager.processed_count < max_pages:
            await asyncio.sleep(0.5)
            if self.queue_manager.queue.empty():
                await asyncio.sleep(1)
                if self.queue_manager.queue.empty():
                    break
        await asyncio.sleep(1)                
        for w in workers: w.cancel()
        
        self._print_stats()
        return self.results

    async def _process_page(self, html, url, depth = 1):
            # 1. Парсинг
        data = await self.parser.parse_html(html, url)
        self.results.append(data)
        # приводим данные к единому виду перед сохранением
        payload = {
            "url": url,
            "title": data.get("title", "No Title"),
            "links": data.get("links", []),
            "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # Добавь это на верхний уровень
            "status_code": 200,
            "metadata": { "depth": depth } 
        }
        if self.storage:
            # Важно: вызываем await, так как запись в БД/Файл — асинхронна
            await self.storage.save(payload)
            logger.info(f"Данные сохранены: {url}")
        # 4. Пополнение очереди новыми ссылками
        if depth < self.max_depth:
            domain = urlparse(url).netloc
            for link in data.get('links', []):
                if urlparse(link).netloc == domain:
                    await self.queue_manager.add(link, depth + 1)

    def _print_stats(self):
        total_time = time.time() - self.start_time
        rps = self.queue_manager.processed_count / total_time if total_time > 0 else 0
        print(f"\n--- Статистика обхода ---")
        print(f"Скорость: {rps:.2f} req/sec")
        print(f"Средняя задержка: {1/rps:.2f} сек/запрос" if rps > 0 else "")
        print(f"Заблокировано robots.txt: {self.blocked_by_robots}")
        print(f"Успешно обработано: {len(self.results)} стр.")
        print(f"Всего финальных ошибок: {self.stats['total_errors']}")
        print(f"Постоянных неудач (404/403): {len(self.stats['permanent_failures'])}")
        print(f"Таймаутов зафиксировано: {self.stats['timeout_errors']}")

    async def close(self):
        if self.session:
            await self.session.close()