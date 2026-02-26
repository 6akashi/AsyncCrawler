import asyncio
from asyncio.log import logger
import random

from AsyncCrawler.Errors import *


class RetryStrategy:
      def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
            self.max_retries = max_retries
            self.backoff_factor = backoff_factor

      async def execute(self, func, *args, **kwargs):
            las_exception = None

            for attempt in range(self.max_retries + 1):
                  try:
                        return await func(*args, **kwargs)
                  except(TransientError, NetworkError) as e:
                        las_exception = e
                        if attempt == self.max_retries:
                              break

                        wait_time = self.backoff_factor * (2 ** attempt) + random.uniform(0,1)
                        logger.warning(f"Попытка {attempt + 1}/{self.max_retries} провалена ({e})"
                                       f"Ждем {wait_time:.2f}с перед повтором...")
                        
                        await asyncio.sleep(wait_time)
                  except PermanentError as e:
                        logger.error(f"Постоянная ошибка: {e}. Повторов не будет")
                        raise e
            logger.error(f"Исчерпанны все попытки({self.max_retries})")
            raise las_exception