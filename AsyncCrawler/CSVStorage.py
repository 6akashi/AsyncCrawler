import aiofiles
import csv
import io
import os
from AsyncCrawler.DataStorage import DataStorage

class CSVStorage(DataStorage):
    def __init__(self, filename: str):
        self.filename = filename
        self.headers = ["url", "title", "crawled_at", "status_code"]

    async def save(self, data: dict):
        file_exists = os.path.exists(self.filename)
        
        # Используем io.StringIO, чтобы подружить csv.writer с асинхронным aiofiles
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.headers, extrasaction='ignore')
        
        # Если файл новый, пишем заголовки
        if not file_exists:
            writer.writeheader()
            
        # Пишем данные
        writer.writerow(data)
        
        async with aiofiles.open(self.filename, mode='a', encoding='utf-8', newline='') as f:
            await f.write(output.getvalue())
        
        output.close()

    async def close(self):
        pass