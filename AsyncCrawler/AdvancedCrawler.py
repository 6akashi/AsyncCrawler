import yaml
import logging
import asyncio
import time
from typing import List, Optional
from .AsyncCrawler import AsyncCrawler
from .SitemapParser import SitemapParser
from .CrawlerStats import CrawlerStats

class AdvancedCrawler(AsyncCrawler):
    def __init__(self, config_path: str = None, **kwargs):
        # 1. Загрузка конфигурации
        self.config = self._load_config(config_path) if config_path else {}
        
        # Приоритет: kwargs > config > default
        max_concurrent = kwargs.get('max_concurrent') or self.config.get('max_concurrent', 5)
        rps = kwargs.get('requests_per_second') or self.config.get('rate_limit', 1.0)
        
        # Инициализируем базовый класс
        super().__init__(
            max_concurrent=max_concurrent, 
            requests_per_second=rps,
            **kwargs
        )
        
        # 2. Новые компоненты Дня 7
        self.sitemap_parser = SitemapParser()
        self.stats_manager = CrawlerStats()
        self._setup_logging()

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфига {path}: {e}. Используем дефолты.")
            return {}

    def _setup_logging(self):
        log_config = self.config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'crawler.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    async def crawl_from_sitemap(self, sitemap_url: str, max_pages: int = 10):
        """Новый метод: запуск через sitemap"""
        await self._init_session()
        print(f"🔍 Анализ Sitemap: {sitemap_url}")
        urls = await self.sitemap_parser.fetch_sitemap_urls(self.session, sitemap_url)
        
        if not urls:
            print("Ссылки в Sitemap не найдены.")
            return
            
        print(f"Найдено {len(urls)} URL в Sitemap. Начинаем обход...")
        return await self.crawl(urls[:max_pages], max_pages=max_pages)

    # Переопределяем метод для сбора расширенной статистики
    async def _process_page(self, html, url, depth):
        # Вызываем логику базового класса (парсинг + сохранение)
        await super()._process_page(html, url, depth)
        
        # Обновляем статистику (здесь мы фиксируем успех)
        self.stats_manager.update(url, 200)