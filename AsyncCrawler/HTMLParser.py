import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class HTMLParser:
    def __init__(self):
        self.soup: Optional[BeautifulSoup] = None

    async def parse_html(self, html: str, url: str) -> Dict:
        try:
            self.soup = BeautifulSoup(html, "lxml")
            
            result = {
                'url': url,
                'title': self.extract_title(),
                'text': self.extract_text(),
                'links': self.extract_links(url),
                'metadata': self.extract_metadata(),
            }
            result['text_length'] = len(result['text'])
            result['links_count'] = len(result['links'])
            return result
        except Exception as e:
            logger.error(f"Ошибка парсинга HTML для {url}: {e}")
            return {'url': url, 'error': str(e), 'links': []}

    def extract_title(self) -> str:
        if self.soup.title and self.soup.title.string:
            return self.soup.title.string.strip()
        h1 = self.soup.find("h1")
        return h1.get_text().strip() if h1 else ""

    def extract_text(self) -> str:
        # Копируем soup, чтобы удаление тегов не испортило ссылки
        temp_soup = BeautifulSoup(str(self.soup), "lxml")
        for tag in temp_soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        text = temp_soup.get_text(strip=True, separator=' ')
        return re.sub(r'\s+', ' ', text).strip()

    def extract_links(self, base_url: str) -> List[str]:
        links = set()
        try:
            for tag in self.soup.find_all('a', href=True):
                href = tag['href'].strip()
                # ИСПРАВЛЕНО: Правильный кортеж для startswith
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                
                absolute_url = urljoin(base_url, href)
                parsed = urlparse(absolute_url)
                if parsed.scheme in ('http', 'https'):
                    links.add(absolute_url)
        except Exception as e:
            logger.warning(f"Ошибка извлечения ссылок: {e}")
        return sorted(list(links))

    def extract_metadata(self) -> Dict:
        metadata = {}
        for meta in self.soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            if name:
                metadata[name.lower()] = meta.get('content', '')
        return metadata