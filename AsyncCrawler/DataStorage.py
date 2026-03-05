from abc import ABC, abstractmethod

class DataStorage(ABC):
      @abstractmethod
      async def save(self, data: dict):
            pass

      @abstractmethod
      async def close(self):
            pass