import json

import aiosqlite

from AsyncCrawler.DataStorage import DataStorage

class SQLiteStorage(DataStorage):
      def __init__(self, db_path: str):
            self.db_path = db_path
            self.db = None

      async def init_db(self):
            self.db = await aiosqlite.connect(self.db_path)
            await self.db.execute('''
                  CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                links TEXT,
                crawled_at TIMESTAMP,
                status_code INTEGER
            )
                                  ''')
            
            await self.db.commit()

      async def save(self, data: dict):
            if not self.db: await self.init_db()
            try:
                  await self.db.execute(
                        "INSERT OR REPLACE INTO pages (url, title, links, crawled_at, status_code) VALUES (?, ?, ?, ?, ?)",
                        (data['url'], data['title'], json.dumps(data['links']), 
                        data['crawled_at'], data.get('status_code', 200))
                  )
                  await self.db.commit()
            except Exception as e:
                  print(f"Ошибка БД: {e}")

      async def close(self):
            if self.db:
                  await self.db.close()