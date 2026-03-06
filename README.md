
# 🚀 Advanced Async Crawler

Мощный асинхронный краулер на Python, созданный за 7 дней интенсивной разработки. Умеет обходить сайты, соблюдая правила вежливости, и сохранять данные в различных форматах.

## ✨ Основные возможности
* **Асинхронность:** Построен на `asyncio` и `aiohttp` для максимальной производительности.
* **Умный обход:** Поддержка `sitemap.xml` и рекурсивный поиск ссылок на страницах.
* **Вежливость:** Автоматическая проверка `robots.txt` и ограничение скорости (Rate Limiting).
* **Гибкое хранение:** Сохранение результатов в **SQLite**, **JSON** или **CSV** на выбор.
* **Отчетность:** Генерация детального HTML-отчета со статистикой работы (RPS, ошибки, домены).

## 🛠 Установка

1. Клонируйте репозиторий:
   ```bash
   git clone [https://github.com/youruser/async-crawler.git](https://github.com/youruser/async-crawler.git)
   cd async-crawler
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Запуск

Краулер поддерживает гибкую настройку через CLI.

### Примеры команд:

* **Простой запуск по URL:**
    ```bash
    python main.py --url [https://quotes.toscrape.com/](https://quotes.toscrape.com/) --limit 20 --format json
    ```

* **Запуск через Sitemap:**
    ```bash
    python main.py --sitemap [https://books.toscrape.com/sitemap.xml](https://books.toscrape.com/sitemap.xml) --limit 50 --format sqlite
    ```

* **С использованием своего конфига:**
    ```bash
    python main.py --config my_config.yaml
    ```

## ⚙️ Параметры CLI

| Флаг | Описание | Дефолт |
| :--- | :--- | :--- |
| `--url` | Стартовый URL для обхода | None |
| `--sitemap` | Ссылка на sitemap.xml | None |
| `--limit` | Макс. количество страниц | 10 |
| `--format` | Формат (json, sqlite, csv) | json |
| `--config` | Путь к YAML-конфигу | config.yaml |

## 📊 Результаты
После завершения работы краулер генерирует:
1. `results.db` (или другой формат) — собранные данные.
2. `report.html` — визуальный отчет со статистикой.
3. `crawler.log` — подробный лог работы.

## 📝 Структура проекта
* `AsyncCrawler/` — ядро системы (логика, парсер, хранилища).
* `main.py` — точка входа и CLI интерфейс.
* `config.yaml` — настройки по умолчанию.
```