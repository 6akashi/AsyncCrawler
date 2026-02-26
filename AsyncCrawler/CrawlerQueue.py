import asyncio
from typing import Set, Tuple


# class CrawlerQueue:
#       def __init__(self):
#             self.queue = asyncio.PriorityQueue()
#             self.visited: Set[str] = set()
#             self.processed_count = 0

#       async def add(self, url: str, depth: int, priority: int = 0):
#             if url not in self.visited:
#                   await self.queue.put((priority, depth, url))
            
#       async def get(self) -> Tuple[int, str]:
#             _, depth, url = await self.queue.get()
#             return depth, url
      
#       def mark_visited(self, url:str):
#             self.visited.add(url)
#             self.processed_count += 1

#       def is_empty(self):
#             return self.queue.empty()

class CrawlerQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.visited: Set[str] = set()
        self.processed_count = 0

    async def add(self, url: str, depth: int):
        if url not in self.visited:
            self.visited.add(url)
            await self.queue.put((url, depth))