import asyncio
from AsyncCrawler.HTMLParser import HTMLParser


async def test_basic_parsing():
    """Тест базового парсинга"""
    print("🧪 Тест базового парсинга")
    print("-" * 40)

    parser = HTMLParser()

    # Простой HTML для тестирования
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Тестовая страница</title>
        <meta name="description" content="Тестовое описание">
        <meta name="keywords" content="тест, парсинг, python">
    </head>
    <body>
        <h1>Главный заголовок</h1>
        <p>Это тестовый текст для парсинга.</p>
        <a href="/page1">Ссылка 1</a>
        <a href="https://example.com/page2">Ссылка 2</a>
        <img src="/image.jpg" alt="Тестовое изображение">
    </body>
    </html>
    """

    url = "https://example.com"
    result = await parser.parse_html(html, url)

    assert result['title'] == "Тестовая страница"
    assert result['text_length'] > 0
    assert len(result['links']) == 2
    assert result['links'][0] == "https://example.com/page1"
    assert result['metadata']['description'] == "Тестовое описание"

    print("✅ Все тесты пройдены!")


async def test_link_conversion():
    """Тест конвертации относительных ссылок"""
    print("\n🧪 Тест конвертации ссылок")
    print("-" * 40)

    parser = HTMLParser()

    html = """
    <html>
    <body>
        <a href="/relative">Относительная ссылка</a>
        <a href="https://absolute.com">Абсолютная ссылка</a>
        <a href="#anchor">Якорь</a>
        <a href="mailto:test@example.com">Email</a>
    </body>
    </html>
    """

    url = "https://example.com"
    result = await parser.parse_html(html, url)

    # Проверяем конвертацию
    assert "https://example.com/relative" in result['links']
    assert "https://absolute.com" in result['links']
    assert len(result['links']) == 2  # Якорь и email не должны быть включены

    print("✅ Конвертация ссылок работает!")


async def test_error_handling():
    """Тест обработки ошибок"""
    print("\n🧪 Тест обработки ошибок")
    print("-" * 40)

    parser = HTMLParser()

    # Битый HTML
    broken_html = "<html><body><p>Незакрытый тег"

    url = "https://example.com"
    result = await parser.parse_html(broken_html, url)

    # Должен вернуть частичные результаты
    assert 'url' in result
    assert result['url'] == url

    print("✅ Обработка ошибок работает!")


async def test_extraction_methods():
    """Тест методов извлечения"""
    print("\n🧪 Тест методов извлечения")
    print("-" * 40)

    parser = HTMLParser()

    html = """
    <html>
    <body>
        <h1>Заголовок 1</h1>
        <h2>Заголовок 2</h2>
        <ul>
            <li>Пункт 1</li>
            <li>Пункт 2</li>
        </ul>
        <table>
            <tr><th>Заголовок</th><th>Значение</th></tr>
            <tr><td>Данные 1</td><td>Данные 2</td></tr>
        </table>
    </body>
    </html>
    """

    url = "https://example.com"
    await parser.parse_html(html, url)

    # Тест заголовков
    headers = parser.extract_headers()
    assert len(headers['h1']) == 1
    assert headers['h1'][0] == "Заголовок 1"

    # Тест списков
    lists = parser.extract_lists()
    assert len(lists) == 1
    assert len(lists[0]) == 2

    # Тест таблиц
    tables = parser.extract_tables()
    assert len(tables) == 1

    print("✅ Методы извлечения работают!")


async def main():
    """Запуск всех тестов"""
    print("🤖 ТЕСТИРОВАНИЕ HTML PARSER")
    print("=" * 50)

    await test_basic_parsing()
    await test_link_conversion()
    await test_error_handling()
    await test_extraction_methods()

    print("\n" + "=" * 50)
    print("✅ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
