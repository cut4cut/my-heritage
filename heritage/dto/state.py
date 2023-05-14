from dataclasses import dataclass
import orjson


@dataclass
class SearchState:
    latitude: float = 55.824322
    longitude: float = 37.611089
    page: int = 1

    def __str__(self) -> str:
        return orjson.dumps(self).decode("utf-8")

    def shift(self) -> None:
        self.page += 1
