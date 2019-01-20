from abc import ABC, abstractmethod


class AbstractURLManager(ABC):
    root_search_url = ""
    query_parameters = ""

    @abstractmethod
    def url_generator(self):
        pass
