from abc import ABC, abstractmethod


class AbstractItemPipeline(ABC):
    @abstractmethod
    def process_item(self, item, spider):
        pass
