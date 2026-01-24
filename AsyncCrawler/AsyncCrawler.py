import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple
import ssl

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AsyncCrawler:
    def __init__(self, max_concurent: int = 10):
        self.max_concurent = max_concurent
        self.session: Optional[aiohttp.ClientSession] = None

    async def _create_session(self):
        if self.session is None:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            timeout = aiohttp.ClientTimeout(
                total=30,
                connect=10,
                sock_read=20
            )

            connector = aiohttp.TCPConnector(
                limit=self.max_concurent,
                ssl=ssl_context)

            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )

    async def fetch_url(self, url: str) -> str:
        await self._create_session()

        logger.info(f"Начало загрузки: {url}")

        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(
                        f"Успешно загружен: {url}, статус: {response.status}")
                    return True, content
                else:
                    error_msg = f"HTTP ошибка {response.status} для {url}"
                    logger.error(error_msg)
                    return False, content

        except asyncio.TimeoutError:
            error_msg = f"Таймаут при загрузке {url}"
            logger.error(error_msg)
            return False, error_msg
        except aiohttp.ClientError as e:
            error_msg = f"Cетевая ошибка для {url}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Неизвестная ошибка для {url}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    async def fetch_urls(self, urls: List[str]) -> Dict[str, str]:
        await self._create_session()

        semaphore = asyncio.Semaphore(self.max_concurent)

        async def fetch_with_limit(url: str) -> Tuple[str, Tuple[bool, str]]:
            async with semaphore:
                succes, content = await self.fetch_url(url)
                return url, (succes, content)

        tasks = [fetch_with_limit(url) for url in urls]
        result_list = await asyncio.gather(*tasks)

        return dict(result_list)

    async def close(self):
        if self.session and not self.session.closed:
            logger.info("Сессия закрыта")
