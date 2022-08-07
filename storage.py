from datetime import datetime
import json
from pathlib import Path
from typing import TypedDict, Protocol

from client_asics import Asic

class AsicStorage(Protocol):
    """Interface for any storage saving asic health"""
    def save(self, health: Asic) -> None:
        raise NotImplementedError

class HistoryRecord(TypedDict):
    date: str
    weather: str


class JSONFileWeatherStorage:
    """Store weather in JSON file"""
    def __init__(self, jsonfile: Path):
        self._jsonfile = jsonfile
        self._init_storage()

    # def save(self, weather: Asic) -> None:
    #     history = self._read_history()
    #     history.append({
    #         "date": str(datetime.now()),
    #         "weather": format_weather(weather)
    #     })
    #     self._write(history)

    def _init_storage(self) -> None:
        if not self._jsonfile.exists():
            self._jsonfile.write_text("[]")

    def _read_history(self) -> list[HistoryRecord]:
        with open(self._jsonfile, "r") as f:
            return json.load(f)

    def _write(self, history: list[HistoryRecord]) -> None:
        with open(self._jsonfile, "w") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)


def save_weather(weather: Asic, storage: AsicStorage) -> None:
    """Saves weather in the storage"""
    storage.save(weather)
