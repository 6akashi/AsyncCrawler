import xml.etree.ElementTree as ET
import aiohttp
import logging

logger = logging.getLogger(__name__)

class SitemapParser:
    async def fetch_sitemap_urls(self, session: aiohttp.ClientSession, sitemap_url: str) -> list[str]:
        urls = []
        try:
            async with session.get(sitemap_url) as response:
                if response.status != 200:
                    logger.error(f"Sitemap вернул статус {response.status}")
                    return []
                
                content = await response.read() # Читаем как байты для ElementTree
                root = ET.fromstring(content)
                
                # Автоматически определяем пространство имен из тега root
                # Например: {http://www.sitemaps.org/schemas/sitemap/0.9}urlset
                ns = ""
                if root.tag.startswith("{"):
                    ns = root.tag.split("}")[0] + "}"
                
                # 1. Ищем вложенные sitemaps (Sitemap Index)
                for sitemap in root.findall(f".//{ns}sitemap"):
                    loc = sitemap.find(f"{ns}loc")
                    if loc is not None:
                        urls.extend(await self.fetch_sitemap_urls(session, loc.text))
                
                # 2. Ищем прямые ссылки на страницы
                for url_tag in root.findall(f".//{ns}url"):
                    loc = url_tag.find(f"{ns}loc")
                    if loc is not None:
                        urls.append(loc.text)
                        
        except Exception as e:
            logger.error(f"Ошибка парсинга Sitemap {sitemap_url}: {e}")
        
        return list(set(urls))