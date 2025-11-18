from abc import ABC, abstractmethod

class Database(ABC):

    @abstractmethod
    def execute_query(self, sql_query: str) -> str:
        pass

    @abstractmethod
    def get_schema(self) -> list[str]:
        pass

    @abstractmethod
    def get_table_info(self, table_name: str, show_sample: bool = True) -> str:
        pass