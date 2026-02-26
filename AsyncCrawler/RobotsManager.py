import aiohttp
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import logging

class RobotsManager:
    def __init__(self, user_agent: str = "*"):
        self.user_agent = user_agent
        self.parsers = {}

    async def can_fetch(self, url: str, session: aiohttp.ClientSession) -> bool:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url not in self.parsers:
            robots_url = f"{base_url}/robots.txt"
            rp = RobotFileParser()
            try:
                async with session.get(robots_url, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        rp.parse(content.splitlines())
                        logging.info(f"✅ robots.txt загружен для {base_url}")
                    else:
                        rp.allow_all = True
            except Exception as e:
                logging.warning(f"⚠️ Не удалось загрузить robots.txt для {base_url}: {e}")
                rp.allow_all = True
            self.parsers[base_url] = rp

        return self.parsers[base_url].can_fetch(self.user_agent, url)