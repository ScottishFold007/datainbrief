from abc import ABC, abstractmethod


class AbstractFieldExtractor(ABC):
    item_selectors = dict()

    @abstractmethod
    def extract_item(self,row):
        pass