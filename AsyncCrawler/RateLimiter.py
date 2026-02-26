import asyncio
from collections import defaultdict
import random
import time


class RateLimiter:
      def __init__(self, requests_per_second: float = 1.0 + random.uniform(-0.1, 0.1)):
            self.delay = 1.0 / requests_per_second
            self.last_request_time = defaultdict(float)

      async def acquire(self, domain: str):
            now = time.time()
            elapsed = now - self.last_request_time[domain]
            wait_time = self.delay - elapsed

            if wait_time > 0:
                  await asyncio.sleep(wait_time)

            self.last_request_time[domain] = time.time() 