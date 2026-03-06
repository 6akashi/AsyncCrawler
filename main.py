import asyncio
import argparse
import sys
import yaml
import logging
from tqdm import tqdm
from AsyncCrawler.AdvancedCrawler import AdvancedCrawler
from AsyncCrawler.JSONStorage import JSONStorage
from AsyncCrawler.SQLiteStorage import SQLiteStorage
from AsyncCrawler.CSVStorage import CSVStorage

async def update_progress_bar(crawler, limit):
    """Фоновая задача для обновления прогресс-бара в реальном времени"""
    with tqdm(total=limit, desc="🚀 Crawling", unit="pg", bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]') as pbar:
        last_count = 0
        while crawler.queue_manager.processed_count < limit:
            current_count = crawler.queue_manager.processed_count
            if current_count > last_count:
                pbar.update(current_count - last_count)
                last_count = current_count
            
            # Если очередь пуста и воркеры ждут, проверяем условие выхода
            if crawler.queue_manager.queue.empty() and current_count >= last_count:
                # Небольшая пауза, чтобы убедиться, что новых ссылок нет
                await asyncio.sleep(1)
                if crawler.queue_manager.queue.empty():
                    break
                    
            await asyncio.sleep(0.2)
        
        # Финальное обновление до лимита, если завершили успешно
        if crawler.queue_manager.processed_count > last_count:
            pbar.update(crawler.queue_manager.processed_count - last_count)

async def main():
    parser = argparse.ArgumentParser(description="🚀 Advanced Async Crawler v2.0")
    
    # Аргументы CLI
    parser.add_argument("--url", type=str, help="Стартовый URL")
    parser.add_argument("--sitemap", type=str, help="URL sitemap.xml")
    parser.add_argument("--limit", type=int, help="Макс. количество страниц")
    parser.add_argument("--config", type=str, default="config.yaml", help="Путь к конфигу")
    parser.add_argument("--format", choices=["json", "sqlite", "csv"], help="Формат вывода")

    args = parser.parse_args()

    # 1. Загружаем конфиг
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        config = {}

    # 2. Определяем параметры (CLI > Config > Default)
    limit = args.limit or config.get('max_pages', 10)
    fmt = args.format or config.get('storage', {}).get('format', 'json')
    output_name = config.get('storage', {}).get('filename', 'results')

    # 3. Инициализируем хранилище
    if fmt == "json":
        storage = JSONStorage(f"{output_name}.json")
    elif fmt == "csv":
        storage = CSVStorage(f"{output_name}.csv")
    else:
        storage = SQLiteStorage(f"{output_name}.db")

    # 4. Инициализация краулера
    crawler = AdvancedCrawler(config_path=args.config, storage=storage)
    
    try:
        # Создаем задачу для прогресс-бара
        progress_task = asyncio.create_task(update_progress_bar(crawler, limit))

        if args.sitemap:
            await crawler.crawl_from_sitemap(args.sitemap, max_pages=limit)
        elif args.url:
            await crawler.crawl([args.url], max_pages=limit)
        else:
            progress_task.cancel()
            print("❌ Ошибка: укажите --url или --sitemap")
            return

        # Ждем завершения прогресс-бара
        await progress_task

        # 5. Экспорт отчетов
        crawler.stats_manager.export_to_json("final_stats.json")
        crawler.stats_manager.export_to_html("report.html")
        print(f"\n✅ Завершено успешно!")
        print(f"📊 Отчет: report.html | Данные: {output_name}.{fmt}")

    except Exception as e:
        print(f"\n⚠️ Критическая ошибка в работе: {e}")
    finally:
        await crawler.close()
        # Проверяем наличие метода close у хранилища
        if hasattr(storage, 'close'):
            await storage.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Работа прервана пользователем.")
        sys.exit(0)