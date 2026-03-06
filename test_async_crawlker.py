import asyncio
import time
from AsyncCrawler.AsyncCrawler import AsyncCrawler
from typing import Dict, List, Optional


async def demo_feth_single():
    """ОДНА СТРАНИЦА"""
    print("===Демонстарция demo_fetch_single")
    crawler = AsyncCrawler(max_concurrent=10)

    urls = [
        "https://example.com",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
    ]

    for url in urls:

        await crawler.crawl(url)

    # if succes:
    #     print(f"УСПЕХ ДЛЯ {url}")
    #     print(f"ЗАГРУЖЕННО СИМВОЛОВ: {len(result)}")
    #     print(f"ПЕРВЫЕ 100 СИМВОЛОВ: {result[100:]}...")
    # else:
    #     print(f"ОШИБКА ДЛЯ {url}")
    #     print(f"ТЕКСТ ОШИБКИ: {result}")

    await crawler.close()


async def demo_feth_multiple():
    """АСИНХРОННОСТЬ"""
    print("===Демонстарция асинхронности")
    crawler = AsyncCrawler(max_concurent=5)

    urls = [
        "https://example.com",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
    ]

    print(f"Загружаем {len(urls)} параллельно")
    start_time = time.time()

    results = await crawler.fetch_urls(urls)

    elapsed_time = time.time() - start_time

    print(f"Время выполнения {elapsed_time:.2f} сек")

    succes_count = sum(1 for succes, _ in results.values() if succes)
    print("===СТАТИСТИКА===")
    print(f"Всего страниц: {len(urls)}")
    print(f"Успешных: {succes_count}")
    print(f"Ошибок: {len(urls) - succes_count}")

    print("===Детально по каждому URL===")
    for url, (succes, content) in results.items():
        if succes:
            print(f"УСПЕШНО: {url}, СИМВОЛОВ: {len(content)}")
        else:
            print(f"ОШИБКА ДЛЯ {url}, ОШИБКА: {content}")

    await crawler.close()


async def compare_sequential_vs_parallel():
    print("===СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ===")

    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/3",
        "https://httpbin.org/delay/1",
    ]

    results_seq = {}
    results_async = {}

    print("\n1. Последовательная загрузка:")
    start_time = time.time()

    crawler_seq = AsyncCrawler(max_concurent=5)
    for url in urls:
        succes, content = await crawler_seq.crawl(["https://example.com"], max_pages=1)
        results_seq[url] = content

    await crawler_seq.close()

    seq_time = time.time() - start_time
    print(f"    Время: {seq_time:.2f} сек")

    print("\n2. Параллельная загрузка")
    start_time = time.time()

    crawler_async = AsyncCrawler(max_concurent=5)
    results_async = await crawler_async.fetch_urls(urls)

    await crawler_async.close()

    par_time = time.time() - start_time
    print(f"    Время: {par_time:.2f}")

    print("===РЕЗУЛЬТАТЫ===")
    print(f"Последовательная: {seq_time:.2f} сек")
    print(f"Параллельная: {par_time:.2f} сек")
    print(f"Ускорение: {seq_time/par_time}x")
    

async def main():
    print("ТЕСТЫ")
    print("=" * 50)

    await demo_feth_single()
    await demo_feth_multiple()
    await compare_sequential_vs_parallel()

    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
