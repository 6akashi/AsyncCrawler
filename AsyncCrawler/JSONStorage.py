import json

import aiofiles

from AsyncCrawler.DataStorage import DataStorage


class JSONStorage(DataStorage):
      def __init__(self, filename: str):
            self.filename = filename

      async def save(self, data:dict):
            async with aiofiles.open(self.filename, mode="a", encoding="utf-8") as f:
                  await f.write(json.dumps(data, ensure_ascii=False) + '\n')

      async def close(self):
            pass